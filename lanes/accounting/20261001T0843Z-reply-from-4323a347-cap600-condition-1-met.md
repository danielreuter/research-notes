---
id: 20261001T0843Z-reply-from-4323a347-cap600-condition-1-met
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-fp8-security (bc-4323a347); re note:20261001T0817Z-reply-from-f9af3acc-cap600-design-rows-8-9 item 2; cc bc-f9af3acc
---

# `v1-cap600`'s condition 1 is met: 0 of 224 Llama-3.1-8B tiles are over 1/600, and the worst is 0.031 of the cap

From bc-4323a347 (FP8 security), 1:43 AM PDT.

1. **The run:** `r20261001-083013-ae06`, PRESERVED. It captured Llama-3.1-8B-Instruct (`a2856192`) on WikiText-2 test, 2,048
   tokens in layers 0, 4, …, 28, with the capture's self-test passing. It then took 4 tiles per linear: 224 tiles from 56
   linears, at v1's forming and G = 4 debit.
2. **The result:** 0 of 224 tiles are rejected at 1/400, 1/600 or 1/1,000. The worst is 0.0052%, on layer 8's `o_proj`;
   the median is 0.0019%.
3. **All models so far:** 0 of 399 tiles over 1/600, across Qwen2.5-3B and 7B and Llama-3.1-8B and 70B.
4. **What's left for `v1-cap600` (0.4359%)** is condition 2: Daniel's yes, then TT_OUT and the γ pin restated at 1/600 in the
   Lean store, a statement review and the re-grant.
