#!/usr/bin/env bash
# vo_match73.sh: the optional part of task 2 on an H100: row #73's Match under fa3_construction = "check-inf-per-iteration".
#   The capture's engine target comes only from the workload's `target` block (`vllm_adapter.load_workload` -> `build.target_of_workload`;
#   `verity-vllm match` passes no --target), and the fold reads the target back from the capture's RunHeader
#   (`TargetProfile.from_run_profile`).  So, in a working copy of the shipped tree, row #73's workload gains
#   `target = {compute_capability [9,0], num_sms 132, fa3_construction check-inf-per-iteration}` -- the H100's own facts plus the knob,
#   the way a row declares a construction (#74 declares fp8_block_gemm there).  The Build reused is the lane's check-inf Build (its 10
#   Programs, derived under the same declared target; r20260927-070351-283d, art:622fbaf1): GP-01's workload Program and the manifest are
#   recomposed over the edited workload so that its sha256 is the one GM-01 G1 checks against the capture header and the Program.
#   Precondition (stop if it fails): a one-token probe capture of the edited workload must carry fa3_construction in its RunHeader.
#   Then `row run ... --stages match` (capture, fold, GM-01 against the check-inf workload Program).
set -u
L=$RESEARCH_RUN_DIR; I=$L/inputs; EV=$L/evidence; mkdir -p "$EV"; S=$PWD
ROW=qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager; ROLE=QWEN3_4B; REPO=Qwen/Qwen3-4B-Instruct-2507
REV=cdbee75f17c01a7cc42f958dc650907174af0554
CK=/workspace/hf/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots/$REV
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
(cd integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --cases "$ROLE" --out /workspace/bootstrap) > "$L/bootstrap.log" 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 "$L/bootstrap.log")"
T=/workspace/vo/tree73m; rm -rf "$T"; mkdir -p /workspace/vo; cp -r "$S" "$T"
WL=$T/integrations/vllm/workloads/$ROW.json
python3 - "$WL" "$EV/workload-edit.json" <<'PY'
import hashlib, json, sys
p = sys.argv[1]
raw = open(p, "rb").read()
d = json.loads(raw)
assert "target" not in d, d.get("target")
d["target"] = {"compute_capability": [9, 0], "num_sms": 132, "fa3_construction": "check-inf-per-iteration"}
new = (json.dumps(d, indent=1) + "\n").encode()
open(p, "wb").write(new)
json.dump({"workload": p, "sha256_before": hashlib.sha256(raw).hexdigest(), "sha256_after": hashlib.sha256(new).hexdigest(),
           "target": d["target"]}, open(sys.argv[2], "w"), indent=1)
print("workload target block added", d["target"])
PY
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 VLLM_BATCH_INVARIANT=1 TOKENIZERS_PARALLELISM=false
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
SW=/workspace/vo/sweep-m73; D=$SW/$ROW; rm -rf "$SW"; mkdir -p "$SW"
tar -xf "$I/r73-v4.tar" -C "$SW" && mv "$SW/r73-v4" "$D"
cd "$T/integrations/vllm"
# the precondition: a one-token probe capture of the edited workload (its RunHeader), beside the recompose
( python -m verity_vllm.pipeline.cli m1-capture --workload "workloads/$ROW.json" --case "$ROLE" --max-num-seqs 8 --checkpoints manifests/checkpoints.json \
    --max-tokens 1 --snapshot-steps 0 --out /workspace/vo/probe73 > "$L/probe.log" 2>&1; echo "probe rc=$? $(date -u +%FT%TZ)" >> "$L/probe.log" ) &
PROBE=$!
DER=(--derived "$D/build_request"); for x in "$D"/build_request_LP*; do [ -d "$x" ] && DER+=(--derived "$x"); done
python -m verity_vllm.pipeline.cli global-program --workload "workloads/$ROW.json" "${DER[@]}" --out "$D/build_workload" --checkpoint-dir "$CK" \
  > "$D/build_workload.log" 2>&1
WD=$(python -c "from verity_vllm.pipeline import row_records as R; print(R.workload_digest('$D'))")
python -c "from verity_vllm.pipeline import row_records as R; R.add_workload('$D', '$WD', 0 if '$WD' else 1)"
echo "GP-01 recomposed over the edited workload: workload digest $WD $(date -u +%FT%TZ)"
python -m verity_vllm.pipeline.cli manifest build-global --fixture "workloads/$ROW.json" --programs-root "$D" --workload-digest "$WD" \
  --out "$D/manifest.json" > "$D/manifest.log" 2>&1
echo "manifest rc=$? $(tail -c 300 "$D/manifest.log" | tr '\n' ' ')"
wait $PROBE
tail -3 "$L/probe.log"
python3 - /workspace/vo/probe73 "$EV/probe-target.json" <<'PY' || { echo "PRECONDITION-FAIL: the capture does not carry the declared target"; exit 3; }
import gzip, json, os, sys
root, out = sys.argv[1], sys.argv[2]
found = []
for dp, _dn, fns in os.walk(root):
    for fn in fns:
        p = os.path.join(dp, fn)
        try:
            txt = (gzip.open(p, "rt").read(4 << 20) if fn.endswith(".gz") else open(p, errors="replace").read(4 << 20))
        except Exception:
            continue
        if "fa3_construction" in txt:
            k = txt.find("fa3_construction")
            found.append({"file": os.path.relpath(p, root), "context": txt[max(0, k - 200):k + 80]})
json.dump({"found": found}, open(out, "w"), indent=1)
print(json.dumps(found)[:1200])
sys.exit(0 if any("check-inf-per-iteration" in f["context"] for f in found) else 1)
PY
echo "PRECONDITION-OK $(date -u +%FT%TZ)"
cd "$T/integrations/vllm"
export SWEEP_DIR=$SW PY=/workspace/venv312/bin/python
python -m verity_vllm.pipeline.cli row run "$ROW" "$ROLE" "$REPO" "$REV" --stages match > "$L/match.log" 2>&1
echo "match rc=$? $(date -u +%FT%TZ)"
cp "$D/stages.txt" "$D/row.log" "$D/global_match.json" "$D/match_summary.json" "$D/match_decomp.json" "$D/global_match.log" "$EV/" 2>/dev/null
for f in fold_summary.json gates.json run.json card.json; do cp "$D/match/$f" "$EV/match-$f" 2>/dev/null; done
python3 - "$D" "$EV/match73-summary.json" <<'PY'
import json, sys
from collections import Counter
d, out = sys.argv[1], sys.argv[2]
res = {}
try:
    fs = json.load(open(f"{d}/match/fold_summary.json"))
    bs = fs.get("by_spec") or (fs.get("report") or {}).get("by_spec") or {}
    fam = Counter()
    for k, v in bs.items():
        fam[k.split("{")[0].rsplit(":", 1)[-1]] += v if isinstance(v, int) else 0
    res["fold_attention"] = {k: v for k, v in fam.items() if k.startswith("Attention")}
except Exception as e:
    res["fold_attention"] = f"unreadable: {e}"
for f in ("match_summary.json", "global_match.json"):
    try:
        j = json.load(open(f"{d}/{f}"))
        res[f] = {k: j.get(k) for k in ("ok", "verdict", "pass", "checks", "summary", "gates", "tokens_equal", "fold") if k in j}
    except Exception as e:
        res[f] = f"unreadable: {e}"
res["stages_tail"] = open(f"{d}/stages.txt").read().splitlines()[-2:]
json.dump(res, open(out, "w"), indent=1, default=str)
print(json.dumps(res, default=str)[:3000])
PY
echo "MATCH73-DONE $(date -u +%FT%TZ)"
