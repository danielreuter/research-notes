---
id: coordinator/20260927T0935Z-handoff-from-flock-netlist
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 855fe81f
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Estimate: re-recording the attention cell at 855fe81f (about $1.5, at most $2.5; 60–90 min); starting now

**Pods.** Two, both terminated again afterwards:
- an L40S prover;
- a verifier in the same data center (last time an RTX A5000 in EU-SE-1).

**Steps:**
1. Boot and build at `855fe81f`: about 20 min.
2. A GPU selftest of attention, since the circuit changed: about 15 min.
3. The cell over the same input set (`art:9551ba66`, T = 129, 16 heads): about 10 min per attempt, up to 3 under IX2.
4. Register the cell.

**Cost:** about $1.5 at about $1.2/h for the pair, and at most $2.5 if IX2 runs all three attempts and the build is slow. Spend
so far is about $30 of the $150 cap.

The new art replaces `art:47f7ec19` in the headline. After that: the device witness (next pod session, only once the code is
ready to test), then multi-table.
