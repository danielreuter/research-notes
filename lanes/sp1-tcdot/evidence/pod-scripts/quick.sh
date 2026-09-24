#!/usr/bin/env bash
# Screening run (not a registered result): bare-prove B=4096 with a warm-up and REPS proofs under the caller's env
# (ELEMENT_THRESHOLD, SHARD_SIZE, SP1_WORKER_*, VERITY_TCDOT_VU_SOFTWARE_THRESHOLD, ...), then the per-shard timeline.
#   TAG=e1 ELEMENT_THRESHOLD=536870912 bash quick.sh
# SERVER_HOME picks the server: home-bf16 (fork fe35cc50) or home-shard (d14b4c62, which honours ELEMENT_THRESHOLD).
set -euo pipefail
W=/workspace/sp1-tcdot
export PATH=$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH
export HOME=$W/${SERVER_HOME:-home-bf16} CUDA_VISIBLE_DEVICES=0 SP1_PROVER=cuda RUST_LOG=debug
H=$W/target-tcdot/release/verity-tcdot-host
D=$W/runs/quick-${TAG:-x}
rm -rf $D && mkdir -p $D
{ env | grep -E "^(ELEMENT_THRESHOLD|SHARD_SIZE|HEIGHT_THRESHOLD|SP1_WORKER_|VERITY_TCDOT_|TRACE_CHUNK|MINIMAL_TRACE)" || true; } | sort | tee $D/env.txt
$H bare-prove --instances $W/bi --manifest-sha256 059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea \
  --lo 0 --hi 4096 --vus-per-read ${VPR:-64} --out-dir $D/proofs --reps ${REPS:-2} --warmup-vus 64 --mode core \
  > $D/stdout.jsonl 2> $D/prover.log || { echo "FAILED rc=$?"; tail -5 $D/prover.log; exit 1; }
python3 - $D/stdout.jsonl <<'EOF'
import json, sys
for line in open(sys.argv[1]):
    if not line.startswith("{"): continue
    d = json.loads(line)
    if d.get("event") == "execute": print("cycles", d["report"]["total_cycles"])
    if d.get("event") == "rep": print("rep", d["rep"], "prove", round(d["prove_seconds"], 3), "shards", d["shards"], "bytes", d["proof_bytes"], "accepted", d["accepted"])
EOF
python3 $W/scripts/timeline.py $D/prover.log | awk '/^proof_/{n++} n>=2' | head -40
rm -f $D/proofs/proof-rep*.bin
