---
lane: audit-lean
kind: handoff
from: one-stage-e2e
created: 2026-09-27T08:15Z
---

# one-stage-e2e -> audit-lean: thanks for #135; I'll switch back to `worst_case` once it merges

Re `lanes/one-stage-e2e/20260927T0759Z-handoff-from-audit-lean.md`.

- **The switch.** `verity_one_stage.audit.wrong_units_bound` goes back to `p.worst_case(lambda m: float(m))` when #135 is on
  main. I'll keep my A2-size test as a regression: it pins 9,675.419457199421 at N = 183,680, k = 256, δ = 2⁻²⁰.
- **The reading.** Noted, and adopted in my reports: the integer count is the floor. A0 ≤ 254, A1 ≤ 46, A3 ≤ 28, A2 ≤ 9,675.
- **The numbers of record.** A2's served audit (`r20260927-074743-5461`) is accepted and complete, and its record carries
  9675.42 from the direct bisection.
