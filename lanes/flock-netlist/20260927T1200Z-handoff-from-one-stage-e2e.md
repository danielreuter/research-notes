---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: flock-netlist · kind: handoff · from: one-stage-e2e · created: 2026-09-27T12:00Z · status: open · repo: danielreuter/verity ·
origin: A4 P6 run r20260927-112223-cc25 (PRESERVED), M0 PR #83 @ e226a920

# `flock-circuit prove` was OOM-killed at 64 GB on P6's GEMM K = 2048 member (6,171,648 instances, 923 drawn)

- **What happened:** the session for member m1 (GEMM K = 2048, shared rows 861 / 21,504, 6,171,648 instances) hit the pod's
  64 GB cgroup limit.
  - `prove` exited −9 after 99 s, with `oom_kill 1` in the cgroup's `memory.events`.
  - `serve`, on the same pod, logged `instances=6171648 … blocks=6171648 k_log=24 … built in 17.16s` and survived.
- **Memory (the run's `resources.jsonl`):**
  - `prove` reached **49.9 GB RSS and was still climbing about 1 GB/s** when it was killed;
  - `serve` held 6.0 GB, and the driver 4 GB;
  - anonymous memory hit 58 GB of the 64 GB.
- **The other members were fine:** GEMM K = 8192 (587,776 instances, 98 drawn) proved and verified, with `prove` at 22 GB,
  and RoPE did too. So the failure scales with the population, not with the draw.
- **The question:** is `prove`'s memory meant to scale with the population's instance count rather than the drawn units?
  If there's a flag or mode that holds only the drawn instances plus the shared tables, I'd use it. For tonight I'm rerunning
  P6 on a 256 GB pod, so there's no rush.
