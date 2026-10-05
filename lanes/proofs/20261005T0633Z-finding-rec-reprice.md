---
id: proofs/20261005T0633Z-finding-rec-reprice
campaign: flock
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: bc-2a00fbff-762d-5c36-a641-1bbff50ddb4d (rec-reprice, for the proofs coordinator bc-8416bc72)
---

# Recursive witness ZK at m = 35: what the outer proof costs against today's `--zk` (K = 4096)

Branch `cursor/rec-reprice-95d4` (origin/main 43bef6294 + `cursor/rec-v0-95d4` cbad2989e). Work in progress; every number
below is marked measured or estimated as it lands.

## Baseline (given, from the dense rollup art:c343ae88d618f9b5ffc8699951fb2a7bf0e36f151a450a671305c88c7bee1996)

| K | mode | run | units | prove | session | verify | bytes/rep |
|---|---|---|---:|---:|---:|---:|---:|
| 4096 | `--zk` | r20261002-062836-96bb | 2,048 | 1.063 s | 3.05 s | 5.72 s | 1,179,202 |
| 4096 | M0 | r20261002-062731-0015 | 2,048 | 0.723 s | 0.876 s | 0.488 s | |
| 14336 | `--zk` | r20261002-122853-c740 | 512 | 1.071 s | 4.85 s | 11.75 s | |
| 14336 | M0 | r20261002-063820-d94b | 512 | 0.740 s | 1.111 s | 1.132 s | |

The baseline prover (cfbad08, branch cursor/vllm-overhead-dense-95d4 at 2b829a1) predates main's circuit format, so this
lane rebuilds main's GPU prover and reruns M0 and `--zk` on the same node for a like-for-like comparison.

## Runs

Script: `backends/flock/pod/85-rec-reprice.sh` (STEP=build|inner|ostage|oprove|lean), node 1 (`vy-nebius-1`), FLOCK_WORK
`/workspace/jobs/rec-reprice`, all via `research run --queue`.

| step | run | started | status |
|---|---|---|---|
| build (K=4096: GPU prover key 47340c664cec521f, Lean 88a84ea16d7e8f86, inner staged) | r20261005-064451-cec2 | 06:44Z | failed: the prover's kernels use `clmad`, which node 1's host CUDA 13.0 ptxas rejects (Lean built) |
| build, CUDA 13.3.1 from NVIDIA's redistributable archives under FLOCK_WORK | r20261005-064928-7c4f | 06:49Z | passed: binary dc3d91dd…, inner m = 35, k_log 24, nbl 11, 2,048 instances, circuit 567 MB |
| inner: proxy M0 ×(1+3), replay, rec_vstar; loopback M0 and --zk ×(1+3) | r20261005-065337-4837 | 06:53Z | running |

## Shape of V* at m = 35 (from `rec_algebra.fast100(35)`, before any run)

fast100 at m = 35 has 7 Ligerito levels (m = 27 had 4), so V* is 7 `RecOpen` sessions plus the algebra. Per level (both reps):
L0 `RecOpen{64,16}` 436 openings × 45 compressions; L1 `{16,15}` 212 × 37; L2 `{16,13}` 142 × 33; L3 `{16,12}` 106 × 31;
L4 `{16,10}` 86 × 27; L5 `{16,8}` 72 × 23; L6 `{16,6}` 64 × 19. 40,630 compressions, 3.31e9 SHA-512 rows for the two reps
(1.65e9 per rep). Unit slots: L0–L4 2^22, L5–L6 2^21, so by table size the outer is about 2^34.4 rows against the inner's
2^35: an estimate to be replaced by the measured runs.
