#!/usr/bin/env bash
# verify-night-3: G3 part 2. Regenerate the route (a) statements myself (tools/cell.py statement, CPU, from the frozen
# bench-instances/v1 rebuilt from the committed seeds), compare them with the producer's (prime_commitment, leaf digests,
# sigma, commitment, public words), then re-run the gate battery at 4096 and 1024 against MY statements. The 1024 public.bin
# is not in the store, so the 1024 battery of 50-g3-route-a.sh could not run the prime verifier (rc 2).
set -uxo pipefail
SRC=$(pwd); O=$RESEARCH_RUN_DIR/out; mkdir -p $O
SRC=$SRC BENCH_INSTANCES=1 SKIP_RUST=1 HEALTH=0 bash backends/direct/ligero/pod_bootstrap.sh > $O/bootstrap.log 2>&1; grep -E "FAILED|manifest" $O/bootstrap.log | tail -5
source /workspace/env.sh
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC:$SRC/backends/gkr:$SRC/backends/gkr/tools"
D=/workspace/g3; P=$D/prover/out; cd $SRC/backends/gkr
for v in 1024 4096; do
  M=$D/mine/c$v; rm -rf $M; mkdir -p $M
  $PY tools/cell.py statement --cell $M --instances /workspace/bench-instances/v1 --vus $v --flock /workspace/bin/flock-link-live 2>&1 | tail -2
  $PY - $M $P $v <<'EOF' | tee $O/statement-compare-$v.json
import hashlib, json, sys
from pathlib import Path
m, p, v = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
h = lambda f: hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
mine, theirs = json.loads((m / "cell.json").read_text()), json.loads((p / f"statements/cell-{v}.json").read_text())
out = {"vus": int(v), "cell_json": {k: [mine.get(k), theirs.get(k), mine.get(k) == theirs.get(k)] for k in ("relation", "prime_commitment", "manifest_sha256", "sigma")},
       "leaf_digests": [h(m / "leaf_digests.bin"), h(p / f"statements/leaf_digests-{v}.bin")],
       "statement_files": {f.name: [h(f), h(p / f"cell-{v}/statement" / f.name), h(p / f"statement-{v}" / f.name)] for f in sorted((m / "statement").iterdir())}}
out["leaf_digests"].append(out["leaf_digests"][0] == out["leaf_digests"][1])
print(json.dumps(out, indent=1))
EOF
  CD=$D/cells-mine/c$v; rm -rf $CD; mkdir -p $D/cells-mine; cp -r $P/cell-$v $CD; rm -rf $CD/statement; cp -r $M/statement $CD/statement
  PC=$($PY -c "import json,sys;print(json.load(open(sys.argv[1]))['prime_commitment'])" $M/cell.json)
  python3 $D/gate/inputs/gate_battery.py --sessions $D/verifier/out/sessions-$v --cells $CD --statement $CD/statement \
      --digests $M/leaf_digests.bin --prime-commitment $PC --vus $v --rust /workspace/bin/verity-gkr-verify-live \
      --flock /workspace/bin/flock-link-live --threads $(nproc) --producer route-a-live --out $O/gate-$v 2>&1 | tail -n 25 | cut -c1-300
  echo "battery-$v rc=${PIPESTATUS[0]}"
done
true
