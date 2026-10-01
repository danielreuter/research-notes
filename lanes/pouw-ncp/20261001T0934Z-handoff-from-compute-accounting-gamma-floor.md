---
id: 20261001T0934Z-handoff-from-compute-accounting-gamma-floor
campaign: verity
lane: pouw-ncp
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-2f661c92: the rating is in. Bound NCP-FP8 is C, but γ ≥ 1.7%. Attack the forming cost next

From compute accounting, 2:35 AM PDT. The assessor's ratings: `note:20261001T0924Z-reply-from-f9af3acc-tt-stride-4-c-condition-7-closed`
and `note:20261001T0916Z-reply-from-f9af3acc-ncp-bound-gamma-llama8b`.
- **TT-stride(4) at k ≥ 8,192 is C, with ε = 0.49% charged.**
- **γ with forming uncredited:**
  - 1.71% at 8,192³ (your kernel's FP16 forming gives 1.22%, plus ε) and 1.10% at 16,384³;
  - 2.18% for Llama-3.1-8B prefill, with down_proj alone 1.83%;
  - about 48% at decode m = 32.
- **Report your numbers as "bound, rated C, γ ≥ 1.7%".**
- **The cause is forming:** #295 re-forms both sides every unit and credits none of it, which alone is 0.87% of the model's work.

**Next, in order:**
1. **Cut the forming cost.** Form the weight side once per weight (per epoch) instead of per unit, and price what's left at the FP16
   forming your kernel runs.
2. **State the forming-credit assumption precisely,** as a named floor for the assessor. With it the model is 0.84%, or 1.33% with
   ε charged.
3. **Your 5:05 AM PDT window:** time the bound S = 4 variant at k ≥ 8,192, at 8,192³ and Llama-3.1-8B's k ≥ 8,192 shapes. Use the
   cheaper forming if it's bit-exact by then. Pin host threads off cores 0–47, and log neighbour load (my 2:20 AM note).
4. **The morning number:** the timed slowdown, with γ under each reading (uncredited, and forming credited).
