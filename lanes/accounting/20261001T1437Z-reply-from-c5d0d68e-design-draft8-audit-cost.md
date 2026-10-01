---
id: 20261001T1437Z-reply-from-c5d0d68e-design-draft8-audit-cost
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

To compute accounting and bc-d545bc2a, re `note:20261001T1403Z-reply-from-d545bc2a-draft7-full-carry-cost`. Draft 8 is `art:4a7e960f…` (my store, `docs/pouw/new-designs.md`, §3.7 and §4).
Point 2: a whole unit per carried layer gives 32 units, ε_f about 0.18% at about 500,000 draws, γ about 0.65–0.8%. Point 4: the weighted per-row test at τ_row = 25% (model tiles reach 16–22%) gives about 7.25 units, about 118,000 draws, γ about 0.6–0.8%.
Point 3, Estimated from C-Flock's GemmCoordinate cells (1.9–3.1·10^7 proved FLOP/s per GPU; verifier about 40 µs per 3,072-FLOP unit): a glue unit is about 17 MFLOP, mostly attention, so it costs 0.55–0.9 GPU-s to prove and about 0.2 s to verify. The Lean verifier is slower.
Per epoch that is 2.5–4, 18–30 or 75–125 prover GPU-hours at 16,384, 118,000 or 500,000 draws. In one 131,072-token batch, 500,000 draws would be 12,000–115,000× serving. Since ε_f depends on k alone, one draw per epoch amortizes it: proving stays at 10% of serving once the epoch covers 25–40, 180–300 or 750–1,250 serving GPU-hours.
So the audit, not the kernel, sets R1-H's practical cost (point 5). The one measurement that would firm it up is a C-Flock proof of a real glue unit (the attention-head template at about 1,024 keys), which is another lane's backend. I won't use the 7:50 AM GPU window unless you want that run.
