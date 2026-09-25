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

## Portability: sm_80 / sm_89 / sm_90 (hash-commit-2, 2026-09-25; report lanes/hash-commit-2/20260925T0932Z-report-hash-commit-2.md)
- The kernels are NVRTC-JITed for the device at hand (`RawModule(options=("-std=c++17",))`, no arch flag); `fv3_top` sizes
  itself from `max_threads_per_block` (896 on A100 and H100). No code change was needed for sm_80 / sm_90.
- Byte-identity suites 98/98 on A100 80GB PCIe (sm_80) and H100 NVL (sm_90) at bcf75db7. bench-vu bf16-hopper+blake3 (4096 VUs,
  batch 8192, p2): commit evidence c90e6d0d… and the 49 statement files are identical on 4090 / A100 / H100, GPU or host
  committer; Rust batch accepts 49/49. Committer (rows + trees): 4090 4.9-5.2 ms, H100 NVL 3.5 ms (host 15.8 s), A100 5.7 ms
  (host 27.2 s). H100 art:c2212273, A100 in the report.
- commit_cost --impl gpu, 4096 x 1536 B rows, commit (leaf + tree, h2d apart): 4090 0.50-0.58 ms, H100 0.53-0.65, A100 0.84-0.87;
  6.3 M 2-byte words: frame-v3 12.5 / 9.3 / 14.6 ms, vllm-v1 8.4 / 6.0 / 9.2 ms (4090 / H100 / A100).
- Gotcha (not the committer): on sm_90, torch 2.6+cu124's `torch._int_mm` (cuBLASLt INT8) accepts only M % 32 == 0 rows
  (17..40, 48, 100, 1000 fail with CUBLAS_STATUS_NOT_SUPPORTED; 32/64/128/1024 work); sm_80/89 take any M > 16. The Poseidon2
  torch int8 MDS pads to 32 on cc >= 9 since 2a92fe61. Other `_int_mm` callers (backends/direct/encode/*) have the same limit.

## Measured (RTX 4090 vy-commit-gpu, PCIe gen4 x8, EPYC 7663)
- h2d 6 MiB uint8: pageable 0.54 ms, pinned 0.48 ms (link-bound ~12 GB/s): pinning does not pay here.
- In a bench, under `--commit-per-rep` (b-ligero-standard-hash r20260925-090404-6311: RTX 4090 vy-b-ligero-sh, tree
  806a2f73 = main 94b1c4d2 merged; fp8-ada+blake3, 4096 VUs, l = 4096, p2):
  - commit.seconds is 0.0107 s on the device vs 0.058 s on host paths;
  - the prover's row chains fall from ~0.8 s to 0.002 s, so t.total is 3.63 s vs 4.42 s;
  - `--commit-evidence` is byte-equal device vs host (sha256 f62b873f…).
