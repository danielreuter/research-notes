---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge request + verdict · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T03:07Z

# #351 (`a5b3b222`), prerequisite 5, the call-boundaries gate: APPROVED once it's out of draft

**What it does:** `verity-vllm gate call-boundaries <row dir>` passes when every `call_boundaries` identity has a source the Commit attaches.
- **Two cases:** an unclaimed identity is covered by S1b's host plan (`call_boundary_source.plan_of`); a claimed one names an attached source (`unattached`).
- **Failure:** otherwise it exits 1, naming the first identity without a source.
- **Callers:** the row driver (`row_stages`, `row_tp`, `row_driver`) now runs it instead of the blanket `call_boundaries` stop.

**Tests,** merged onto main `b4fd93e9` (clean): `tests/acquire`, `tests/pipeline` (including the new `test_row` cases), the vLLM lints, `test_no_by_name_rules` and `test_no_dead_modules`.
- They pass, except two failures already known on main: `test_closure_covers_every_core_file` (fixed by #338) and `test_compiled_source::test_renumber…` (class C of the 02:27Z triage).
- The new `test_gate_call_boundaries.py` covers pass, uncovered and unattached.

**Please confirm on the check pod:** the gate passes on #74's stored Build (`art:39d08c35`). That's the plan's acceptance for lifting the stop.
