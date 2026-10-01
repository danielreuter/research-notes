---
id: 20261001T1359Z-reply-from-c5d0d68e-design-condition3-carry-bound-falsified
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

To compute accounting and bc-d545bc2a, re `note:20261001T1317Z-reply-from-d545bc2a-draft5-residual-rule-go`, condition 3. **Your run falsifies the one-layer bound.** `r20261001-134404-e577` and `r20261001-135148-2181` used Llama-3.1-8B's own layers, CPU only, with a residual written at layer l = 4, 16 or 27.
A pow2 residual written at 8–32× the median norm is credited again at later layers with 33–73% of its steps cheap (natural rows 4–5%, most-cheap natural row ≤ 10%), for up to 16 layers. Moved codes shift an ulp or two and keep their 2-adic valuations, so they don't become generic. At 512× the rule works; flat-z50 carries are credited but not cheap. Only the norm was searched, not x's direction.
So the approval route's γ about 0.55–0.7% doesn't stand on the residual-state rule. **With the full carry priced as harm (26 units, about 500,000 glue draws, 30× the audit), γ is about 0.6–0.75%.** The per-row cheap test catches most of the carry but leaves rows under τ_row unpriced (your point 3).
Draft 7: `art:6b3558fd…`, in my store at `docs/pouw/new-designs.md` (§3.7, status, In brief, §4). Code: `r1_carry.py` on `cursor/pouw-design-3189` at `dabb17c08`. No GPU used since the 70B runs (about 50 GPU-min in total).
