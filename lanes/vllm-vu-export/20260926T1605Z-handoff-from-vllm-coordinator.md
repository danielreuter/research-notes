---
lane: vllm-vu-export
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T16:05Z
---
# Re your 1547Z ask: steps 1–4 approved now; step 6 queued, pending Daniel's budget

- **Approved by Daniel (root, 15:52Z), yours to run now:** build `Q_word_v1{X}` and the `query/word.py` width check; diff the manifests on
  all 13 rows; and **one #101 L40S run** to confirm the run root is unchanged (your plan's step 4; about $2–5).
  - Your pods are under the vyv- guard. Spend is $716.74 of $770, and the deadline is 16:45Z; I step it (≤ 4 h) if the #101 run
    needs longer. Tell me the expected end.
  - Keep `Q_module_body_v1` as the query of record: the new query stays opt-in. I review your PRs against that, and against #101
    run root / Program / manifest = record.
- **Not approved:** switching the query of record, and step 6 (the re-baseline epoch, about $150–250, over the cap). Both sit at the top
  of my after-epoch queue as "pending Daniel's budget decision", together with the rest of this epoch (right-sized re-records, deferred
  2c/3/4, #4's reclassification), so one epoch covers all of it.
- **If Daniel approves step 6:** yes, it runs as a lane under the vLLM coordinator, as last time (brief, pods under the guard, merge and
  review through me). I'd brief it from your plan's §5 and the epoch review packet.
