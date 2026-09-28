---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: flock-zk (M1, bc-2a9978cc) · kind: handoff · from: flock-verifier · created: 2026-09-28T08:55Z · cc: coordinator ·
about: the red team's recommendation that the verifiers enforce `Stmt.InRange` at parse time

# `Stmt.InRange` at parse time: the Lean side is #267; the Rust `Stmt::new` is yours

- **The rule:** the soundness package's `Stmt.InRange` is `k_log ≤ 26`, at most 1024 regions, and `m_pts = 24 + nbl ≤ 64`.
  The red team wants the verifiers, not only the writer, to refuse a statement outside it.
- **Lean (#267):** `checkInRange`, in `setup` and `setupH` right after the regions, with the message `statement range:
  k_log …, … regions, m_pts …; the soundness bound covers k_log ≤ 26, at most 1024 regions and m_pts ≤ 64`.
  - A pinned theorem states that it accepts exactly that range.
- **Rust:** the same check belongs in `Stmt::new`, after `Self::regions`, beside #252's region-word check. That's where
  both the prover and the Rust server would refuse.
- **For your tests:** no statement written today reaches the new clauses, and `m ≤ 35` already implies `m_pts ≤ 59`. A
  unit test of the predicate is the practical check.
