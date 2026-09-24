#!/bin/bash
# sp1-table (pod): exploratory prover-option probe, not a registered result.  B=4096 indexed, REPS reps per config after a
# 64-VU warmup, stock SP1 GPU prover with the given environment (KEY=VALUE,KEY=VALUE or "base").  Prints each config's
# prove s per rep, shard count (ProveShard tasks of the last rep), proof bytes, verify s.  Waits for the previous config's
# sp1-gpu-server to exit first (a new prover that starts while the old server holds the port gets "Connection refused").
#   HOST=...-k7m REPS=2 bash probe_env.sh base FULL_SIZE_SHARDS=true SP1_WORKER_NUM_CORE_WORKERS=8,SP1_WORKER_CORE_BUFFER_SIZE=8
set -uo pipefail
H=/workspace/bin/${HOST:-veritor-zk-host-cuda-relation-bare-k7m}
F=/workspace/src/fixtures/bench-instances/v1
M=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
O=/workspace/sp1-table/probe-env; mkdir -p "$O"
for cfg in "$@"; do
  for _ in $(seq 60); do pgrep -f sp1-gpu-server > /dev/null || break; sleep 1; done
  tag=$(echo "$cfg" | tr ',=' '_-')
  envs=(); [ "$cfg" = base ] || IFS=, read -ra envs <<< "$cfg"
  rm -rf "$O/proofs-$tag"
  env "${envs[@]}" SP1_PROVER=cuda RUST_LOG=debug "$H" bare-prove --instances "$F" --manifest-sha256 $M --lo 0 --hi 4096 \
      --layout indexed --out-dir "$O/proofs-$tag" --reps "${REPS:-1}" --warmup-vus 64 --mode core --skip-execute > "$O/$tag.jsonl" 2> "$O/$tag.log"
  rc=$?
  python3 - "$O/$tag.jsonl" "$cfg" "$rc" <<'PY'
import json, re, sys
jl, cfg, rc = sys.argv[1:4]
lines = open(jl, errors="replace").read().splitlines()
reps = [json.loads(l) for l in lines if l.startswith('{"event":"rep"')]
events = [i for i, l in enumerate(lines) if l.startswith('{"event":')]
last = max((i for i in events if lines[i].startswith('{"event":"rep"')), default=0)
prev = max((i for i in events if i < last), default=0)
shards = sum("submitting task of kind ProveShard" in re.sub(r"\x1b\[[0-9;]*m", "", l) for l in lines[prev:last])
prove = " ".join(f"{r['prove_seconds']:.2f}" for r in reps) or "nan"
r = reps[-1] if reps else {}
print(f"{cfg:72s} rc={rc} prove=[{prove}]s shards={shards} bytes={r.get('proof_bytes')} verify={r.get('verify_seconds', float('nan')):.2f}s", flush=True)
PY
done
