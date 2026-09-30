#!/usr/bin/env bash
# sm_120 TP2 on one host (lane vllm-sm120-kernels): two RTX PRO 6000 GPUs, NCCL with P2P off.  The device gate (both GPUs), the pod
# runtime (pod_bootstrap.sh --cpu), the two-rank collectives against AllReduce2_v1 / AllGather2_v1 op-level (collectives_difftest) and
# inside a tiny TP2 vLLM engine (sm120_tp2_live.py), and the TP2 vocabulary-range property.  (The quarantine AllReduceSumBf16 adapter
# spawns rank processes that re-import the verity-vllm launcher and hang the parent: not run.)
# research run --on <pod> --project verity --custody-r2 --source <tree> --cwd source --send captures_tp2.sh --send sm120_tp2_live.py \
#   -- bash -c 'bash "$RESEARCH_RUN_DIR/inputs/captures_tp2.sh"'
set -uo pipefail
T=$(pwd -P); IN=$RESEARCH_RUN_DIR/inputs; OUT=$RESEARCH_RUN_DIR/out; mkdir -p "$OUT"
VENV=/workspace/venv312; PY=$VENV/bin/python
export CUDA_HOME=/usr/local/cuda-12.9; export PATH=$CUDA_HOME/bin:$PATH
export NCCL_P2P_DISABLE=1
log() { echo "[sm120-tp2] $(date -u +%FT%TZ) $*" | tee -a "$OUT/steps.log"; }
declare -A V
step() { local name=$1; shift; log "BEGIN $name"; if "$@" >"$OUT/$name.log" 2>&1; then V[$name]=PASS; else V[$name]="FAIL rc=$?"; fi; log "END $name ${V[$name]} ($(tail -1 "$OUT/$name.log" | cut -c1-240))"; }

nvidia-smi --query-gpu=index,name,driver_version,compute_cap,memory.total --format=csv,noheader | tee "$OUT/nvidia_smi.csv"
nvidia-smi topo -m > "$OUT/topo.txt" 2>&1; cat "$OUT/topo.txt"
python3 - "$OUT/nvidia_smi.csv" <<'EOF' || { log "DEVICE-GATE-FAIL"; exit 40; }
import sys
rows = [r.split(", ") for r in open(sys.argv[1]).read().strip().splitlines()]
bad = [] if len(rows) == 2 else [f"{len(rows)} GPUs, not 2"]
for idx, name, drv, cc, mem in rows:
    if int(drv.split(".")[0]) < 575: bad.append(f"gpu {idx}: driver {drv} < 575")
    if cc.strip() != "12.0": bad.append(f"gpu {idx}: compute capability {cc} != 12.0")
    if "RTX PRO 6000" not in name: bad.append(f"gpu {idx}: {name}")
print("DEVICE-GATE", "FAIL " + "; ".join(bad) if bad else "OK", rows)
sys.exit(1 if bad else 0)
EOF

cd "$T/integrations/vllm"
step bootstrap bash verity_vllm/ops/pod_bootstrap.sh --cpu --cases B0 --out "$OUT/bootstrap"
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
export PATH=$VENV/bin:$PATH HF_HOME=/workspace/hf
$PY - <<'EOF' | tee "$OUT/device.json" || { log "DEVICE-GATE-FAIL (torch)"; exit 40; }
import json, sys, torch
d = [{"i": i, "name": torch.cuda.get_device_name(i), "cc": list(torch.cuda.get_device_capability(i)),
      "sms": torch.cuda.get_device_properties(i).multi_processor_count} for i in range(torch.cuda.device_count())]
p2p = torch.cuda.can_device_access_peer(0, 1) if len(d) == 2 else None
print(json.dumps({"devices": d, "can_device_access_peer_0_1": p2p, "nccl": ".".join(map(str, torch.cuda.nccl.version())), "torch": torch.__version__}))
sys.exit(0 if len(d) == 2 and all(x["cc"] == [12, 0] and x["sms"] == 188 for x in d) else 1)
EOF
log "device gate OK (2 x 188 SMs, cc 12.0)"

AD=verity_vllm.program.registry
step collectives_produce verity-vllm properties-admission produce --adapter $AD.collectives_difftest --n 30 --seed 5 --out "$OUT/collectives"
step collectives_check verity-vllm properties-admission check --adapter $AD.collectives_difftest --dir "$OUT/collectives" --out "$OUT/collectives/collectives.json"
step tp2_live $PY "$IN/sm120_tp2_live.py" "$OUT/tp2_live"
step vocab_range_tp2 $PY tests/properties/vocab_range_exactness_gpu.py --case tiny --out "$OUT/vocab_range"

{ printf '{'; first=1; for k in "${!V[@]}"; do [ $first = 1 ] || printf ','; first=0; printf '"%s": "%s"' "$k" "${V[$k]}"; done; printf '}\n'; } > "$OUT/summary.json"
log "SUMMARY $(cat "$OUT/summary.json")"
echo "SM120-TP2-DONE"
