---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator · created: 2026-09-27T02:40Z

# Program graphs regenerated (`art:c74deac4…`), and PR #99 merge-ready: tap labels; no partition, checker or manifest digest moves from #99

**The export lane can rerun now.** The 13 program graphs are `art:c74deac43ad3f8ad9b634266ac02d04091f90c011ef33018a12b0d3e5d6f30` (preserved). They supersede `art:f0c33059…`, and are mirrored in `internal/datasets/program-graphs/`. `art:d583032e…` was an intermediate put (its `ops` files didn't match its index); ignore it.

- **Code:** `main` `fa662029` + PR #98 `d7f76916` (the `unit_rule` member check) + PR #99 `13c294d6` (labels). The graphs were built with vu-export's `program_graphs.py` (`--record expected`), then `catalog`, then `with_word_rules`. The scripts are in the notes: `lanes/vllm-cross-call-check/evidence/{regen13,label13,index13}.py`.
- **`param_inputs` (#94):**
  - Present on the 11 rows rebuilt from their programs artifacts.
  - **#4 and #101 keep the previous graphs**, with Q_word_v1 re-applied: their redraw Builds (run `r20260926-035624-a133`) are not in the store. For their `param_inputs`, the export lane's next pod run must rebuild them from a fresh Build (`program_graphs.py` on the pod, as `vux_row.sh` did).
- **Checks** (`checks.json` in the dataset):
  - Every row has the same calls, modules, groups and edges as the old index.
  - Units, gates and committed words are identical on all 13 rows.
  - `max_scaled` words equal the plan table on every row (#101: 242,688 exactly).
  - New-tap bytes per token equal the plan table on the 9 non-MoE rows, within 1 B of rounding on #39 and #74.
  - The 4 MoE rows are higher (#67: 80,036 against 18,484), because the graphs partition the recorded kernel-order router, while the table uses the selection-order router (§4b's two columns).
- **Violations:** only #74, `cut` on 581,040 Calls. This comes from #98's member check (FP8 block scale product), not from #99.
  - Without #98 the rows have 0 violations, as before.
  - #101 keeps its 32 redundant gates (the sampler's; #101's sampler PR removes them at the re-baseline).

**PR #99 merge-ready:** [PR #99](https://github.com/danielreuter/verity/pull/99), branch `cursor/max-scaled-not-committed-666c` @ `13c294d6` (base `main` `fa662029`, merged in).
- `max_scaled` (attention `F32MulFtz_v1`): `committed_today` is `None`, and `new_tap_in` is "FA2 / FA3 tap build (MS plane, `max_scaled`)".
- Guarded max (`GuardNegInfZero_v1`): it **stays a new tap**, as the table treats the opt-in norm-scale and router taps. Its `new_tap_in` is "FA2 / FA3 tap build (ROW word 3, opt-in `GUARDED_MAX_TAP=1`, #95)".
- `tap_kernel(scope, head)` is used by `with_word_rules`.
- This is a label change only: the partition, the checker and every manifest digest are unchanged (#101 `368283ad…`).
- Tests: `test_word.py` (the new test sits beside `test_query_id_and_parse`, so it doesn't conflict with #98), `test_program_graph.py`, `tests/lint` and `program/test_lint` pass.
- #98 and #99 merge cleanly in either order.

**Plan doc** (`docs/fine-query-plan.md`):
- A `max_scaled` column, with its bytes moved from "Committed today" to "New taps", per your table.
- §3's `max_scaled` row reads "none today (MS plane pending)"; the heading is "All but two".
- A tap-list bullet; the §0 summary reads "the guarded max and `max_scaled` are new taps".
- The guarded-max column is marked "built, #95, opt-in".
- §4b and §5 use moetap's `topkGating` wording (from `lanes/vllm-vu-export/20260927T0102Z-handoff-from-vllm-rf-moetap.md`).
- §0 names the two recomputes found after the fact (FP8 #74 and Gemma #57, see the #98 handoff), and the dataset id.
