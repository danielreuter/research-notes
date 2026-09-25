---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T05:07Z
---

# SCOPE CORRECTION (user): commit x, W AND y and bind the commitments in the proof; public-input binding is not the full relation

Per the user's committed-relation rule (kb/TABLES.md "Same full relation"): binding the frozen x and W as PUBLIC inputs is not the
full relation (a verifier holding the operands could recompute the outputs). The target statement is:
- the prover commits x, W and y with a CORE-DEFINED commitment scheme (packages/verity `verity.commitments`, the scheme B-Ligero's
  --auth / in-proof-hash columns and SP1's guest already use; name the exact scheme id in the variant's configuration / security
  record, which feeds its Table 1 configuration), and the A-GKR proof binds its operand and output columns to those commitments
  (the verifier checks the binding; it never trusts the prover's word for which values were committed);
- its own relation name(s), with their own circuit-pin lines (PR #13, backends/gkr/verifier/pins.txt); never reuse bf16-ampere /
  fp8-ada / ... for the new statement.

Order:
1. Finish step 1 (integration a2edab4d + E4M3/NVFP4 pins; handoff "agkr integration ready") as planned.
2. The public-input version: finish it only if already nearly done (it is a useful intermediate and its negatives still matter);
   do not measure it on all five rows.
3. BEFORE building the committed version: estimate whether it fits your remaining budget ($15 cap) and FINAL (12:00Z). If it does
   not, write a handoff to lanes/coordinator titled "agkr-bound revised estimate" (design sketch: which scheme, where the binding
   check lives in the circuit/verifier, expected prover-cost delta, pod-hours and $), set your checkpoint to `blocked` on it, and
   wait for the answer (poll your inbox every ~10 min; keep the lane alive; terminate your pod while you wait).
