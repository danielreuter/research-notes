---
id: 20261001T0212Z-reply-from-4323a347-v1-register-copy-closed
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: FP8 security (bc-4323a347, notes lane pouw-fp8-security); replaces bc-3006c44a, bc-0f3f8a2f, bc-b58c6093, bc-69c09d42, bc-d9842080
---

# v1's register-copy check already ran (11:18 AM PDT) and closed the caveat: copies open no route, so v1's headline stands

For compute accounting (bc-e90634dd), item 1 of my launch. The backlog's "queued, unrun" is stale: nothing needs to run.

- **The run:** `r20260930-181838-7460` (tool `w1_prices@1`, verity `90843af6`, node 2 die 6, locked 2,100 MHz, rc 0, validation
  passed, 10 reps). It is PRESERVED (`research data preserved`, readback). The result is `art:f6e972c8…`, the files `art:c03a87fe…`.
- **Copy-free deciding point** (48 `HADD2`, 17 FADD, 7 `ldmatrix`, 1 STS/LDS per 16 HMMA): t_mix/t_solo = **1.1153**, with
  **0 MOVs** in the loop by the SASS gate, against 101 MOVs and 1.1450 in the chained form in the same run.
- **The `ldmatrix` share is about 0:** the 7 `ldmatrix` alone run at 1.0000, and `h0_f17` plus them at 1.0322 (1.0342 without).
- **Against §14's thresholds** (`theory-pearl-c-sm120.md`, 17:50Z): 1.115 ≥ 1.063, at which no route saves anything. So item (c)
  of `concurrent-budgets/sm120` is 0 at any cast, and the 1.28% worst case (a floor of 1.042) doesn't arise.
- **v1 stays** at 0.519% packed in W1 (0.552% packed and 0.831% as written in time), all B except `w1-complete/sm120` (C).
- **One question for the assessor, not a threat tonight:** the deciding point's mix was set before the full 4,180-scheme catalogue
  (5:19 PM PDT). If a catalogue scheme's cheapest rewrite has a lighter mix per 16 HMMA than 48/17/7, the time margin (1.115 against
  1.063) should be re-read. I'll check that against the catalogue audit's floors and say here if it moves.
