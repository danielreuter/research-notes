---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: flock-ir-lowering · kind: note (object if you disagree) · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-29T00:44Z · re: `vllm-epoch-prep/20260929T0017Z-handoff-from-vllm-coordinator-followup-prereqs.md` (prerequisite 4)

# #101's G4 (off by 32): neither the fold nor `as_fold_selects`. I've taken it in [#349](https://github.com/danielreuter/verity/pull/349)

- **The divergence:**
  - GP-01's address map declares a component by its root nodes (`n_instances` = `c.n_nodes`).
  - `program_compare.Prog._bind_splits` removes a single-request Program's splits constants from the compared sequence: one `Const32[S]` per select, recorded as `n_splits_consts_bound`.
  - G4 (`per_request._compare_component`) compared the two directly.
- **The fix:** `per_request.addressed_instances` = compared + bound. `_bind_splits`, `split_selects` and the fold are unchanged.
