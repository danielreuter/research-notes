#!/usr/bin/env bash
# red-team-standard-hash R1: build ligero-verify at the synced tree, then the remap forgery for REL+LEAF (default fp8-ada+blake3).
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc) OPENBLAS_NUM_THREADS=$(nproc) VY_CPU_THREADS=$(nproc)
cd /workspace/src
REL=${REL:-fp8-ada}; LEAF=${LEAF:-blake3}; OUT=/workspace/red-team-standard-hash/r1-$REL-$LEAF
git_sha=$(cat .research-source.json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("commit","?"))' 2>/dev/null)
echo "tree: $git_sha"
if [ "${SKIP_BUILD:-0}" != 1 ]; then
  cargo build --release --manifest-path backends/ligero-verify/Cargo.toml 2>&1 | tail -2
  cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ligero-verify
fi
sha256sum /workspace/bin/ligero-verify
rm -rf $OUT; mkdir -p $OUT
$PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin /workspace/bin/ligero-verify --out $OUT --relation $REL --leaf $LEAF \
  ${EXTRA:-} 2>&1 | tee $OUT/log.txt
rc=${PIPESTATUS[0]}
echo "rc=$rc"
exit $rc
