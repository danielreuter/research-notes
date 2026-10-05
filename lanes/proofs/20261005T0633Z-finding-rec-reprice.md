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

Script: `backends/flock/pod/85-rec-reprice.sh` (STEP=build|inner|ostage|alg|oprove|lean), node 1 (`vy-nebius-1`), FLOCK_WORK
`/workspace/jobs/rec-reprice`, all via `research run --queue`.

| step | run | started | status |
|---|---|---|---|
| build (K=4096: GPU prover key 47340c664cec521f, Lean 88a84ea16d7e8f86, inner staged) | r20261005-064451-cec2 | 06:44Z | failed: the prover's kernels use `clmad`, which node 1's host CUDA 13.0 ptxas rejects (Lean built) |
| build, CUDA 13.3.1 from NVIDIA's redistributable archives under FLOCK_WORK | r20261005-064928-7c4f | 06:49Z | passed: binary dc3d91dd…, inner m = 35, k_log 24, nbl 11, 2,048 instances, circuit 567 MB |
| inner: proxy M0 ×(1+3), replay, rec_vstar; loopback M0 and --zk ×(1+3) | r20261005-065337-4837 | 06:53Z | passed (GPU 4; prover on 16 cores 96-111, verifier 112-127) |
| ostage: V*'s 7 RecOpen statements (`rec_outer --link-rows`, 4 at once) | r20261005-065619-2e26 | 06:56Z | passed: every level staged, every query opened |
| oprove: each level --zk on loopback ×(1+3), upstream replay --zk | r20261005-070734-c714 | 07:07Z | passed: every session accepted (serve, replay --zk) |
| inner rerun: loopback M0 and --zk only (INNER_PROXY=0), prover cores' background load recorded | r20261005-071603-4d28 | 07:16Z | passed |
| alg: InnerClaims + rec_residuals (InnerRepCheck, both reps) on the inner's last proxied session | r20261005-072008-d624 | 07:20Z | failed: InnerClaims gave the verifier no partition object (the inner binds `verity/partition/v1`) |
| alg again: InnerClaims `--partition` (the inner's q-word object, checked against META), rec_residuals | r20261005-073130-72a8 | 07:31Z | passed: claims 2:03 wall at 3.0 GB; InnerRepCheck staged, 4,281 products, holds on both reps, 16:20 at 19.7 GB |
| oprove alg: the algebra --zk on loopback ×(1+3), upstream replay --zk | r20261005-075524-97c1 | 07:55Z | passed: 4 of 4 accepted by serve, the last by replay --zk (prover cores 99.8% busy before it) |
| build K=14336 (N=512): the second size's inner staged | r20261005-075635-aef2 | 07:56Z | passed: m = 35, k_log 26, nbl 9, 512 instances, circuit 1.93 GB, stage 16:01 at 43.5 GB |
| lean: Lean `verify --zk` on V*'s 8 last sessions (4 at once), then the inner's proxied session | r20261005-080101-741c | 08:01Z | passed: all 9 accepted |
| inner K=14336: proxy M0, replay, rec_vstar; loopback M0 and --zk | r20261005-081442-dc2b | 08:14Z | running |
| lean zk: Lean `verify --zk` on today's --zk session (K=4096) | r20261005-081504-864d | 08:15Z | running |

## Shape of V* at m = 35 (from `rec_algebra.fast100(35)`, before any run)

fast100 at m = 35 has 7 Ligerito levels (m = 27 had 4), so V* is 7 `RecOpen` sessions plus the algebra. Per level (both reps):
L0 `RecOpen{64,16}` 436 openings × 45 compressions; L1 `{16,15}` 212 × 37; L2 `{16,13}` 142 × 33; L3 `{16,12}` 106 × 31;
L4 `{16,10}` 86 × 27; L5 `{16,8}` 72 × 23; L6 `{16,6}` 64 × 19. 40,630 compressions, 3.31e9 SHA-512 rows for the two reps
(1.65e9 per rep). Unit slots: L0–L4 2^22, L5–L6 2^21, so by table size the outer is about 2^34.4 rows against the inner's
2^35: an estimate to be replaced by the measured runs.

## Inner and today's numbers, same node and build (measured, r20261005-065337-4837)

Medians over 3 timed sessions after 1 warm; prove = the prover's `prove_total_s` (both reps), session = the rollup's
definition (time between verdicts), verify = serve's own `verify_s` per session (circuit already loaded).

| statement | prove | session | verify | bytes/rep | host RSS | GPU peak |
|---|---:|---:|---:|---:|---:|---:|
| inner M0 against the rec proxy (salted SHA-512 of rounds and caps) | 0.875 s | 0.909 s | upstream replay: accepted, 8.96 s wall incl. parse | 963,794 | 20.7 GB | 74.0 GiB |
| inner M0 on loopback | 0.722 s | 0.873 s | 0.392 s | 963,794 | 20.8 GB | 71.9 GiB |
| `--zk` on loopback (main) | 5.53 s | 7.85 s | 6.88 s | 1,179,202 | 21.1 GB | 74.0 GiB |

The proxy adds 0.15 s of prove (its Python round trips): 278 rounds, 510 message rows, 2,082 coins and 16 caps per
session. `rec_vstar` (V*'s hashing reference) accepts the proxied session: 1,118 openings over 7 levels, 510 message rows.

Main's `--zk` against the rollup's 1.063 s (cfbad08), decomposed from main's own records: the mask-rank check (`ZKRANK`,
`zk_veil::mask_rank_ok`, single-threaded Gaussian elimination over all 262,144 mask words, 2 then 4 claim points) 2.60 s
per session; level 0's hiding draw (`level0_zk`, one ChaCha stream, single-threaded, counted in rep 0's `prove_s`) 1.03 s;
the two reps' device proofs 0.84 s each (cfbad08: 0.52 s; `t.zk_inner` 0.11 s against 0.01 s, and about 0.2 s between
`t.total` and `t.upstream`). Neither CPU step is in cfbad08's numbers, and both are linear in the statement's blocks, so the
outer pays them too; the ratios below are given against both baselines.

## V* staged (measured, r20261005-065619-2e26)

| level | template | instances | unit rows | block | padded m | stage wall | stage RSS | circuit |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| L0 | RecOpen{64,16} | 436 | 3,335,169 | 2^23 | 32 | 6:02 | 8.3 GB | 498 MB |
| L1 | RecOpen{16,15} | 212 | 2,686,977 | 2^23 | 31 | 6:49 | 6.8 GB | 406 MB |
| L2 | RecOpen{16,13} | 142 | 2,401,281 | 2^23 | 31 | 5:14 | 6.1 GB | 367 MB |
| L3 | RecOpen{16,12} | 106 | 2,258,945 | 2^23 | 30 | 4:36 | 5.7 GB | 347 MB |
| L4 | RecOpen{16,10} | 86 | 1,973,249 | 2^23 | 30 | 4:04 | 5.1 GB | 308 MB |
| L5 | RecOpen{16,8} | 72 | 1,679,361 | 2^22 | 29 | 3:31 | 4.4 GB | 268 MB |
| L6 | RecOpen{16,6} | 64 | 1,393,665 | 2^22 | 28 | 3:08 | 3.8 GB | 229 MB |

Committed size, padded: 2^33.43 over the 7 statements against the inner's 2^35 (0.34×); the earlier 2^34.4 estimate
assumed 2^24 blocks.

## V*'s RecOpen sessions with --zk (measured, r20261005-070734-c714)

Each level on loopback, GPU 4, the same build, prover on 16 cores and serve on 16; medians over 3 timed sessions after 1 warm.
Every session accepted by serve (4 of 4 per level) and the last one by upstream's `replay --zk`.

| level | m | instances | prove | session | verify (serve) | bytes/rep | host RSS | GPU peak | rank check | level-0 draw | replay --zk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| L0 | 32 | 436 | 1.277 s | 1.777 s | 1.480 s | 1,037,530 | 8.3 GB | 10.9 GiB | 0.695 s | 0.142 s | accepted, 13.5 s wall |
| L1 | 31 | 212 | 0.798 s | 1.237 s | 1.244 s | 1,005,602 | 5.5 GB | 6.8 GiB | 0.352 s | 0.113 s | accepted, 10.4 s |
| L2 | 31 | 142 | 0.767 s | 1.187 s | 1.185 s | 1,005,602 | 5.4 GB | 6.7 GiB | 0.341 s | 0.105 s | accepted, 9.3 s |
| L3 | 30 | 106 | 0.507 s | 0.848 s | 1.043 s | 946,586 | 4.5 GB | 4.6 GiB | 0.141 s | 0.078 s | accepted, 8.7 s |
| L4 | 30 | 86 | 0.572 s | 0.853 s | 0.927 s | 946,586 | 3.8 GB | 4.6 GiB | 0.147 s | 0.072 s | accepted, 7.8 s |
| L5 | 29 | 72 | 0.448 s | 0.684 s | 0.683 s | 834,202 | 3.1 GB | 2.8 GiB | 0.133 s | 0.078 s | accepted, 6.6 s |
| L6 | 28 | 64 | 0.356 s | 0.586 s | 0.654 s | 777,946 | 2.6 GB | 2.2 GiB | 0.063 s | 0.073 s | accepted, 6.2 s |
| sum | | 1,118 | 4.726 s | 7.172 s | 7.216 s | 6,554,054 | max 8.3 GB | max 10.9 GiB | 1.872 s | 0.661 s | |

The device work is small (L0's two reps: `t.total` minus the rank check about 0.15 s each); the rest is per-session CPU work
of `--zk` (rank check, level-0 draw, the inner proof and replay, about 0.06-0.07 s a rep) and the round trips.

## Today's numbers again (measured, r20261005-071603-4d28)

The prover's 16 cores were 77% busy with other lanes' no-pool jobs just before each run (queue jobs naming no pool share
96-127), and the numbers hold: M0 0.728 s prove, 0.876 s session, 0.382 s verify; `--zk` 5.21 s prove (rank check 2.49 s,
level-0 draw 0.97 s), 7.50 s session, 6.90 s verify, 1,179,202 bytes/rep, 21.3 GB host, 74.0 GiB GPU; upstream `replay --zk`
accepted. Main's `--zk` on this node is 5.2-5.5 s.

## K = 14,336 needs only the inner and the algebra

V*'s RecOpen statements depend on m alone (fast100(m)'s levels, lanes, Merkle depths and query counts), so at m = 35 the
seven statements are the same for K = 14,336 as for K = 4096; only the inner and the algebra's Shape(35, k_log, c) change.
