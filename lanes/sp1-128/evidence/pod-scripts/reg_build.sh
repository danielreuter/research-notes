#!/bin/bash
# sp1-128 (pod): preserve the sec134 build evidence as run-files/v1: the CPU verifier host (VERIFIER_ONLY=1 build), the
# source diffs (prover sp1 v6.6.0 fork, verifier sp1-primitives, harness sp1-cuda), the GPU server's sha256 and host info.
# The credential is `research data mint-credential --env` output on STDIN, never a file.
#   research data mint-credential --ttl 1h --env | research pods ssh POD -- bash /workspace/sec128/reg_build.sh
set -euo pipefail
set -a; eval "$(cat)"; set +a
C=/workspace/sec128/store.pod.toml
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=${TOOL%/} RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$C
W=/workspace/sec128/reg/build; rm -rf "$W"; mkdir -p "$W/tree/prover-build" "$W/tree/verifier-build"
install -m 0755 /workspace/bin/veritor-zk-host-relation-bare-sec134-cpu "$W/tree/"
for f in prover-source.diff verifier-source.diff harness-source.diff server.sha256 host-info.json; do
  cp /workspace/sec128/$f "$W/tree/prover-build/"
  [ -f /workspace/sec128-verifier/$f ] && cp /workspace/sec128-verifier/$f "$W/tree/verifier-build/"
done
(cd "$W/tree" && sha256sum veritor-zk-host-relation-bare-sec134-cpu > SHA256SUMS)
id() { python3 -c 'import json,sys; d=json.load(sys.stdin); assert (d.get("preserve") or {}).get("preserved"), d; print(d["id"])'; }
python3 -m research data put --kind run-files/v1 --tree "$W/tree" \
  --meta '{"lane": "sp1-128", "what": "SP1 sec134 build evidence: CPU verifier host (backends/sp1/sec128/build.sh VERIFIER_ONLY=1, run r20260924-220550-61cb), source diffs, GPU server sha256 (build run r20260924-214910-0c80)", "listed": ["veritor-zk-host-relation-bare-sec134-cpu", "SHA256SUMS", "prover-build", "verifier-build"]}' \
  --preserve --json | id
rm -rf "$W"
