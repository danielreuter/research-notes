#!/usr/bin/env bash
# agkr-nvf4 negatives: the fp4-nvf4 battery (gpu.nvf4.negatives) proved by the GPU prover and checked by the Python
# verifier (gpu.run negatives) and the independent Rust verifier (negatives + mutate on the honest control proof).
# usage: 03_negatives.sh STMT OUT
set -uo pipefail
source /workspace/env.sh
STMT=$1; O=$2; rm -rf $O; mkdir -p $O
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
V=/workspace/bin/verity-gkr-verify
echo "== build $(date -u +%H:%M:%S)"
$PY -m gpu.nvf4.negatives build --stmt $STMT --out $O/dir 2>&1 | grep -v Warn | tail -3
echo "== honest control $(date -u +%H:%M:%S)"
$PY -m gpu.run prove $O/dir --proof-out $O/honest.bin --json $O/honest_py.json 2>&1 | grep -E "verified|written|Error" | cut -c1-200
$V verify --dir $O/dir --proof $O/honest.bin --threads 15 --json $O/honest_rust.json; echo "rust honest rc=$?"
echo "== python negatives $(date -u +%H:%M:%S)"
$PY -m gpu.run negatives $O/dir --proof-dir $O/negproofs --json $O/neg_py.json 2>&1 | grep -vE "Warn|searchsorted" | tail -4
echo "== rust negatives $(date -u +%H:%M:%S)"
$V negatives --dir $O/dir --proofs $O/negproofs --threads 15 --json $O/neg_rust.json | tail -2; echo "rust negatives rc=$?"
echo "== rust mutate (honest control) $(date -u +%H:%M:%S)"
$V mutate --dir $O/dir --proof $O/honest.bin --threads 15 --sample 24 --json $O/mutate_rust.json | tail -4; echo "rust mutate rc=$?"
python3 - $O <<'EOF'
import json, sys
o = sys.argv[1]
py = json.load(open(f"{o}/neg_py.json")); ru = json.load(open(f"{o}/neg_rust.json"))
acc_py = [k for k, v in py["results"].items() if not v["rejected"]]
acc_ru = [r["id"] for r in ru["results"] if not r["rejected"]]
where = {}
for v in py["results"].values():
    where[v["where"]] = where.get(v["where"], 0) + 1
print(json.dumps({"python": f"{py['rejected']}/{py['total']}", "python_where": where, "python_accepted": acc_py,
                  "rust": f"{ru['rejected']}/{ru['total']}", "rust_accepted": acc_ru}))
EOF
echo "== done $(date -u +%H:%M:%S)"
