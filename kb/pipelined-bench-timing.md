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

## Fused prover kernels: byte equality and shared-memory limits (lane red-team-arith, 2026-09-25)
- Under fixed coins (`backends/direct/ligero/redteam_arith_det.py` keys every os.urandom draw by sub-batch and draw
  number, reset per prove_many pass) arith's 9d1a7f15..92dab0ad dumps are byte-identical to main 22741456 on 5090,
  H100 and A100 (lanes/red-team-arith report; evidence art:34e47954, art:6f099c8b, art:6f8e4c5c).
- `intt_scaled` (intt_rows) runs only when 4n <= the opt-in shared memory: n <= 16384 on sm_89/sm_120, 32768 on
  sm_80 (166912 B), 32768 on sm_90. Only the H100 Table 2 rows reach it; the 5090 (n=32768) and A100 (n=65536) fall back.
- quad_v4 / lincomb2 launch with >48 KiB of dynamic shared memory and no opt-in, and do not fall back: CUDA_ERROR_INVALID_VALUE
  for D=6 with Q > 262144 general constraints per sub-batch, D=7 with Q > 224768, and lincomb2 at D=7 with a row chunk > 877
  rows. Table 2 shapes (Q 212-881, D=6) are far below; larger relations or Fiat-Shamir at scale would hit it.

## Custody of pod-side puts
- `research notes checkpoint LANE final` reads the laptop catalog, which never sees `data put --preserve` done on a pod.
- To fix it, run a bounded laptop-side `research data preserved <ids>` in batches of about 7, with the store creds
  loaded; each batch takes about 6 s. After that the checker counts the arts as preserved.

## Commitment building of B-Ligero + in-proof hash (lane hash-commit, 2026-09-25; paused when Poseidon2 was dropped)
- `bench-vu --commit-reps N --commit-evidence FILE` (lane/hash-commit 96cb0d28) builds the commitment 1 + N times, asserts
  identical evidence, and reports `commit.seconds` (median of the N), `commit.cold_seconds`, the breakdown
  `commit.{rows,chain,trees,host}_seconds` and `e2e.seconds` = commit + t.total. The evidence JSON holds tree roots, level shas,
  digest and chain shas. Without `--auth-cache`: Table 2's 4090 cell (1.04 s) ran WITH it, so its trees were loaded.
- Where main's committer spends 2.30 s (4090 fp8-ada, 4096 VUs): host numpy Poseidon2 in `Poseidon2Leaf.native` 1.77 s,
  the same sponges again in torch for the prover's chain states 0.33 s, `np.asarray` over 2 x 4096 x 1536 Python ints
  0.18 s (the instance lists; `.tolist()` in instances, converted back in commit), Python SHA trees ~0.04 s.
- lane/hash-commit b862be30: 0.035 s (cold 0.089), byte-identical (evidence, stmt files, Rust accepts). It uses one CUDA
  thread per committed row for the whole sponge, passes the instance arrays through, and hashes SHA-256 trees from a per-domain
  prefix `.copy()`. The last two carry over to any hash: a SHA-256 / BLAKE3 committer should not rebuild rows from Python lists.
- `research run --on M --send F --cwd DIR`: sent files land in `$RESEARCH_RUN_DIR/inputs/`, not the cwd.
- A `pods sync`ed tree has `.research-sync-files` and `.research-source.json` besides the git files, and it does ship
  tracked-but-ignored files; to prove a synced / patched tree IS commit X, `git add -A . && git add -f <git ls-files -ci
  --exclude-standard>`, drop those two, `git write-tree`, compare with `X^{tree}` (lanes/hash-commit 30-ab.sh).
