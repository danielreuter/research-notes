---
cursor:
  subagentId: "bc-75d1b678-7ce5-5b01-a155-7dde36338030"
---

# PoUW accountable compute in Lean (design note §12.2)

The accountable-compute theorem of [the sampled-proofs design note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/sampled-proofs-circuit.md)
§12.2, proved against `main`'s `Stratified` law, `stratified_escape` and one-stage audit profile, with `harm_bound`'s
specification stated. It covers the red team's verdict on §12 (X-SPC-43 to 46, in
[`redteam-sampled-proofs-circuit.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw-fp8/redteam-sampled-proofs-circuit.md)).

**Status.** Every statement below is proved: no `sorry`, no `axiom`, no `native_decide`, and only `propext`,
`Classical.choice` and `Quot.sound` (AXIOMS.txt). Verity's Lean audit (`tools/lean/audit.py` at origin/main b4fd93e9)
passes: 682 declarations in 15 modules, 21 pinned theorems, kernel replay. The pins await a named statement reviewer;
`review.txt` lists each pinned signature and each definition it reads.

~~~text
VERITY_CHECKOUT=<a Verity checkout at b4fd93e9 or later> ./check.sh     # ALL CHECKS PASSED
~~~

`check.sh` checks the vendored files' digests (and diffs them against the checkout), builds, compares the axioms with
AXIOMS.txt, and runs the checkout's audit. The pins' records are in that audit's format; the store's older copy of
`tools/lean` (6746f408) prints signatures differently and reports every pin as changed.

## Setup

- **Toolchain and Mathlib:** Lean v4.34.0 and Mathlib `5ed2965`, the revision Verity's soundness package pins through
  ArkLib. `lake exe cache get`, then `lake build`.
- **`main`'s audit law, vendored byte for byte** (`FlockSoundness/`, digests in VENDORED-FROM): `Game.Basic`,
  `Game.Interleave`, `Game.Union`, `Game.Prob`, `Audit.Circuit`, `Audit.Law`, `Audit.OneStage`, `Audit.Extraction` and
  `Audit.Stratified`. That is the whole import closure of `Audit/Stratified.lean`, and it needs only Mathlib, so the
  package builds without ArkLib. The audit covers these modules too.
- **This package** (`PouwAccountable/`): `Charging`, `Closure`, `HarmBound`, `Assumptions` and `Accountable`.

## The model

- A window's units are `Fin n`. Its tiles are `Fin nT`, with work `w t` (the tile's `W_ref`, at least 0).
- A tile's **closure** `cl t` is the set of units its credit depends on. In PoUW (`Layout`) that is its own tile unit,
  the X strip and Y strip it reads, and the node units on its X strip's path to D_A.
- A tile is **sound** when its closure holds no wrong unit. `soundWork` is the verified work, and `unsoundWork` is the
  rest. Together they make up `totalWork` (`soundWork_add_unsoundWork`).
- **Laws** are `main`'s `Law` (uniform coins, a drawn unit set per coin, `escape B`).
- **The audit** is `main`'s `audit L Reg session` with an `Analysis`.
  - The committed transcript `A.committedOf σ'` is fixed at registration.
  - `KnowledgeSound ε_ks` and `LinkSound δ_link` are the proof system's per-unit errors, which the note writes as
    ε_proof = ε_ks + δ_link.
- **Width is abstract.** No statement reads a tile's outputs. Whether Z is a tile output or is certified by narrow units
  changes only the partition (`n`, `cl`) and the observable-bits harm `hb`, and both are parameters.

## The statements

The table lists every pinned theorem, with the hypotheses that each one takes. All of them are **Proved**.

| Theorem | What it says | Hypotheses beyond the model |
|---|---|---|
| `unsoundWork_singleton` | **Harm charging is exact** for one wrong unit: `unsoundWork cl w {u} = harm cl w u`, where `harm cl w u` is the work of every tile whose closure holds `u` | none |
| `unsoundWork_le_harm` | **Coverage** (§12.2 (1)): `unsoundWork cl w B ≤ ∑_{u∈B} harm cl w u` | `w ≥ 0` |
| `harm_le_unsoundWork` | **Drawn or not, a wrong unit's whole harm is counted**: `u ∈ B → harm cl w u ≤ unsoundWork cl w B`. A wrong node unit that no draw reaches still has every tile beneath it counted | `w ≥ 0` |
| `Layout.harm_tile`, `harm_xs`, `harm_ys`, `harm_node` | §12.1's harm column. A wrong tile spoils its own work; a wrong X or Y strip spoils the work of the tiles that read it; a wrong node unit spoils the work of the tiles whose X strip's path holds it | each unit plays one role (the tile map is injective, and tile, strip and node units are distinct) |
| `mem_closureLaw_draw` | **The closure draw proves exactly the closures of the drawn tiles.** A node unit beneath no drawn tile is never proved, and has no stratum | none |
| `closureLaw_escape` | **The closure draw's escape is the tile law's escape of the unsound tiles**: `(closureLaw Lt cl).escape B = Lt.escape (unsoundTiles cl B)` | none |
| `both_escape_le` | **Drawing more only lowers every escape**: closure draws plus independent floor draws `M` | none |
| `harmOpt_isHarmBound`, `harmOpt_le` | The exact optimum H*(δ) (`harmOpt`, a finite maximum that includes ∅) is the least harm bound | `δ ≤ 1` for the least-ness |
| `stratified_isHarmBound` | **A closed-form harm bound for `main`'s stratified law.** Suppose every stratum is proved whole (`k_s = N_s`) or satisfies `N_s·hmax_s ≤ c·k_s`. Then `c·ln(1/δ)` bounds the harm of every set that escapes with probability at least δ. With `c = εW/ln(1/δ)` this is §12.3's harm-proportional sizing | `h u ≤ hmax(σ u)`, `c ≥ 0`, `δ > 0` |
| `audit_damage` | **Accountability for any covered damage** (width-abstract): `Pr[accept ∧ H < D(wrong)] ≤ δ + ε_ks + δ_link`, for any `D ≤ ∑ h` and any harm bound H of the law at δ | `KnowledgeSound`, `LinkSound`, `IsHarmBound L h δ H` |
| `exfiltration` | The observable-bits bound from the same draw, with an abstract `hb` | as above |
| `audit_strata` | §12.2 (2) as the note first stated it: any law, each unit charged `harm cl w` | as above, and `w ≥ 0` |
| `audit_closure` | **§12.2 (2′), the closure law** (X-SPC-44): for any law whose escapes are at most the closure draw's, `Pr[accept ∧ H*_tiles(δ) < unsoundWork(wrong)] ≤ δ + ε_ks + δ_link`, where H*_tiles is a harm bound of the tile law with each tile's work as its harm. Node units need no stratum | `KnowledgeSound`, `LinkSound`, `IsHarmBound Lt w δ H`, `hdom` |
| `accountable_compute` | **The conclusion.** Tiles are drawn by `main`'s stratified law, with each stratum proved whole or sized so that `N_s·wmax_s·ln(1/δ) ≤ εW·k_s`. Each drawn tile is proved with its closure, plus any other draws. Then `Pr[accept ∧ soundWork(wrong) < (1 − ε)·W] ≤ δ + ε_ks + δ_link` | `KnowledgeSound`, `LinkSound`, `0 < δ < 1`, `ε > 0`, `w ≥ 0`, `w ≤ wmax`, `hdom` |
| `accountable_compute_floor` | The same, for the window's law `both (closureLaw …) M` | as above |
| `compute_used` | **The γ step** (§12.2 (3)), in any game: `Pr[accept ∧ cost < (1 − γ)(W − H)] ≤ a + δ_in + δ_idx + η_TT + ε_cr` | `γ ≤ 1`, (2)'s bound `a`, **A9** `AnchoredInputs`, **A11** `UniqueCallIndices`, **A8 with A10** `PerTileCount` |
| `compute_used_audit` | The γ step on the audit: `Pr[accept ∧ cost < (1 − γ)(1 − ε)·W] ≤ δ + ε_ks + δ_link + δ_in + δ_idx + η_TT + ε_cr` | as `accountable_compute` and `compute_used` |

## Named hypotheses (`PouwAccountable.Assumptions`) and the note's A1 to A11

- **A8 with A10, `PerTileCount`** (not proved): PoUW's per-tile count statement.
  - It is claimed only on transcripts whose inputs are anchored and whose call indices are unique. On those, except
    with probability `η_TT + ε_cr`, the cost is at least `(1 − γ)` times the verified work.
  - A10 enters here. The statement is in the random-oracle model (`random-oracle`: the Program's SHA-512 and SHAKE256
    stand in for TT_NCP_U's oracle). `ε_cr` is `cr/sha-512`'s collision term for D_s and the node hashes.
  - PoUW's Lean states TT_NCP_U per call, not per tile (§8 item 13).
- **A9, `AnchoredInputs`**: an accepted audit has a salt, forward index or weights off their anchors with probability at
  most `δ_in`. It is `main`'s `Partition.AnchorsSound`, stated as an event.
- **A11, `UniqueCallIndices`**: an accepted audit repeats a call index with probability at most `δ_idx`, which is 0 for
  the verifier's refusal at registration.
- **`IsHarmBound L h δ H`** is the specification of core's `Stratified.harm_bound`: every set escaping with probability
  at least δ has harm at most H.
  - The Python greedy fill is not proved here. Using its value is a hypothesis.
  - `harmOpt` and `stratified_isHarmBound` are proved instances.

How the note's assumptions enter:

| Note | In Lean |
|---|---|
| A1, pinning | `main`'s model: `A.committedOf σ'` is a function of the registration and the strategy, fixed before the draw |
| A2, the partition | Only through `main`'s `Analysis`: `wrong(τ)` is defined when cross-unit reads go through committed values, and the per-unit errors are per unit. **"No exception" appears in no hypothesis: it is policy.** The exception form satisfies the same theorems |
| A3, harms from the layout | `cl`, `w`, `wmax` and the harms are parameters that don't depend on `σ'` |
| A4, uniform harm per stratum | **Cost only.** No theorem assumes it. `stratified_isHarmBound` uses a per-stratum maximum `hmax`, and uniform harm only makes that maximum exact |
| A5, the cap | The law's well-formedness (`hk : k_s ≤ N_s`). A stratum proved whole needs no sizing condition: `stratified_isHarmBound` shows it holds no wrong unit of a set escaping with positive probability |
| A6, independence | Built into `main`'s `Law.stratified`. Under closure it is needed only among the tile strata |
| A7, proofs | `KnowledgeSound ε_ks`, `LinkSound δ_link` |
| A8, A10 | `PerTileCount` |
| A9 | `AnchoredInputs` |
| A11 | `UniqueCallIndices` |

## Where the note's theorem had to change to be provable

1. **The closure needs its own statement** (X-SPC-44).
   - The note's Lean block states the stratified law over every class. The decided law is the closure, which is not a
     stratified law on units. With the node stratum at k = 0, the stratified statement is vacuous.
   - `audit_closure` is the statement to pin, (2′). Its escape is the tile law's alone (`closureLaw_escape`). Node
     units are covered without a stratum (`mem_closureLaw_draw`, `harm_le_unsoundWork`).
   - The window's real law adds floor draws, which `hdom` and `both_escape_le` cover.
2. **"With probability ≥ 1 − δ" is joint, not conditional on acceptance.** The provable statement is
   `Pr[accept ∧ verified < (1 − ε)W] ≤ δ + ε_ks + δ_link`, where ε_proof is `main`'s two per-unit terms.
3. **H\* is any harm bound.**
   - The note's `sSup` over ℚ became a finite maximum that includes ∅ (`harmOpt`).
   - The theorems take any H satisfying `IsHarmBound`, so `harm_bound`'s value can be used under its specification.
4. **Harm-proportional sizing is proved with ln(1/δ)/ε, as an upper bound.**
   - `stratified_isHarmBound` bounds each stratum's risk by `k·m/N` (from `main`'s `choose_sub_mul_pow_le` and
     `1 − x ≤ e^−x`), so it certifies t = ln(1/δ)/ε: 27,726 draws at ε = 0.1%, δ = 2⁻⁴⁰.
   - `harm_bound` certifies 27,707 (X-SPC-47). The gap, 0.07%, is the relaxation's.
   - With non-uniform harm the rule uses each stratum's maximum harm (A4 is cost-only).
5. **(3) needs A9 and A11 as acceptance events, and the per-tile statement restricted to them** (X-SPC-45).
   - The note's (3) took η alone.
   - The provable form splits acceptance on anchored inputs and unique call indices, and adds A10's collision term:
     `δ + ε_ks + δ_link + δ_in + δ_idx + η_TT + ε_cr`.
6. **(3) lives in a composed game that `main` doesn't have.** The per-tile statement's randomness is the salt, and
   `main`'s audit game has no salt.
   - `compute_used` is stated for any game, and applies once PoUW composes serving with the audit.
   - `compute_used_audit` is the salt-fixed instance on `main`'s audit.
7. **§12.1's harm column holds when each unit plays one role** (`Layout.harm_*`). The theorems use `harm cl w`
   directly, so they need no role condition.

## Not formalized here

- Core's `harm_bound` implementation (its specification is `IsHarmBound`).
- PoUW's per-tile count statement, and the composed salt, serving and audit game.
- Hashes, which appear only as the named terms of A10.
- Reusing Y proofs across a run's windows (X-SPC-51). It lowers the cost, and the per-window law and (2) are unchanged.
- The tighter exact rule, `−ln(1 − ε)` in place of ε. It would need `(1 − m/N)^k` and Jensen's inequality across
  strata.
