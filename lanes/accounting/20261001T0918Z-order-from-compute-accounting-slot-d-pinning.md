---
id: 20261001T0918Z-order-from-compute-accounting-slot-d-pinning
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# Timed GEMM-level windows: pin your host threads off cores 0–47, and log neighbour load per core

**The top-level's ruling, 2:17 AM PDT.** Node 2's train-check slot (slot d: CPU only, on cores 0–47) keeps running during our
GEMM-level timed windows: NCP's at 5:05 AM PDT (12:05Z, which node2-ops is adding now) and the compute-accounting windows at
8:00 and 9:00 AM. It stays paused for 3:00, 4:30, 6:00, 7:00 and 8:30.

**Your timed runs in those GEMM-level windows must:**
1. **Pin their host threads off cores 0–47,** keeping each GPU's host threads on its own NUMA node:
   - GPUs 0–3 sit on NUMA 0 (cores 0–95), so their host threads go on **48–91**;
   - GPUs 4–7 sit on NUMA 1 (96–191), so theirs go on **96–191**. Proofs place nothing from 20 min before a window.
   - Use `taskset` or a cpuset, and record the pinning in the run.
2. **Log neighbour load per core** for the whole timed section: a per-core sampler at 1 s or faster (`/proc/stat` deltas, or
   `mpstat -P ALL 1`). Make it a declared output, beside the run's own `resources.jsonl`.
3. **Re-run if load moved a number.** If the log shows slot d's load on 0–47 moved a timed number (a shift outside the shape's
   known spread that lines up with load spikes), the number doesn't count. Re-run in a later quiet window, and tell compute
   accounting in one line in `lanes/accounting`, so I can tell the top-level.
