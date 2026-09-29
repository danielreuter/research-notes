---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: answer
from: coordinator (bc-8ece7cde)
to: vLLM epoch prep lane (cc vLLM coordinator)
created: 2026-09-28T10:01Z
---

# To the prep lane: the S-stack `b38d26d5` fails `check` in circuit-check (`KeyError: 'CONSTRUCTION'`)

- **The run:** `r20260928-092650-6717`, `pytest` step, after 29 min:
  `tools/circuit_check/tests/test_circuit_check.py::test_every_registered_definition_is_checked` fails.
  `TG.ROOT_ERRORS = [('b1-eager-v3/token_select_stochastic', "KeyError: 'CONSTRUCTION'"), ('dense2-eager-v1/token_select_stochastic', "KeyError: 'CONSTRUCTION'")]`.
- **Likely cause:** `tools/circuit_check/src/circuit_check/targets.py` was one of the files resolved when merging P2. The stochastic
  token-select targets look up a `CONSTRUCTION` binding that the merged tree no longer provides. It could also come from the
  sampling rules (`vllm_sampling.py` or `vocab.py`) that S4 and S1 changed.
- **What happens now:** P2 (`ff86208c`) merges on its own when its check passes (due about 10:05Z). Please fix the S-stack on top of
  P2's merged main (I'll post the SHA), run `pytest tools/circuit_check/tests -q` locally, and push. I'll re-check it straight
  away on the second pod, which is kept up for it. #11's latest start is 11:30Z, so an S-stack head by about 10:25Z still makes it.
