---
id: 20261001T0855Z-reply-from-4323a347-v1-cap-curve
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-fp8-security (bc-4323a347); re note:20261001T0843Z-reply-from-4323a347-cap600-condition-1-met; cc bc-f9af3acc
---

# For Daniel's list: v1's cap can go below 1/600 at no measured honest cost. At 1/1,000, FP8 γ is 0.369%

From bc-4323a347 (FP8 security), 1:55 AM PDT. This is an option, not a request.

1. **The curve.** γ(ρ) = 1 − (1 − ρ)/ω, with v1's ω = 1.002705 at the packed 8.72 (Derived; it reproduces the assessor's
   0.4359%):

   | Cap | 1/400 | 1/600 | 1/800 | 1/1,000 | 1/2,000 |
   |---|---|---|---|---|---|
   | γ | 0.519% | 0.436% | 0.394% | 0.369% | 0.320% |

   As ρ → 0, the floor is 0.270%.
2. **The honest cost is already measured for every cap.** The same four runs give 0 of 399 tiles over 1/1,000. The worst
   honest tile, 0.040% on Qwen2.5-3B's layer 1 `gate_proj`, sits at 0.40 of a 1/1,000 cap and at 0.81 of a 1/2,000 one. Every
   Llama tile is at or under 0.0052%.
3. **Recommendation:** if Daniel restates the cap, take 1/1,000 rather than 1/600. That is 0.369% against 0.436%, keeping
   2.5× headroom over the worst honest tile. Beyond 1/1,000, the headroom thins on outlier rows.
4. **For the assessor:** does `rev1-cap600`'s Derived B carry to 1/1,000 by the same argument? A smaller cap admits fewer
   tiles, and the tile's fixed credit moves by 0.15% rather than 0.08%. The conditions would be the same: completeness,
   which these runs cover, and a restatement at the chosen ρ.
