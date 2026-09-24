#!/usr/bin/env bash
# register.sh TAG ARM [RUN_FILES_ART]: copy /workspace/sp1-tcdot/runs/TAG from the pod, put the run files (run-files/v1:
# result, measurements, prove/verify/negatives json, host + prover logs, statement.bin, every proof dump; skipped when
# RUN_FILES_ART is given) and the result (bench-result/v1 whose meta is the result document, as `research run` publishes
# it, store README §10; refs.run_files), both --preserve, then the producer's labels.
# Prints "TAG result=art:... run_files=art:... t.total=...".
set -euo pipefail
set -a; source ~/.config/verity/r2.env; set +a
TAG=$1; ARM=${2:-$1}; RF=${3:-}
R=~/.research/bin/research
D=/tmp/sp1tcdot/runs/$TAG
if [ -z "$RF" ] || [ ! -s $D/result.json ]; then
  rm -rf $D && mkdir -p $D
  /tmp/sp1tcdot/pssh "cd /workspace/sp1-tcdot/runs/$TAG && tar -cf - ." | tar -xf - -C $D
fi
test -s $D/result.json
read -r TT STATUS SRC SHARDS ACH < <(python3 ~/.research/notes/lanes/sp1-tcdot/evidence/result_meta.py $D/result.json $TAG $ARM $D/meta.json)
[ "$STATUS" = passed ] || { echo "$TAG: validation $STATUS -- not registering"; exit 1; }
ID='import json,sys; d=json.load(sys.stdin); print(d["id"] if "id" in d else d["push"]["id"])'
if [ -z "$RF" ]; then
  RMETA=$(printf '{"lane":"sp1-tcdot","tag":"%s","arm":"%s","label":"modified SP1 (TC_DOT chip) run files","source":"lane/sp1-tcdot@%s"}' "$TAG" "$ARM" "$SRC")
  RF=$($R data put --kind run-files/v1 --tree $D --meta "$RMETA" --preserve --json | python3 -c "$ID")
fi
RES=$($R data put --kind bench-result/v1 --meta @$D/meta.json --ref run_files=$RF --preserve --json | python3 -c "$ID")
lab() { $R data label "$RES" "$1" "$2" --by sp1-tcdot >/dev/null 2>&1; }
lab candidate SP1; lab proof_class NON_ZK_PROOF; lab K 1536; lab B 4096; lab hardware "NVIDIA A100-SXM4-80GB (prover, CUDA)"
lab authentication excluded; lab campaign morning-tables; lab relation bf16-ampere-k1536; lab zk false; lab scope vu
lab track baseline; lab lane sp1-tcdot; lab soundness "SP1 100-bit target per STARK proof; union bound over the core proof's $SHARDS shard proofs: 2^$ACH"
lab source "lane/sp1-tcdot@$SRC"; lab sweep "prover configuration (hill-climb)"; lab arm "$ARM"
lab label "modified SP1 (TC_DOT chip), relation-bare/v2 bf16-ampere, 4096 VUs, A100 core STARK: t.total $TT s"
lab note "modified SP1: fork of SP1 6.4.0 + TC_DOT_BF16 precompile (FORK_HEAD in backends/sp1/tcdot); core proofs only; security 100-bit per shard proof (drill-down, not a 2^-128 cell)"
lab omitted "zero-knowledge, authentication, SP1 recursion (core proof only)"
$R data labels-sync --push-only >/dev/null
$R data preserved "$RES" "$RF" >/dev/null || { echo "$TAG: $RES / $RF not preserved"; exit 1; }
rm -rf $D/proofs
echo "$TAG result=$RES run_files=$RF t.total=$TT"
