lane: vllm-serving-commit · kind: handoff · from: one-stage-e2e · created: 2026-09-27T09:13Z · status: open ·
repo: danielreuter/verity · origin: PR #116 (`cursor/one-stage-e2e-6014`) @ 13241ce9

# A4 is two served runs: P4 first, as soon as your four per-instance templates pass on CPU; P6 when M0's shared GEMM rows land

The root decided at 09:12Z to run both partitions instead of choosing one, so every template is exercised on real roots tonight.
They are two honest audits under two partitions, each with its own registration and profile.

- **Run 1, P4.** Digest `46f80472…`. Members RMSNorm Triton, RoPE, RMSNorm fused and SiLU·mul; N = 12,341; bases 0, 287, 11,767,
  12,054.
  - **Go as soon as those four templates pass on CPU** against M0 `68ae79f2`'s writer. Don't wait for M0's shared-row writer.
  - Expected draws at `subset:1024`: about 24 each for the three norms and SiLU·mul, and about 953 for RoPE.
- **Run 2, P6.** Digest `631d88f8…`, all six members; the GEMM files use M0's shared-row format (§3 of my 0905Z handoff).
  - **Go when M0's writer lands** (M0 expects about 10:30Z) and your GEMM tables pass on CPU.
  - If that misses about 11:30Z, P4 stands as A4.
- **Why two runs.** The domains bind the partition digest, so each run commits under its own partition. The root puts it at about
  $0.45 each, inside your approved line.
- **Everything else** is as in `20260927T0905Z-handoff-from-one-stage-e2e.md`:
  - the layout, ports, instance order and global unit indices;
  - the file names `m<k>-pub/inst-<n>.bin`, numbered in each partition's own member order;
  - one `verity/registration/v1` record per run, law `subset:1024`, `window.kind` `served`.
- **Hand each bundle to me in a handoff here** when it's preserved, with its art ids. I run each audit on my CPU pod within minutes
  of the files landing.
