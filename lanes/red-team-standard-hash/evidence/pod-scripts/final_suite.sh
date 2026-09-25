#!/usr/bin/env bash
# red-team-standard-hash: the R1 / R4 / H2 suite on main 3301c435 (fp8-ada+blake3; /workspace/src-main) and on
# b-ligero-sha256 da74b03e (fp8-ada-x4+sha256; /workspace/src-sha2), plus a compress_one / leaf_bytes differential.
set -uo pipefail
source /workspace/env.sh
export OMP_NUM_THREADS=$(nproc) MKL_NUM_THREADS=$(nproc) OPENBLAS_NUM_THREADS=$(nproc) VY_CPU_THREADS=$(nproc)
suite() {  # T REL LEAF S_OK S_BAD
  T=$1; REL=$2; LEAF=$3
  cd /workspace/src-$T
  O=/workspace/red-team-standard-hash/final-$T; rm -rf $O; mkdir -p $O
  cat .research-source.json > $O/source.json
  find backends/ligero-verify -name '*.rs' -exec touch {} +
  echo "===== $T build"; cargo build --release --manifest-path backends/ligero-verify/Cargo.toml 2>&1 | tail -1
  cp $CARGO_TARGET_DIR/release/ligero-verify /workspace/bin/ligero-verify-$T; B=/workspace/bin/ligero-verify-$T; sha256sum $B | tee $O/bin.sha256
  echo "=== $T R1 remap ($REL+$LEAF)"
  $PY -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $B --out $O/r1 --relation $REL --leaf $LEAF --set-binding > $O/r1.log 2>&1; echo "r1 rc=$?"; grep -E "^(forgery|control)" $O/r1.log | cut -c1-330
  echo "=== $T R4 orphan"
  $PY -m backends.direct.ligero.redteam.rtsh_orphan_e2e --bin $B --out $O/r4 --relation $REL --leaf $LEAF --vus 3 > $O/r4.log 2>&1; echo "r4 rc=$?"; tail -4 $O/r4.log | cut -c1-330
  echo "=== $T H2"
  for s in $4 $5; do
    $PY -m backends.direct.ligero.redteam.rtsh_steps_e2e --bin $B --relation $REL --leaf $LEAF --steps $s --out $O/h2-steps$s > $O/h2-steps$s.log 2>&1; echo "steps $s rc=$?"; tail -1 $O/h2-steps$s.log | cut -c1-330
  done
}
suite main fp8-ada blake3 48 64
suite sha2 fp8-ada-x4 sha256 12 24
cmp -s /workspace/bin/ligero-verify-main /workspace/bin/ligero-verify-sha2 && echo "WARNING: main and sha2 binaries identical"
echo "=== sha2 compress_one / leaf_bytes differential"
cd /workspace/src-sha2
$PY - <<'PY' 2>&1 | tee /workspace/red-team-standard-hash/final-sha2/compress_one.log
import hashlib, numpy as np
from backends.direct.ligero.leaf import sha256 as S
rng = np.random.default_rng(0)
bad = 0
edge = [0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFE, 0xFFFFFFFF]
for i in range(20000):
    h = rng.integers(0, 1 << 32, size=8, dtype=np.uint64).astype(np.uint32)
    if i < 64:
        h = np.array([edge[(i + j) % len(edge)] for j in range(8)], dtype=np.uint32)
    blk = rng.integers(0, 256, size=64, dtype=np.uint8).tobytes() if i % 7 else bytes([255 * (i % 2)]) * 64
    a = S.compress_one(tuple(int(x) for x in h), blk)
    b = tuple(int(x) for x in S.compress_np(h[:, None].copy(), S._words_be(blk)[:, None])[:, 0])
    bad += a != b
print("compress_one vs compress_np: 20000 cases,", bad, "mismatches")
leaf = S.Sha256Leaf()
bad2 = 0
for wb in (8, 16):
    for role in (1, 2):
        rows = rng.integers(0, 1 << wb, size=(64, S.K_VU), dtype=np.int64)
        rows[0] = 0; rows[1] = (1 << wb) - 1
        d = leaf.native(rows, word_bits=wb, role=role)
        got = [leaf.leaf_bytes(r) for r in d]
        many = leaf.leaf_bytes_many(d)
        ref = leaf.reference_digest(rows, word_bits=wb, role=role)
        bad2 += sum(g != r for g, r in zip(got, ref)) + sum(m != r for m, r in zip(many, ref))
print("leaf_bytes / leaf_bytes_many vs reference (hashlib over prefix||row): 256 rows,", bad2, "mismatches")
print("DIFF OK" if bad == 0 and bad2 == 0 else "DIFF MISMATCH")
PY
