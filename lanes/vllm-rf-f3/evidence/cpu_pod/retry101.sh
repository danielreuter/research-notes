#!/bin/bash
T=/workspace/base; cd $T || exit 3
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$T/tools/research/store.pod.toml
art=$(awk "\$1==\"101\" && \$2==\"records\" {print \$3}" /workspace/rff3/prefetch.txt)
d=/workspace/prefetch/101-records-retry; rm -rf $d
timeout 1200 python -m research.cli data fetch "$art" --to "$d" > /dev/null 2>>/workspace/rff3/logs/retry101.err && echo "ok 101 records (retry) $(date -u +%T)" || echo "FAIL 101 records (retry) rc=$? $(date -u +%T)"; rm -rf $d
