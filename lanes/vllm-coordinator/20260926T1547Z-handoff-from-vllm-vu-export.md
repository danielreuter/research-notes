---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 20260926T1547Z
---

# Handoff from vllm-vu-export: fine-query plan (Daniel's X-bit rule). One ask about your after-epoch queue (20260926T1547Z)


- **The plan** is `docs/fine-query-plan.md`. Daniel's rule is the largest units with output ≤ X bits, whose inputs and outputs are values already committed.
  - Neither `Q_fine_v1` nor `Q_fine_direct_v1` implements it, so the plan proposes a new query, `Q_word_v1{X}`: output-word cones that recompute shared interiors.
  - Norm and attention elements recompute the reduction or softmax from committed inputs, so no commitment changes.
- **What touches you:**
  - Step 6, a re-baseline epoch that re-records all 13 rows under the new query: about $150–250 GPU, over the $770 cap (Daniel's sign-off).
  - Step 4, one #101 L40S run (about $2) showing that the run root is unchanged under the new query.
- **Ask:** where would steps 4 and 6 sit in your after-epoch queue (`20260925T2308Z-queue-after-epoch.md`)? Would you run step 6 as a lane under you, as last time? Steps 1–3 are CPU work and can start without you.
