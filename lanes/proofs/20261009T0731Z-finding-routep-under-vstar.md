---
id: proofs/20261009T0731Z-finding-routep-under-vstar
campaign: recursive-private-circuits
lane: proofs
kind: finding
status: open
repo: danielreuter/verity
origin: cursor/routep-main-95d4 @ 3b73219f9 (on main c6c268f72)
---

# Route P as the inner proof under V*: what each stage costs V*, and what VBridge must add

Route P is rebased onto main. V* prices route P at 2.4x the rows it needs for C-Flock `--zk` on the same circuit
(2^34.58 against 2^33.32 committed rows at 2^27 cells). The universal unit has no price here: at these sizes its inner
circuit alone has 2^40 to 2^49 ANDs, before any recursion, which is past every schedule V* has (fast100 covers
m 22 to 35). The VBridge additions come to about 2,200 Lean lines (the product GKR, extra claims whose values are
messages, a lone PCS opening, the composition), plus about 725 lines of inner soundness that has no Lean today, chiefly
the product GKR's. All of these are estimates.

Evidence: the pricing scripts and their outputs are `art:fdb2f30b39e35a11e73e1ad5a4f3486fdca48a4962c72f0b0062566c53276c96`
(`price.json`, `tables.md`, `summary.txt`). The class sizes come from rec-holo's recorded `--zk` run
`r20261004-070703-82f9` (`art:b01c152def7e1adf99241c85146b62fb3f0c6f6ef1b853e39e0de0dad70ad4cb`, `meta-*.json`).

## The rebase

`cursor/routep-main-95d4`, three commits on main `c6c268f72`:

- `31316249e` Lean. `RouteP.lean` (562 lines, `route_p_sound`, still an unlisted theorem) and the seven
  hidden-reads modules it needs that main lacks (`InstanceDefs`, `InstanceHides`, `ReadsBind`, `ReadsCompose`,
  `ReadsDefs`, `ReadsHidden`, `ReadsSound`). They go under `Security/Proofs/Flock/Soundness/Discharge/PrivateCircuit/`,
  with their imports renamed and their namespaces unchanged. No sorry. The line citing `Assumptions.RegHides`, which
  main does not have, is dropped.
- `dbe3640b4` the pod port. These are rec-holo's eight pod files (the route P prover is Rust that runs on upstream
  Flock and on C-Flock's patched checkout, with `rec_holo_types.py` as the builder for the unit types), moved under
  `verity/ml/flock/pod/`. On main the builder writes all 12 unit types. SHA-512's traced gate list now has 57,947
  ANDs, down from 81,402; its C-Flock rows are unchanged.
- `3b73219f9` a test, `verity/ml/flock/tests/test_rec_holo_types.py`. On main's builders, a type's gate list and its
  C-Flock rows agree on random inputs. A row whose constant is flipped disagrees. The file's header matches what it wrote.

Lean on node 1: run `r20261009-063326-b0e2`, `check.py --build --update Security/Proofs` at `31316249e`, **PASS**. It
covers 62,108 declarations in 965 modules, with axioms `propext`, `Classical.choice` and `Quot.sound` only. There is no
sorry and no escape, and `lean-audit.json` is unchanged. Python on node 1: run `r20261009-072613-9eb9` at `3b73219f9`
ran both suites in full, with no `--quick`, and **passed** them. `verity-flock` had 847 passed and 10 skipped; its
inputs had changed under both `pod/` and `Security`. `repository` had 161 passed.

## How it was priced

V*'s builder on main (`verity_flock.rec_*`) produced every count, and V*'s rules gave each statement's shape:

- RecOpen{LANES,H}: the unit rows come from `rec_outer.lowering(L, H).layout.useful`. Ten shapes were built:
  {16,2..7,9,10} and {64,6,7}. Six more are extrapolated linearly in H at the step measured between built shapes
  (143,360 rows a level for 16 lanes, 141,312 for 64): {64,3}, {64,8}, {64,11}, {64,13}, {16,8} and {16,12}.
- The algebra of a C-Flock session uses the builder's own `rec_residuals.parts(spec(Shape(m, k_log, claims)))`. Each
  part's unit rows follow `ir_lower.layout`'s placement, and the result equals the built layout on the parts checked.
  Block, slots and session m follow `circuit.compose`'s fit and `rec_vstage`'s m rule, which match compose on the
  shapes checked.
- An instance's ANDs are its unit rows plus 2^18 for each of its SHA-512 and hm96 slots. Committed rows are 2^m for
  each statement.
- The stages V* has no builder for are estimated:
  - The product GKR: a stand-in `GfResiduals` S of upstream's `verify_batched_core` (flock-core
    `product_gkr.rs` 1907-2041), run through the builder's parts and layout. It has one absorbing round per
    sumcheck round, μ(μ+1)/2 + 2 rounds in all.
  - The σ opening: a lone Ligerito opening, whose RecOpen levels the builder counts. Its algebra is ring switch,
    Ligerito's c0 and c1, and T, with the counts the builder gives at that m.

The shapes are those of rec-holo's run. The gate session is m = μ, k_log 16, with 9 claims (2, then the wiring's 3 and
the I/O regions' 4). The σ opening is at m = μ + 5. The acyclicity session is m = μ + 5, k_log 23, 5 claims, and it
comes with the link opening. Plain C-Flock `--zk` is m 26, k_log 23, 6 claims at 2^27 cells and m 25, k_log 22 for the
8 units of 2^22 cells.

Under V*, re-registration and `RegHides` drop out, because the σ openings sit in V*'s witness and inner ZK is off.
Grinding nonces must be zero, because the coins come from the firewall.

## The pricing

At 2^27 cells (μ = 27, one unit, W = 1):

| stage | V* statements (instances) | committed rows | V* ANDs | how |
|---|---|---|---|---|
| gate-row session (C-Flock session, m 27) | 7 (902) | 2^33.83 | 2^32.33 | measured ({64,8} extrapolated one level) |
| product GKR (μ = 27; 380 rounds, 929 products, 30 residuals) | 8 (8) | 2^30.91 | 2^27.38 | estimated |
| σ opening (m 32, one claim, one rep) | 7 (528) | 2^32.95 | 2^31.66 | RecOpen measured ({64,13}, {16,12} extrapolated); algebra estimated |
| **per proof** | 22 (1438) | **2^34.58** | **2^33.06** | |
| acyclicity, first draw of a class only (m 32 session + link opening) | 15 (1586) | 2^34.55 | 2^33.26 | as above |
| C-Flock `--zk`, same circuit (m 26) | 6 (900) | **2^33.32** | 2^32.27 | measured |

Route P under V* is 2.39x C-Flock `--zk` under V* in committed rows and 1.73x in ANDs.

Rec-holo's class sizes (units of 2^22 cells):

| form | gate | GKR | σ | per proof | C-Flock `--zk` | ratio (committed) |
|---|---|---|---|---|---|---|
| 8 units in one session (μ 25), σ opened per unit (8 openings at m 27) | 2^33.32 | 2^30.70 | 2^35.75 | 2^36.04 | 2^33.32 | 6.6x |
| 8 units (μ 25), one σ commitment opened once (m 30) | 2^33.32 | 2^30.70 | 2^32.86 | 2^34.24 | 2^33.32 | 1.9x |
| one unit (μ 22, σ at m 27) | 2^33.00 | 2^30.32 | 2^32.75 | 2^34.00 | 2^33.00 (m 22 shape estimated) | 2.0x |

The acyclicity session for a 2^22-cell class costs 2^34.36 once.

The universal unit (`and_count`, exact, with N_OUT taken as rec-holo's I/O rows; that term is under 1%):

| class | G | N_IN | ANDs |
|---|---|---|---|
| 2^27 cells | 25,263,279 | 71,188 | 6.43e14 (2^49.19) |
| one unit of 2^22 cells | 1,048,472 | 4,075 | 1.11e12 (2^40.01) |
| 8 units of 2^22 cells | (each) | (each) | 8.86e12 (2^43.01) |

These counts are for the inner circuit alone. Proving them needs a C-Flock table of about m 42 to 52, past
fast100's m ≤ 35 and past any prover we run. Route P's inner table is the gate rows at m = μ (2^24.6 rows at 2^27
cells).

## What the numbers say

- **V*'s cost of a C-Flock session hardly depends on m.** From m 22 to 27 it runs 2^33.0 to 2^33.8, and the RecOpen
  levels dominate (fast100's queries are fixed). So the extra price of route P is how many PCS openings it adds, not
  how big they are. Per proof it adds one, the σ opening, and that is most of the 2.4x.
- **The GKR is small but badly shaped.** Its roughly μ²/2 absorbing rounds each cost an hm96 slot plus compressions,
  split across 7 or 8 parts of one instance each. Each part is padded to the 8-block minimum, so 2^27.9 rows are used
  out of 2^30.9 committed. The fix is one `GkrLayer` template, run as μ + 1 instances of one statement, which brings
  2^30.9 down to 2^29.0. That is about 6% of the per-proof total.
- **Opening σ per unit is the expensive choice.** Eight openings at m 27 (2^35.75) cost 7.4x one opening of a
  single σ commitment at m 30 (2^32.86). With sampled units, commit σ once per class and open it once per proof at the
  drawn slots (ŝ_σ(ρ) = Σ_slot eq(ρ_slot, slot)·ŝ_{σ_u}(ρ_loc) + tag already has that form).
- **The acyclicity table is a one-time cost per class** (2^34.4 to 2^34.6), about one proof's worth.

## What VBridge must add

These are modelled on the landed VBridge pieces (`Security/Proofs/Flock/VBridge/`, 6,393 lines). Sizes are Lean lines
and are estimates.

| stage | proposed lemma(s) | shape | lines |
|---|---|---|---|
| gate session's wiring claims | `FlockVBridge.Algebra.residuals_eq_run_xv`, `FlockVBridge.Algebra.ringSwitch_of_residuals_xv` | `residuals_eq_run` / `ringSwitch_of_residuals` where an extra claim's value is a message (ŵ(ρ) from the GKR's last round) and its point is coins. Today `claimsOf` takes extras as constants (`cst e.value`). | 180 |
| product GKR: the algebra | `FlockVBridge.Gkr.structureOf`, `FlockVBridge.Gkr.run`, `FlockVBridge.Gkr.run_sim` | `structureOf`/`run`/`run_sim` (`Algebra/Structure`, `Sim`) for `verify_batched_core`: per layer, λ, k rounds (g1, g_inf, g0 from the running claim), vl0, vl1, vr0, vr1, the gate check and the next claim | 450 |
| product GKR: residuals = run | `FlockVBridge.Gkr.residuals_eq_run` | as `Algebra/Eval.residuals_eq_run`, over `buildAll_spec` | 120 |
| product GKR: the layers | `FlockVBridge.Gkr.layers_of_residuals` | as `zerocheck_of_residuals`: zero residuals imply every round's g0 + g1 + g_inf identities and every gate check over F128 | 250 |
| product GKR: the inputs | `FlockVBridge.Gkr.input_of_residuals` (with `FlockVBridge.Gkr.sId_eval`) | zero residuals imply f(ρ) + α·s_id(ρ) + β and g(ρ) + α·ŝ_σ(ρ) + β, with ŝ_σ(ρ) the slot-weighted sum of the σ openings' values | 260 |
| λ·vr0·vr1 | `FlockVBridge.sound_residualForms_scaled`, `FlockVBridge.OfVStar.residualForms_eq_scaled` | `sound_residualForms` / `OfVStar.residualForms_eq` for a residual term coin × message × message. `GfResiduals` refuses a message × message term whose coefficient isn't 1, so this also needs a new V* op. Alternative: unbatch the GKR (two product sumchecks, +2^30.9 committed, about 8%) and add no new form. | 120 |
| σ opening | `FlockVBridge.Algebra.pcsOnly_of_residuals` (with `runPcs`, `runPcs_sim`, `residuals_eq_runPcs`) | a lone Ligerito opening of one claim: ring switch and Ligerito with no zerocheck or lincheck, reusing `ringSwitch_of_residuals` and `ligerito_of_residuals` | 300 |
| σ's RecOpen levels | none: `unit_recOpen` at one rep | needs σ's tree to have plain SHA-512 leaves under a salted top, as the firewall's sessions do. RecOpen refuses hm96 salted leaves. | 0 |
| composition | `FlockVBridge.routeP_vBridge` | `VBridge`'s four conjuncts for route P's statements: the gate session, the GKR parts and the σ opening chained over one transcript. Its size depends on G (`note:lean/20261008T1756Z-finding-vbridge-g-inner`). | 300 |
| recursion | `FlockSoundness.Discharge.Recursion.routePInner`, `FlockSoundness.Discharge.Recursion.routeP_recursive_sound` | `RecursiveSound` at route P's inner verifier | 200 |

The VBridge total is about 2,180 lines (about 2,060 without the scaled form). Also needed, outside VBridge, for an
end-to-end guarantee:

| lemma | what it is | lines |
|---|---|---|
| `FlockSoundness.Gkr.batched_sound` | the product GKR's soundness error. No product GKR exists in Lean; it can reuse `Soundness/Rounds.residualPoly`, whose round form is the same. | 300 |
| `FlockSoundness.Discharge.PrivateCircuit.ordered_of_acycTable` | the acyclicity table's session gives `RouteP.Ordered` | 175 |
| `FlockSoundness.Discharge.PrivateCircuit.route_p_inner_sound` | `route_p_sound` composed with GKR soundness, σ binding and acyclicity: what an accepting compiled verifier implies | 250 |

The Lean verifier of record also gains two forms: the product GKR's check and the σ opening. By the ruling, neither
lands ahead of its proof. Each new V* unit kind (the GKR parts, the PCS-only part) also needs pinning in G's sense
(G's items 1 to 3). These are `InnerRepCheck_v2{S}` instances with a different S producer, so the cost on top of G's
generic pin is small, about 100 lines each. It is included in neither total, since it depends on how G lands.

## Open

- Should the gate check's λ·vr0·vr1 get a new `GfResiduals` form, or should the GKR be unbatched? I recommend
  unbatching: about 8% more rows, and no change to the V* template G is pinning.
- σ under V* has to be one commitment per class with plain leaves under a salted top. Both are changes to route P's
  pod prover; the pricing assumes them.
