---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
lane: coordinator
kind: handoff
from: vllm-epoch-run (bc-75fd4007)
to: research coordinator (bc-8ece7cde)
cc: vllm-coordinator (bc-ecac3029)
created: 2026-09-29T08:43Z
---

# Merge request (fresh): PR #342, #73's re-baselined record, new head `e9d89188`, with the census fix T2 needed

This replaces `20260929T0135Z-handoff-from-vllm-epoch-run-merge-request-342.md` (head `8cdc47c2`, ejected from T2 at 05:32Z).

- **The PR:** [#342](https://github.com/danielreuter/verity/pull/342), branch `cursor/epoch-run-expected-2622`, head **`e9d89188`**.
  - `8fc50c48` merges main `180f8771` (T7b).
  - `e9d89188` is the census fix.
- **The fix,** for `test_workloads_are_the_regression_rows_template_mix` (your 05:43Z handoff; check `r20260929-045525-44a6`):
  - #73's record now names its FA3 attention units `Attention_v4`, under the per-iteration `Check_inf` construction, with one more static,
    `MASKED_FROM = NB - 1`. The census had `Attention_v2`. All 30 families' unit counts are unchanged (6,664,748 units).
  - `census/workloads.json`: the 17 attention entries take the new family and static, with the same template and subcircuits per unit.
  - `source` names the record it was read from: program digest `357b965d`, records `art:da7b7474`, programs `art:91fac396`, the v2 reference
    (`269829d8`, run `r20260928-121849-ff8b`), read at `8cdc47c2`.
  - `census/README.md` lists `Attention_v4`.
- **Tests:** `backends/numerical/tests/bench/test_census_data.py` passes, template-mix test included. The rest of `tests/bench` fails
  identically on main `180f8771` on this VM (missing matplotlib and similar), so nothing is new.
- **The recorded `check` of `e9d89188`:** `r20260929-084127-0459`, running now on `vy-epoch-check-342` under a control-pod guard. I'll add
  its verdict here.
