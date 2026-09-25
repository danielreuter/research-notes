#!/usr/bin/env bash
# b-ligero-standard-hash: red-team R4 fix check -- the red team's rtsh_orphan_e2e.py (lane/red-team-standard-hash 21393756,
# sent as an input) must print "not reproduced" with the control PASSING and both variants FAILING; then the honest plateau
# dump still passes commitment_problems, and a proof removed from a copy of it (manifest unchanged) is refused.
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 52-r4check.sh --send rtsh_orphan_e2e.py \
#     --env DUMP=/workspace/research/runs/r20260925-073210-f45c/sweep/p4-16384/proofs -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/52-r4check.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
cp $IN/rtsh_orphan_e2e.py backends/direct/ligero/redteam/rtsh_orphan_e2e.py
$PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $V --out $RD/orphan > $RD/orphan.log 2>&1
echo "rtsh_orphan_e2e rc=$? (1 = not reproduced)"; grep -vE "^\s*$" $RD/orphan.log | tail -n 8 | cut -c1-500
rm -f backends/direct/ligero/redteam/rtsh_orphan_e2e.py
$PY - "${DUMP:?}" "$RD" <<'EOF'
import json, os, sys
from pathlib import Path
from backends.direct.ligero import reverify as RV
p, rd = Path(sys.argv[1]), Path(sys.argv[2])
man = json.loads((p / "manifest.json").read_text())
pin = man["relation"]["statement_relation"]
reps = sorted(d.name for d in p.iterdir() if d.is_dir() and d.name.startswith("rep"))
print("honest:", RV.commitment_problems(p, man, pin, reps))
neg = rd / "neg"
for r in reps:
    (neg / r).mkdir(parents=True)
    for f in (p / r).iterdir():
        os.symlink(f, neg / r / f.name)
(neg / reps[0] / "sub_07.proof").unlink()
print("neg proof removed:", RV.commitment_problems(neg, man, pin, reps))
EOF
echo "r4 honest/neg rc=$?"
