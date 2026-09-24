#!/bin/bash
# agkr-fp8 (pod): register + preserve the negatives tree of a 01_fp8_dev.sh run (all 5 variants' statement + proof + verdicts,
# plus the dev run's stdout), refs to the recorded result it backs.   bash 04_put_neg.sh REL DEV_RUN RESULT_ART SOURCE_SHA
set -euo pipefail
REL=$1 RUN=$2 RES=$3 SHA=$4
set -a; . /workspace/agkr-fp8/r2.env; set +a
C=/workspace/agkr-fp8/store.pod.toml
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
T=/workspace/agkr-fp8/$REL/neg-evidence
rm -rf "$T"; mkdir -p "$T"
cp -r /workspace/agkr-fp8/$REL/neg "$T/neg"
cp /workspace/research/runs/$RUN/stdout.log "$T/dev_run_stdout.log"
cp /workspace/agkr-fp8/scripts/01_fp8_dev.sh "$T/"
python3 -m research data put --kind gate-log/v1 --tree "$T" --preserve \
  --meta "{\"lane\": \"agkr-fp8\", \"relation\": \"$REL\", \"run_id\": \"$RUN\", \"source_commit\": \"$SHA\", \"candidate\": \"A-GKR\", \
\"what\": \"A-GKR negatives at 4096 VUs: honest + public word +1 / -1 / sign bit 21 / exponent +1 (bit 13), each rejected by gpu.prover.verify and verity-gkr-verify (Rust); the producer's own run\"}" \
  --ref "result=$RES"
