# GPU committer (native hashing for frame-v3 and vllm-v1)

Lane hash-commit / commit-gpu (2026-09-25), branch `lane/hash-commit`. Report:
`lanes/hash-commit/20260925T0525Z-report-hash-commit.md` (section commit-gpu, FINAL).

## What it is
- `backends/shared/hash_gpu/frame_v3.py` (cupy RawModule): frame-v3 leaf / pad / node kernels (one thread per hash), the
  vllm-v1 node/lift level kernel, keyed BLAKE3 of rows (thread per 1 KiB chunk + per-row parent fold), SHA-256(prefix || row).
  Byte-identical to `verity.commitments` (core vectors in `packages/verity/tests/commitments`), hashlib and the `blake3`
  package: `backends/shared/hash_gpu/tests/test_frame_v3.py`.
- Heads: every frame-v3 launch hashes a constant head (frame, tag, domain id [, level]). All of one tree's heads go up in ONE
  upload and ONE `sha_mids` launch (`_Heads`); never hash them on the host in Python (0.16 ms per midstate, 3.2 ms per
  fresh-binding tree at 4096 leaves -- hidden by any cache keyed on the binding when a bench re-commits the same set).
- Trees: level by level into one device buffer; levels with <= `max_threads_per_block` nodes in one single-block launch
  (`fv3_top`); the host copy eager <= 4 MiB (row / output trees), lazy above (openings read it).
- Launch overhead dominates at 4096 leaves, not hashing: pass device pointers as `np.uint64` (a cupy slice costs ~5-10 us),
  cache constant uploads (keys, prefixes), fuse small elementwise steps into one kernel.
- ligero integration: `backends/direct/ligero/frame_gpu.py` (`LIGERO_COMMIT_GPU=0` = host paths; `LIGERO_GPU_STRICT=1` makes a
  broken GPU path an error), `commit.committer_seconds` = rows to the device + the three trees (row digests, framing, y leaves).
- `benchmarks/commitments/commit_cost.py --impl gpu` (commit_cost_gpu.py): the four variants, every rep's root checked
  against the plain reference.

## Pitfalls seen
- Hand the committer the committed set in its words' dtype (uint8 fp8 / uint16 bf16 rows), not per-VU int64 arrays: the
  bench's int64 list cost 8.8 ms of stacking + 96 MiB h2d per commit on a 4090.
- A `@contextmanager` that wraps its `yield` in `try/except ImportError` swallows ImportErrors raised by the caller's block
  ("generator didn't stop after throw()"): import first, then yield outside the try.
- fp8-ada+blake3 at batch 8192 with `--pipeline 4` OOMs a 24 GB 4090 in the prover; `--pipeline 2` fits.

## Measured (RTX 4090 vy-commit-gpu, PCIe gen4 x8, EPYC 7663)
- h2d 6 MiB uint8: pageable 0.54 ms, pinned 0.48 ms (link-bound ~12 GB/s): pinning does not pay here.
- In a bench, under `--commit-per-rep` (b-ligero-standard-hash r20260925-090404-6311: RTX 4090 vy-b-ligero-sh, tree
  806a2f73 = main 94b1c4d2 merged; fp8-ada+blake3, 4096 VUs, l = 4096, p2):
  - commit.seconds is 0.0107 s on the device vs 0.058 s on host paths;
  - the prover's row chains fall from ~0.8 s to 0.002 s, so t.total is 3.63 s vs 4.42 s;
  - `--commit-evidence` is byte-equal device vs host (sha256 f62b873f…).
