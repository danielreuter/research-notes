#!/bin/bash
# GM-01 row #23 inputs (the v2 match record and the correspondence builds) into /workspace/gm23, then the key is deleted at once.
#   usage: gm_prefetch.sh TREE      log: /workspace/out/gm/prefetch.log
T=$1; L=/workspace/out/gm/prefetch.log; mkdir -p /workspace/out/gm /workspace/gm23
cd "$T" || exit 3
set -a; . /root/r2ro.env; set +a
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
echo "start $(date -u +%FT%TZ)" > $L
for pair in matchrec:art:33632a009b86fb07e24c8cf39ff7aabb31836ebbb4f58cda56943c3a5588d7d4 \
            build:art:7e51cdad13a4328b58697762a5b7d48598bcd4445db26d8bbaa2c01d34654542; do
  d=/workspace/gm23/${pair%%:*}; art=${pair#*:}; rm -rf "$d"; t0=$(date +%s)
  python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>>$L.err && echo "ok ${pair%%:*} $(( $(date +%s) - t0 ))s" >> $L || echo "FAIL ${pair%%:*}" >> $L
done
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
echo "key deleted; done $(date -u +%FT%TZ)" >> $L
cat $L
