#!/usr/bin/env bash
# b-ligero-standard-hash: red-team-standard-hash R1 / R2 fix check (3af90e71 + de2fa317), producer-side:
#   1. rebuild /workspace/bin/ligero-verify from the synced tree, cargo test;
#   2. pytest hashauth_test (layout rule), sweep_vu_test, blake3_test;
#   3. the red team's harness rtsh_remap_e2e.py (lane/red-team-standard-hash 8ace1ada, sent as an input) with and without
#      --set-binding: must exit 1 ("not reproduced"), the forgery refused by Python, Rust and reverify;
#   4. R2 on honest data: reverify.commitment_problems on every dumped sweep point of SWEEP_RUN (trees recomputed from the
#      set must equal the statements'), then reverify.verify_tree end to end on the smallest dumped point;
#   5. R2 negatives on a copy of that dump: a wrong set digest, a statement removed from a rep (coverage), one tree root flipped.
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 50-fixcheck.sh --send rtsh_remap_e2e.py \
#     --env SWEEP_RUN=r20260925-073210-f45c -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/50-fixcheck.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}; SW=/workspace/research/runs/${SWEEP_RUN:?}/sweep
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
SRC=$(pwd)
export PATH="$HOME/.cargo/bin:$PATH" CARGO_TARGET_DIR=/workspace/cargo-target
(cd backends/ligero-verify && cargo build --release 2>&1 | tail -n 2 && cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ \
  && sha256sum /workspace/bin/ligero-verify && cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked" | head -n 20)
$PY -m pytest -q backends/direct/ligero/hashauth_test.py backends/direct/ligero/sweep_vu_test.py backends/direct/ligero/leaf/blake3_test.py 2>&1 | tail -n 4
echo "pytest rc=${PIPESTATUS[0]}"

cp $IN/rtsh_remap_e2e.py backends/direct/ligero/redteam/rtsh_remap_e2e.py
for sb in "" "--set-binding"; do
  $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $V --out $RD/remap${sb:+-sb} $sb > $RD/remap${sb:+-sb}.log 2>&1
  echo "rtsh_remap_e2e ${sb:-plain}: rc=$? (1 = not reproduced)"; grep -E "^(forgery|control):|not reproduced|R1:" $RD/remap${sb:+-sb}.log | cut -c1-400
done
rm -f backends/direct/ligero/redteam/rtsh_remap_e2e.py

$PY - "$SW" "$RD" "$V" <<'EOF'
import json, shutil, sys
from pathlib import Path
from backends.direct.ligero import reverify as RV
sw, rd, vbin = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
dumps = sorted((p for p in sw.glob("p*/proofs") if (p / "manifest.json").is_file()), key=lambda p: int(p.parent.name.split("-")[1]))
print("dumped points:", [p.parent.name for p in dumps])
for p in dumps:
    man = json.loads((p / "manifest.json").read_text())
    reps = sorted(d.name for d in p.iterdir() if d.is_dir() and d.name.startswith("rep"))
    pin = man["relation"]["name"]
    print(f"{p.parent.name}: commitment_problems reps={reps}:", RV.commitment_problems(p, man, pin, reps))
if not dumps:
    sys.exit(0)
p = dumps[0]
man = json.loads((p / "manifest.json").read_text())
v = RV.Verifier(vbin.resolve(), RV._sha256(vbin), None)
rep = RV.Report(f"local:{p.parent.name}")
RV.verify_tree(p, man, v, rep, jobs=4, params={}, asserted=None, out_dir=rd / "reverify-honest")
print(f"verify_tree {p.parent.name}: {rep.status} {rep.why} pinned={rep.relation} hashed={rep.hashed}")
print(RV.detail(rep, v) if rep.status == "PASS" else "")
neg = rd / "neg"
shutil.copytree(p, neg)
reps = sorted(d.name for d in neg.iterdir() if d.is_dir() and d.name.startswith("rep"))
pin = rep.relation or man["relation"]["name"]
bad = json.loads(json.dumps(man)); bad["set"]["instances"] = "0" * 64
print("neg wrong set digest:", RV.commitment_problems(neg, bad, pin, reps))
from backends.direct.ligero.serialize import read_statement, statement_bytes
stmts = sorted((neg / reps[0]).glob("*.stmt"))
f = stmts[0]
st = read_statement(f.read_bytes())
ha = st.hash_auth
t0 = ha.trees[0]
flipped = type(t0)(t0.name, t0.binding, t0.owner, t0.count, bytes([t0.root[0] ^ 1]) + t0.root[1:])
import dataclasses
st2 = dataclasses.replace(st, hash_auth=dataclasses.replace(ha, trees=(flipped, *ha.trees[1:])))
orig = f.read_bytes()
f.write_bytes(statement_bytes(st2))
print("neg flipped root:", RV.commitment_problems(neg, man, pin, reps))
f.write_bytes(orig)
f.rename(f.with_suffix(".stmt.off"))
print("neg removed statement:", RV.commitment_problems(neg, man, pin, reps))
EOF
echo "r2 checks rc=$?"
