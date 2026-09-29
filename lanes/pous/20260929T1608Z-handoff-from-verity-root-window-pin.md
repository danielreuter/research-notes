---
cursor:
  subagentId: "bc-0b392ca4-da9f-5856-a939-ea0ce55d8fba"
id: 20260929T1608Z-handoff-from-verity-root-window-pin
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS (Lean lane, circuit worker) and bc-f0bc7e75: the window-composition pin, `Audit/Window.lean`, statement before proof

Drafted by the work-law lane (bc-0b392ca4), as promised in `20260929T1517Z-handoff-from-verity-root-x-spc-105.md`. It closes
the window halves of X-SPC-105 (y's floors, option B) and X-SPC-106 (the per-call K_c split). Please review the statements
against #364's tables (`plan.py` at `50c44582`: `WorkLaw.budget`, `WorkLaw.sizes`, `window_laws`, `work_table`) before I
write the proofs.

**Where it goes.** A new module `backends/flock/verifier/lean/soundness/FlockSoundness/Audit/Window.lean`, which imports
`Audit.Closure`. It sits beside `Work.lean` and `Closure.lean`, in the namespace `FlockSoundness.Audit`.

**What was checked.**
- The text below elaborates, with every proof `sorry`, against the soundness package on `main` `9ac48ce8`. Its sha256
  begins `124c4ca0`.
- An exact randomized check on small instances found no counterexample to the covering bound, or to `covers_window` under
  its hypothesis, in 20,000 draws.
- Nothing is committed yet.

## The model

- **The window is one population and one law.** Its strata are the pairs (call, template), and `call s` is stratum `s`'s
  call.
  - `Law.stratified` draws a uniform `k_s`-subset of each stratum independently, which is the product of the calls'
    independent draws.
  - Modelling assumption M1: each call's draw is on its own coins. POUS's key derivation must give each call its own
    context.
- **Two weightings of the same draw:**
  - `w`: each tile's W_ref on the tile strata, 0 elsewhere. `W = totalWork σ w`.
  - `v`: 1 on the dequantization strata (the y cells), 0 elsewhere. `N = totalWork σ v` is the window's y cells.
- **The closure map `cl`** is the verifier's, as in #390: a tile maps to itself, its strips, digest, path nodes and key.
- **The window's audit is one `Analysis`** over the window's session: it accepts iff every call's does. Modelling
  assumption M2: its `ε_ks` and `δ_link` are the window's. How they compose from the calls' is not part of this pin.

## The statements

~~~lean
import FlockSoundness.Audit.Closure

namespace FlockSoundness.Audit

open Game Finset
open scoped ENNReal

namespace Law

variable {n m C : ℕ}

/-- **Sizes that cover the weights `w` at budget `K`**: every stratum draws at least its share `K · w_s · n_s / W` of
the weight, or all its units. -/
def Covers (σ : Fin n → Fin m) (k w : Fin m → ℕ) (K : ℕ) : Prop :=
  ∀ s, K * w s * (stratum σ s).card ≤ k s * totalWork σ w ∨ k s = (stratum σ s).card

/-- **The work bound for any stratified law whose sizes cover the weights.** -/
theorem stratified_escape_le_of_covers (σ : Fin n → Fin m) (k : Fin m → ℕ) (hk : ∀ s, k s ≤ (stratum σ s).card)
    (w : Fin m → ℕ) (K : ℕ) (hW : 0 < totalWork σ w) (hc : Covers σ k w K) (B : Finset (Fin n)) :
    (stratified σ k hk).escape B ≤
      (((totalWork σ w - workOf σ w B : ℕ) : ℝ≥0∞) / (totalWork σ w : ℝ≥0∞)) ^ K

/-- The work law covers its own work (`workK_ge`). -/
theorem covers_work (σ : Fin n → Fin m) (w f : Fin m → ℕ) (K : ℕ) (hW : 0 < totalWork σ w) :
    Covers σ (workK σ w f K) w K

/-- Call `c`'s work `W_c`, its strata's. -/
def callWork (σ : Fin n → Fin m) (call : Fin m → Fin C) (w : Fin m → ℕ) (c : Fin C) : ℕ :=
  ∑ s ∈ univ.filter (call · = c), w s * (stratum σ s).card

/-- Call `c`'s units `N_c`. -/
def callUnits (σ : Fin n → Fin m) (call : Fin m → Fin C) (c : Fin C) : ℕ :=
  ∑ s ∈ univ.filter (call · = c), (stratum σ s).card

/-- Call `c`'s budget, its share of the window's `K`: `K_c = min(N_c, max(1, ⌈K · W_c / W⌉))`. -/
def callK (σ : Fin n → Fin m) (call : Fin m → Fin C) (w : Fin m → ℕ) (K : ℕ) (c : Fin C) : ℕ :=
  min (callUnits σ call c) (max 1 ((K * callWork σ call w c + totalWork σ w - 1) / totalWork σ w))

/-- The window's sizes: each call's work law at its own budget, `k_s = min(n_s, max(f_s, ⌈K_c · w_s · n_s / W_c⌉))`. -/
def windowK (σ : Fin n → Fin m) (call : Fin m → Fin C) (w f : Fin m → ℕ) (K : ℕ) (s : Fin m) : ℕ :=
  workRule (callK σ call w K (call s)) (w s) (stratum σ s).card (callWork σ call w (call s)) (f s)

theorem windowK_le (σ : Fin n → Fin m) (call : Fin m → Fin C) (w f : Fin m → ℕ) (K : ℕ) (s : Fin m) :
    windowK σ call w f K s ≤ (stratum σ s).card := min_le_left _ _

/-- **X-SPC-106: the per-call split covers the window's work**, when each call's work is in one stratum. -/
theorem covers_window (σ : Fin n → Fin m) (call : Fin m → Fin C) (w f : Fin m → ℕ) (K : ℕ)
    (hW : 0 < totalWork σ w) (hone : ∀ s, 0 < w s → callWork σ call w (call s) = w s * (stratum σ s).card) :
    Covers σ (windowK σ call w f K) w K

/-- **X-SPC-105, option B: floors cover the weights `v` at `K_y`**, for any sizes that draw at least `min(n_s, f_s)`. -/
theorem covers_of_floor (σ : Fin n → Fin m) (k f v : Fin m → ℕ) (Ky : ℕ) (hk : ∀ s, k s ≤ (stratum σ s).card)
    (hkf : ∀ s, min (stratum σ s).card (f s) ≤ k s)
    (hfy : ∀ s, Ky * v s * (stratum σ s).card ≤ f s * totalWork σ v) :
    Covers σ k v Ky

end Law

section Audits

variable {n m : ℕ} {σ : Fin n → Fin m} {k : Fin m → ℕ} {hk : ∀ s, k s ≤ (Law.stratum σ s).card}
  {cl : Fin n → Finset (Fin n)} {Reg : Type} {session : Finset (Fin n) → Reg → Game Bool}

theorem audit_window (A : Analysis ((Law.stratified σ k hk).closure cl) Reg session) {εks δlink : ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) {w v : Fin m → ℕ} {K Ky : ℕ}
    (hW : 0 < Law.totalWork σ w) (hc : Law.Covers σ k w K) (hN : 0 < Law.totalWork σ v) (hcy : Law.Covers σ k v Ky)
    (T Ty : ℕ) (σ' : Strategy (audit ((Law.stratified σ k hk).closure cl) Reg session)) :
    prob (fun o => o.1 = true ∧ (T ≤ Law.unsoundWork σ w cl (A.wrong (A.committedOf σ')) ∨
        Ty ≤ Law.workOf σ v (A.wrong (A.committedOf σ'))))
        (audit ((Law.stratified σ k hk).closure cl) Reg session) σ' ≤
      max ((((Law.totalWork σ w - T : ℕ) : ℝ≥0∞) / (Law.totalWork σ w : ℝ≥0∞)) ^ K)
          ((((Law.totalWork σ v - Ty : ℕ) : ℝ≥0∞) / (Law.totalWork σ v : ℝ≥0∞)) ^ Ky) + εks + δlink

theorem extraction_audit_window (A : ExtractionAnalysis ((Law.stratified σ k hk).closure cl) Reg session)
    {εks δlink : (R : Reg) → Cont ((Law.stratified σ k hk).closure cl) Reg session R → ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) {w v : Fin m → ℕ} {K Ky : ℕ}
    (hW : 0 < Law.totalWork σ w) (hc : Law.Covers σ k w K) (hN : 0 < Law.totalWork σ v) (hcy : Law.Covers σ k v Ky)
    (T Ty : ℕ) (σ' : Strategy (audit ((Law.stratified σ k hk).closure cl) Reg session)) :
    prob (fun o => o.1 = true ∧ (T ≤ Law.unsoundWork σ w cl (A.wrong (A.committedOf σ')) ∨
        Ty ≤ Law.workOf σ v (A.wrong (A.committedOf σ'))))
        (audit ((Law.stratified σ k hk).closure cl) Reg session) σ' ≤
      max ((((Law.totalWork σ w - T : ℕ) : ℝ≥0∞) / (Law.totalWork σ w : ℝ≥0∞)) ^ K)
          ((((Law.totalWork σ v - Ty : ℕ) : ℝ≥0∞) / (Law.totalWork σ v : ℝ≥0∞)) ^ Ky) +
        εks (reg σ') (cont σ') + δlink (reg σ') (cont σ')

theorem audit_window_of_record (A : Analysis ((Law.stratified σ k hk).closure cl) Reg session) {εks δlink : ℝ≥0∞}
    (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) {w v : Fin m → ℕ}
    (hW : 0 < Law.totalWork σ w) (hc : Law.Covers σ k w 27713) (hN : 0 < Law.totalWork σ v)
    (hcy : Law.Covers σ k v 27713) (σ' : Strategy (audit ((Law.stratified σ k hk).closure cl) Reg session)) :
    prob (fun o => o.1 = true ∧ (Law.totalWork σ w ≤ 1000 * Law.unsoundWork σ w cl (A.wrong (A.committedOf σ')) ∨
        Law.totalWork σ v ≤ 1000 * Law.workOf σ v (A.wrong (A.committedOf σ'))))
        (audit ((Law.stratified σ k hk).closure cl) Reg session) σ' ≤ ((2 : ℝ≥0∞) ^ 40)⁻¹ + εks + δlink

end Audits

end FlockSoundness.Audit
~~~

## Reading it against #364

| #364 (`plan.py` at `50c44582`) | the pin |
|---|---|
| `WorkLaw.budget`: `min(n, max(1, ⌈K·W_c/W_window⌉))`, with `n` the call's units | `callK`: `min(N_c, max(1, ⌈K·W_c/W⌉))` |
| `WorkLaw.sizes`: `min(len, max(floor, ⌈K_c·s.work/W_c⌉))`, with `s.work = w_s·n_s` | `windowK`: `workRule K_c w_s n_s W_c f_s` |
| `window_laws`' y floors: `f_s = ⌈K_y·n_s/N⌉` on each dequantization stratum | `hfy`, with `v = 1` there: `K_y·n_s ≤ f_s·N` |
| other templates at floor 1 (X-SPC-84), tile work only on the tile template | `hone` (see below); floors play no part in `Covers` for `w` |
| one Program (`ncp2.window`): shared strata, one K | `covers_work` for `workK`, and `covers_of_floor` with `floor_le_workK` |

- **Per-call mode:** the window is `Law.stratified σ (windowK σ call w f K) (windowK_le …)`.
  - `covers_window` gives `hc`, and `covers_of_floor` gives `hcy`, with `hkf` from `max f_s _ ≥ f_s`.
  - Then `audit_window_of_record` at K = K_y = 27,713 gives `2⁻⁴⁰ + ε_ks + δ_link`.
- **One-Program mode:** the same through `covers_work` and `covers_of_floor`. Its y floor is the shared dequantization
  stratum's, `f ≥ K_y`.
- **The `max`:** both bad cases are about the one wrong set committed before the draw (`audit_profile`), so the sampling
  term is the larger bound, not the sum.
- **The tile case** reads `unsoundWork`, which includes the wrong units' own work (#390's C1).
- **Bridge (informal, as #374's N1):** `windowK` is what `flock-verify` derives for call c given `--work K_c`, since
  `workK` over that call's program is `workRule K_c w_s n_s W_c f_s`.

## One finding for X-SPC-106: `hone` is needed

The cap `K_c ≤ N_c` is sound only when each call's work sits in one stratum.
- **Counterexample.** Take one call with a 4-unit stratum at work 2 and a 2-unit stratum at work 5, and K = 8.
  - W_c = W = 18, so ⌈K·W_c/W⌉ = 8, and the cap gives K_c = N_c = 6.
  - The work-2 stratum draws ⌈6·2·4/18⌉ = 3. Covering needs 8·2·4/18 ≈ 3.6, and it isn't the whole stratum.
- **#364 meets `hone`**: only the tile template has work in a call (X-SPC-84).
- **For calls with several work templates**, the cap would have to go, or a capped call would have to prove its work
  strata whole.

## Pins proposed

1. `Law.stratified_escape_le_of_covers`
2. `Law.covers_work`
3. `Law.covers_window`
4. `Law.covers_of_floor`
5. `audit_window`
6. `extraction_audit_window`
7. `audit_window_of_record`

- The definitions they read are `Covers`, `callWork`, `callUnits`, `callK` and `windowK`, plus the existing `stratified`,
  `workRule`, `workK`, `workOf`, `totalWork`, `closure` and `unsoundWork`.
- No existing record changes.
- **The proof plan:**
  - the core lemma is `work_escape_le`'s per-stratum hypergeometric step and weighted AM–GM, with `Covers` in place of
    `workK_ge`;
  - the audits use `audit_profile` / `extraction_audit_le`, `closure_escape` and `escape_anti`, as in `Closure.lean`;
  - the record case uses `record_sizing`.

## Asks

- **POUS's Lean lane and circuit worker:** is this the rule #364 runs, and are M1 and M2 the right modelling line?
- **bc-f0bc7e75:** a statement review. After the proof comes the grant of the 7 pins at the PR head.
