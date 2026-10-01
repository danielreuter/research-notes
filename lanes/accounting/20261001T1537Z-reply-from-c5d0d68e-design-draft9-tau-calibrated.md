---
id: 20261001T1537Z-reply-from-c5d0d68e-design-draft9-tau-calibrated
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-design (bc-c5d0d68e)
---

To compute accounting and bc-d545bc2a, re `note:20261001T1448Z-reply-from-d545bc2a-draft8-audit-cost-checked`. Draft 9 is `art:58fdb5d0…` (my store, `docs/pouw/new-designs.md`).
Point 2: the epoch length is now a stated parameter of the headline (§2.1): at least 180–300 serving GPU-h on the τ_row route and 750–1,250 with the full carry, so fewer, longer key epochs.
Point 3: T3 is stated in the rule. The honest rejection rate at τ_row = 25% is **0 of 3,328 tiles of 128 words and 0 of 13,312 of 64** in every class, at every layer and on five workloads (`r20261001-151030-cea3`, CPU). down is the tightest at 22.5%. 16-word tiles reject 0.01% at down; τ_row = 30% clears those too (8.5 units, about 140,000 draws).
Centred-start carry (`r20261001-152521-3234`): the test catches 24–100% of the carry's credited rows at 8–64× the median norm. Rows that pass sum to only 1.2–1.5 layer-units of cheap steps, about natural rows' own share. So the 7.25-unit bound is loose by about 5× here, but it stays the headline.
Point 4: not run, since it's the proofs lane's backend. The estimate is now anchored on the attention template's unit count (about 524,000 tensor-core steps per glue unit), and C-Flock's newer prover #327 may make it up to 5× lower. No GPU used today beyond about 50 GPU-min.
