#!/bin/bash
# sp1-table (pod): exploratory prover-option probe, not a registered result.  B=4096 indexed, one rep per config after a
# 64-VU warmup, stock SP1 GPU prover with the given environment (KEY=VALUE,KEY=VALUE or "base").  Prints each config's
# prove s, shard count (into_record lines), proof bytes, verify s.
#   HOST=...-k7m bash probe_env.sh base FULL_SIZE_SHARDS=true MINIMAL_TRACE_CHUNK_THRESHOLD=2097152,SP1_WORKER_NUM_CORE_WORKERS=8
set -uo pipefail
H=/workspace/bin/${HOST:-veritor-zk-host-cuda-relation-bare-k7m}
F=/workspace/src/fixtures/bench-instances/v1
M=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
O=/workspace/sp1-table/probe-env; mkdir -p "$O"
for cfg in "$@"; do
  tag=$(echo "$cfg" | tr ',=' '_-')
  envs=(); [ "$cfg" = base ] || IFS=, read -ra envs <<< "$cfg"
  rm -rf "$O/proofs-$tag"
  env "${envs[@]}" SP1_PROVER=cuda RUST_LOG=debug "$H" bare-prove --instances "$F" --manifest-sha256 $M --lo 0 --hi 4096 \
      --layout indexed --out-dir "$O/proofs-$tag" --reps 1 --warmup-vus 64 --mode core --skip-execute > "$O/$tag.jsonl" 2> "$O/$tag.log"
  rc=$?
  python3 - "$O/$tag.jsonl" "$O/$tag.log" "$cfg" "$rc" <<'PY'
import json, re, sys
jl, log, cfg, rc = sys.argv[1:5]
reps = [json.loads(l) for l in open(jl) if l.startswith('{"event":"rep"')]
text = re.sub(r"\x1b\[[0-9;]*m", "", open(log, errors="replace").read())
shards = len(re.findall(r"into_record: tracing chunk", text))
r = reps[-1] if reps else {}
print(f"{cfg:60s} rc={rc} prove={r.get('prove_seconds', float('nan')):.2f}s shards~{shards} bytes={r.get('proof_bytes')} verify={r.get('verify_seconds', float('nan')):.2f}s")
PY
done
