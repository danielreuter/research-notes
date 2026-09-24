#!/usr/bin/env bash
# lane ajtai-leaf-3, pod side: bench arms at --pipeline 4 (4096 VUs, l = 16384, --zk interactive, local coins), each rep-1
# dump verified by the Rust `batch` built from THIS tree (the G1 key-structure check included once it is committed).
# usage: ajtai3_bench.sh [--build] [ARM...]   ARM in ajtai hash bare hajtai hhash hbare; env ALLOC=<PYTORCH_CUDA_ALLOC_CONF>
set -uo pipefail
export PATH="$HOME/.cargo/bin:$PATH"
SRC=$(pwd)
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"
export LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
export TRITON_CACHE_DIR=/workspace/triton-cache
[ -n "${ALLOC:-}" ] && export PYTORCH_CUDA_ALLOC_CONF="$ALLOC"
OUT="$RESEARCH_RUN_DIR"
RV=${RV_OVERRIDE:-/workspace/bin/ligero-verify}
echo "LIGERO_CHAIN_ENC_CHUNK=${LIGERO_CHAIN_ENC_CHUNK:-} LIGERO_CHAIN_TERM_CHUNK=${LIGERO_CHAIN_TERM_CHUNK:-} RV=$RV"
stage() { echo; echo "=== [$(date -u +%H:%M:%S)] $*"; }
fail=0
BUILD=0; [ "${1:-}" = "--build" ] && { BUILD=1; shift; }
ARMS=("$@"); [ ${#ARMS[@]} -eq 0 ] && ARMS=(ajtai hajtai)
git -C "$SRC" rev-parse HEAD 2>/dev/null | tee "$OUT/tree_sha.txt"
echo "PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-}"
if [ $BUILD -eq 1 ]; then
  stage "cargo build --release + full cargo test --release"
  RV="$OUT/ligero-verify"
  ( cd "$SRC/backends/ligero-verify" && CARGO_TARGET_DIR=/workspace/cargo-target cargo build --release 2>&1 | tail -1 \
    && cp /workspace/cargo-target/release/ligero-verify "$RV" && mkdir -p target/release && cp "$RV" target/release/ligero-verify \
    && CARGO_TARGET_DIR=/workspace/cargo-target cargo test --release 2>&1 | grep -E "^test .*(FAILED|ok)$|test result|panicked" | grep -vE "^test .* ok$" ) \
    | tee "$OUT/cargo_full.txt" || fail=1
  grep -qE "FAILED|panicked" "$OUT/cargo_full.txt" && fail=1
  sha256sum "$RV" | tee "$OUT/rv_sha256.txt"
fi

COMMON="bench-vu --zk --mode interactive --batch 16384 --total-vus 4096 --reps 3 --device cuda --instances-cache /workspace/instances-cache --dump-reps 1 --pipeline ${DEPTH:-4}"
for arm in "${ARMS[@]}"; do
  case "$arm" in
    bare)     REL=fp8-ada;     EXTRA="" ;;
    hash)     REL=fp8-ada;     EXTRA="--auth included-hash" ;;
    ajtai)    REL=fp8-ada;     EXTRA="--auth included-hash --leaf ajtai-n64" ;;
    hbare)    REL=bf16-hopper; EXTRA="" ;;
    hhash)    REL=bf16-hopper; EXTRA="--auth included-hash" ;;
    hajtai)   REL=bf16-hopper; EXTRA="--auth included-hash --leaf ajtai-n128" ;;
    *) echo "unknown arm $arm"; fail=1; continue ;;
  esac
  D="$OUT/bench/$arm"; mkdir -p "$D"
  stage "bench $arm: $REL $COMMON $EXTRA"
  "$PY" -m backends.direct.ligero.run --relation $REL $COMMON $EXTRA --dump-dir "$D/proofs" --out "$D/result.json" > "$D/bench.log" 2>&1
  rc=$?; echo "rc=$rc"; [ $rc -eq 0 ] || { fail=1; tail -8 "$D/bench.log"; continue; }
  "$PY" - "$D/result.json" <<'PYEOF'
import json, sys
r = json.load(open(sys.argv[1]))
for m in r["measurements"]:
    n = m["name"]
    if n in ("t.total", "rows_per_unit", "prove_wall", "relation.hash.auth_openings_seconds", "gpu.peak_mem_bytes") or n.startswith("split.") or "peak" in n:
        print(f"  {n:44s} {m['value']:.4f}" if isinstance(m["value"], float) else f"  {n:44s} {m['value']}")
print("  pipeline", r["workload_fingerprint"].get("pipeline"), r["workload_fingerprint"].get("pipeline_depth"))
PYEOF
  REP=$(ls -d "$D"/proofs/rep* 2>/dev/null | head -1)
  if [ -n "$REP" ]; then
    stage "rust batch verify of the $arm dump ($RV)"
    "$RV" batch --system "$D/proofs/system.bin" --dir "$REP" --jobs 8 --threads 4 --json "$D/rust_batch.json" > "$D/rust_batch.log" 2>&1
    "$PY" - "$D/rust_batch.json" <<'PYEOF'
import json, sys
j = json.load(open(sys.argv[1]))
print({k: j[k] for k in j if k in ("accepted", "rejected", "batch_accepted", "pinned_relation", "system_pinned")})
PYEOF
    grep -q '"batch_accepted": *true' "$D/rust_batch.json" || fail=1
  else
    echo "no dump"; fail=1
  fi
done
stage "done"
if [ $fail -eq 0 ]; then echo BENCH_OK; else echo BENCH_FAILED; exit 1; fi
