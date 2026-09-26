#!/bin/bash
# prefetch.sh ROWNUM...: fetch the regression fixtures (fixtures.toml art ids) of these rows into the pod store with the short-lived
# read-only key in /root/r2ro.env, then delete the key. cwd = source/integrations/vllm. Log: $RESEARCH_RUN_DIR/prefetch.txt
L=$RESEARCH_RUN_DIR/prefetch.txt
[ -e /root/r2ro.env ] || { echo "no /root/r2ro.env" >> $L; exit 4; }
set -a; . /root/r2ro.env; set +a
export PYTHONPATH=../../tools/research/src RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=../../tools/research/store.pod.toml
ARTS=$(/workspace/venv312/bin/python - "$@" <<'EOF'
import sys, tomllib
fx = tomllib.load(open("tests/regression/fixtures.toml", "rb"))
want = {int(x) for x in sys.argv[1:]}
arts = set(v for v in (fx.get("artifacts") or {}).values() if isinstance(v, str) and v.startswith("art:"))
for k, r in fx["rows"].items():
    if int(r["row"]) in want:
        arts |= {v for v in (r.get("artifacts") or {}).values() if isinstance(v, str) and v.startswith("art:")}
print(" ".join(sorted(arts)))
EOF
)
ok=0; bad=0
for a in $ARTS; do
  if /workspace/venv312/bin/python -m research data fetch "$a" > /dev/null 2>> $L; then ok=$((ok+1)); echo "ok $a" >> $L; else bad=$((bad+1)); echo "FAIL $a" >> $L; fi
done
rm -f /root/r2ro.env
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "$(date -u +%FT%TZ) fetched ok=$ok fail=$bad; key deleted" >> $L
