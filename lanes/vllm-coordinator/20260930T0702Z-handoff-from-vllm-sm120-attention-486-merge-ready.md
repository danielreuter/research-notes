---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-attention
created: 2026-09-30T07:02Z
---

# MERGE-READY #486: FA2's per-iteration Check_inf as Attention_v5 on sm_120; exact on every head; gate (b) 0 unexpected failures

- **Branch and head.** `cursor/vllm-sm120-fa2-check-inf-0ec6` @ `70a4504e`, stacked on #477 (`4975dc66`). Merge order: #465, #477, #486.
- **What it does.**
  - Adds `AttnBlock_v5` / `AttentionHead_v5` / `Attention_v5{…, MASKED_FROM}` (`registry/fa2_check_inf.py`). `CHECK` guards only the rescale; FA2 guards `max * scale` in every block, which is why `v4` isn't reusable (handoff 0438Z).
  - `MASKED_FROM` is the 64-row tile's `n_block_max` less `n_masking_steps` (2 causal, 1 when `max_seqlen_q == 1`).
  - Bound only where the family registers `fa2_construction = "check-inf-per-iteration"` (`blackwell_consumer`).
  - Wired like #105: vocabulary (optional `FA2_MASKED_FROM`), Build rule, fold, twin, row evaluator, replay lists, `FLASH_ATTENTION_LAUNCHES`.
- **What doesn't change.** sm_89 (`Attention_v3`) and H100 FA2/FA3 bindings, Program digests, and the vocabulary version. The same guard placement holds on sm_89 and H100 FA2; reported, not changed, per your decision.
- **Acceptance, as you set it.**
  - **Every head bit-exact, non-finite rows included:** `fa2_target_capture` `2f7cc71f` (`r20260930-045505-2350`, `art:7bc06ae3`; second RTX PRO 6000, driver 580.17). The registered `Attention_v5` matches 122,228/122,228 heads, including 112 non-finite (±inf and NaN score sets). The target's `attention_spec` binds that exact Definition on all 19,232 rows.
  - **No record digest moves:** only `blackwell_consumer` binds `v5`; the jdiff shows no sm_89/sm_90 test changes.
  - **circuit-check passes:** 0 failures on `Attention_v5` / `AttentionHead_v5` (`art:97c2dbcf`); its one dead-gates warning is the same as on `v4`/`v2`.
- **Partition checker** (`query.word`, T = 40, NH 2, KVH 1, D 16, BN 16, Hopper DOT, Fa2InvSum):
  - `unit_rule(Attention_v5{MASKED_FROM=2})`: violations [], max_out_bits 32, committed guard words 0, `F32MulFtz` 6.
  - `unit_rule(Attention_v5{MASKED_FROM=0})`: violations [], max_out_bits 32, guards 4, `F32MulFtz` 6 (identical to `v4`'s counts).
  - `units(AttentionHead_v5{MASKED_FROM=2}, X=16, W=32)`: cut ok, **0 recomputed gates**, all units ok. The same is pinned in `test_fa2_check_inf.py::test_the_partition_rule`.
- **Gate (b)**, same pod `vy-sm120-attention-2` (`gate_b2.sh`):
  - Base `4975dc66` `r20260930-051932-96ce` (`art:7f6c0964`): 37 failed / 4408 passed / 16 errors.
  - Head `12cea8ee` `r20260930-051942-008f` (`art:1b03bd9b`): 38 / 4418 / 16.
  - jdiff `art:a5c0e8e5`: the one new failure is P10 (`derived_rows.py` 949 > 944 lines), fixed at `70a4504e` by rejoining wrapped lines. `70a4504e`'s lints and touched tests pass (`r20260930-052148-661b`, `art:5b51253d`). The 12 new tests pass; the one extra skip is an order-dependent allocator test.
- **Found, not fixed.**
  - The chains' `_v1` FMA NaN is `0x7FC00000` where the GPU writes `0x7FFFFFFF` (row sums on NaN rows only).
  - `vu_export` exports no `Attention_v4` / `v5` VUs.
  - `backends/numerical` `ATTN_SEMANTICS` has no FA2-on-Hopper-step entry.
- **Pods.** `vy-sm120-attention-2` was terminated at 07:01Z. Lane spend is about $8.00 of $12.
