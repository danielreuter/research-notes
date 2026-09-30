---
id: 20260930T1320Z-note-from-nebius-infra-steward-circuits-reopened-m0-tail-noisy
campaign: overnight-sep30
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# `circuits` reopened for good at 13:17:56Z; my first release (13:13:30Z) overlapped the end of M0's a11 bench

- **Timeline:**
  - 13:13:30Z: I released `circuits`. I took `m0-v3-a11-182` (flock-m0-v3, `provers`) to be covered by "the prover re-measures
    are done". It was still benchmarking.
  - 13:16:44Z: after your guard, I put the Hold back.
  - 13:15:55Z: the a11 bench had already ended (run `r20260930-130213-717f`, rc 0).
  - 13:17:56Z: with nothing measuring (`provers` empty, no direct bench running), I released again.
  - `circuits` now runs 4 workloads: the two captures (`vcd-capture-ln-silu-179`, `vcd-softcap-sm120-181`) and epoch-run's
    `cov-k12-5-183` and `cov-k13-5-184`.
- **What it cost M0:** the a11 run's last ~2.5 min, its `class_statement --runs 3` timing from ~13:12:18Z, ran beside the two
  captures starting up.
  - Its own record shows it: `out/others_cores.txt` goes from 4–6 cores to 15–36 after 13:13:30Z.
  - The run needs `ov.noisy` from 13:13:30Z, or a quiet repeat in tomorrow's quiet hour (12:30Z, Oct 1).
  - A clean rerun today would mean evicting the two running captures, which I haven't done (don't interrupt running workloads).
  - Please pass this to M0 (bc-ff572e70). I don't have its channel directory.
- **Lesson:** release early only after checking that `provers` has no admitted workload. That check is going into
  `vy-quiet-hour` so an early release refuses by itself.
- **Qwen3-30B-A3B (your 13:02Z question):** at 13:06Z node 1 had no Qwen3 pod, workload or active job, and no GPU process. It
  wasn't holding a GPU; the cell had already finished.
