#!/usr/bin/env bash
# sm_120 kernel captures, job A (lane vllm-sm120-kernels): the device gate, the pod runtime (pod_bootstrap.sh --cpu: venv312,
# the pinned vLLM d9105ea80 cu129 wheel, B0's checkpoint), then the existing exactness checks of the kernels this lane owns:
#   norm tap (fused CUDA RMSNorm + Triton RMSNorm + the norm-scale source), router tap (MoE topk_softmax), the top-p split probe
#   (every S, drain), the Gumbel top-p token select difftest.
# research run --on <pod> --project verity --custody-r2 --source <tree> --cwd source --send captures_a.sh -- bash "$RESEARCH_RUN_DIR/inputs/captures_a.sh"
# Exit 40 = device gate failed (terminate the pod); otherwise 0, with every step's verdict in $OUT/summary.json.
set -uo pipefail
T=$(pwd -P)
OUT=${RESEARCH_RUN_DIR:-/workspace/sm120}/out; mkdir -p "$OUT"
VENV=/workspace/venv312; PY=$VENV/bin/python
log() { echo "[sm120-a] $(date -u +%FT%TZ) $*" | tee -a "$OUT/steps.log"; }
declare -A V
step() { local name=$1; shift; log "BEGIN $name"; if "$@" >"$OUT/$name.log" 2>&1; then V[$name]=PASS; else V[$name]="FAIL rc=$?"; fi; log "END $name ${V[$name]} ($(tail -1 "$OUT/$name.log" | cut -c1-200))"; }

# ---- 0. device gate (before anything is installed) ----
nvidia-smi --query-gpu=index,name,driver_version,compute_cap,memory.total --format=csv,noheader | tee "$OUT/nvidia_smi.csv"
nvidia-smi > "$OUT/nvidia_smi.txt" 2>&1
python3 - "$OUT/nvidia_smi.csv" <<'EOF' || { log "DEVICE-GATE-FAIL"; exit 40; }
import sys
rows = [r.split(", ") for r in open(sys.argv[1]).read().strip().splitlines()]
bad = []
for idx, name, drv, cc, mem in rows:
    if int(drv.split(".")[0]) < 575: bad.append(f"gpu {idx}: driver {drv} < 575")
    if cc.strip() != "12.0": bad.append(f"gpu {idx}: compute capability {cc} != 12.0")
    if "RTX PRO 6000" not in name: bad.append(f"gpu {idx}: {name} is not an RTX PRO 6000")
print("DEVICE-GATE", "FAIL " + "; ".join(bad) if bad else "OK", rows)
sys.exit(1 if bad else 0)
EOF
log "device gate (driver, cc) OK"

# ---- 1. runtime: venv312 + vLLM d9105ea80 + torch cu129 + B0 (no native taps: this lane builds only its own two) ----
cd "$T/integrations/vllm"
step bootstrap bash verity_vllm/ops/pod_bootstrap.sh --cpu --cases B0 --out "$OUT/bootstrap"
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
export PATH=$VENV/bin:$PATH HF_HOME=/workspace/hf

# ---- 2. the device as torch and vLLM see it: 188 SMs, cc 12.0, sm_120 code in the wheel ----
$PY - "$OUT/device.json" <<'EOF' || { log "DEVICE-GATE-FAIL (torch)"; cat "$OUT/device.json" 2>/dev/null; exit 40; }
import glob, json, os, subprocess, sys
import torch, vllm, triton
p = torch.cuda.get_device_properties(0)
d = {"name": p.name, "cc": [p.major, p.minor], "multi_processor_count": p.multi_processor_count, "total_memory": p.total_memory,
     "device_count": torch.cuda.device_count(), "torch": torch.__version__, "torch_cuda": torch.version.cuda,
     "torch_arch_list": torch.cuda.get_arch_list(), "vllm": vllm.__version__, "triton": triton.__version__,
     "python_import_verity_sampled_proofs": __import__("verity_sampled_proofs").__file__}
try:
    from vllm.utils.platform_utils import num_compute_units
except Exception:
    num_compute_units = None
d["vllm_num_compute_units"] = num_compute_units(0) if num_compute_units else None
vdir = os.path.dirname(vllm.__file__)
elf = {}
for so in sorted(glob.glob(os.path.join(vdir, "_*C*.so")) + glob.glob(os.path.join(vdir, "vllm_flash_attn", "_vllm_fa2_C*.so"))):
    r = subprocess.run(["cuobjdump", "--list-elf", so], capture_output=True, text=True)
    archs = sorted({t for line in r.stdout.splitlines() for t in line.replace(".", " ").split() if t.startswith("sm_")})
    r2 = subprocess.run(["cuobjdump", "--list-ptx", so], capture_output=True, text=True)
    ptx = sorted({t for line in r2.stdout.splitlines() for t in line.replace(".", " ").split() if t.startswith("sm_")})
    elf[os.path.basename(so)] = {"sass": archs, "ptx": ptx}
d["vllm_native"] = elf
bad = []
if (p.major, p.minor) != (12, 0): bad.append(f"cc {p.major}.{p.minor}")
if p.multi_processor_count != 188: bad.append(f"multi_processor_count {p.multi_processor_count} != 188")
if "sm_120" not in d["torch_arch_list"]: bad.append(f"torch arch list {d['torch_arch_list']} has no sm_120")
if "d9105ea80" not in vllm.__version__: bad.append(f"vllm {vllm.__version__}")
for so in ("_C.abi3.so", "_moe_C.abi3.so"):
    if so in elf and "sm_120" not in elf[so]["sass"]: bad.append(f"{so}: no sm_120 SASS ({elf[so]})")
d["gate"] = "FAIL " + "; ".join(bad) if bad else "OK"
json.dump(d, open(sys.argv[1], "w"), indent=1)
print(json.dumps(d))
sys.exit(1 if bad else 0)
EOF
log "device gate (torch, 188 SMs, sm_120 SASS) OK"
step epoch_device verity-vllm epoch device --expect-sms 188 --expect-cc 12.0

# ---- 3. norm tap: build for sm_120, then the full exactness property ----
step norm_tap_build env VENV=$VENV bash verity_vllm/ops/pod_norm_tap.sh
step norm_tap_exactness $PY tests/properties/norm_tap_exactness_gpu.py --so /workspace/cp/norm_tap/build/verity_norm_tap.so --out "$OUT/norm_tap"
cp /workspace/cp/norm_tap/build/build_info.json "$OUT/norm_tap_build_info.json" 2>/dev/null

# ---- 4. router tap (topk_softmax): build, exactness (op-level + live on the tiny MoE engines) ----
step router_tap_build env VENV=$VENV bash verity_vllm/ops/pod_router_tap.sh
step router_tap_exactness $PY tests/properties/router_tap_exactness_gpu.py --so /workspace/cp/router_tap/build/verity_router_tap.so --out "$OUT/router_tap"
cp /workspace/cp/router_tap/build/build_info.json "$OUT/router_tap_build_info.json" 2>/dev/null

# ---- 5. top-p split: every S with ties, the drain through vLLM's own entry at this device's SM count ----
step topp_probe_produce verity-vllm topp-split-probe produce --out "$OUT/topp_probe"
step topp_probe_check verity-vllm topp-split-probe check --dir "$OUT/topp_probe" --out "$OUT/topp_probe/check.json"

# ---- 6. Gumbel top-p token select (temperature, split top-p, seeded Gumbel) against Sampler.sample's kernels ----
step gumbel_produce verity-vllm properties-admission produce --adapter verity_vllm.program.registry.sampling_topp_difftest --n 40 --seed 13 --out "$OUT/gumbel"
step gumbel_check verity-vllm properties-admission check --adapter verity_vllm.program.registry.sampling_topp_difftest --dir "$OUT/gumbel" --out "$OUT/gumbel/sampling_topp.json"

# ---- summary ----
{ printf '{'; first=1; for k in "${!V[@]}"; do [ $first = 1 ] || printf ','; first=0; printf '"%s": "%s"' "$k" "${V[$k]}"; done; printf '}\n'; } > "$OUT/summary.json"
log "SUMMARY $(cat "$OUT/summary.json")"
echo "SM120-A-DONE"
