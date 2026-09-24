---
lane: arith
kind: report
created: 2026-09-24T19:04Z
brief: campaigns/afternoon/BRIEF.md (### arith)
branch: lane/arith (worktree ~/projects/verity-main-wt/arith), base main@22741456
final: 01:10Z hard; budget $10
status: open
---

CHECKPOINT 1a69ab6 (20:50Z) [open] 4090: s1 arith 0.0477->0.0417 verified (art:7775888d..); s2+s3 kernels bit-exact, A/B noisy; cause = ragged-layout graph captures in timed reps; fix 92ea2531 fixed slot per sub-batch, A/B running; next register+reverify, then H100
CHECKPOINT none (20:23Z) [open] steps 2 (0baefa9d lincomb2 w+v one pass, 0.39->0.25ms) + 3 (f550fdc6 intt_rows) bit-exact; step1 reverify PASS x3 (art:20f128cf art:d6273533 art:118efdc0); 3-arm A/B s1/s2/s3 running (pod noisy: medians)
CHECKPOINT none (19:57Z) [open] step1 quad_v4 9d1a7f15: 4090 v3x4 p8 A/B arith .0477->.0417, total .0968->.0875 (3v3); art:7775888d art:1523b35c art:021aeabb (trees preserved); reverify --by arith running; next: tests-graph glue + w/v fusion
CHECKPOINT none (19:42Z) [open] step1 quad_v4+reduce kernel (lane/arith 9d1a7f15) bit-exact; micro quad_general 1.40->0.785ms, quad_p0 1.88->~1.25ms; base on pod: 4090 v3x4 p8 total .1014 arith .0481; A/B r20260924-194155-a3a0 running
CHECKPOINT 99a3b82 (19:10Z) [open] started; pod vy-arith (4090 EU-RO-1, 5q4d3ealzkud5d, guard 90) up, syncing worktree; next: bootstrap, profile tests graph of fp8-ada-v3x4 p8 baseline
# arith: hill-climb the arithmetic phase of B-Ligero

Inbox at startup: nothing new.

## Baseline (Table 2 / Table 3 at the 1800Z render, B-Ligero column, authentication excluded)
| target | cell art | config | t.total s | arithmetic s | overhead x |
|---|---|---|---|---|---|
| A100 BF16 | art:e1fcf643 | bf16-ampere-v3 fused l=16384 | 0.2413 | 0.164 | 6.0e6 |
| H100 BF16 | art:aadcd93f | bf16-hopper-v3x4 fused l=4096 | 0.1292 | 0.0799 | 1.0e7 |
| H100 E4M3 | art:85569708 | fp8-hopper-v3x4 fused l=4096 | 0.0738 | 0.0426 | 1.2e7 |
| 4090 E4M3 | art:fb4934af | fp8-ada-v3x4 fused l=4096 p8 | 0.0907 | 0.045 | 2.4e6 |
| 5090 NVFP4 | art:d5c9e1f3 | fp4-nvf4 l=8192 p8 | 0.0340 | 0.0222 | 4.5e6 |

## Pods
- vy-arith 5q4d3ealzkud5d: RTX 4090 reference part, SECURE EU-RO-1, 8 vCPU, host Ryzen 9 7950X, $0.74/h, created 19:10Z,
  `guard = 90` in machines.toml.

## Log

### 19:25Z baseline on vy-arith (main 22741456, fp8-ada-v3x4 l=4096, 4096 VUs, reps 5)
- p8: t.total 0.1014, arithmetic 0.0481, enc+commit 0.0367; p4: 0.1081 / 0.0516. This pod has a 6.8-core cgroup quota (the
  headline pod 13.6) and is noisy: one p8 rerun at 0.2154, and any CPU work on the pod during a run (parsing a trace) inflates
  it 3x (s1-base-p8-r1 0.3505, void).
- Profile (torch.profiler on pass 3, /workspace/arith/prof/base-v3x4-p8): the pass is GPU-bound (union busy ~ wall unprofiled).
  Kernel time per pass: commit graph 119.5 ms (witness_program 54.7, blake3 26, rs_encode 18.3), tests graph 50.5 ms
  (quad_u32 20.1, boolcomb_rows 6.9, lincomb 5.6, ~17 ms torch glue over ~130 small kernels), hints 15.8 ms.

### 19:44Z step 1: general quadratic constraints in Montgomery arithmetic (lane/arith 9d1a7f15)
- `tests_fused.quad_v4`: 4 columns per thread (uint4 row loads, one CSR table read per 4 columns), lazy 4-product sums with
  one Montgomery reduction each, canonical 32-bit intermediates, rho staged in shared memory, constraint chunks as consecutive
  blocks (QFAST: the chunks of one column slice meet in L2), 128 threads x 128 chunks (swept on the real system).
  `reduce_partial`: the (S, D, cols) uint32 partial sums of every lincomb/quad call in one kernel (was int64 upcast+sum+mod).
- Bit-exact: tests_fused_test.py quad_v4 vs the scalar kernel over thread/split/qfast settings with values near p, and
  reduce_partial vs torch (PASS on the pod); kbench on the real system with random U: identical outputs.
- Micro (4090, real system): quad_general 1.40 -> 0.785 ms, quad_p0 1.88 -> ~1.25 ms per sub-batch.
- Interleaved A/B on vy-arith (base = main 22741456 tests_fused*.py in /workspace/src-base), p8 reps 5:

| arm | t.total s | arithmetic s | art (bench-result) |
|---|---|---|---|
| base r2 / r3 / (19:19Z r1) | 0.0932 / 0.0957 / 0.1014 | 0.0481 / 0.0468 / 0.0481 | art:ed45196e / art:42d37c74 / - |
| tip r1 / r2 / r3 | 0.0852 / 0.0895 / 0.0879 | 0.0392 / 0.0446 / 0.0412 | art:7775888d / art:1523b35c / art:021aeabb |

  Means: arithmetic 0.0477 -> 0.0417 (-13%), total 0.0968 -> 0.0875 (-10%). Run-files trees (proofs): art:dc7c1488,
  art:a06b309c, art:92f25bb9. All preserved (`data preserved` rc=0). Tip profile: kernel sum 0.2019 -> 0.1854 s per pass.
- Reverify (--by arith, producer check) running: r20260924-195635-207d.
- Reverify (--by arith, a producer check; Table 2 wants a non-producer): all three PASS -- custody 40/40, pinned
  fp8-ada-v3x4, 13/13 proofs, 2^-128.33 -- verdicts art:20f128cf (art:7775888d), art:d6273533 (art:1523b35c),
  art:118efdc0 (art:021aeabb), preserved.

### 20:05Z step 2: w and v in one pass (lane/arith 0baefa9d)
- `lincomb2_v4`: the ZK linear tests w = r.coefs and v = alpha.coefs[:m] read coefs (7126 x 4352 int32, 124 MB) once instead
  of twice; the coefficient matrices (int64, r a row-strided view of the challenge block) are reduced and Montgomery-scaled
  while staged in shared memory (drops the C32 conversion kernels), running sums canonical 32-bit (179 registers, no spill).
  The ZK prover no longer computes beta (discarded; it only sends v).
- Bit-exact vs two lincomb calls (tests_fused_test.py, row-strided C1 with negative / >= p entries; kbench on the real system,
  every thread/split setting). Micro: 0.392 -> 0.251 ms per sub-batch.
- A/B vs step 1 (3 rounds): s1 0.1000 / 0.1464 (outlier) / 0.0855, tip 0.0858 / 0.0877 / 0.1431 (outlier); arithmetic
  s1 0.0482 / 0.0753 / 0.0417, tip 0.0396 / 0.0382 / 0.0648. ~1 run in 3 on this pod is an outlier (host-side, not cgroup
  throttling: nr_throttled 2 over the session), so steps 2+3 get a 4-round, 3-arm A/B judged on medians.
  Profile: GPU union busy per pass 0.0890 -> 0.0827 s.

### 20:15Z step 3: quotient INTTs as one kernel (lane/arith f550fdc6)
- `intt_rows`: the h and q quotients' INTT_n (n = 16384) plus the n^-1 g^-i scale, one block per row in shared memory
  (was a bit-reversal gather, 14 torch butterfly stages and two scale kernels, ~45 us per call uncontended). Bit-exact vs
  field.intt * post for n in {2, 8, 1024, 16384} (tests_fused_test PASS on the pod).
- 3-arm A/B (4 rounds, rotating order; t.total s): s1 0.0843 / 0.0879 / 0.0870 / 0.3370; s2 0.0849 / 0.3673 / 0.1286 /
  0.1755; tip 0.3289 / 0.1605 / 0.3116 / 0.0926. Every arm has outliers; not decidable from these runs.

### 20:45Z noise diagnosis: lazy graph captures inside timed reps
- Capture-logging trees (dbg_patch.py, never committed): the 16 full-config captures (8 commit, 8 tests graphs, ~0.22 s
  each) happen during warm-up; the ragged 13th sub-batch (4 VUs) has its own tests-graph layout key, captured once per
  slot (~0.23 s). `prove_many` gives each job the lowest-index free slot, so completion-order wobble lands the ragged
  sub-batch on a slot that has no capture for it yet -> +0.23 s inside a timed rep, booked to arithmetic (the tests stage).
  That explains the 0.13-0.37 s runs in every arm; the code under test is not the cause.
- Fix (lane/arith 92ea2531, step 4): `pipeline.FIXED_SLOTS` -- sub-batch i always runs on slot i % depth (the next job waits
  for its slot; that slot's holder is always the oldest active job, which the scheduler already blocks on). The
  (slot, layout) pairs are then identical every pass, so only the first (warm-up) pass captures. This is a prover
  scheduling change (no proof-system change) -- disclosed to the coordinator.
- Step-4 A/B (s3 vs fixed slots, 4 rounds): s3 0.0831 / 0.0914 / 0.3427 / 0.0915, tip 0.0874 / 0.3456 / 0.0826 / 0.1859
  -- the fixed slots alone do not remove the outliers. Per-rep: t.total is the MEDIAN rep (phase_rep rule), and rep 1 was
  ALWAYS ~0.33 s: the untimed warm pass (relchain) proved subs[:depth] + subs[-1:], i.e. the ragged sub-batch as job 8 ->
  slot 0, while the timed passes run it as job 12 -> slot 4 (fixed) / wherever (old). So every run paid one ~0.25 s
  capture in rep 1 and an outlier needs only 2 more slow reps out of 4. (fp4/chain.py already warms with a full pass for
  the same reason, r20260923-091019-38d8.)
- Every graph capture costs ~0.22 s, nearly all of it a gen-2 gc.collect() that torch.cuda.graph runs on entry (dbg_patch2
  gc callback: gen=2 ms=211-229 before each capture) -- the big Python heap, not the capture itself.

### 21:10Z step 5: full untimed warm pass (lane/arith 92dab0ad)
- relchain warm pass = every sub-batch once (with FIXED_SLOTS: each slot meets exactly the layouts it will run).
  Result: tip rep 1 0.079-0.080 s (was 0.33-0.35 s in every run before).
- A second, independent slow-rep mechanism remains: timed rep 2 (right after rep 1's proof dump) is 0.3-1.9 s in most
  non-diagnostic runs of every arm, and was clean in all 7 runs made with PYTHONUNBUFFERED=1 + the capture log. Diagnosis
  run 77-dbg3.sh (per-pass stage/gc log, buffered vs unbuffered).
