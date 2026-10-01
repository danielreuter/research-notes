---
id: 20261001T0950Z-handoff-from-circuits-bool-switch-attention-v8-scalar-dedupe
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---
# @proofs-ir (proofs-ir-attn): your branch is on the Boolean integration branch; Attention_v8 added; two merge resolutions to keep

2:50 AM PDT. `cursor/proofs-ir-attn-95d4` @ `1256f06fc` is merged into `cursor/bool-switch-8c79` (`8d4b9f305`). With it,
Gemm_v2 → Gemm_v3 serves on the target row (SmolLM2-135M TP1 B1, `cov-k01-10`).

- **The served FA2 row's attention is `Attention_v5`** (`fa2_check_inf`, FA2's per-iteration `Check_inf`), not v2/v3. I added
  `AttnBlock_v8` / `AttentionHead_v8` / `Attention_v8` (v5's body on bits) in your `boolean_attention.py` (`e272fb466`):
  `_block(..., check=True)` (default keeps v6/v7 unchanged) and `_head` calls `block_of(b, nvis, first)`. Tests: pins,
  agreement with v5, and a control that `CHECK` is read. With it, boolean-purity on the row is **0 / 0**. v8 is taken; if you
  edit this file further, merge `e272fb466` first.
- **`verity.ml.boolean.scalar` add/add conflict**: my branch had the comparator/selects there. Resolution: union, but
  `F32Add/Mul/Fma/Div_v3` and `Bf16ToF32_v2` were already `elementwise`'s and `cast`'s (same builder, same digest), and the
  registry raises on a second Definition per id. They stay in `elementwise`/`cast`, and `scalar` re-exports them (names and
  `__all__` unchanged for `tail_pieces`/`boolean_export`). `test_boolean_scalar.py` holds both sides' tests.
- **Re-pinned** `integrations/vllm/tests/program/test_boolean_attention.py` v6/v7 (`1d456b4c7`): the integration tree's
  `MufuEx2Ftz_v2` is 1,073 ANDs (mufu's range scaling without multiplies), so every chain is a few thousand ANDs smaller.
  Core and circuit-check pins (`Fa2InvSum_v2` 947) already agree.
