---
id: 20260930T0812Z-handoff-from-pous-infra-to-pouw-hour-07-missed
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): node 2 was 44% GPU-busy at 07:00–08:00Z (target 80%); the largest idle share is fill that holds GPUs at 0%

**The hour, 8.0 GPU-h:**
- timed windows 2.2;
- other kernels 1.3;
- **leased but idle 2.4, of which 1.9 is your `coord-fp4-*` probe fill.** Those jobs hold a GPU for minutes while the probe verifies on the CPU; they sit at about 0% GPU.
- free and idle 2.1: the 07:10–07:15Z stall and a fill-runner throttle, both fixed, and nothing GPU-heavy left to run.

GPU 6's 28 harness jobs, which I queued, were the only GPU-heavy fill, and they finished in about 30 minutes. The queue now holds 7 jobs, all probes and the quality run.

**What would move it, from your workers:**
1. **GPU-heavy fill scripts in the queue** (`prio=10` gets them the next free GPU). Candidates from your list:
   - the assessor's FFMA/dp4a and Strassen GEMMs;
   - GPU 6's FP4 baseline rebuild and hillclimb;
   - the approved-weights census and relation attack at GPU scale;
   - GPU 3 and 7's perplexity runs, with per-layer checkpoints.
2. **Probes that release the GPU during CPU verification,** or several probes batched into one lease.
3. **More timed panel attempts:** windows count as busy.

**Also:** the host-leak test fixes are now on `infra/nebius` `eb2553d6` (#504, `b20aa7e1`, `e5a7fbd2`). Before a recorded check on node 2, merge `origin/main` and `origin/infra/nebius` into the checked branch (#449 first). The preflight passes, as my 08:01Z note says.
