#!/usr/bin/env bash
# b-ligero-standard-hash: red-team R2 (de2fa317) on real data -- 50-fixcheck.sh's step 4/5 redone: the pinned relation is the
# statement's (`relation.statement_relation`, what `system-digest` pins), not the manifest's base name (that recomputed under
# the Poseidon2 schema), and the dump is the one with rep dirs (the sweep keeps only the plateau's proofs).
#   honest: commitment_problems on the plateau dump, then reverify.verify_tree end to end with /workspace/bin/ligero-verify;
#   negatives on a copy of the statements: a wrong set digest, one tree root flipped, one statement removed (coverage).
# research run --on POD --project verity --cwd /workspace/src --send lib.sh --send 51-r2check.sh \
#     --env DUMP=/workspace/research/runs/r20260925-073210-f45c/sweep/p4-16384/proofs -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/51-r2check.sh"'
IN=$(dirname "$0"); source "$IN/lib.sh"
RD=${RESEARCH_RUN_DIR:?}
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
$PY - "${DUMP:?}" "$RD" "$V" "$NT" <<'EOF'
import dataclasses, json, shutil, sys, time
from pathlib import Path
from backends.direct.ligero import reverify as RV
from backends.direct.ligero.serialize import read_statement, statement_bytes
p, rd, vbin, nt = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), int(sys.argv[4])
man = json.loads((p / "manifest.json").read_text())
pin = man["relation"]["statement_relation"]
reps = sorted(d.name for d in p.iterdir() if d.is_dir() and d.name.startswith("rep"))
t0 = time.time()
print(f"honest commitment_problems ({pin}, reps {reps}):", RV.commitment_problems(p, man, pin, reps), f"{time.time() - t0:.1f}s")
v = RV.Verifier(vbin.resolve(), RV._sha256(vbin), None)
rep = RV.Report("local:plateau")
t0 = time.time()
RV.verify_tree(p, man, v, rep, jobs=nt, params={}, asserted=None, out_dir=rd / "reverify-honest")
print(f"verify_tree: {rep.status} {rep.why} pinned={rep.relation} hashed={rep.hashed} "
      f"accepted={sum(x['accepted'] for x in rep.reps.values())}/{sum(x['n'] for x in rep.reps.values())} {time.time() - t0:.1f}s")
if rep.status == "PASS":
    print(RV.detail(rep, v))
neg = rd / "neg"
for r in reps:
    (neg / r).mkdir(parents=True)
    for f in (p / r).glob("*.stmt"):
        shutil.copy(f, neg / r / f.name)
bad = json.loads(json.dumps(man))
bad["set"]["instances"] = "0" * 64
print("neg wrong set digest:", RV.commitment_problems(neg, bad, pin, reps))
f = sorted((neg / reps[0]).glob("*.stmt"))[0]
orig = f.read_bytes()
st = read_statement(orig)
ha = st.hash_auth
t0_ = ha.trees[0]
flipped = dataclasses.replace(t0_, root=bytes([t0_.root[0] ^ 1]) + t0_.root[1:])
f.write_bytes(statement_bytes(dataclasses.replace(st, hash_auth=dataclasses.replace(ha, trees=(flipped, *ha.trees[1:])))))
print("neg flipped a root:", RV.commitment_problems(neg, man, pin, reps))
f.write_bytes(orig)
print("control (restored):", RV.commitment_problems(neg, man, pin, reps))
f.rename(f.with_suffix(".off"))
print("neg removed statement:", RV.commitment_problems(neg, man, pin, reps))
EOF
echo "r2check rc=$?"
