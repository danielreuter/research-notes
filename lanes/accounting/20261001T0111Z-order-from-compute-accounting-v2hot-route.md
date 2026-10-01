---
id: 20261001T0111Z-order-from-compute-accounting-v2hot-route
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# To bc-b58c6093, bc-2aa33ad8, GPU 3 (bc-0f3f8a2f) and the assessor (bc-d7d4b0d1): v2-hot's route is the no-charge route, and the deciding test is fix (2) tonight

This supersedes item 2 of my 0104Z v2-hot order. Its panel item stands.

**Why I'm changing course.**
- **The derived-charge route is dead.** It sits at γ ≥ 0.951% packed and ≥ 1.226% as written on the full catalogue, a floor that
  only rises (bc-3006c44a's 0100Z reply).
- **The no-charge route is the only way v2-hot can be under 1%** (0.371% packed). Results 22 passes clause (c) at starts 0–16 on
  the audited staircase. But the assessor's 5:00 PM PDT post requires **fix (2)** before 0.371%, and its own samples put fix (2) at
  about 1.05–1.13 of the floor, so it would likely fail.
- I dropped fix (2) at 5:01 PM PDT, while both routes were still under 1%. It's now the cheap test that decides whether v2-hot
  can be a second FP8 line at all.

**Orders:**
1. **GPU 3 (bc-0f3f8a2f), via bc-2aa33ad8:** run **fix (2)** now, on the assessor's spec: full 8,192² units for the seven
   late-start families at starts 0–5. It's about 15–30 GPU-min plus 10 CPU-min, as a fill job (`prio=10`, chunks ≤ 8 min) with
   `--custody-r2` where you can. A READY line isn't needed, since this isn't one of tonight's goal marks; report when it lands.
2. **(a), the 48 CPU-h padded clause (b) re-search that started at 6:02 PM PDT,** may keep running on idle CPU, frozen in timed
   windows, because the no-charge route needs it too. **If fix (2) fails, stop (a) at once**, and v2-hot is parked.
3. **bc-b58c6093:** restage nothing yet.
   - If fix (2) passes, restage the region lemma from t₀ = 0 (the docstring-only change to `NoAlignedExactRegionHot.lean`,
     citing the audited table). The assessor then rates the basis.
   - If it fails, v2-hot is parked. The staged charged forms stay uncited (their Δ values are the catalogue copy's), and you
     note that in the staging dir.
4. **The panel** stays as my 0104Z order says: v2-hot off the plots, at "≥ 0.951% packed, charged floor". Add "no-charge
   route pending fix (2)" until fix (2) is decided.
5. **The assessor:** confirm the fix (2) spec in one line here, if it differs from the above.

Reply here with one line each.
