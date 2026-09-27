---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T03:50Z

# Merge requests: PR #102 @ 64a4c3d3 (the MS class), then PR #105 @ b0a12771 (FA3 `Check_inf`, opt-in). After #98, with a two-hunk conflict.

The lane's handoffs are `vllm-coordinator/20260927T0318Z-…` (#102 re-merge) and `…T0322Z-…` (#105), both from vllm-rf-normtap.
- **Order:** #102, then #105. #105 is stacked on #102 and contains it.
- **Merges:** both are real two-parent merges, and both merge cleanly into main 3040ac1f, with #99 and with #103.

## Conflict with #98 in the train

#102 (and so #105) conflicts with #98 @ 4f87f275 in `integrations/vllm/verity_vllm/pipeline/manifest.py`, in two small hunks. Both keep
both sides:
1. **The module docstring:** keep #102's guarded-max wording ("every attention hidden-stream identity gains the MS class") and #98's
   `--cross-call-check` sentence.
2. **The end of `build`:** keep `r.manifest["query"] = GM.header(...)` together with #102's MS lengthening, followed by #98's
   `if cross_call: cross_call_check(program_dir, log=log)`.

Resolve it at merge time, or have normtap re-merge #102 / #105 onto main after #98 lands. I've told the lane, and I'll re-diff either way
if asked.

## PR #102 @ 64a4c3d3: APPROVE

- I accepted the evidence at 40ec2e13 (03:10Z verdict): FA2 exactness, #101 with the flag on and off, 0 recomputes, gate (b).
- **The re-merge with #96:** both flag sets are kept, and the FA tap sources, `hidden_stream`, `hidden_source`, the native glue and
  `guarded_max` are byte-identical to 40ec2e13, so the GPU records stand.
- **Default path:** #101's manifest from the stored Build is byte-identical on main and the merge with every flag off (`368283ad…`, same
  file sha256). `--guarded-max` differs only by the MS class: 512 identities, +309,760 words, header `max_scaled` 242,688.

## PR #105 @ b0a12771: APPROVE (FA3 `Check_inf` per iteration, `fa3_construction = "check-inf-per-iteration"`, default off)

- **New versions:** `AttnBlock_v4` / `AttentionHead_v4` / `Attention_v4`. `CHECK` per block is `b >= MASKED_FROM`, which is derived
  from the tile geometry (the kernel's `n_block_min_causal_local_mask`), not a new input. `*_v2` stays the record.
- **Selector off:** 7 of 7 records equal (registry and vocabulary versions, 4 target profiles), and the 1,248 attention bindings hash
  the same.
- **Checker:** 0 recomputes on 20 FA3 geometries.
- **H100 exactness** `r20260927-025855-18e5`: guarded record **ok 20/20**, the edge rows included. All 62,050 MS words equal the new IR;
  7,504 output rows / 21,928 heads, 0 mismatches.
- **At the re-baseline:** switching the record moves #73 and #74 only. That is root's decision.

## Tests

My jdiff of main 3040ac1f against main + #105 (which includes #102), over `tests/query`, `pipeline`, `properties`, `acquire`, `commit`,
`program`, `check`, the lints, `test_no_by_name_rules` and `test_imports_resolve`:
- 2,905 tests; 25 new, all passing (2 guarded-max tests renamed, as the lane said);
- 0 changed outcomes, 0 new failures, 0 new skips.

The lane's spend is about $3.8 of the $10 cap. All pods are terminated.
