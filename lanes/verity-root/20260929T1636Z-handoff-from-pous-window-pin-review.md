---
id: 20260929T1636Z-handoff-from-pous-window-pin-review
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (work-law lane bc-0b392ca4, cc bc-f0bc7e75): window pin, Lean-lane review GO WITH CHANGES; X-SPC-107 fix in #364

Re: `lanes/pous/20260929T1608Z-handoff-from-verity-root-window-pin.md`. This is our Lean lane's review, from the author
of #408, #412 and #416. The circuit worker's row-by-row table check against #364 follows once its `9ac48ce8` merge head
is pushed.

## Verdict: GO WITH CHANGES

The statements are sound, and M1 and M2 are the right modelling line for a sampling pin. The `max` is justified: both
conditions are on the one set `committedOf σ'`, drawn in one draw, so each such set meets one of the two bounds. The
constant is right. 1000 = 1/ε; `record_sizing` gives (999/1000)^27,713 ≤ 2⁻⁴⁰, and `record_sizing_one_fewer` shows
27,712 fails. `Covers` isn't vacuous. `hone` is necessary; the counterexample checks out, with 64 > 54. `covers_of_floor`
is correct: when f_s > n_s, `hk` forces k_s = n_s.

**Required: add `audit_window_of_le`.** It states the audit bound for any law `L` with
`∀ B, L.escape B ≤ (Law.stratified σ k hk).escape B`, at `audit (L.closure cl)`. The proof is unchanged, since
`audit_profile` holds for every law and `closure_escape` carries the bound through. Without it, the pin can't compose
with `execStratified_escape_le` (#412) or `execOS_escape_le` (#416).

**Required: name "distinct contexts" as part of M1** in the pin's text.

**Optional:** state the y event with `unsoundWork σ v cl` instead of `workOf`. It's strictly stronger, by
`workOf_le_unsoundWork`, at no cost.

**For the record: the tier-3 status of the window draw.** #364's draw is `Traced.draw` → `plan.draw` → Python
`Key.subset`, on SHA-256 counter-mode streams from one window key. It never reaches `Flock.Draw.drawOS`, so
#408/#412/#416 don't cover it. This is the keyed-draw case, X-SS-2. A tier-3 statement would need three things:
- a named keyed-stream assumption: distinct contexts give independent uniform streams (random-oracle or PRF style);
- `Key.subset` shown equal to `Flock.Draw.subset`, which today is only tested;
- a lemma that C per-call draws, each numbering its own units, form one stratified law over the window.

`callK` and `windowK` versus `WorkLaw.budget` and `WorkLaw.sizes` is tested, not proved. The closure matching
`Law.closure` relies on `check_layout` refusing any layout but the verifier's own. We're raising the tier-3 question with
Daniel and aren't asking you for any of it now.

## X-SPC-107 was worse than stated, and is being fixed in #364

At `50c44582`, `Ledger.admit` is called only from `test_circuit_anchors.py`. No verifier path admits before
`Traced.draw`, which reads `anchors.call_index` directly. So two calls sharing (forward, position) draw identical subsets
under the one key, and the window's draw is not the product law M1 assumes.

The circuit worker is making the draw take admission itself, with a test that a repeated index is refused before any
draw. The fix comes in the same push as the `9ac48ce8` merge, carried into #380 and #391, and the circuit red team
reviews it there. #364's recorded check reruns at that head.
