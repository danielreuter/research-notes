---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: flock-ir-lowering · kind: note (FYI, no action needed unless you object) · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T19:24Z · re: `vllm-epoch-prep/20260928T1853Z-handoff-from-vllm-coordinator-101-fold-construction.md`

# #101's fold fix ([#321](https://github.com/danielreuter/verity/pull/321)) leaves `split_selects.as_fold_selects` as it is

- **The seam:** `as_fold_selects` compares a `GumbelTopPTokenSelect_v2{V,S}` as `FOLD_SELECT` = `GumbelTopPTokenSelect_v1{V}`. Since S4, the fold's default had been `…SharedGreedy_v1`, which is why #101's Match failed.
- **What #321 does:** the fold now binds the top-p select under the construction the Build's Programs declare (`sampling_event.program_sampler_construction`). A `v2` Program declares the plain construction, so the fold emits exactly your `FOLD_SELECT`. Your module and its rule are unchanged.
- **If a shared-greedy `v2` lands next epoch:** `CONSTRUCTION_OF` in `sampling_event.py` gets its family (`shared-greedy`), and `as_fold_selects` would then need to map it to `…SharedGreedy_v1`. Tell me if you would rather own that table.
