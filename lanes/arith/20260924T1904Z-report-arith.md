---
lane: arith
kind: report
created: 2026-09-24T19:04Z
brief: campaigns/afternoon/BRIEF.md (### arith)
branch: lane/arith (worktree ~/projects/verity-main-wt/arith), base main@22741456
final: 01:10Z hard; budget $10
status: open
---

CHECKPOINT cd3f5e5 (23:05Z) [open] A100 done: tip .2534/.1799 vs base .2873/.2062 (cell .2413/.164, pod slower); 4/4 reverify PASS, preserved; a100b terminated 23:05Z; ~$5.35 spent; next 5090 fp4-nvf4 l=8192 p8
CHECKPOINT f5b5810 (22:24Z) [open] H100 done: E4M3 tip .0742/.0432 vs base .0795/.0454 (cell .0738); BF16 live tip .1822 vs base .2499 (pod noisy, cell .1292); 13/13 reverify PASS, preserved; h100 terminated 22:23Z, ~$4.3 spent; next A100 bf16-ampere-v3
CHECKPOINT 5543d80 (21:36Z) [open] 4090 step5 (92dab0ad: fixed slots + full warm pass): tip total .0870/.0840/.0863/.0891 arith .0409 mean vs base .0968/.0477; reverify PASS x4 (art:def461c7 art:bb75ba4f art:d2b01b3f art:f3978133); handoff 2135Z; next malloc test then H100
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
- Step-5 A/B (4 rounds): s3 (f550fdc6) 0.0846 / 0.0851 / 0.0921 / 0.1211 (arith 0.0392 / 0.0391 / 0.0466 / 0.0545);
  tip 0.0870 / 0.0840 / 0.0863 / 0.0891 (arith 0.0413 / 0.0387 / 0.0400 / 0.0437): 0 of 4 tip medians off (was ~1 in 3).

| 4090 E4M3 fp8-ada-v3x4 l=4096 p8 | t.total s | arithmetic s | overhead x | art |
|---|---|---|---|---|
| Table 2 cell (main) | 0.0907 | 0.045 | 2.4e6 | art:fb4934af |
| base main 22741456 here (3 runs) | 0.0968 | 0.0477 | ~2.6e6 | art:ed45196e art:42d37c74 (+19:19Z r1) |
| tip 92dab0ad (4 runs, mean) | 0.0866 | 0.0409 | ~2.3e6 | art:def461c7 art:bb75ba4f art:d2b01b3f art:f3978133 |

  Overhead x scaled from the cell's by t.total (same native-peak denominator). Reverify --by arith PASS x4 (verdicts
  art:39382cd4 art:171af5c1 art:04e43e2e art:51788c35), all preserved (readback); sent to verify-po
  (lanes/verify-po/20260924T2140Z-handoff-from-arith.md). s3 arm results meta-only: art:bf963bc6 art:0c9c7c72 art:5fff3060
  art:8b57609d.

### 21:40Z the remaining slow reps (4090, diagnosis stopped)
- The rest of the noise is main-thread time in the LAST stage (openings unpack: numpy copies out of pinned buffers into fresh
  arrays): 97-313 ms instead of ~10 ms per pass, no gc in it (dbg3). Most often rep 2, right after rep 1's proof dump
  (dump-D: rep 2 0.831 / 0.082 / 0.555 s), but also without any dump (dump-N: rep 1 0.384, rep 4 0.416 / rep 2 0.446,
  rep 4 0.313). PYTHONUNBUFFERED makes no difference (dbg3 U vs B). glibc pinned (MALLOC_MMAP_THRESHOLD_=1 GiB,
  MALLOC_TRIM_THRESHOLD_=64 GiB) lowers but does not remove it (rep 2 0.195 / 0.316 / 0.419 vs 0.416 / 1.182 / 1.120).
  Consistent with host page-fault / reclaim stalls on a shared host (THP madvise); a single slow rep no longer moves the
  median now that rep 1 is clean, so no code change for it.
- vy-arith (4090) TERMINATED 21:40Z (19:10-21:40 = 2.5 h, ~$1.85).

## H100 port (vy-arith-h100 a3924egsj0agq3, H100 80GB HBM3 SECURE US-MO-1, 26 vCPU / quota 22.1, $3.49/h, 21:41Z)
- Bootstrap OK (RELS=bf16-hopper-v3x4,fp8-hopper-v3x4). Live verifier on the same pod under nice 19, LIVE_JOBS=4,
  ligero-verify f05bb9cb (= the cell's), live-verifier@92dab0ad.
- A/B h100-ab.sh (r20260924-214905-44a7): base = main 22741456's 5 changed files over the tip tree vs tip, 3 alternating
  rounds; E4M3 local then BF16 live; LIGERO_REFERENCE_HINTS=0 as fill-dc.
- Per-run t.total s (arithmetic s), rotating order:
  - E4M3 local base 0.0763 0.0826 0.1071 0.0736 0.0734 0.0895 (arith .0429 .0547 .0826 .0426 .0416 .0479);
    tip 0.0772 0.0732 0.0715 0.0822 0.0752 0.0706 (arith .0493 .0434 .0430 .0532 .0397 .0413).
  - BF16 LIVE base 0.6198 0.1925 0.2499 (arith .3970 .1195 .1506); tip 0.1822 0.2130 0.1530 (arith .1165 .1493 .0842).
  - BF16 local base 0.2213 0.1552 0.5473 0.1452 (arith .1380 .1191 .3357 .0904); tip h16L 0.1131 0.1588 0.1201 0.1333
    + hsy 0.1111 0.1076 0.1312 (arith .0642 .0897 .0840 .0882 / .0618 .0621 .0788).
- Base rep 1 (the capture): E4M3 0.31-1.52 s in every base run, tip 0.07-0.12 s. BF16 (25 = 3 x 8 + 1 sub-batches: the
  ragged job 24 is slot 0 in FIFO order, which is where the old warm pass captured it) base rep 1 is mostly clean.
- This pod is much noisier than fill-dc's EU-NL-1 H100: random 0.3-6.6 s reps in every arm (rep 2 most often). os.sync()
  after the rep-1 dump (untimed; diagnostic tree, not committed) does not help (hsy-sync 0.1599 0.9832 0.1178 0.1092).

| H100 (medians over runs) | t.total s | arithmetic s | overhead x | tip arts (verified --by arith) |
|---|---|---|---|---|
| E4M3 cell (main) | 0.0738 | 0.0426 | 1.2e7 | art:85569708 |
| E4M3 base here (6) | 0.0795 | 0.0454 | ~1.3e7 | meta: art:e1a11597 art:ba74492e art:27cbd152 art:dc10aedc art:dc1390dd art:c454adc2 |
| E4M3 tip (6) | 0.0742 | 0.0432 | ~1.2e7 | art:e9ae289c art:c6271278 art:8182f9ae art:efd871f6 art:7a8443b4 art:709ab20c |
| BF16 LIVE cell (main) | 0.1292 | 0.0799 | 1.0e7 | art:aadcd93f |
| BF16 LIVE base here (3) | 0.2499 | 0.1506 | ~1.9e7 | meta (registered.txt) |
| BF16 LIVE tip (3) | 0.1822 | 0.1165 | ~1.4e7 | art:415d6cde art:b23719dd art:16feee34 |
| BF16 local base (4) | 0.188 | 0.129 | - | meta |
| BF16 local tip (4 + 3 meta) | 0.1201 | 0.0788 | - | art:e3362256 art:064a3a75 art:593f8249 art:debd7e1d |

  Reverify --by arith: 13/13 PASS (E4M3 13/13 proofs 2^-128.33, BF16 25/25 2^-128.05), verdicts in evidence/h100/verdicts.txt;
  all 56 arts preserved (pod-side `data preserved` rc=0). The within-pod A/B favours the tip; the absolute BF16 live numbers
  do NOT beat the cell (pod noise) -- Table 2 should keep art:aadcd93f or be re-measured on a quiet pod.
- vy-arith-h100 TERMINATED 22:23Z (21:41-22:23, ~$2.44). Spend so far ~$4.29.
- verify-po request: lanes/verify-po/20260924T2226Z-handoff-from-arith.md (13 H100 tip results).

## A100 port
- vy-arith-a100 (l98atdkvkkmege, US, 22:25Z) TERMINATED 22:44Z unused: upload link < 170 KB/s (10 MB did not arrive in
  60 s), sync impossible (~$0.50). Replacement vy-arith-a100b (1porug6orhjdy7, A100-SXM4-80GB SECURE US-KS-2, host EPYC
  7742 x256, $1.59/h, 22:45Z; EUR-IS-1 had no A100). Sync needed rsync installed on the pod first.
- Bootstrap OK (BENCH_INSTANCES=1 RELS=bf16-ampere-v3). A/B a100-ab.sh (r20260924-225542-83fe), bf16-ampere-v3 l=16384
  p8 local, 4 alternating rounds, LIGERO_REFERENCE_HINTS=0:
  base 0.3067 0.2915 0.2667 0.2830 (arith .2260 .2109 .1945 .2014); tip 0.2374 0.2552 0.2540 0.2528 (arith .1599 .1784
  .1814 .1830). Base rep 1 0.311 / 0.328 / 0.855 s, tip 0.273 / 0.262 s (steady ~0.23).

| A100 BF16 (medians) | t.total s | arithmetic s | overhead x |
|---|---|---|---|
| cell (main, EUR-IS-1) art:e1fcf643 | 0.2413 | 0.164 | 6.0e6 |
| base here (4) | 0.2873 | 0.2062 | ~7.1e6 |
| tip (4) | 0.2534 | 0.1799 | ~6.3e6 |
- Tip arts (verified --by arith, 4/4 PASS, preserved): art:5bcbf3fb art:b83f1ff0 art:4e87bc8a art:228f07b1 (verdicts
  art:e683a0e1 art:3e969524 art:ffd250cf art:008dd251); base meta art:31046cd8 art:b32e7981 art:75f77e79 art:1fe99bf2.
  verify-po request lanes/verify-po/20260924T2306Z-handoff-from-arith.md.
- vy-arith-a100b TERMINATED 23:05Z (22:45-23:05, ~$0.53). Spend so far ~$5.35 (4090 1.85, H100 2.44, A100 0.50 + 0.53).
