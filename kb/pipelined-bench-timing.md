# Pipelined B-Ligero bench timing: graph captures and slow reps

Facts measured by lane arith (2026-09-24, lanes/arith/20260924T1904Z-report-arith.md; evidence/4090, evidence/h100).

## t.total is the median rep
`bench_vu_rel` (relchain) and `bench_vu_fp4` report the rep whose prover total is the median of `--reps`
(phases.median_rep, `phase_rep` in the result). One slow rep never moves it; three of five do.

## Graph captures inside timed reps (fixed on lane/arith 92ea2531 + 92dab0ad)
- The commit and tests CUDA graphs are captured per (stream, layout); the ragged last sub-batch (e.g. 4096 VUs at l=4096 =
  12 x 341 + 4) is its own layout.
- Each capture costs ~0.22 s, almost all of it the gen-2 `gc.collect()` that `torch.cuda.graph` runs on entry (big Python
  heap), not the capture itself.
- main's relchain warm pass proved `subs[:depth] + subs[-1:]`: the ragged sub-batch ran as job `depth`, i.e. on slot 0.
  `pipeline.prove_many` handed out the lowest-index free slot, so in timed passes it landed elsewhere. For 13 sub-batches
  at p8 that is slot 4 in FIFO order, so every run paid one ~0.25 s capture in timed rep 1 (4090 fp8-ada-v3x4, H100
  fp8-hopper-v3x4: rep 1 0.31-1.5 s vs ~0.07 s steady). With 25 = 3 x 8 + 1 sub-batches FIFO puts it on slot 0 and rep 1
  is mostly clean. fp4/chain.py already warmed with a full pass (r20260923-091019-38d8).
- Fix: `pipeline.FIXED_SLOTS` (sub-batch i always on slot i % depth) + a full untimed warm pass. Tip rep 1 = steady.

## Remaining random slow reps (host)
- 0.1-6.6 s reps in every arm on shared hosts (4090 EU-RO-1 Ryzen 7950X; H100 US-MO-1 Xeon 8470). All the extra time
  is main-thread time in the last stage (numpy copies out of pinned buffers into fresh host arrays); no gc in it.
- Most frequent in rep 2, right after rep 1's `--dump-reps 1` proof dump, but they also happen without dumps.
- Not fixed by PYTHONUNBUFFERED, glibc tuning (MALLOC_MMAP_THRESHOLD_ / MALLOC_TRIM_THRESHOLD_ lowers it), or
  `os.sync()` after the dump.
- fill-dc's H100 (EU-NL-1) was much quieter than arith's US-MO-1 H100: compare cells on the same pod, alternate arms, and
  use >= 4 runs per arm.

## Host class matters (5090 fp4-nvf4 l=8192 p8)
- The Table 2 cell art:d5c9e1f3 ran on a Ryzen 9 9950X host: 0.0340 s total, 0.0222 s arithmetic. The same code (main
  22741456) on a 5090 with an EPYC 9354 host got 0.077 / 0.066 in 7 runs, 2.2x slower.
- Torch 2.8.0+cu128, the driver, the instances and bf16 matmul throughput (227 TFLOP/s) matched, and no other GPU process
  was running. A host-bound (kernel-launch) phase is the suspect; this is not verified.
- Record the host CPU with every cell (the result's workload_fingerprint.hardware.cpu), and do not compare absolute
  numbers across host classes.

## Custody of pod-side puts
- `research notes checkpoint LANE final` reads the laptop catalog, which never sees `data put --preserve` done on a pod.
- To fix it, run a bounded laptop-side `research data preserved <ids>` in batches of about 7, with the store creds
  loaded; each batch takes about 6 s. After that the checker counts the arts as preserved.
