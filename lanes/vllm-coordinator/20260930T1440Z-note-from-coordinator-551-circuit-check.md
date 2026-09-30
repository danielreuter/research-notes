---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: vllm-coordinator
kind: note
from: coordinator
created: 2026-09-30T14:40Z
---

# #551 came out of train TVI: it fails `tools/circuit_check`'s registered-definition test

- **The failure:** TVI's check `r20260930-135913-9920` failed pytest on `tools/circuit_check/tests/test_circuit_check.py::test_every_registered_definition_is_checked`:
  `('b1-eager-v3/attention_dot+MASKED_FROM+CAP', "TypeError: a softcap off the accepted target is registered only under FA2's per-iteration Check_inf")`.
- **Bisected locally:** `main` `be3149a1` passes; `main` + #551 `f23660d1` alone fails.
- **TVI now:** `be3149a1` + #552 + #553 (the `dead_code_keep.json` entries of both kept). Check `r20260930-143618-7121` on slot c; expected merge `5448a7de`.
- **Please:** fix #551 so every registered softcap definition passes circuit_check, then re-grant. It takes the next vLLM train (it unblocks the Gemma-2 cells).
