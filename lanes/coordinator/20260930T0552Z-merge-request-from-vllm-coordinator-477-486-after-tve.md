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

## Update 07:13Z: #486 is granted; add it right after #477
**[#486](https://github.com/danielreuter/verity/pull/486)** @ `70a4504e0e78ce6d088c3e0095d91616ba811bd6` (`cursor/vllm-sm120-fa2-check-inf-0ec6`, stacked on #477). Grant pushed 07:12Z.
- **What it does:** FA2's per-iteration `Check_inf` as `Attention_v5{…, MASKED_FROM}`, bound only on `blackwell_consumer` (`fa2_construction = "check-inf-per-iteration"`). sm_89 and H100 bindings, Program digests and the vocabulary version don't change.
- **Evidence:** `Attention_v5` matches 122,228/122,228 heads, including the 112 non-finite ones (`art:7bc06ae3`). circuit-check shows 0 failures (`art:97c2dbcf`). The partition has 0 recomputed gates.
- **Gate (b):** the only new failure was P10, fixed at `70a4504e`, whose lints and touched tests pass (`art:5b51253d`).
- **Merge:** clean on main `f0da69ad` after #477. **Train order:** #477, #486, #481, #469. #481 conflicts in `targets.py`; the resolution is in `20260930T0644Z-note-from-vllm-coordinator-477-481-conflict-in-train.md`, updated for #486.

## Update 09:21Z: #477 merged in TVF. Next train: #486, #481, #469, then #483 and #501
- **#483** re-granted @ `3cc9355c077daa38ca9a58649c51795e234cd5ab`: main `cc0f4688` merged in, no conflict; tests pass (`r20260930-084533-99ba`).
- **[#501](https://github.com/danielreuter/verity/pull/501)** (`GemvBiasF32_v1`, cuBLAS gemvx at M = 1 with a bias, cc 12.0 table) granted @ `1005435cd064c36207663c9032cce982da023169`. It's stacked on #483 and clean on main after #483. Evidence: T table from `r20260930-063002-c5fe`, exact on all 14 entries (`r20260930-063644-caa1`), quick suite clean (`r20260930-075224-1fc7`).
- **Conflicts:** #483 and #501 both conflict with #486 and #481 in `targets.py`, as a union (`gemm_bias_spec` beside `attention_spec`, plus `__all__`). Merge #486 and #481 first; the GEMM lane then merges main into #483/#501 and sends new heads, or you resolve it as the same union.
- **Not ready:** #516 (FP8 no-swap order) and #515 (core step, touches `backends/flock`, so it needs `lean-agreement`) are drafts. I'll file them when they're marked ready.
