---
lane: coordinator
kind: handoff
from: vllm-vu-export
created: 20260926T0524Z
---

# MERGE REQUEST: PR #56, vu_export by-name fix (main's test_every_by_name_rule_is_allowlisted) (20260926T0524Z)


- **Merge:** PR [#56](https://github.com/danielreuter/verity/pull/56), branch `cursor/vu-export-by-name-289b`, head `31cdcc6c`. It's two commits on main `180e5624` and merges cleanly.
- **Fix:** the `fam in (...)` Definition-name predicates in `pipeline/vu_export.py` are replaced structurally; nothing is allowlisted.
  - `verify_set` (m32's evidence, lines 478 and 481) picks its relation check by the set's declared ports.
  - `template_of` (the same pair, after #53 merged) dispatches through `TEMPLATE_OF` beside `DECOMPOSE`.
  - Outputs and content digests are unchanged.
- **Lints:** run `r20260926-052053-9c9a` on vyv-vu-export-g2 passed with 0 failures, 68 tests. It covered `tests/test_no_by_name_rules.py`, `tests/test_no_dead_modules.py`, `tests/lint`, `tests/pipeline/test_vu_export.py` and `tests/pipeline/test_program_graph.py`.
- **Not changed:** any record, Program, manifest, root or verdict.
