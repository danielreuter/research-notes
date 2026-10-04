#!/usr/bin/env bash
# Window 7 (the MVP's -h2 on #596), in the slot bc-2aa33ad8 proposed: wait on the node until START (UTC), then take the whole
# node for the timed window (window.sh, default MODE), then, only on a passed validation, the reference verify of its
# retained passes into this run's directory (verify.sh, CPU).  The window's env (SCHEME, GRAPHS, FP8_GRAPHS, SCHEDULE,
# SHIP_TAR) comes from research run --env.
set -uo pipefail
START=${START:?the slot, UTC}
T=$(date -u -d "$START" +%s)
echo "window7: waiting for $START ($(TZ=America/Los_Angeles date -d "$START" '+%-I:%M %p %Z'))"
while [ "$(date -u +%s)" -lt "$T" ]; do sleep 30; done
echo "window7: asking for the timed lease at $(date -u +%H:%M:%SZ)"
gpu-lease 8 --wait --timed --max-min 20 -- timeout 1140 bash benchmarks/pouw/pearl_c_vllm/window.sh
rc=$?
echo "window7: window.sh exited $rc at $(date -u +%H:%M:%SZ)"
[ "$rc" -eq 0 ] || exit "$rc"
D=${RESEARCH_RUN_DIR:?}
python3 - "$D" <<'EOF' || exit 5
import json, pathlib, sys
d = pathlib.Path(sys.argv[1])
res, e2e = json.loads((d / "result.json").read_text()), json.loads((d / "e2e.json").read_text())
vp = e2e["summary"]["verify_pass"]
bad = []
if res.get("validation", {}).get("status") != "passed":
    bad.append("validation " + str(res.get("validation", {}).get("status")))
if (d / "jit-built.txt").read_text().strip():
    bad.append("a FlashInfer JIT build inside the window")
if not e2e["summary"]["gates"].get("arm"):
    bad.append("the arm's gates")
for p in ("prefill", "decode"):
    if not vp.get(p, {}).get("same_commitment_as_timed"):
        bad.append(f"{p}: the verify pass did not repeat its timed commitment")
    if vp.get(p, {}).get("same_commitment_eager") is False:
        bad.append(f"{p}: its eager replay did not repeat the commitment")
print("window7: validation " + ("passed" if not bad else "FAILED: " + "; ".join(bad)), flush=True)
sys.exit(1 if bad else 0)
EOF
echo "window7: verify from $(date -u +%H:%M:%SZ)"
bash benchmarks/pouw/pearl_c_vllm/verify.sh "${RESEARCH_RUN_ID:?}" 48
