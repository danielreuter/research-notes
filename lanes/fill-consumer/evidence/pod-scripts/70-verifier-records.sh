#!/usr/bin/env bash
# fill-consumer: custody of vy-fill-consumer-vtest's live_serve store before terminating it (kb/live-verifier.md): the
# records only (index.jsonl; per session hello / session / verdict json, the verifier-side Rust verdicts, sub_*.coins),
# not the proofs / statements / system.bin (the provers' dumps carry those), with a sha256 list; put --preserve from here.
set -uo pipefail
: "${AWS_ACCESS_KEY_ID:?no R2 credential in the environment}"
export PYTHONPATH="/workspace/lv-src-1b3c7be6/packages/verity/src:/workspace/lv-src-1b3c7be6/backends/numerical/python:/workspace/lv-src-1b3c7be6/tools/research/src:/workspace/lv-src-1b3c7be6"
PY=/workspace/venv312/bin/python
S=/workspace/live/sessions; D=/workspace/fc-records; rm -rf $D; mkdir -p $D/sessions
cp $S/index.jsonl $D/sessions/
cd $S && for s in s2026*; do
  mkdir -p $D/sessions/$s
  cp $s/hello.json $s/session.json $s/verdict.json $s/rust_batch.json $s/rust_sub_*.json $s/sub_*.coins $D/sessions/$s/ 2>/dev/null
done
cd $D && find sessions -type f | sort | xargs sha256sum > SHA256SUMS
n=$(find $D -type f | wc -l | tr -d ' '); sz=$(du -sb $D | cut -f1)
sessions=$(ls -d $D/sessions/s2026* | wc -l | tr -d ' ')
echo "records: $n files, $sz bytes, $sessions sessions"
cd /workspace/lv-src-1b3c7be6 && $PY -m research data put --kind run-files/v1 --tree $D --preserve \
  --meta "{\"lane\": \"fill-consumer\", \"what\": \"live_serve records of vy-fill-consumer-vtest (1vchd2ej1iey9k, EU-RO-1, live-verifier@1b3c7be67343, ligero-verify ae5a0abf91585cbd): $sessions sessions (RTX 5090 fp4-nvf4 bare + fp4-nvf4+poseidon2, RTX 4090 fp8-ada-v3x4 bare, fp8-ada bare and --auth included-hash)\", \"files\": $n, \"listed\": [\"SHA256SUMS\", \"sessions/index.jsonl\", \"sessions/*/{hello,session,verdict,rust_batch,rust_sub_*}.json\", \"sessions/*/sub_*.coins\"], \"missing\": [\"sub_*.proof\", \"sub_*.stmt\", \"system.bin (the provers' run-files carry the dumps)\"]}" 2>&1 | tail -3
