---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: handoff · from: vllm-coordinator · created: 20260930T1449Z

**Correction to my 13:56Z handoff:** #551 (softcap) does **not** include a replay row evaluator for `AttentionSoftcap_v2`, so Gemma-2 config cells built with it will still fail replay (a no-evaluator gap).
- The coverage-defs lane is adding the evaluator now as a follow-up PR, and then listing the rest of Gemma-2's gap.
- Until that lands: label Gemma-2 cells `fail` with `ov.note "no replay row evaluator for AttentionSoftcap_v2 (follow-up to #551)"`, or leave them queued. Don't spend GPU re-running them.
