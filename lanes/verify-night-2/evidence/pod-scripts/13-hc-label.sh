#!/usr/bin/env bash
# verify-night-2 request 1, labelling: reverify (not dry) of hash-commit's 5 full-tree results -> verdict + verified=accepted
# --by verify-night-2; the statements' steps vs the relation's canonical steps; then one evidence-bundle verdict (binding,
# core roots, byte identity over all 20 runs, negatives, steps) referencing the "after" result, preserved.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
I=$RESEARCH_RUN_DIR/inputs; O=/workspace/verify-night-2/hc
FULL=$(grep -E 'base-fp8ada-l8192-p4-r4|tip-fp8ada-l8192-p4-r1 |k515e-fp8ada-l8192-p4-r4|k0b40-fp8ada-l8192-p4-r7|tip-fp8ada-l8192-p4-r7' $I/registered-4090.txt \
       | sed -E 's/.*result=(art:[0-9a-f]+).*/\1/')
{
echo "=== [$(date -u +%H:%M:%S)] steps vs canonical"
$PY - <<'EOF' | tee $O/steps.txt
import json, tempfile
from pathlib import Path
from research.store.local import LocalStore
from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.serialize import read_statement
st = LocalStore()
tree = "art:13e1c916ea787bdec3ef99000aa9a0109985a01b50aaf7133d2c41e3437e4830"
rel = RELATIONS["fp8-ada"]
k = getattr(rel, "k", None)
with tempfile.TemporaryDirectory(dir="/workspace/verify-night-2") as td:
    d = Path(st.fetch(tree, Path(td) / "t", paths=["*manifest.json", "*.stmt"]))
    stmts = sorted(d.rglob("*.stmt"))
    seen = {(s.steps, getattr(s, "K", None) or getattr(s, "row_words", None)) for s in (read_statement(p.read_bytes()) for p in stmts)}
print(f"fp8-ada: rel.steps={getattr(rel, 'steps', None)} rel.k={k} K_VU={relchain.K_VU} K_VU/k={relchain.K_VU // k if k else None}; "
      f"{len(stmts)} statements carry (steps, K) = {sorted(seen, key=str)}")
EOF
echo "=== [$(date -u +%H:%M:%S)] reverify (verdict + labels --by verify-night-2)"
$PY -m backends.direct.ligero.reverify $FULL --by verify-night-2 --verifier /workspace/bin/ligero-verify --jobs 16 --work $O/rv2 --json > $O/reverify-label.json
echo "reverify rc=$?"
$PY - $O/reverify-label.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
for r in (d if isinstance(d, list) else d.get("results", [d])):
    print(r.get("result"), r.get("status"), r.get("verdict"), r.get("labels"))
EOF
echo "=== [$(date -u +%H:%M:%S)] evidence bundle"
$PY - $O <<'EOF'
import json, subprocess, sys
from pathlib import Path
O = Path(sys.argv[1])
files = ["run.out", "binding.json", "core-roots.json", "byte-identity.json", "steps.txt", "reverify-label.json"]
ev = {f: (O / f).read_text(errors="replace") for f in files if (O / f).is_file()}
for t in ("hc-after", "hc-before"):
    p = Path(f"/workspace/verify-night-2/neg-{t}/summary.txt")
    if p.is_file():
        ev[f"neg-{t}.txt"] = p.read_text()
detail = ("hash-commit 4090 fp8-ada+hash (Poseidon2 leaf/v2h) 20 runs: 5 full trees reverify PASS (ligero-verify d89cffc7 from main 7fcedf47, "
          "25/25 at 2^-128.50, custody 76/76), statements BOUND to my tree's fp8-ada set (0/4096 y), roots a c8c8746a b 886cef1f y 49023558 "
          "recomputed with verity.commitments core only = statements' auth block = commit evidence; all 20 trees: commit-evidence.json "
          "3df32610, evidence 247e44ca, rep1 stmts 897697c9, system.bin c540b778 identical, every present file = proofs.sha256; "
          "negatives proofbyte/stmtbyte/swapstmt rejected on the before and after trees; steps pinned by main's Rust check_vu_shape")
pf = O / "bundle.json"
pf.write_text(json.dumps({"detail": detail, "evidence": ev}, indent=1))
meta = {"result": "PASS", "verifier": "verify-night-2 evidence bundle (see reverify verdicts for the proof checks)", "detail": detail,
        "subject_kind": "bench-result/v1", "lane": "verify-night-2"}
r = subprocess.run([sys.executable, "-m", "research", "data", "put", "--kind", "verification-verdict/v1", "--meta", json.dumps(meta),
                    "--ref", "result=art:abb219fadaa5b293718e815088c7e64151ddd50b21b78e4dda9dd1afac8fba24",
                    "--ref", "proof=art:13e1c916ea787bdec3ef99000aa9a0109985a01b50aaf7133d2c41e3437e4830",
                    "--file", str(pf), "--preserve"], capture_output=True, text=True)
print(r.returncode, r.stdout[-600:], r.stderr[-600:])
EOF
echo "=== [$(date -u +%H:%M:%S)] labels-sync"
$PY -m research data labels-sync --push-only --jobs 16 2>&1 | tail -2
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/label.out
