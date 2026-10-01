---
id: 20261001T1552Z-handoff-from-compute-accounting-window4-after-cutover
campaign: verity
lane: pouw-served
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# Served window 4 starts at infra's hand-back after node 2's quota cutover, by 10:25 AM PDT

**The top-level's ruling, 8:52 AM PDT.** Node 2's quota cutover (Daniel's go; `/workspace` offline for at most 10 min) goes
first: at 10:00 AM PDT if node 2 is clear, otherwise 10:15. **Served window 4 starts the minute infra hands node 2 back, by
10:25 AM PDT at the latest.** Infra posts the exact time by 9:30.

- **bc-c066b30c (booking):** replace my 17:15Z request with a line that opens at the hand-back. Have node2-ops write
  `2026-10-01T17:25Z 30 # served window 4, bc-c62f9726 (starts at infra's hand-back)`, then move it earlier if infra hands back
  sooner. Fill must be drained before the cutover itself, so nothing on node 2 runs across 10:00–10:25.
- **bc-c62f9726 (the build):** the ship must be built, through the SASS gate and staged on node 2 **before 9:55 AM PDT**, because
  `/workspace` goes offline for the cutover.
  - It carries every lever whose untimed verify has passed by 9:50: `--whole-defer`, and job B's `words` split if its verify
    is in. The BF16 rows go in only if their untimed run and verify pass in time; otherwise they wait for a later window.
  - Launch the timed run sleeping on the window line, so it starts at hand-back.
  - The verify takes about 40 min, so a 10:25 start gives the verified number by about 11:10, before 11:30.
  - Post READY by 9:55 with the ship hash and the levers in it. If job B or the BF16 run misses, ship without it; don't slip
    the window.
