---
cursor:
  subagentId: "bc-eab8c043-7f1c-5a4d-802c-0b9aa73f289b"
---

# Handoff from vllm-vu-export: PR #92, the #101 sampler resolved; merge-ready, please re-review (20260926T2310Z)

lane: vllm-vu-export · kind: handoff · from: vllm-vu-export (agent bc-eab8c043) · created: 20260926T2310Z · re: `internal/lanes/vllm-vu-export/20260926T2245Z-handoff-from-vllm-coordinator.md`

**PR #92** (`cursor/no-recompute-partition-289b`, head `194ac3f9`, now based on `main`, with main merged in cleanly, including #86 and #90).

## What the sampler does, and what I changed

- **The finding:** `GumbelTopPTokenSelect_v1` computes `temp == 0` twice, once in `TemperatureScale_v1` (the kernel's early-return
  `skip`) and once in `GumbelSelectF32_v1` (`noisy`). That is **one** repeated gate per Call. It is the only repeated value in any
  Definition of the 13 rows. `GumbelTokenSelect_v1` has the same pair.
- **Where it sits:** the whole sampler is one unit, since its output is one 32-bit token. Both copies are in that unit, so no boundary
  runs through the value. Option (b) doesn't apply: there is nothing to tap.
- **Under the invariant it isn't a recompute either.** "Each computation gate is computed in exactly one unit; cross-unit reads go only
  through committed values." The value is computed in exactly one unit and read by no other. The old check was stricter than the
  invariant: it failed any repeated value, even inside one unit.
- **The fix is in the checker** (`8e18a2b7`), not in the Definition:
  - `validate_unit_cut` fails `gate-recomputed` only when copies of a value sit in **different units**. That is the rounds router's
    failure, and it stays caught (test `test_a_recompute_fails_the_cut`, plus a new core-level case).
  - A copy inside its own unit is counted as `detail["redundant_gates"]`, carried by `unit_rule` and program.json.
  - The recompute check stays in permanently.
- **Why not option (a), restating the sampler:** any restatement moves the sampler's Definition digest, so #101's Program changes. The
  Program's structure is also mirrored in C-Flock's lowering (`verity_flock/ir_sampling.py`), `census/subcircuits.json` and the
  captured-101 bench manifests. None of that seemed worth it for 1 gate in 2.18 M. Flock's verifier already computes
  `[temp, rcp, skip, noisy]` once per row as public row scalars.
- **Semantics to confirm:** this reads "no recompute" as "no value computed in two units". If Daniel wants no repeated value even
  inside one unit, the restatement is small: compute `is0 = F32Eq(temp, 0)` once in `GumbelTopPTokenSelect` and pass it to flag-taking
  variants of `TemperatureScale` / `GumbelSelectF32`. It is not built, because it is a Program change for every stochastic row plus the
  Flock and census moves.

## Checker output

- **#101, strict `verity-vllm manifest build --word-check 16/32`,** from the row's fixtures (`programs` `art:a9be8f7c…` + `records`
  `art:a4ea1a18…`), locally on CPU:

  | Tree | Policy | rc | Result |
  | --- | --- | --- | --- |
  | #92 at `b21ce332` (before) | off | **1** | `QueryRuleViolation: … GumbelTopPTokenSelect_v1{V=128256}: cut, 32 Call(s)` (normtap's finding, reproduced) |
  | #92 at `194ac3f9` (after, main merged) | off | **0** | 46,558 Calls, 64,169,215 committed interior words. Manifest digest `368283ad…` = the record's (`commit/manifest_verify.json`) |
  | #92 at `194ac3f9` | `--norm-scales` | **0** | Same query result, 9,471 words acquired by the tap. Manifest `03c89529…` (the opt-in policy's own) |

- **Every row, every Definition** (`with_word_rules` over the 13 rows' program graphs, on `8e18a2b7`): 0 violations and 0 cross-unit
  recomputes on all 13. The one repeated value is the sampler's, 32 redundant gates on #101. No other row has any. Recompute findings
  to list for other owners: none.
- The #101 program.json is regenerated (its `cut: 32` is gone, and it now carries `redundant_gates: 32`), with the index updated. The
  dataset is `art:f0c33059…`, superseding `art:9362857f…`. The other 12 rows' files are unchanged: their numbers don't move.

## Tests and lints (local stub runner on the merged tree; no gate (b))

- Pass: `test_word` (22, three of them new), `test_program_graph` (10), `test_norm_scales` (9; one monkeypatch test not run locally),
  `test_moe_router_ordered` (8) and `program/test_lint` (31).
- Also clean: P01–P12, `test_no_by_name_rules`, `test_no_dead_modules` and `test_imports_resolve`.
- `test_program_graph::test_word_rules_per_group_and_row` pinned the pre-#92 query id and failed at the old head. It now pins
  `R=no-recompute`.
- **Not run:** the full gate (b), which needs a pod; say if you want it before merge. Spend: $0, all CPU on the VM.

Evidence: `notes-asset:lanes/vllm-vu-export/evidence/no-recompute/` (`rc13.json`, `rc13.py`, `gumbel_rc.py`, the #101 manifest logs).
The plan doc (`docs/fine-query-plan.md` §0) is corrected.
