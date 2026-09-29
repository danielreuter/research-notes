---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029), one-stage audit (bc-c520c11b)
created: 2026-09-28T04:42Z
---

# Merge request: PR #220, one partition implementation (consolidation fix 5), right after #219

- **PR:** [#220](https://github.com/danielreuter/verity/pull/220), branch `cursor/one-partition-ac68`, head **`1457fa1f833ed79addbd1064bfb9a13fd05c5a87`**.
- **Order:** stacked on #219's branch, because both add one-stage tests and the merge commit resolves that once. Merge #219 first, then #220; or take #220's head alone, which lands both.
- **Contents:**
  - `verity_one_stage.partition` delegates to core's `verity.ir.partition_object`, so core's `order_violation` and malformed-object checks now apply;
  - core's `template_id` becomes public;
  - vLLM's verbatim copy of `cut.separable` in `query/word.py` is removed, and `word.py`, `verity_flock/boolean_export.py` and the cross-call test call core's.
- **Nothing recorded moves:**
  - tests, added before the change and passing on the old module, pin byte equality with core and with the pinned vectors;
  - no digest, vector, Lean file, `lean-audit.json` or circuit changes.
- **Tests:** `protocols` 66; core `ir` + boundaries 263; vLLM `test_word.py` + `test_cross_call.py` 38; `test_boolean_export.py` 3; `circuit_check` 828 passed, 2 xfailed. After merging #219's branch: 337 across protocols, profile and template tests.
- **Epoch:** moves no digest of record, so it may land any time, G0 included.

**For the vLLM coordinator:**
- The only edits in the integration are `query/word.py` (the `_separable` copy deleted and core's imported) and a one-line change in `query/cross_call.py` and its test.
- If S1's PR edits `word.py`, rebase over this; it's about 25 lines.
- **An optional add for the epoch:** vLLM's `Q_word_v1{…,EXTRAS,R}` label is in no digest. But it is written into recorded outputs (the Boolean export's `commitments.json` and `index.json`, the program graph's `q_word_v1` field, circuit-check reports) and read back by `boolean_export` and `serving_view`.
  - With `EXTRAS = 0` it means exactly core's `partition_object.query(X, W)`.
  - Since those outputs are rewritten in the epoch anyway, S1 could record the core query object there, with the field and its readers switched together.
  - Your call; I made no change.

**For the one-stage lane:** #168's `protocols/one_stage` files equal `main`'s, so it needs no rebase. Its new `a4.py` uses only names #220 keeps.
