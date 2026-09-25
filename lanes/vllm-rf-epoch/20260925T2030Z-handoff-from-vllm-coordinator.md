---
lane: vllm-rf-epoch
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T20:30Z
---
# DECISION: option 2, with the 216–233 GB pods tried first. Deadline 03:00Z

- **The vyv- deadline is now 2026-09-26T03:00Z (8 PM PT)**, set at 20:26Z. The cap stays $770: spend is $540.70, and the
  project burn is $19/h.
- **Partial epoch accepted.** Rows that can't get memory stay on their old `expected/`, listed in READY.md and in the
  REVIEW handoff as "not re-baselined, pre-epoch evidence", each with its reason.
- **Before waiting on a ≥256 GB RunPod pod, use the pods you already have.** Measured at 20:25Z: `vyv-rf-epoch-big` and
  `tp70b` have 216 GB cgroups (2 GPUs each), and `tp70` and `h100` have 233 GB.
  - #39 died at 125 GB, and #67's head and base died at 175 GiB (b1c), so 216–233 GB may fit #39 and #11. Check the
    admission prediction first, **with epoch item 6 (the `workload_target` lag import) fixed**, so the prediction isn't
    about 12 GiB short.
  - Place a row only where the corrected bound fits the cgroup with margin, one memory-heavy row per cgroup at a time. Use
    `CUDA_VISIBLE_DEVICES` to put an L40S tp1 row on one GPU of a 2x pod, as b1 did.
  - **Don't queue #11 on moe67 or moe68** (about 125 GB; it will fail like #39).
  - Keep the ≥256 GB retry loop going. Anything that can't finish by about 02:30Z stays on old expected values.
- **Start item 7 (`research_tools.CLOSURE`) now**, on the VM or a CPU pod, in parallel. It's CPU-side and needn't wait.
- **Budget:** up to **$130** (was $110). Stop and ask before passing it.
- **7 PM PT:** the review packet won't be complete. At about 01:30Z (6:30 PM PT) send a status handoff: rows done and
  pending, the epoch commits (items 1–7), and the planned time for the `rebaseline.py write`. The coordinator reports it
  against the day plan.
- Checkpoint `WAIT ...` lines as before, then end your turn.
