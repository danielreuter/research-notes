---
lane: bligero-real-k
kind: handoff
from: red-team-bligero-real-k (bc-cbd1f3e8-36d9-57ec-9a9b-feb10db40819)
created: 2026-09-26T09:17Z
---

# Your 0512Z class request: GRANTED WITH CONDITIONS (COMPLETE_ZK_BACKEND); proof_class on all 16 new-sender cells; note A1 before any more K8192 BF16 cells

The verdict, conditions and evidence are in `lanes/coordinator/20260926T0917Z-handoff-from-red-team-bligero-real-k.md` (evidence art:dc790613).

- **No break found.** None of the attacks got through: cross-K relabels in both directions, mixed-steps reps, steps / K lies,
  sized-frame digest tampers, R2 / R4, the real-K leaf scans, and malformed or replayed PROOF frames against the streaming sender.
- **Labels:** `proof_class COMPLETE_ZK_BACKEND` on the 16 new-sender cells, with a `finding HOLDS ...` label on each.
- **A1, the part that concerns your queue:** the chain test's field term is (deg / p)^6 per proof, and it is not in
  `protocol.soundness` or Rust `soundness()`.
  - deg comes from the linked-row count: 183 for BF16 K8192 (549 linked rows), which gives 2^-140.35 per proof.
  - Your cells stay at or below 2^-128. The tightest is b1d710da: 2^-128.104 becomes 2^-128.086.
  - A K8192 BF16 cell reported at 2^-128.00 to 2^-128.01 would fall below the bar.
  - Keep that margin until the accounting books the term.
