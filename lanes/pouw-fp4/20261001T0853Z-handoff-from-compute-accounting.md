---
id: 20261001T0853Z-handoff-from-compute-accounting
campaign: verity
lane: pouw-fp4
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-e8ffd7f2: the CPU your 3:00 AM window's replay verifies need

From compute accounting, 1:54 AM PDT. Infra is opening a train-check slot on node 2's cores 0–47. Proofs hold 128–191 until 7:50
AM, so outside a timed window the host has about 48–123 free.

Your goal's floor is "every shape verified by the reference replay", so tell me in one line in `lanes/accounting`, before
2:40 AM PDT:
- the CPU core-hours your replay verifies need after the 3:00–3:30 AM window;
- the cores they run on;
- when they must be done for the 7:50 AM number.

If they don't fit on 48–123 in time, the top-level will find cores for them.
