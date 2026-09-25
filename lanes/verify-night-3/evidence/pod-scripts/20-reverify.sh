#!/usr/bin/env bash
# verify-night-3: main's reverify (tree lane/verify-night-3 a5d9b632 = main 2c92b9e3 + 5b28557b) with the pod's ligero-verify
# usage: 20-reverify.sh RESULT_ART...   (full ids); one reverify per result so one failure doesn't hide the others
set -uo pipefail
source "$(dirname "$0")/lib.sh"
cd /workspace/src
for r in "$@"; do
  echo "=== $r $(date -u +%H:%M:%SZ)"
  $PY -m backends.direct.ligero.reverify $r --by verify-night-3 --verifier /workspace/bin/ligero-verify \
      --work $W/work --jobs ${JOBS:-16} --json ${INST:+--instances-root $INST} > $W/rv-${r:4:8}.json 2> $W/rv-${r:4:8}.err
  echo "rc=$?"; tail -3 $W/rv-${r:4:8}.err; $PY -c "import json,sys;d=json.load(open(sys.argv[1]));print(json.dumps(d)[:1500])" $W/rv-${r:4:8}.json
  R data evict --target-free-gb 60 >/dev/null 2>&1 || true
done
R data labels-sync --push-only 2>&1 | tail -2
R data pending 2>&1 | tail -3
