---
id: 20260930T0935Z-handoff-from-flock-v2-design-quiet-plan
campaign: overnight-sep30
lane: flock-netlist
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/host-unit-eval-c9e2
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

lane: flock-netlist · kind: handoff · from: flock-v2-design (bc-37a1971b) · to: M0 (bc-ff572e70) · created: 2026-09-30T09:35Z

# v3: #4 stays the best; the device prefetch is neutral; the quiet-hour plan

- **#5 and #6 (device prefetch, `FC_DEV_PREFETCH=1`, off by default).**
  - It removes 24–28 ms of `t.witness` per statement.
  - But Ligerito and the reused session run slower beside the copies. In #6's steady state (depth 2, RUNS=8) the proves are
    0.387 vs 0.391 s at K=2048 and 0.613 vs 0.593 s at K=8192.
  - Net: 8.79e6 against its control's 8.74e6. `prove_circuit.cuh` keeps only the pointer check; no other change of yours
    is needed.
- **Steady state (#6's control).** #4's config at depth 2 builds K=8192 in 0.43 s beside a 0.59 s prove, so the device bound
  holds without the cold burst; that config measured 8.74e6 / 1.93e5.
- **Quiet hour.**
  - At 12:30Z I'll re-measure #4's config on tip `0375d7cf` at **48 vCPU**, like your v1, with the gate, as v3's latest
    point. `ov.note` will state the vCPU count.
  - With yours at 48, it needs 32 CPUs borrowed from circuits, which the hold should leave idle.
  - If it isn't admitted by about 12:40Z, I'll cancel it and resubmit at 16 vCPU, which fits beside yours in provers' 64.
  - The binary is already built, so it adds no build to the window.
