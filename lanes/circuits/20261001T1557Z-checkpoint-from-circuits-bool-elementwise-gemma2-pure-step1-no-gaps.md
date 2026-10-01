---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T15:57Z

**Gemma-2-2B step 1: no gaps on main (8:57 AM PDT).** I ran `boolean-purity --dry-run` on main `d784c58ee` against
`cov-k06-7`'s Gemma-2-2B TP1 B1 greedy word Program (i256/o15; word Program `02a49d51…`). Result: **0 non-Boolean
Definitions, 0 specializations**. All 21 derived Calls map to their Boolean versions: `AttentionSoftcap_v2→_v3`, `Gemm_v2→_v3`,
`MeanTriton`, `RsqrtF32`, `NarrowF32ToBf16`, `Bf16Tanh`, `GeluTanhMul` and the dense rows (`art:6674b1e5…`). Node 1 has no TP1
B1 greedy 256/32 Gemma-2 row yet, so step 2 submits one. Branch `cursor/bool-gemma2-pure-8c79` is off main, with no change
needed so far. Next: the `cov-g2b-bool` row on the boundary tree.
