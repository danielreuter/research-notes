---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: merge request · from: vllm-coordinator · created: 2026-09-30T05:52Z

# Merge request: #477 in the first train after TVE, with #486 right after it once its gate passes

**Order:** TVE carries #465 first; **don't restart TVE** for this. Then the next train takes:
1. **[#477](https://github.com/danielreuter/verity/pull/477)** @ `4975dc66a5e50df9a48c6880348baf974f9aec31` (`cursor/vllm-sm120-attention-0ec6`). Stacked on #465 @ `f740c1d5`.
2. **[#486](https://github.com/danielreuter/verity/pull/486)**, stacked on #477. Its gate finishes around 06:45Z. I'll grant it and append its head here when the handoff arrives; if it misses the train's cut, it takes the next one.

**#477:**
- **What it does:** FA2 on sm_120 binds `Attention_v2{BN=fa2_kblock_n(D), DOT=HopperBF16WgmmaDot16_v1, INV=Fa2InvSum_v1}` for `blackwell_consumer`. cc 12.0 requires the FA2 hidden stream, and it adds the `fa2_target_capture` property record.
- **Size:** 7 files under `integrations/vllm/`.
- **What doesn't change:** sm_89 and sm_90 bindings, Program digests, manifests, the vocabulary version; no Definition is added.
- **Grant:** `pr:477@4975dc66…` grant vllm-coordinator, pushed to the remote store at 05:51Z.
- **Merge:** `merge-tree` is clean on main `eeaa6847`, since #477 contains #465.
- **Evidence** (RTX PRO 6000, cc 12.0, 188 SMs): `fa2_target_capture` `art:d342a748`, `Attention_v2` exact on all 122,228 finite heads; `fa_tap_exactness` 76/76 (`art:592bc0ae`).
- **Gate (b)** on base `f740c1d5` vs head: the only new failure was the P8 lint, fixed at `4975dc66`, whose lints and touched tests pass (`art:0f9bf31a`). jdiff is `art:a175e2b2`.

The train's full `check` runs `test_tp_moe_members::test_the_stored_tp2_moe_builds_merge_with_every_peer_bound`, which gate (b) doesn't finish in reasonable time: about 50 min per row on pre-#443 trees.
