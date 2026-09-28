#!/bin/bash
# side_record.sh N: row N's regression record with its frozen v1 reference in reach (VM side).  On a pod `rebaseline run` resolves the
#   reference (fixtures.toml: the row's `artifacts.records` / `artifacts.programs` and the shared `[artifacts]` trees) through the data
#   store, which a pod does not have, so every check but `verdict` skips as "does not apply".  Here the VM fetches those trees, unions
#   them as `<key>/` of a rows root (VERITY_REGRESSION_ROWS_ROOT: plain files, still checked against the frozen sha256 pins), and a side
#   run on the row's pod (fresh custody key) runs `rebaseline run -k r<N>` against the pod's sweep with that root.  Prints the side run
#   id; finish_row.sh N reads its record with SIDE_RUN=<id>.
set -u
N=${1:?row}; H=$(cd "$(dirname "$0")" && pwd); LANE=$RESEARCH_NOTES/lanes/vllm-epoch-run
R="env PYTHONPATH=/workspace/tools/research/src python3 -m research"
IFS='|' read -r POD RUN < <(awk -F'\t' -v n="$N" '$1==n && $8=="live" {print $2"|"$4}' "$LANE/evidence/spend.tsv" | tail -n 1)
[ -n "${RUN:-}" ] || { echo "#$N: no live row"; exit 2; }
KEY=$(python3 -c "import json;print(json.load(open('$H/rows.json'))['rows']['$N']['key'])")
SHA=$($R pods ssh "$POD" -- "sed -n 's/^EPOCH_SHA=//p' /workspace/research/runs/$RUN/evidence/row_env.txt" < /dev/null 2>/dev/null | tail -n 1)
WT=/workspace-wt/epoch-${SHA:0:8}
REF=/tmp/regref-$N; rm -rf "$REF"; mkdir -p "$REF/$KEY"
python3 - "$WT/integrations/vllm/tests/regression/fixtures.toml" "$KEY" "$REF/$KEY" <<'EOF' || exit 3
import os, shutil, subprocess, sys, tomllib
from pathlib import Path
fx, key, dst = sys.argv[1], sys.argv[2], Path(sys.argv[3])
t = tomllib.load(open(fx, "rb"))
trees = [(role, art, "") for role, art in sorted((t["rows"][key].get("artifacts") or {}).items()) if art]
trees += [(name, art, key) for name, art in sorted((t.get("artifacts") or {}).items()) if art]
env = {**os.environ, "PYTHONPATH": "/workspace/tools/research/src"}
for role, art, sub in trees:
    p = subprocess.run([sys.executable, "-m", "research", "data", "fetch", art], capture_output=True, text=True, env=env, cwd="/workspace")
    src = Path(p.stdout.strip().splitlines()[-1]) if p.returncode == 0 and p.stdout.strip() else None
    if src is None or not src.is_dir():
        sys.exit(f"fetch {role} {art} failed: {p.stderr.strip()[-300:]}")
    src = src / sub if sub else src
    if not src.is_dir():
        print(f"{role}: no {sub}/ in {art}"); continue
    n = 0
    for f in src.rglob("*"):
        if f.is_file():
            d = dst / f.relative_to(src)
            if d.exists():
                if d.read_bytes() != f.read_bytes():
                    sys.exit(f"{role}: {d.relative_to(dst)} differs between reference trees")
                continue
            d.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(f, d); n += 1
    print(f"{role} {art[:16]}: {n} files")
EOF
tar czf "$REF.tgz" -C "$REF" "$KEY" && echo "reference root $(du -sh "$REF" | cut -f1) -> $REF.tgz"
cd /workspace
$R run --on "$POD" --project verity --campaign vllm-rebaseline-epoch --custody-r2 --custody-ttl 3h --timeout 7200 --source "$WT" \
  --cwd source/integrations/vllm --send "$REF.tgz" --env ROWNUM="$N" --env EPOCH_SHA="$SHA" --env POD="$POD" \
  -- bash -c "set -u; EV=\$RESEARCH_RUN_DIR/evidence; mkdir -p \$EV; T=\$(cd ../.. && pwd -P); PY=/workspace/venv312/bin/python
export PYTHONPATH=\$T/integrations/vllm:\$T/packages/verity/src:\$T/tools/research/src:\$T/protocols/sampled_proofs RESEARCH_STORE=/workspace/epoch/store GPU_NAME=side
RR=/workspace/epoch/regref-$N; rm -rf \$RR; mkdir -p \$RR; tar xzf \$RESEARCH_RUN_DIR/inputs/regref-$N.tgz -C \$RR
VERITY_REGRESSION_ROWS_ROOT=\$RR VERITY_REGRESSION_CANDIDATE=/workspace/epoch/sweep timeout 5400 \$PY -m tests.regression.rebaseline run --record \$EV/record --tier T0,T1,T2 -- -k r$N -ra > \$EV/rebaseline_run.log 2>&1
rc=\$?; echo \"rebaseline run rc=\$rc \$(grep -E 'passed|failed|error' \$EV/rebaseline_run.log | tail -n 1)\"; exit 0" \
  2>&1 | tee "$LANE/evidence/side-record-$N.txt" | grep -o 'r20[0-9]\{6\}-[0-9]\{6\}-[0-9a-f]\{4\}' | head -n 1
