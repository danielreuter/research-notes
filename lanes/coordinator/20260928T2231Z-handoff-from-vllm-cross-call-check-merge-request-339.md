---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
lane: coordinator
kind: handoff
from: vllm-cross-call-check (bc-f7aadce6)
to: research coordinator (bc-8ece7cde)
cc: vllm-coordinator (bc-ecac3029)
created: 2026-09-28T22:31Z
---

# Merge request: PR #339, three of #337's known failures (the untied lm_head tests), stacked on #337

- **The PR:** [#339](https://github.com/danielreuter/verity/pull/339), branch `cursor/untied-lm-head-tests-666c`, head `bb0728fc`, on
  #337 (`cursor/gate-vllm-suite-f880` @ `dedcb565`). Merge it after #337.
- **The triage** (rows 2–4 of `20260928T2223Z-plan-from-vllm-coordinator-337-known-failures.md`): the tests were stale, and the
  refusal rule is right.
  - `Serve_v4` reads an untied checkpoint's own `lm_head` field (`b1.weights_type` / `b1.lm_head_of`), so the diagnostic `ServeUntied`
    family is `Serve_v4` node for node. The PR retires it; nothing outside the tests read it.
  - The tests now check what holds: `Serve_v4`'s untied binding differs from its tied one only at the 16 lm_head operands, and the
    untied Program reads V×H more input words than the tied record.
  - The `Serve_v1` family refusal stays.
- **The three entries** are deleted from `integrations/vllm/tests/conftest.py`'s `KNOWN_FAILURES`, and the three tests pass outright.
- **No digest moves:** no Program, manifest, construction source or profile identity is touched.
- **Tests:** `test_gen_ov_easy.py`, `test_derive.py` and the lints pass. No pods.
