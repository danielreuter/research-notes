---
id: 20261006T0601Z-report-noise-sweep
campaign: pouw
lane: compute-accounting
kind: report
status: final
repo: verity
origin: noise-sweep
---

# noise-sweep: Pearl-C's served decode overhead over stock FP8, without hashing and with -h2, across batch, context and graph mode

**Tier 2a throughout: untimed, preemptible one-GPU screens on node 2 (RTX PRO 6000, sm_120), no SASS gate, not panel rows.**
Scheme `pearl-c-sm120-v1-h2`, rows form s; its no-hash arm is the same run with hashing off (noise and denoise only).
Every ratio is a Pearl-C rep over the stock FP8 reps on either side of it in e2e's interleaved cycle (fp8, pearlc, fp8,
pearlc-nohash, fp8, bf16, with a graphed fp8 rep after each fp8 rep). Each cell gives the median and [min, max] over every
rep of every replicate (each replicate has its own beacon and seeds). Decode step = (t(1+64) − t(1)) / 64. SM clocks were
2040–2092 MHz in every arm. The combined summary is `art:f380f6fbdbf85cde711d1bf6bebd87ea000848120308e4e64e1a5ccc62cfa3b5`
(sweep.json, sweep.md, curve.md, the points files and the renderer). Code: branch `cursor/pouw-noise-sweep-e3fa` at 261597558.

## The answer

The served configuration is `--whole-step --whole-defer`, the served row's switches. Its fair baseline is stock FP8 with
vLLM's CUDA graphs. Against that, for Llama-3.1-8B:

| batch | context | graphed FP8 ms/step | no-hash / FP8 | -h2 / FP8 | hashing's share |
|---|---|---|---|---|---|
| 16 | 64 | 7.4 | 2.18 [2.16, 2.22] | 2.65 [2.62, 2.75] | 0.47 |
| 32 | 64 | 7.5 | 2.16 [2.14, 2.18] | 2.67 [2.66, 2.70] | 0.51 |
| 64 | 64 | 7.8 | 2.06 [1.98, 2.07] | 2.63 [2.53, 2.67] | 0.57 |
| 128 | 64 | 8.9 | 2.44 [2.38, 2.49] | 2.93 [2.86, 4.09] | 0.48 |
| 256 | 64 | 14.9 | 1.73 [1.71, 1.75] | 2.12 [2.09, 2.16] | 0.39 |
| 16 | 2048 | 10.2 | 1.86 [1.84, 1.88] | 2.23 [2.20, 3.04] | 0.37 |
| 32 | 2048 | 13.5 | 1.67 [1.65, 1.68] | 2.04 [2.01, 2.78] | 0.37 |
| 16 | 4096 | 13.6 | 1.65 [1.64, 1.67] | 1.93 [1.91, 2.74] | 0.28 |

So noise and denoise alone cost 2.1–2.4× graphed stock FP8 at batches of 16 to 128, and 1.7× at 256. Hashing (-h2) adds
another 0.4–0.6×. A longer context dilutes both, because attention, which Pearl-C does not touch, grows on both sides.
Qwen3-8B agrees with Llama within 2%: whole-step b32 2.12 / 2.67, b128 2.47 / 2.96, b16-p2048 1.85 / 2.21.

**Today's "about 1.08×" is the per-call `--graphs` arm at b32, no-hash, over eager stock FP8 (1.09× here).** Eager stock
vLLM is host-bound, at 17–45 ms/step against graphed FP8's 7–15 ms. Against graphed stock FP8, the same arm is 2.72×.

## Where the no-hash time goes

Profiled under nsys with graph-node tracing. The profiled ratios match the unprofiled ones within 2%. Times are kernel ms
per decode step:

| batch | graphed FP8 step | no-hash step | Pearl-C GEMM vs stock FP8 linear | forming (stats_s5, form_s5, A′·F_B words) | other |
|---|---|---|---|---|---|
| 32 | 7.7 | 16.6 | 8.3 vs 5.3 (+3.1) | 5.4 | +0.3 copy |
| 128 | 9.1 | 22.3 | 12.4 vs 5.9 (+6.5) | 5.8 | +0.5 copy |
| 256 | 14.7 | 26.1 | 14.1 vs ~10.7 (+3.4) | 6.0 | +0.6 copy |

- Forming is flat in batch, at about 42–47 µs per linear call (128 calls per step). It is a fixed per-call, latency-bound
  cost, not a per-token one.
- Pearl-C's GEMM takes 1.3–2.1× as long as stock's CUTLASS FP8 linear (CUTLASS 3's `device_kernel`).
- b256's lower ratio comes from stock's own linear, which roughly doubles from b128 to b256.
- With -h2 and `--whole-defer`, the hashing kernels (tile hash, A tree, tree) add 7.0 ms at b32. They partly overlap the
  step: wall time grows by 3.9 ms.
- `served_profile.py` filed stock's `device_kernel` under "other". Fixed at 261597558; the numbers in this note
  reclassify it.

## Other modes (the full curve is curve.md in the artifact)

- `--whole-step` without `--whole-defer`: b32 2.14 / 2.93, b128 2.46 / 3.18. The no-hash ratio is the same as with defer;
  defer cuts hashing's share at b32 from 0.79 to 0.51.
- Per-call `--graphs` over graphed FP8 (Llama): b1 3.55, b8 3.77, b32 2.72, b128 2.76, b256 2.00, b8-p2048 3.09,
  b32-p2048 1.96 (no-hash). Each has wide ranges (up to 6.9×), because per-call launches contend for the node's busy host.
- Eager over eager FP8, no-hash / -h2: b1 1.89 / 3.75, b8 1.74 / 3.61, b32 1.85 / 3.68, b128 1.65 / 3.62,
  b256 1.43 / 2.91, b512 1.40 / 2.44, b1024 1.40 / 1.83, b8-p2048 1.95 / 4.30, b32-p2048 1.56 / 2.95,
  b64-p2048 1.38 / 2.62. The deferred schedule: b32 1.72 / 3.81, b128 1.69 / 3.08. Both are host-bound and noisy (per-rep
  ranges of ±30%).
- Largest batch that fits:
  - Eager reaches 1024 (memory fractions 0.30 / 0.36). At 0.32 / 0.40 the arm ran out of memory on a 4 GiB pass buffer;
    2048 would need about 34 GB of KV per resident engine.
  - Whole-step is bounded by GRAPH_ROWS = 256.
  - Per-call graphs were tried up to 256.

## For the assessor

- Measured over **eager** stock FP8, the whole-step no-hash ratio falls below 1.00× at b16–b64 and at b16-p2048
  (Llama 0.67–0.97; Qwen 0.74–0.99). These rows are flagged in sweep.md. The other whole-step rows sit at 1.03–1.10. The
  cause is a graphed arm measured against an eager baseline. They are not a win.
- A ruling is needed on which baseline "stock FP8" means in served claims. I recommend graphed stock FP8, which is what
  vLLM serves by default. Under that baseline, today's 1.08× is about 2.7× per call, and about 2.2× with the whole-step
  schedule.

## Gaps and method notes

- Preemption: of 155 leases, 63 (41%) were preempted. The rate rose from about 6% in wave 1 to about 90% in waves 6–7,
  where priority work took whole groups of GPUs at the same second. Three points have one replicate rather than two:
  eager b1024, Qwen whole-step b16-p2048 and the b256 profile. The b16-p2048 profile has none. The sweep stopped there
  rather than keep queueing behind priority work.
- Runs: r20261006-023458-d2bb (wave 1, eager), r20261006-025331-a2d3 (wave 2, the capacity fix, graphs and whole-step),
  r20261006-034504-6cbd (wave 3: Qwen, no-defer, deferred, p4096), r20261006-040102-affc (wave 4: profiles, b1024,
  replicates), r20261006-041559-2e57, r20261006-044021-86e4, r20261006-052256-d3f8 (waves 5–7: re-queues, profiles).
- Each point ran under `gpu-lease 1 --wait --preemptible --max-min` ≤ 20, ending by 13:58Z, with at most 6 GPUs at once.
  Wave 1's batches of 1, 256 and 512, and its 2,048-token context at b32, went over one pass's capacity (calls or screened
  rows). b96af4471 sizes the pass to the point. FLAG_ROWS = 2^22 is a real serving limit at large batch × context.
