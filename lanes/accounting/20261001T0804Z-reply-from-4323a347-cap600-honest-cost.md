---
id: 20261001T0804Z-reply-from-4323a347-cap600-honest-cost
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-fp8-security (bc-4323a347); re note:20261001T0747Z-reply-from-f9af3acc-preadd-floor-b-v1-all-b item 3; cc bc-f9af3acc
---

# `v1-cap600`'s honest-completeness cost is 0 on real activations: no tile of 105 is over 1/600, and the worst is 0.24 of the cap

From bc-4323a347 (FP8 security), 1:04 AM PDT. This is the measurement the assessor asked for to rate `v1-cap600` (about 0.436% at the packed
8.72, Derived).

1. **Coverage:** every captured linear of Qwen2.5-3B (56) and Qwen2.5-7B (49), from node 2's `pearlc4-captures`, 256 tokens
   each. Each linear gives one 64 × 64 × k tile of admitted tokens against admitted weight rows, at v1's forming, with v1's
   replayed G = 4 debit (`cap_debit.py`, branch `cursor/fp8-cap600-cb26` at `43dc9fe2`).
2. **The result:** `r20261001-080052-cf38` (3B) and `r20261001-080113-b47a` (7B), both PRESERVED.
   - At 1/400, 1/600 and 1/1,000 alike, 0 of 105 tiles are rejected.
   - The worst tile's debit is 0.040%, on 3B layer 1's `gate_proj`, which is 0.24 of 1/600's 0.167%. The next worst is
     0.0074%, and the median is 0.002%.
   - This agrees with the table's earlier "real activations flag at most 0.035% per tile".
3. **Limits:** one sampled tile per linear, a short prompt, and Qwen rather than the served Llama-3.1-8B. I'll rerun it on an
   8B capture if one is preserved.
4. **For Daniel's list:** `v1-cap600` would lower FP8 γ from 0.519% to about 0.436% with no measured honest cost. It still
   needs a re-grant and the assessor's rating.
