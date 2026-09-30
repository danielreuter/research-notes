---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-attention
created: 2026-09-30T04:38Z
---

# FA2's partial -inf guard can't reuse Attention_v4 bit-exactly: FA2 guards `max * scale` in every block; I'll add the FA2 form stacked on #477

- **The difference.** In an unguarded iteration, FA3 (`hopper/softmax.h`) reads the raw running max in both places: the rescale and `max_scaled = m * scale_log2`. `AttnBlock_v4{CHECK=false}` models that. FA2's `softmax.h::scale_apply_exp2` guards `max_scaled` (`max == -inf ? 0 : max * scale`) in **every** block, and only the rescale's `scores_max_cur` depends on `Check_inf`.
- **Measured on CPU with the registered primitives**, for a row whose running max is -inf at an unguarded block:
  - FA2: `max_scaled` = `0x00000000`, P = `0x00000000`;
  - `v4`: `max_scaled` = `0xff800000`, P = `0x7fffffff`;
  - the head's output is the same NaN (`0x7fff`) under both, where `v2` gives `0x0000`.
- **Why it matters.** The committed interior words would differ: the guarded-max tap's MS class (max * scale, per block) and the hidden stream's P words. So `v4`'s proof units would disagree with the tap on such rows. At the output level alone, `v4` would look exact.
- **Plan.** `AttnBlock_v5` / `AttentionHead_v5` / `Attention_v5{T,NH,KVH,D,BN,DOT,INV,MASKED_FROM}`, patterned on `fa3_check_inf.py`:
  - the same `MASKED_FROM` static, with FA2's boundary: `n_block_max` of the row's 64-row tile minus `n_masking_steps` (2 for a causal launch, 1 when `max_seqlen_q == 1`);
  - `CHECK` guards only the rescale;
  - bound on `blackwell_consumer` FA2 only.
  It gets its own PR stacked on #477, with a GPU correspondence on the constructed ±inf/NaN score sets (the capture already evaluates this placement: 0 mismatches on all 122,228 heads, the 112 non-finite ones included) and circuit-check.
- **sm_89 / sm_90.** The same placement holds on every FA2 target (it's the same PTX), so `Attention_v3` and forced-FA2 `Attention_v2` miss it too, on non-finite rows only. Reported, not changed, per your decision.
- **#477.** Gate (b) is still finishing: base and head both at 98%, in `test_the_stored_tp2_moe_builds`. The head's lints failed P8 on arch literals in my evidence string; fixed at `4975dc66`, whose lints and touched tests pass (`r20260930-042000-6c90`). The merge-ready handoff follows when the jdiff is in.
