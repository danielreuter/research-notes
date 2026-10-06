---
id: rec-ksweep/20261006T0505Z-finding-rec-ksweep-curve
campaign: flock
lane: rec-ksweep
kind: finding
status: active
repo: danielreuter/verity
origin: bc-40d090a9-36d4-501d-8cd0-915bf17f2de2 (rec-ksweep, for the proofs coordinator)
---

# The recursive witness ZK's overhead from K = 2048 to 16384

**Outcome.** The overhead, (inner M0 against the rec proxy + V*'s total `--zk` prove) / today's `--zk` prove, is
1.71× at K = 2048, 1.70× at 4096, 1.96× at 8192 and 1.99× at 16384. Recursion's own cost does not grow with K: V* takes
6.9 to 7.9 s at every K. The ratio rises because today's `--zk` gets cheaper (5.1 s down to 4.0 s): its zk-rank step
scales with the number of instances, and m = 35 halves the instances each time K doubles past 4096. K = 16384 is in
reach (inner GPU peak 80 GiB of the RTX PRO 6000's 96 GiB). The curve, its JSON and the assembler that rendered it:
`art:14821352140f16b745c9a9fb937292429383e2a26624cfb2a83c201d4747932f` (label `title`, by rec-ksweep).

Pipeline: `backends/flock/pod/85-rec-reprice.sh` at `cursor/rec-step2-95d4@b6139d9b6`, one STEP per `research run`
on vy-nebius-1, `FLOCK_WORK=/workspace/jobs/rec-ksweep`, `TAG=k<K>`. Statement: the `Gemm_v2{K, N=4096}` coordinate
(`GemmCoordinate_v2{K, DOT=HopperBF16WgmmaDot16_v1}`), with m held at 35. Medians over three timed sessions after one warm.

| K | instances | inner M0 (proxy) | V* `--zk` (levels + algebra) | today's `--zk` (of it zk-rank) | overhead | without the inner's coin wait | Lean V* / inner / today's `--zk` verify |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4096, rec-step2 | 2048 | 0.931 s | 7.898 s (4.747 + 3.151) | 5.339 s (2.49) | 1.65× | 1.61× | 449 s / — / — |
| 2048 | 2048 | 0.764 s | 7.940 s (4.590 + 3.351) | 5.098 s (2.43) | 1.71× | 1.69× | 463 s / 31 s / 34 s |
| 4096 | 2048 | 0.872 s | 7.750 s (4.526 + 3.224) | 5.082 s (2.40) | 1.70× | 1.68× | 478 s / 52 s / 54 s |
| 8192 | 1024 | 0.840 s | 6.893 s (4.340 + 2.553) | 3.949 s (1.22) | 1.96× | 1.93× | 441 s / 90 s / 94 s |
| 16384 | 512 | 0.881 s | 7.184 s (4.648 + 2.535) | 4.055 s (0.70) | 1.99× | 1.95× | 436 s / 175 s / 173 s |

Run ids (build, inner, proxy re-measure, vstage, oprove, lean):

- K = 2048: r20261006-024622-0722, r20261006-025029-49cd, r20261006-041015-2762, r20261006-034849-ad3d, r20261006-035959-b99f, r20261006-040848-96d5
- K = 4096: r20261006-023110-4fee, r20261006-025059-d2d2, r20261006-041006-97f1, r20261006-032431-a99f, r20261006-034840-bb77, r20261006-040615-0a8c
- K = 8192: r20261006-025009-dce9, r20261006-035529-b788, —, r20261006-040041-d97a, r20261006-041537-afc2, r20261006-042418-ee32
- K = 16384: r20261006-030016-e828, r20261006-040126-0b2d, —, r20261006-041547-19ad, r20261006-043025-e7b1, r20261006-043811-83d6
- reference (rec-step2): r20261005-204822-8403, r20261005-194909-c4fb, —, r20261005-214203-b6fc, r20261005-221419-ad0a, r20261005-224601-2a56

## What the curve says

- **V* is flat in K at fixed m.** Its seven level statements are the same circuits at every K (same instances, k_log 23,
  same bytes). The three algebra parts total the same 899 MB at every K, but split differently: at K ≤ 4096 alg-p0 pads to
  k_log 26 (1.45 s), and from K = 8192 on every part is k_log 25 (alg-p0 0.91 s): 0.54 s of the 0.86 s V* drops between
  4096 and 8192. The identical level statements take 4.34 to 4.65 s across this sweep's runs (4.75 s in rec-step2), which
  is the noise band on the shared node. V*'s proof is 19.5 to 19.6 MB at every K, against today's 2.36 MB.
- **Today's `--zk` falls with the instance count.** Its zk-rank step takes 2.43, 2.40, 1.22 and 0.70 s for 2048, 2048,
  1024 and 512 instances; the rest of its prove is 2.67, 2.68, 2.73 and 3.35 s. So the overhead's rise from 1.70× to
  1.99× is the denominator shrinking, not recursion costing more.
- **The inner M0 is flat** at 0.76 to 0.88 s against the proxy (0.69 to 1.21 s in loopback).
- K = 2048 carries half the multiply-accumulates of the other points: its instance pads to the same k_log 24 as K = 4096,
  so m = 35 caps it at 2048 instances.
- Lean: V*'s ten statements verify in 436 to 478 s at every K (JOBS=3 on shared cores). The inner's and today's `--zk`
  Lean verify grow with the inner circuit: 31/34, 52/54, 90/94 and 175/173 s, at most 9.6 GB.
- Peaks: V* 9.7 to 9.8 GB host and 10.9 to 14.3 GiB GPU. The inner M0 and today's `--zk` take 70 to 80 GiB GPU and 14 to
  30.5 GB host; the K = 16384 build took 13:08 at 47 GB.

## Checks

- **K = 4096 reproduces rec-step2** (`note:proofs/20261005T1536Z-finding-rec-step2`): V* 7.750 s against 7.898 s,
  levels 4.526 / 4.747, algebra 3.224 / 3.151, byte-identical V* proof sizes, today's `--zk` 5.082 / 5.339, inner proxy
  0.872 / 0.931 s. The binary hash differs (f31e1499 here, d2dd3a9a there) because the build path differs; the sources are
  the same commit.
- **Forgeries (K = 4096 only)** were rejected in exactly their statements, by the Rust replay and by Lean alike: comb at
  alg-p0 ("the batched constraint fails"), message at alg-p0 (ring-switch claim mismatch), sum at L0, L6 and alg-p2 (the
  batched constraint fails). The other six forged statements were accepted, as staged. Every honest statement, the inner
  and today's `--zk` were accepted by Lean at all four K.

## Caveats

- Every node-1 queue job runs on cores 96 to 127, which other lanes share. The Python rec proxy answers the inner's coins
  on that range, so its latency picks up their load. In the first inner runs at K = 2048 and 4096 the proxied prove read
  5.45 s and 2.29 s, of it 4.82 s and 1.61 s coin wait. I re-measured the proxy alone (TAG k2048r and k4096r, reading the same
  stage), and those runs (wait 0.10 s) are the curve's inner M0 term; the first readings are kept as `proxy_first` in the
  JSON. The "without the inner's coin wait" column takes the remaining wait out too.
- K = 2048 is built untiled (`FLOCK_GEMM_TILE=64x64`), because the default 4x4 tile fits the whole instance at K = 2048
  and the build then found no instance file (r20261006-023932-05e2, failed).
- GPU held: 0.50 GPU-hours by the lease records (of about 2 approved). Until 03:46Z (8:46 PM PDT) the node-1 pool was
  2 GPUs, then 8.
- An orphaned vLLM engine core (another lane's), left in an expired lease scope whose owner had died, held GPU 6 for about
  17 minutes, and `n1_lease` never signalled it. The fix is on branch `cursor/n1-lease-orphan-scope-2de2` (a61d6065a,
  test included), for the research coordinator to review.
- Cancelled: inner K = 4096 r20261006-023920-0f34 (its 60-minute timeout ran out in the GPU queue; relaunched with 150).
- My `data/` intermediates on the node are deleted (22 GB). The shared build (`cache`, `flock-circuit`, 2 GB) is kept.
