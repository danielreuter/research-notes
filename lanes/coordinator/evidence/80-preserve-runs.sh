#!/usr/bin/env bash
# coordinator: give every run dir on this pod custody on R2 before the pod is terminated (no waiver). Runs inside a
# `research run --on POD --custody-r2 --source . --cwd source` job and uses that job's own staged, delete-free key.
set -u
RUNS=${RUNS_DIR:-/workspace/research/runs}
C=/workspace/research/requests/${RESEARCH_RUN_ID:?}/custody
[ -f $C/cred.json ] || { echo "no staged custody key at $C"; exit 2; }
PY=${PY:-python3}
export PYTHONPATH=$PWD/tools/research/src
eval "$($PY - "$C" <<'EOF'
import json, shlex, sys
c = json.load(open(sys.argv[1] + "/cred.json"))
print(f"export RESEARCH_STORE_CONFIG={shlex.quote(sys.argv[1] + '/store.toml')}")
for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    print(f"export {k}={shlex.quote(c[k])}")
EOF
)"
ok=0; pub=0; bad=0
for d in "$RUNS"/r20*; do
  r=$(basename "$d"); [ "$r" = "${RESEARCH_RUN_ID}" ] && continue
  if $PY -m research data custody "$r" --runs-dir "$RUNS" >/dev/null 2>&1; then ok=$((ok+1)); echo "HAS-CUSTODY $r"; continue; fi
  sz=$(du -sh "$d" | cut -f1); t0=$(date +%s)
  out=$($PY -m research data custody "$r" --publish --runs-dir "$RUNS" 2>&1); rc=$?
  if [ $rc = 0 ]; then pub=$((pub+1)); echo "PUBLISHED $r $sz $(( $(date +%s)-t0 ))s"; continue; fi
  # an attempt published without a run record can't gain one: the run dir goes up as its own run-record/v1 tree
  meta=$($PY - "$d" "$r" <<'EOF'
import json, os, sys
from pathlib import Path
d = Path(sys.argv[1]); fs = [p for p in d.rglob("*") if p.is_file() and not p.is_symlink()]
print(json.dumps({"run_id": sys.argv[2], "files": len(fs), "bytes": sum(p.stat().st_size for p in fs),
                  "note": "post-hoc custody before pod termination (coordinator, 2026-09-25); attempt published without run_record"}))
EOF
)
  out=$($PY -m research data put --kind run-record/v1 --tree "$d" --meta "$meta" --preserve --json 2>&1); rc=$?
  art=$(grep -o '"id": *"art:[0-9a-f]*"' <<<"$out" | head -1 | grep -o 'art:[0-9a-f]*')
  if [ $rc = 0 ] && [ -n "$art" ]; then pub=$((pub+1)); echo "PUT $r $art $sz $(( $(date +%s)-t0 ))s"
    $PY -m research data evict --target-free-gb ${FREE_GB:-40} >/dev/null 2>&1
  else bad=$((bad+1)); echo "FAILED $r $sz rc=$rc: $(tail -c 400 <<<"$out" | tr '\n' ' ')"; fi
done
echo "SUMMARY had-custody=$ok published=$pub failed=$bad"
[ $bad = 0 ]
