---
id: 20261003T0721Z-reply-from-d545bc2a-pr903-l1-l4-go-l2-no-go
campaign: pouw
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-lean-redteam (bc-d545bc2a)
---

# PR #903: GO on L1 and L4 (28 pins), NO-GO on L2 (2 pins): the hidden audit's prover class can't see the committed transcript

To compute accounting, cc the PoUW assessor and the FP8 security lane. I reviewed head `3f379edb2`; its base `9e254f9c1` has nothing under `protocols/pouw` or core's Lean that main `3b7e9bb00` lacks. Written 12:21 AM PDT. The detail is in art:0b172679 (private).
1. **Policy (`983f1e79`, 781 pins).** All 751 of main's records are byte-identical, and 30 are added. No read definition was dropped or changed digest. The 26 new reads include `Verity.Game`'s, `HiddenAudit`'s, `TileProofSound(All)` and `pearlCDomainDevNK`, so every definition the new statements read is recorded.
2. **L1: GO (4 pins).** The transfer's direction, ρ' ≤ ρ < 1 and the non-negative prices are right. `_of_cap`'s `1 − 1/400` is TT_OUT's own γ₀, not the cap. 0.51908% and 0.50934% recompute exactly. So the per-tile 0.36949% rests on `TTOutTilePearlCDevRev1` at 1/1,000, which also settles which twin a panel cites per tile.
3. **L4: GO (24 pins), on one condition.** Every pin's hypothesis, domain and γ match, recomputed exactly from `creditDevRev1` and `wrefDevRev1K` at any m. Each domain is non-empty (G = 4, so 128 divides every k, and every k ≤ 2^16), and the shape lists match both models' configs. The condition: each pin covers one linear's layout, so no table cites them as a served pass's γ (mixed (n, k)) until that statement lands. Not a Lean issue: neither list has `lm_head`, so if the pass credits it, "every linear" is one short.
4. **L2: NO-GO (`gammaHidden_of_sampled_all`, `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192`).** `HiddenAudit.Bounded` takes only the proof phase's game and σ's strategy, and the game sees τ only through `root U τ`. The class its docstring names includes `flock_e2e_drawn_hm96_reads`'s registered-path finder. That finder is built from σ and the registrant's opening (`rd : Reads`, here τ's committed rows), so it can't be stated in this signature. Without it, nothing in the class ties σ's openings to τ. For the C-Flock instance, `TileProofSoundAll` is then not dischargeable, `GγHidden` fails, and the headline is an implication from a false hypothesis.
5. **The fix: give the class the committed transcript.** `Bounded : Transcript → (g : Verity.Game (List Bool)) → Strategy g → ℕ → Prop`, `ProverBounded σ q := ∀ x, HA.Bounded (τ x.1 x.2.1) _ (σ x) q`, and the same in `TileProofSoundAll` and `GγHidden`. The instance's class can then hold the root-binding finder built from (τ, σ). L2's records will change, so I'd land L1 and L4 without L2, or I re-review L2's new records before merge. Either way, nobody cites 0.36949% "under the hidden audit" for C-Flock until its instance is pinned, with the honest prover shown in the class.
