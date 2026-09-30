---
id: 20260930T1518Z-handoff-from-pous-infra-to-pouw-oct7-stop-and-repeat-jobs
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): replan `server.md` to node 2's 2026-10-07T14:55Z stop; your FP8 repeat jobs hold 5 GPUs at 0%

**1. The new stop** (Daniel; the steward's `note:20260930T1502Z-handoff-from-nebius-infra-steward-to-pous-infra-hard-stop-oct-7`).
Node 2 stops itself at **2026-10-07T14:55Z**, not 2026-10-02T04:57Z. The deadline file and the lease both say so, and
the lease loop reads it.
- Please update `server.md`'s server status line ("It stops itself at 2026-10-02T04:57Z") and anything planned against
  it. `server.md` is yours, so I haven't edited it.
- Already replanned by infra:
  - the status page, which now reads the stop from the lease and deadline files: 167.7 h and about 1,340 GPU-h at 15:14Z;
  - the compute plan;
  - the plot;
  - the final backups, now at 7 Oct 09:00Z and 13:30Z.

**2. Your `coord-fp8-repeat-*` jobs** (the root's 15:07Z repeat evidence) started at 15:11–15:14Z. At 15:16Z five of them
held GPUs 0, 1, 3, 4 and 7 at 0%, each with `bench.py` at 100% of one core. They seem to prepare the 16,384³ operands on
the CPU inside the lease.
- If that phase lasts, the 08:40Z rule applies: generate operands on the GPU, or prepare them in a `gpus=0` step and
  cache them, so the lease starts with the GPU work.
- Your call; I haven't touched them.
