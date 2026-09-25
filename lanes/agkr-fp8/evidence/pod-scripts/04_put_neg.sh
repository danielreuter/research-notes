#!/bin/bash
# agkr-fp8 (pod): register + preserve the negatives tree of a 01_fp8_dev.sh run (all 5 variants' statement + proof + verdicts,
# plus the dev run's stdout), refs to the recorded result it backs.   bash 04_put_neg.sh REL DEV_RUN RESULT_ART SOURCE_SHA
set -euo pipefail
REL=$1 RUN=$2 RES=$3 SHA=$4
set -a; . /workspace/agkr-fp8/r2.env; set +a
C=/workspace/agkr-fp8/store.pod.toml
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
H=${H:-/workspace/agkr-fp8/$REL}
T=$H/neg-evidence
rm -rf "$T"; mkdir -p "$T"
cp -r $H/neg "$T/neg"
WHAT_LK=""
if [ -d $H/lookup_neg ]; then
  cp -r $H/lookup_neg "$T/lookup_neg"; cp /workspace/agkr-fp8/scripts/12_lookup_neg.sh "$T/"
  [ -n "${LK_RUN:-}" ] && cp /workspace/research/runs/$LK_RUN/stdout.log "$T/lookup_neg_stdout.log"
  WHAT_LK="; lookup_neg/: one unit column read by the merged LK table +1 (T_OP / SHIFT / TNORM output, R5 key term) with honest multiplicities from a prover copy whose LogUp self-check is a no-op, each rejected by both verifiers (12_lookup_neg.sh)"
fi
cp /workspace/research/runs/$RUN/stdout.log "$T/dev_run_stdout.log"
cp /workspace/agkr-fp8/scripts/01_fp8_dev.sh "$T/"
python3 -m research data put --kind gate-log/v1 --tree "$T" --preserve \
  --meta "{\"lane\": \"agkr-fp8\", \"relation\": \"$REL\", \"run_id\": \"$RUN\", \"source_commit\": \"$SHA\", \"candidate\": \"A-GKR\", \
\"what\": \"A-GKR negatives at 4096 VUs: honest + public word +1 / -1 / sign bit 21 / exponent +1 (bit 13), each rejected by gpu.prover.verify and verity-gkr-verify (Rust); the producer's own run$WHAT_LK\"}" \
  --ref "result=$RES"
