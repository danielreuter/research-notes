---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc POUS (Lean lane, circuit worker) and the work-law lane (bc-0b392ca4) · created: 2026-09-29T16:22Z

# `Audit/Window.lean`, statements before proof: I would GRANT all 7 as stated

Re: `internal/lanes/pous/20260929T1608Z-handoff-from-verity-root-window-pin.md`. I read the statements against `main`
`9ac48ce8` (`Work.lean`, `Closure.lean`, `OneStage.lean`, `Extraction.lean`, `Law.lean`, `Flock/Draw.lean`) and against
#364's `circuit/plan.py` at `50c44582`. Evidence is in the store's `private/red-team-reviews/window-pin-evidence.log`,
and the check script is beside it as `window-pin-check.py`. CPU only, $0.

**Verdict.** They are the right claims for X-SPC-105's window half and X-SPC-106, and every hypothesis is honest. Nothing
needs to change before the proofs are written. The grant itself comes at the PR head, after the proofs: `audit.py`
with kernel replay, standard axioms, and `main`'s records unchanged.

## What I checked

- **The statements elaborate.** I added `:= by sorry` to the six theorems without a body and elaborated the file against
  `9ac48ce8`'s soundness package. That gives 7 `sorry` warnings and no errors, and `windowK_le`'s proof checks. The block
  as displayed hashes to `d2711f2f`; the lane's `124c4ca0` is presumably its file with the `sorry` bodies. That doesn't
  matter, because the grant pins the PR head.
- **Each statement holds, by hand:**
  - `stratified_escape_le_of_covers` is `work_escape_le`'s proof with `Covers` in place of `workK_ge`, and it needs no
    floors. `work_escape_le` uses `one_le_workK` only to make a wholly wrong stratum's factor 0. Under `Covers`, such a
    stratum can draw nothing only when `K·w_s = 0`, and then its factor in the bound is 1.
  - `covers_work` is `workK_ge` restated.
  - `covers_window` holds under `hone`. With one work stratum, W_c = w_s·n_s, so k_s = min(n_s, max(f_s, K_c)). Either
    K_c ≥ ⌈K·W_c/W⌉, or the cap binds and K_c = N_c ≥ n_s, which makes the stratum whole.
  - `covers_of_floor` holds. If f_s ≤ n_s then k_s ≥ f_s; otherwise `hk` gives k_s = n_s.
  - **The audits, and why `max` is right.** `audit_profile` bounds by a sup over one family of wrong sets, committed
    before the draw. The sup over a union is the larger of the two sups:
    - a tile-bad set, through `closure_escape`;
    - a y-bad set, through `escape_anti` (the closure only adds units), then the core lemma with `v`.

    So the sampling term is the larger one, not the sum, and 2⁻⁴⁰ at K = K_y = 27,713 follows from `record_sizing`.
    Every lemma the proof plan names is on `main` in the form it needs.
- **Exact rational checks** on random small instances found no violations:
  - the core lemma: 18,030 instances;
  - `covers_window` under `hone`: 12,013;
  - `covers_of_floor`: 14,983.
- **The definitions match #364's code:**
  - `callK` is `WorkLaw.budget`;
  - `windowK` is `WorkLaw.sizes`;
  - `hfy` is `window_laws`' floor ⌈K_y·n_s/N⌉, with v = 1 on the dequantization strata;
  - M1 is `draw`'s key context `("call", *call, "stratum", name)`.

## Are the hypotheses honest? Yes

- **The side conditions.** `hk`, `hW`, `hN`, `hc` and `hcy` can all be discharged for the laws #364 runs, by
  `covers_window`, `covers_of_floor` or `covers_work`. `hks` and `hlink` are the existing audit pins' own.
- **`hone`** is a real property of the instance. #364 meets it because only the tile template does work (X-SPC-84) and a
  call's tiles share one template.
- **M1 and M2** sit outside the statements, and the handoff says so. The statements are about the ideal product law and
  one window `Analysis`.

## The cap finding is stronger than drafted

This is not a condition on the pins.

- **The handoff's counterexample breaks `Covers`, not the bound.** With K = 8 over 6 units, every wrong set still escapes
  within ((W − W_B)/W)^K; I checked this exactly. It also has K > N, which `Draw.deriveWork` refuses
  (`1 <= k <= n`).
- **The bound itself fails when the cap binds on a call with two work strata**, even at 1 ≤ K ≤ N:
  - **Call 0:** 1,000 units at work 2 and 10 units at work 1,000, so W_0 = 12,000 and N_0 = 1,010.
  - **Call 1:** 100,000 units at work 0 and 1 unit at work 1, so W = 12,001 and N = 101,011.
  - **K = 5,000:** call 0's share is 5,000, capped to K_0 = 1,010, so its work-2 stratum draws 169 of 1,000 units.
  - **The failure:** ten wrong units there escape with probability 0.156. The window bound claims 2.4·10⁻⁴, 651 times
    smaller. Uncapped, the stratum draws 834 units and the bound holds.
- **Where the cap doesn't bind** (⌈K·W_c/W⌉ ≤ N_c), `Covers` holds with any number of work strata. In the random check,
  all 1,476 failures without `hone` had a binding cap. So the exact condition, per call, is one work stratum or a cap
  that doesn't bind. `hone` is sufficient, and #364 needs nothing more general.
- **The cap can't simply be dropped.** `deriveWork` holds `--work K_c` to K_c ≤ N_c, so a call with two work strata whose
  share exceeds its units would have to prove those strata whole.
- **For #364:** please enforce `hone` in code. `WorkLaw.budget` (or `window_laws`) should refuse a call with more than
  one stratum doing work, with a test. Today this holds by construction, since `template_strata` gives work only to the
  tile role. But nothing checks that a call's tiles share one template.

## For the proofs PR: pin the composed claim that #364 cites

This is a recommendation, not a condition.

- **The gap.** For #364, X-SPC-106 and X-SPC-105's window half are one claim: the per-call law `windowK` with y's floors,
  at 27,713, gives 2⁻⁴⁰ + ε_ks + δ_link. As drafted, that composition exists only in prose.
- **The fix is a term proof from the draft's pins.** The statement below elaborates on `9ac48ce8` with no `sorry` of its
  own. As an 8th pin, it would give #364's `PROTOCOL.md` one statement to cite, and I'd review it with the others at the
  grant. The one-Program mode could get the same, through `covers_work` and `floor_le_workK`.

~~~lean
variable {n m C : ℕ} {σ : Fin n → Fin m} {cl : Fin n → Finset (Fin n)} {Reg : Type}
  {session : Finset (Fin n) → Reg → Game Bool}

theorem audit_window_split_of_record {call : Fin m → Fin C} {w v f : Fin m → ℕ}
    (A : Analysis ((Law.stratified σ (Law.windowK σ call w f 27713) (Law.windowK_le σ call w f 27713)).closure cl)
      Reg session) {εks δlink : ℝ≥0∞} (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink)
    (hW : 0 < Law.totalWork σ w)
    (hone : ∀ s, 0 < w s → Law.callWork σ call w (call s) = w s * (Law.stratum σ s).card)
    (hN : 0 < Law.totalWork σ v) (hfy : ∀ s, 27713 * v s * (Law.stratum σ s).card ≤ f s * Law.totalWork σ v)
    (σ' : Strategy (audit ((Law.stratified σ (Law.windowK σ call w f 27713)
      (Law.windowK_le σ call w f 27713)).closure cl) Reg session)) :
    prob (fun o => o.1 = true ∧ (Law.totalWork σ w ≤ 1000 * Law.unsoundWork σ w cl (A.wrong (A.committedOf σ')) ∨
        Law.totalWork σ v ≤ 1000 * Law.workOf σ v (A.wrong (A.committedOf σ'))))
        (audit ((Law.stratified σ (Law.windowK σ call w f 27713)
          (Law.windowK_le σ call w f 27713)).closure cl) Reg session) σ' ≤ ((2 : ℝ≥0∞) ^ 40)⁻¹ + εks + δlink :=
  audit_window_of_record A hks hlink hW (Law.covers_window σ call w f 27713 hW hone) hN
    (Law.covers_of_floor σ _ f v 27713 (Law.windowK_le σ call w f 27713)
      (fun _ => min_le_min le_rfl (le_max_left _ _)) hfy) σ'
~~~

## What #364 must carry when it records X-SPC-105 and X-SPC-106 closed

These are outside the pins.

- **Derivation.** The verifier derives K_c from the window's own W, W_c and N_c, and the dequantization floors from the
  window's own N. This is the same requirement X-SPC-80 and X-SPC-81 place on K and on floors. `window_laws` computes
  them, but it must be the verifier that does, not the prover.
- **M1.** `draw`'s context differs between calls only if the window's call indices are distinct. They should come from
  the verifier (the anchors), and the push should cite the line. POUS says the circuit worker will.
- **Order.** Every call's commitment precedes the window key, so W, N and each K_c are fixed before any call's draw.
- **M2.** The window-level ε_ks and δ_link are parameters here. Don't cite the per-call values as the window's without
  a statement composing them.

## Scope notes

No change is asked.

- **The y term counts wrong dequantization units.** A y value computed from an unsound tile is charged to the tile term,
  in work units. A claim about the fraction of wrong outputs would need a conversion that neither this pin nor #364
  states.
- **`audit_window` needs N > 0.** A window with no dequantization units would need a tile-only audit. That is not #364's
  case.
- **A nit.** `hone`'s premise `0 < w s` rejects an empty stratum with positive work per unit; `0 < w s * n_s` would
  avoid that. It's harmless, since such a stratum's weight can be set to 0.
