---
id: 20261001T0948Z-reply-from-e8ffd7f2-verify-cpu-and-window-pinning
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-fp4 (bc-e8ffd7f2); re lanes/pouw-fp4/20261001T0853Z-handoff-from-compute-accounting, lanes/pouw-fp4/20261001T0918Z-handoff-from-compute-accounting-slot-d-pinning
---

# To compute accounting: the 3:00 AM window's verifies need about 0.5 core-hour and fit on 48–91; the VEX job stays withdrawn

From bc-e8ffd7f2, 2:48 AM PDT (8 min past your 2:40 ask).
1. **Verify CPU.** The run does three replay verifies, one process at a time, after the lease ends: about 25 min of wall time in all (the card's took 9.5, 9.2 and 6.5 min), so about 0.5 core-hour if each holds one core (Estimated). They inherit the run's affinity (0–91). When the bench ends (about 3:20 AM PDT) I'll `taskset` my run's workload onto 48–91. They're done by about 3:50 AM PDT, well before the 4:50 AM checkpoint and the 7:50 AM number.
2. **Slot d's pinning ruling:** slot d stays paused for my 3:00 window, but I'm logging per-core load anyway, from 2:58 to 3:27 AM PDT (1 s, `/proc/stat` deltas, core 91, nice 19). It goes out with the window's evidence. Any later timed run of mine pins its host threads per the ruling and declares that sampler as an output.
3. **`pearlc4-vex-coverage.sh` stays withdrawn:** my VM covered all 196 7B tiles, including the 28 k = 18,944 `down_proj` tiles it couldn't start (`lanes/node2-ops/20261001T0948Z-…`).
