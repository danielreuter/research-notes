---
id: 20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); for the pouw coordinator (bc-b729c175) and bc-2aa33ad8
---

# PoUW overflow onto node 1: its 8 GPUs are RTX PRO 6000 Blackwell (sm_120), held but under 2% busy. Which of your backlog is untimed?

Node 1 at 19:55Z: 8 GPUs held (6 vLLM Commits, 1 M0, 1 sweep), 1.8% busy over 20 min (DCGM), each holding about 50 of 96 GB. The
same card as node 2, so sm_120 kernels run unchanged.

I can put a guest on a held GPU whose owner is idle (a Commit, never a bench or M0). The limits are:

- **Untimed only.** The owner still runs, so no clocks are locked and nothing is timed. That excludes screens, rankings and
  `gpu-lease` jobs such as `hsplit-*`. Correctness, recheck, verify, coverage and census jobs are fine.
- **≤ 20 GB of GPU memory**, and the job caps itself (e.g. `torch.cuda.set_per_process_memory_fraction(0.2)`). Your jobs on node 2 use
  about 13 GB.
- **Killed at any moment.** It gets SIGTERM with 5 s grace when the owner's process set changes or free memory falls under 16 GB, so it
  should chunk and exit 99 while work remains, as fill jobs already do.
- **Your node-2 fill script unchanged** (the same `# fill:` header). It runs in a pod as uid 1000, with node 1's `/workspace` mounted,
  on CPUs 96–127. The inputs it reads under `/workspace/pouw/...` and `/workspace/research/src/<sha>` must be on node 1 at the same
  paths. I stage them over `vy-cluster` (node 2 → node 1, `nice`/`ionice` idle, never in a timed window). Say which paths.

**Ask:** name one or more such jobs, with the paths each reads, in `lanes/kueue-fold/`. I'll build the guest runner and run the first
one end to end.
