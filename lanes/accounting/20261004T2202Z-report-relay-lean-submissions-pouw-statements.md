---
id: 20261004T2202Z-report-relay-lean-submissions-pouw-statements
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/lean/submissions/pouw/STATEMENTS.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/lean/submissions/pouw/STATEMENTS.md`, sha256 `54c0b73c3464d9e3b17049d538b2a72d98c952219803d7289bd94b5eef70ff86`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# PoUW Lean statements: what each definition and pinned statement says

Package `lean/submissions/pouw/` (library `Pouw`). Lean `v4.34.0`, Mathlib `5ed2965`, the POUS pin. Section numbers are the problem statement's (`docs/pouw/problem-statement.md`, draft 2). Trusted files: `Pouw/Basic/*`, `Pouw/Game/*`, `Pouw/Protocol/{D1,M1}.lean`, `Pouw/Witness/{Model,Copy}.lean`, `Pouw/Assumptions.lean`, `Pouw/Pinned.lean`; the NCP chain's trusted modules (§7 to §11) are listed in `ASSUMPTIONS.md`. Everything else is proof, checked by the kernel and the audit.

Revision of 21:27Z (red-team phase B): `N ≤ 2^64` in the domain (B1); domains are predicates on layouts, and the milestone domain requires every weight to serve at least `2^16` rows (B3); the honest reference is one program that reads the activations as input (B3); (d′) and (d″) in budget form over `Ω_max` with `W_ref` generic (B3); the named instance `D1.m1` (B4); `CostModel.Queries` inside TT, and TT's error takes `(q, N)` (B6, B1).

Revision of 21:50Z (the coordinator's 21:21Z order, red-team B3, B4 and B8): `IsMilestone` uses `GroupShared 16` in place of `EpochShared`; `D1.m1` has `E_R` per (epoch, weight, group of 16), tt-attacks §4's orientation (outer factors in `[−3, 3]`, inner factors `±1`) and the domain `2^12 ≤ m ≤ 2^17`, `k = n = 2^16`, with `≥ 2^16` rows per (group, weight); `m1Wref` is the explicit `H_ref` schedule (llm-shapes §3), and `MilestoneWref` pins its bound. R_copy (tt-attacks §6) is the second, noise-dependent witness: `CopyBound`, `CopyNzWitness`, `Sanity.copy_zero_noise`.

Revision of 22:00Z (the coordinator's 21:35Z and 21:47Z entries): `m1Wref` uses red-team B3's recount, `mkn + 2mkr + 6mrn + 20mk + 32mn` per unit (the LOP3 that returns `A + E` to signed int8) and `20kn` for `B + F` per weight, so `Ω_M1 = 8221/8192` and `γ_M1 = 1749/205525 ≈ 0.851%`; §5 lists W1-3 and W1-4.

Revision of 28 Sep 06:00Z (red-team P7-4): Daniel's 28 Sep 03:35Z W1 rule prices sub-word extraction like PRMT, at 16 units per word produced, so the int8 limb split of `X1 = (A + E)·F_L` and of `G_g` is priced (red-team Phase 7, P7-4, applied in the `.lean` files by the `barrier` worker; `internal/pouw/new-crypto/barrier.md`). `m1Wref` adds `576·m` per unit and a row share of `576·n` per group, so `Ω_M1 = 65769/65536` and `γ_M1 = 14017/1644225 ≈ 0.8525%`; §5 lists the sub-word rule.

Revision of 28 Sep 06:55Z: §7 lists the `barrier` worker's 30 `Pouw.Dimension` pins of 06:00Z and 06:53Z (149 pins in the package).

Revision of 28 Sep 09:30Z (documentation only; 220 pins at 09:21Z): §7's rows follow red-team P9B-1 (every A2 hypothesis now reads only the non-final checked words) and P11-1 (the named assumptions sit in assumptions modules). §8 lists the 16 pins of Theorem 1 in Lean and A2 on the words (07:58Z to 09:07Z). §9 lists route U's 55 pins (09:21Z; approved by the red team in Phase 13, 09:50Z). It also records that the unbiased `TTNCP` is retired for NCP's checked values. Since 07:57Z `lean-audit.json` has been written by Verity's current `tools/lean` (one digest per definition), and the red team confirmed in Phase 11 that the switch changed the format only.

Revision of 28 Sep 12:40Z (documentation only; 243 pins). §10 lists the open pipe's 9 pins (approved, red team Phase 14). §11 lists the M4090 embedding's 14 pins, which are in draft semantics and await statement review (red team Phase 15). §5 notes the proposed W1 amendment for branching (G-branch), pending Daniel.

Revision of 28 Sep 13:25Z (documentation only; 243 pins). §11's 14 pins are approved (red team, Phase 15), with the definitions they read. Round 6 measured FSET at 16, so FSET is `int` and the FP32 class is exactly FFMA, FADD and FMUL (a docstring change; no record changed).

Revision of 29 Sep 00:25Z (documentation only; 294 pins). §12 lists the 12 `Pouw.Fp8Atom` pins of 28 Sep 22:25Z. Red-team gate R1 passed them at 29 Sep 00:15Z, with one open condition. They are the bit-exact `HOPPER_E4M3_K32` step and the FP32 running add, M1 of `internal/pouw-fp8/lean-atom-plan.md`. The 39 pins added between 12:40Z and 22:25Z are not yet listed here: 36 in `Pouw.Dimension.H100` (`H100*.lean`) and 3 in `Pouw.Dimension.Fp8Mma`, which brought the package to 282.

Revision of 29 Sep 01:10Z (294 pins; no pin record changed). In §12, `conformance` and `addConformance` now pin branch covers, 631 steps and 1,090 adds, in place of the 10,549 steps and 5,000 adds. The definitions they read changed (`Conformance`, `AddConformance`, `vectors` and `Vectors.add`), so both await statement review (red team, R1). Every vector that left the kernel still runs in `check.sh`, as a compiled test that is not a proof (`PouwBulk.lean`), together with R1's 166,000 differential steps. `check.sh` passes in 8 min instead of about 22.

Revision of 29 Sep 02:30Z (310 pins; no existing record changed). §13 lists H-1T's 16 M2 pins, which red team Phase 19d granted at 03:27Z.

Revision of 29 Sep 04:10Z (321 pins; no existing record changed). §14 lists the 11 pins of M3 and M4a and the new named assumption `H1TRunningWords`; they await statement review. §12 marks R1's F1 closed (Round 11, 04:02Z). §13 applies Phase 19d's notes X-M2-3 to X-M2-5.

Revision of 29 Sep 05:40Z (321 pins; no pin record changed). §14 is granted (Phase 19f, 05:17Z), with its notes X-M3-1 to X-M3-3 applied. §15 narrows `Hard` by column (M4b). `Hard`, `H1TOneFlip` and `H1TRunningWords` changed, and `FarTags` and `OppLater` are new, so four granted records now read changed definitions; they await statement review.

Revision of 29 Sep 06:05Z (323 pins; no existing record changed). §16 states `TTH1T`, the per-tile count statement, as a named assumption, with the two pins `tth1tAllRight` and `tth1tSat`; they await statement review.

Revision of 29 Sep 07:20Z (323 pins; one record changed, `tth1tSat`). §15 and §16's pins are granted (Phase 19h, 06:42Z); `TTH1T`'s statement was not (X-M4-4). §17 gives `TTH1T` layout A's domain of tiles (`Tiling.AtLeast r c`) and narrows `Hard` further (M4c: X-M4-1, X-M4-2). `Hard`, `H1TOneFlip`, `H1TRunningWords` and `TTH1T` changed, and `Early`, `SkipsLast`, `Stuck` and `Tiling.AtLeast` are new; they await statement review.

Revision of 29 Sep 08:55Z (documentation only; 323 pins; no record changed). §17 is granted (Phase 19j, 08:14Z). §17.1's lucky-guess figure is corrected (X-M4c-1): `(9/256)^r`, about `2^(−77.3)` per tile at `r = 16` in the zero-coded family, or `2^(−128)` for layout A's aligned blocks, where it had column 0's `64^(−r)`; the conclusion stands.

Revision of 29 Sep 13:45Z (328 pins; no existing record changed). §18 lists the five pins of `H1TCrossLate` in the exact-512 regime, granted by red team Phase 19p (bc-89770364, 13:26Z, v2.37), with its ten definitions moved into a statements layer (X-CL-2).

Revision of 29 Sep 14:29Z (323 pins; no existing record changed). §18's five theorems are granted, not pinned: pin when used (the requester's correction, 13:27Z). Their records left `lean-audit.json`; the 323 earlier records are byte-identical to before 13:45Z. The statements layer `H1TCrossLate.lean` stays, built and audited.

## 1. Definitions

| Lean | Problem statement | What it says |
|---|---|---|
| `pr P` (`Basic/Prob.lean`) | §3.3 "probabilities over H, s and 𝒜's coins" | the fraction of a finite type where `P` holds (0 on an empty type). Adversaries are deterministic; a randomized one is an average of deterministic ones within the same budget |
| `Mat`, `mm k A B` (`Basic/Mat.lean`) | §3.2 useful computation | integer matrices as functions `ℕ → ℕ → ℤ`; `mm k` is the exact product over inner dimension `k` |
| `InInt7`, `InNoise`, `InInt8`, `InInt32` | §3.2 headroom | `[−64, 63]`, `[−63, 63]`, `[−128, 127]`, `[−2^31, 2^31 − 1]` |
| `wrap32`, `accW`, `mmW` | §3.2 "int32 outputs" | two's-complement int32 wraparound; an int32 accumulator; the product as the accumulator computes it |
| `Shape`, `Shape.Wmm` (`Game/Defs.lean`) | §3.2 | `(m, k, n)`; `W_mm = m·k·n` |
| `Layout`, `Workload` | §3.2 workload | `N` units `0 … N − 1` (index = position), each with a shape and weight id; plus the weights `B_w` |
| `Shape.InDefaultDomain`, `milestoneShape`, `Layout.ShapesIn`, `Layout.rowsOf` | §3.2 shapes, §6 D1 notes | default shape domain: `m` a positive multiple of 16, `k, n ∈ [2^10, 2^16]` multiples of 64; milestone shape `(2^12, 2^16, 2^16)`. `ShapesIn D L`: every unit's shape is in `D` (§3.2's domain is `ShapesIn InDefaultDomain`). `rowsOf L w = ∑_{u : w(u) = w} m_u` |
| `Workload.InDomain D` | §3.2, W3 | `D` is a predicate on layouts, part of `Π`. In the domain: **`N ≤ 2^64`** (the index is a 64-bit field; red-team B1), the layout satisfies `D`, and every weight entry a unit reads is int7 |
| `State`, `Commit`, `Transcript` | §3.3 steps 2 and 4 | `σ` is any finite data (`List ℤ`). A transcript gives each unit a commitment `(A_u, checked values, useful output)` or a blank |
| `CostModel Q R S` | §3.1, design requirement 2 | a model's programs, `run`, `cost` and `calls` on (oracle, workload, **activation input**, state, salt). **The model fixes cost and call counting; the adversary only picks a program.** M_4090 is one instance; every theorem is for every cost model |
| `CostModel.Queries` | red-team B6 | programs reach `H` only through counted queries: on fixed inputs a run is a `QTree`'s result and `calls` counts its queries. Required inside TT |
| `Protocol Q R S` | §3.2 "the protocol Π fixes four things" | `Y(H, s, U, u, A_u)` (noise derived from `H` inside `Y`), which entries are compared (`checkIdx`), `H_ref`'s checked values and decoded output, and `W_ref` (from the layout only, never from input values) |
| `ActOK`, `CheckedOK`, `OutOK`, `Correct` | §3.2 correct unit | committed `A_u` int7 in shape; compared checked entries equal `Y`; useful output equals `A_u·B_{w(u)}` on `m × n`. `Correct = CheckedOK ∧ OutOK` |
| `correctSet` (K), `checkedSet` (K′) | §3.3 step 5, §4.4 | `K` = correct units; `K′` = units with correct checked values. `K ⊆ K′` by definition |
| `Protocol.Complete D` | §3.2 "H_ref is complete" | on the domain, for every `H`, `s` and int7 `A`, `H_ref`'s checked values equal `Y` and its output equals `A·B` |
| `honestTranscript`, `AdmitsRef CM P D qref` | §3.2 `W_ref` = H_ref's cost | **one program**, fixed before the workload and the activations, outputs the honest transcript on every in-domain workload and int7 activation input, with no preprocessing, at cost `≤ ∑_u W_ref(u)` and `≤ qref U` oracle calls (`∃ prog ∀ U ∀ act`; red-team B3: a real kernel reads its operands, it does not embed them) |
| `QTree Q R α`, `eval`, `calls` (`Basic/QTree.lean`) | §3.3 step 2 | adaptive oracle programs: any computation between queries; `calls` counts the queries on the path taken |
| `Adversary CM`: `pre`, `online`, `act` | §3.3 steps 2 and 4 | `pre : QTree Q R State` (an oracle program chosen after the workload, unbounded computation, never sees the salt); `online` is a program of the model; `act` is the activation input it reads as the units' own operands (it may commit other activations) |
| `Adversary.Bounded U T q` | §3.3 step 4 | for every `H` and `s`: online model cost `≤ T`, and preprocessing queries plus online model calls `≤ q` (surely). Preprocessing costs nothing (red-team A3's fix) |
| `Wins P U γ T τ H s` | §3.3 step 5 | `T/(1 − γ) < ∑_{u ∈ K} W_ref(u)` |
| `Gγ CM P D γ η` | §3.3 requirement | `∀ U ∈ D, ∀ T ≥ 0, ∀ q ≤ 2^64, ∀ 𝒜 within (T, q): Pr_{H,s}[𝒜 wins] ≤ η(q, N)` |
| `Requirement CM D γ η` | §3.3 requirement | `∃ Π, ∃ qref`: `Π` complete, the model runs `H_ref` at `≤ W_ref`, and `Gγ` holds. Quantifier order `∃Π ∀U ∀T ∀q ∀𝒜` |
| `Ticket w N`, `AuditAccepts K c` | §3.5 work-weighted sampling | unit `u` owns `w(u)` tickets, so a uniform ticket picks `u` with probability `w(u)/∑w`; the audit accepts iff all `t` sampled units are in `K` |
| `Salt`, `reductionGamma`, `Params.γ0` (`Game/Params.lean`) | §1.2, §4.4 | `Fin (2^128)`; `γ = 1 − (1 − γ₀)/Ω_max`; `γ₀ = 1/200` |
| `D1.Params`, `D1.Params.toProtocol` (`Protocol/D1.lean`) | §4.4 TT's Π, §6 D1 | rank `r`, checked depth `d`, the noise derivation (query lists `qAct`, `qWt`; expansions `expWt` of the weight's answers and `expAct` of the unit's and the weight's answers), `W_ref`. Checked values: running partial sums of `(A + E_L·E_R)(B + F_L·F_R)` at depths `d, 2d, …` (last block capped at `k`). `H_ref`: the same in int32, decode `C′ − (A·F_L)·F_R − E_L·(E_R·B′)` in int32 |
| `D1.nBlocks`, `D1.blockEnd`, `GroupShared G`, `IsMilestone`, `NoiseRange`, `QueryBound` | §5 item 1, §6, W4 as replaced at 21:18Z | `⌈k/d⌉` blocks; `GroupShared G`: `qWt` ignores the unit, and for every oracle `E_R` depends only on (salt, weight, `⌊u/G⌋`, shape); milestone = `r = d = 16` and `GroupShared 16` (red-team B8; `W_ref` is not fixed here); noise entries in `[−63, 63]`; at most `c` noise queries per unit |
| `D1.m1 Wref`, `M1Q`, `M1R`, `m1ELQ`, `m1ERQ`, `m1FQ`, `m1Queries` (`Protocol/M1.lean`) | §3.2 derivation, tt-attacks §4, W4, W6; red-team B4, B8 | **the named instance.** Queries: unit `u`'s `E_L` (`m × 16`) from `(s, u, A_u, w(u), c)`, `c < 2^21`; the `E_R` (`16 × k`) of group `⌊u/16⌋` on `w` from `(s, w, g, c)`, `c < 2^20`; weight `w`'s `F_L` (`k × 16`) and `F_R` (`16 × n`) from `(s, w, c)`, `c < 2^21` (64-bit index and weight-id fields, 60-bit group; `A_u` as its block on `2^17 × 2^16` mod 128, injective on int7). Distribution (tt-attacks §4): outer factors `E_L`, `F_R` uniform on `{−3, …, 3}`, inner factors `E_R`, `F_L` uniform on `{±1}`, all independent (answers `Fin 7 × Bool`). `W_ref` is a parameter |
| `M1Shape`, `m1GroupRows`, `m1Domain` | tt-attacks §4's D, red-team B3 | milestone shapes: `2^12 ≤ m ≤ 2^17`, `16 ∣ m`, `k = n = 2^16` (so `m·G ≤ 2^21`). `m1GroupRows L u`: the rows of `u`'s group on its weight. `m1Domain`: milestone shapes, 64-bit weight ids, `≥ 2^16` rows in every unit's group on its weight (so also on its weight) |
| `rowShare`, `m1Wref`, `m1Omega` | llm-shapes §3, red-team B3 | `rowShare work m_u rows = ⌈work·m_u/rows⌉`. `m1Wref`: `H_ref`'s W1 schedule, `mkn + 16mk (E) + 12mk (pack E) + 4mk (A + E, biased) + 4mk (back to s8) + 16mk (X1) + 96mn (three limb groups) + 32mn (combine)`, plus `u`'s row share of its group's `E_R,g·B′` (`16kn`) and of its weight's `F_L·F_R` and `B + F` (`16kn + 20kn`), and (P7-4) `576m` for the int8 limb split of `X1` plus `u`'s row share of the split of `G_g` (`576n` per group). `Ω_M1 = 65769/65536` |
| `Copy.Adversary`, `classes`, `cost`, `Correct`, `correctSet`, `Nz`, `bits` (`Witness/Copy.lean`) | tt-attacks §6 (R_copy) | a restricted model: unit `u` has `n_u` positions with noise-dependent values; a copy adversary fixes a class per position before the salt, pays 16 per class, and is correct on `u` iff values agree within each class. `Nz`: given its unit's other positions, any set `P` of positions hits targets read from outside `P` with probability `≤ 2^−|P|`. `bits`: `M` independent uniform bits |
| `outputPriced`, `freeModel` (`Witness/Model.lean`) | witnesses only | programs are `QTree`s of (workload, activation input, state, salt); `outputPriced` charges `m·k·n` per committed unit and nothing else; `freeModel` charges nothing. Both are query models |

## 2. Named hypotheses

| Hypothesis | Where | Witness (proved) |
|---|---|---|
| `Assumptions.TT CM P D γ₀ ε` (§4.4): `CM.Queries`, and in the same game `Pr[∑_{u ∈ K′} m·k·n > T/(1 − γ₀)] ≤ ε(q, N)` | (a), (d), (d′), (d″) | `TTWitness`: in `outputPriced`, for `D1.m1` with `W_ref ≥ W_mm`, TT(0.5%) holds with `ε = 0` (`Proofs.tt_outputPriced`: for every protocol) |
| `AdmitsRef CM P D qref`: one program runs `H_ref` at `≤ W_ref` | (d′) | `TTWitness`, second half: `outputPriced` runs `H_ref` at `∑ W_mm ≤ ∑ W_ref` with `N·m1Queries` calls |
| `W_ref ≤ Ω_max·W_mm` on the domain, `Ω_max ≤ 199/198` | (a), (d), (d′), (d″) | `MilestoneWref`: the explicit schedule `m1Wref` meets it at `Ω_M1 = 65769/65536`; `Sanity.milestone_hypotheses_consistent`: at `m1Wref` and `Ω_M1`, together with `AdmitsRef` and TT in `outputPriced`. Whether M_4090 runs `H_ref` within `m1Wref` (`AdmitsRef` at M_4090) is not proved |
| Theorem 1's sampling bound `Pr[accept ∧ ∑_{u∉K} W_ref > ε_s·W] ≤ δ_s` | (b) | proved outright for work-weighted sampling by (c), with `δ_s = (1 − ε_s)^t`; (d) discharges it |
| Theorem 1's `Gγ` | (b) | from TT by (a); witnessed through `TTWitness` |
| `P.NoiseRange` (a property of Π's factor distribution) | (e5), `GameCanBeLost` | `MilestoneInstance`: `D1.m1` has it (noise in `[−48, 48]`); `Proofs.noiseRange_of_factor_bounds`: any factors with `|E_L| ≤ α`, `|E_R| ≤ β`, `|F_L| ≤ α′`, `|F_R| ≤ β′`, `r·α·β ≤ 63` and `r·α′·β′ ≤ 63` |
| `Copy.Nz` (R_copy only) | `CopyBound` | `CopyNzWitness`: independent uniform bits; `Sanity.copy_zero_noise`: constant values fail it, and the bound with them |

No random-oracle or collision-resistance hypothesis appears: TT is stated in the same game as `Gγ`, with the same `q` free oracle calls, so grinding and collisions are inside `ε(q, N)`, and `η = ε_TT` (within §3.3's `η ≤ (q + |U|)·2^-λ + ε_A`, which `ε(q, N)` can now express).

## 3. Pinned statements (`Pouw/Pinned.lean`)

| Pinned | Section | Statement |
|---|---|---|
| `GammaFromTT` (a) | §4.4 Lean split 1 | for every model, protocol, domain: `γ₀ < 1`, `Ω_max > 0`, `W_ref(u) ≤ Ω_max·W_mm(u)` on the domain, and TT(γ₀, ε) give `Gγ` at `γ = 1 − (1 − γ₀)/Ω_max`, `η = ε` |
| `Theorem1` (b) | §3.5 Theorem 1 | `γ < 1`, `Gγ` with `η`, and the sampling bound `δ_s` for an adversary within `(T, q)` give `Pr_{H,s,c}[accept ∧ T < (1 − γ)(1 − ε_s)·W] ≤ δ_s + η(q, N)`; any audit coins independent of `H, s`, any acceptance predicate |
| `WorkWeightedSampling` (c) | §3.5 | `t` samples `∝ w(u)`, accept iff all in `K`: `Pr[accept ∧ ∑_{u∉K} w > ε_s·∑w] ≤ (1 − ε_s)^t` for `ε_s ≤ 1` |
| `EndToEnd` (d) | §2, §3.5, §4.4 Lean split 2 | TT and the `Ω_max` bound give, for every in-domain workload, `T ≥ 0`, `q ≤ 2^64` and adversary: `Pr[accept_t ∧ T < (1 − γ)(1 − ε_s)·W] ≤ (1 − ε_s)^t + ε(q, N)` |
| `MilestoneRequirement` (d′) | §3.3 at the milestone, budget form | for `D1.m1` on `m1Domain`, any model and `W_ref`: `0 < Ω_max ≤ 199/198`, `W_ref ≤ Ω_max·W_mm`, `AdmitsRef` and TT(0.5%, ε) give `Requirement` at `γ = 1 − (199/200)/Ω_max` with `η = ε`, and that `γ ≤ 1%` |
| `MilestoneExhaustion` (d″) | §2 at the milestone | (d) for `D1.m1` on `m1Domain` at `γ = 1 − (199/200)/Ω_max` |
| `GammaBudget` | §4.4 budget | under TT(0.5%), `γ ≤ 1%` iff `Ω_max ≤ 199/198` |
| `Usefulness` (e1) | §4.1 usefulness, §4.4 Lean split 3 | over ℤ, `(A + E_L E_R)(B + F_L F_R) − (A F_L) F_R − E_L (E_R (B + F_L F_R)) = A·B`, all dimensions |
| `Int32Transcript` (e2) | §3.2 exactness | operands in `[−127, 126]`, `k ≤ 133144`: the int32 accumulator equals the exact sum, which is in int32 |
| `NoisedKBound` (e3) | §3.2 exactness | `133144` products of `[−127, 126]` entries always fit int32; `133145` products `(−127)²` do not |
| `Int8KBound` (e3′) | §3.2 | the problem statement's bound checked: `k ≤ 2^17 − 1` suffices for int8, `2^17` products `(−128)²` overflow |
| `Int32Decode` (e4) | §3.2, §4.1 | `H_ref`'s int32 decode (every step wrapping, any integer factors) equals `A·B` for int7 `A`, `B`, `k ≤ 2^19 − 1` |
| `D1Complete` (e5) | §3.2 completeness | D1's `H_ref` is complete on the default domain (`ShapesIn InDefaultDomain`) when noise is in `[−63, 63]` |
| `TTWitness` | hygiene rule | for `D1.m1` with `W_ref ≥ W_mm`: TT(0.5%) with `ε = 0` and `AdmitsRef` (one program, `N·m1Queries` calls) in `outputPriced` |
| `MilestoneInstance` | hygiene rule, red-team B4, B8 | for every `W_ref`: `D1.m1` is a milestone instance (`r = d = 16`, `GroupShared 16`) with `NoiseRange`, `QueryBound m1Queries`, `E_L` queries that no other unit below `2^64` asks, and nonzero noise on an in-domain workload |
| `Proofs.milestoneERSeparated` | red-team phase D, D1 | the `E_R` queries of two (weight, group) pairs with weights below `2^64` and groups below `2^60` meet only if the pairs are equal, so `E_R` is per (epoch, weight, group) by a pinned property, not only by `m1ERQ`'s definition (`GroupShared 16` alone would also hold for an epoch-shared `E_R`) |
| `MilestoneWref` | red-team B3, P7-4 | `W_mm ≤ m1Wref ≤ (65769/65536)·W_mm` on every in-domain unit, `65769/65536 ≤ 199/198`, and `γ = 1 − (199/200)/Ω_M1 = 14017/1644225 ≈ 0.8525%`. With (d′): `AdmitsRef` at `m1Wref` and TT(0.5%) give §3.3's requirement at that `γ` |
| `HonestComplete` | hygiene rule | for complete Π: honest `K = U`, and the honest reference does not win at `T = W`, `0 ≤ γ < 1` |
| `GameCanBeLost` | hygiene rule | every D1 instance with `NoiseRange` and `≤ c` queries per unit (`16c ≤ 2^64`) and `W_ref ≥ Ω·W_mm` on `m1Domain`, `Ω ≥ 1`: in `freeModel`, `Gγ` fails whenever `η(16c, 16) < 1`; in `outputPriced`, it fails for every `γ < 1 − 1/Ω` |
| `CopyBound` | tt-attacks §6 | in R_copy, under Nz, for `0 ≤ γ₀ < 1`: `Pr[∑_{u ∈ K′} 16·N_u > cost/(1 − γ₀)] ≤ ∑_u 2^(−γ₀·N_u)` for every copy adversary |
| `CopyNzWitness` | tt-attacks §6 | Nz holds for `M` independent uniform bits per unit |

Sanity lemmas (degenerate instances and side conditions, `Pouw/Sanity.lean`, all pinned): see the table at the top of that file and `NOTES.md`.

## 4. Simplifications

1. **Ideal commitments.** The online phase outputs the committed values themselves; there is no Merkle tree. Bridge (not formalized; a gap): Merkle binding under a random oracle makes a root determine the opened values except with probability about `q²/2^256`, so an adversary with roots can be turned into one with values. TT is stated in the same ideal game, so the reduction itself needs no bridge; a Merkle version would change TT's game and `ε` equally.
2. **Finite oracle `H : Q → R`**, uniform over all functions; SHAKE256's domain is infinite. With `N ≤ 2^64` the protocol's queries lie in a finite set on the domain, and `D1.m1`'s activation queries are injective in the unit below `2^64`. The noise is any deterministic expansion of `H`'s answers to finitely many queries (`D1.Params`), so XOF-style expansion is `qAct` returning several counter-tagged queries.
3. **Uniform salt** on `S` (the chain's instance is `Fin (2^128)`), rather than any source with 128 bits of min-entropy.
4. **Deterministic adversaries** (see `pr`). Bridge: `Sanity.randomized_of_deterministic` (proved): an adversary with coins independent of `(H, s)`, within `(T, q)` for every coin value, wins with probability at most `η`.
5. **The workload is fixed before `H`**, following the requirement's quantifier order rather than step order 0 then 1 (see Proposed corrections in `NOTES.md`).
6. **Commitments carry `A_u`**, and `H_ref`'s activations are arbitrary int7 matrices (completeness for every input). Both `H_ref` and the adversary receive an activation input read as the units' own operands; the adversary chooses its input, so this adds power to it.
7. **Matrices as functions `ℕ → ℕ → ℤ`**; only entries inside a shape are read. Correctness compares entries inside the shape only.
8. **`W_ref` reads the layout** (shapes and weight ids), not only the unit's shape, so a unit's share of per-epoch work on its weight can be expressed. It never reads input values.
9. **Committed activations must be int7** for a unit to count, in both `K` and `K′`.
10. **Weights sharing an id need not share a shape**: each unit reads its own `k × n` corner. This only enlarges the domain.
11. **Theorem 1 in budget form** (red-team A9): `T` is a budget fixed before the game and the adversary's cost is at most `T` surely. The realized-cost form (abort when the cost would exceed `(1 − γ)(1 − ε_s)·W`, then commit a default transcript) is not formalized: it needs cost monitoring and default commitments to be free in the model, which an abstract `CostModel` does not provide. A gap.
12. **`D1.m1`'s distribution is tt-attacks §4's** (W6 as fixed at 21:18Z), exactly uniform per entry because the answer type is `Fin 7 × Bool`; a byte-oriented XOF would need rejection sampling or a named non-uniform map. Changing it changes `M1.lean` and needs a statement reviewer.
13. **`A_u` enters `E_L`'s queries as its block on `2^17 × 2^16`**, the box holding every in-domain shape, not cut to `m_u` rows. Entries outside the shape are the adversary's to choose and only re-randomize its own `E_L`.
14. **`m1Wref` apportions shared work by rows, rounded up** (`Sanity.rowShare_covers`: the shares cover it). `lone_unit_over_budget`: without the domain's row condition, a lone unit's `m1Wref` exceeds `(199/198)·W_mm`.
15. **`m1Domain` asks for rows, not full groups.** Each unit's group must serve at least `2^16` rows on its weight, which is what bounds the group's share of `E_R·B′`. Draft 3's full groups (16 consecutive indices on one weight, red-team CL1 item 3) are a special case (`Sanity.fullGroups_inDomain`), so every pin over `m1Domain` holds on the full-group domain too.

## 5. What the intended model prices (for M_4090, not formalized)

The Lean leaves `CM.cost` abstract; it reads the program, the state and the inputs. For TT at M_4090 to be plausible, M_4090 must price, besides W1's instruction classes:
- **pre-salt data** at 345 units per byte on first fetch: the state `σ`, declared weights, and **the online program's text** (immediates and constant banks included; a move from an immediate is an instruction of its class). This is red-team W1-1 with tt-attacks H2 and H3.
- **supplied operands only for correct units** (red-team W1-3): the first fetch of a unit's activations `A_u` and of its weight `B_w(u)` is free only if the unit is correct; every other first fetch of a supplied or pre-salt byte costs 345. `AdmitsRef`'s `∃ prog ∀ U ∀ act` makes the activations an input of `run`, so the honest reference reads them free and its program text holds no operands.
- atomics, reductions and warp reductions as INT32 instructions per lane operation, and a load address as one register plus an immediate (tt-attacks H1).
- **data-dependent accesses and control** (tt-attacks H5, the coordinator's 22:20Z entry, draft 3 §3.1): a memory access or shuffle whose address depends on data (the salt, the noise, the inputs, or anything computed from them), and a branch or predicate that depends on data, costs one INT32 instruction (16) per lane. Oblivious online traffic stays free. Without this, byte stores and keyed reloads evaluate any function for free and TT is false for every Π. `D1.m1`'s dense `H_ref` is oblivious: fixed addresses, immediate PRMT selectors, and arithmetic noise expansion (`a − 3`, `2b − 1`), so `m1Wref` gains no term.
- **sub-word extraction at 16 per word produced** (Daniel, 28 Sep 03:35Z), like PRMT. This prices the int8 limb split of `X1` and of `G_g`, which `m1Wref` counts since P7-4 (`internal/pouw/new-crypto/barrier.md`).
- queries through `QTree` only (`CostModel.Queries`, part of TT).

Excluding texture filtering and b1 `mma` from the priced instructions is a named modelling assumption of M_4090 (red-team W1-4), until they are measured and priced.

The `barrier` worker's `M4090` (§11) makes W1 precise for NCP's checked words, in draft semantics (S-1 to S-11, pending Daniel). It covers predication but not data-dependent branching (gap G-branch). The proposed W1 amendment for branching, pending Daniel, is in `ASSUMPTIONS.md`.

## 6. What is not modelled

M_4090's instruction set as a `CostModel` (deliberately; it is one `CostModel`, and the `barrier` worker's `M4090` of §11 is a `Machine` on the noise grid for NCP's words, not a `CostModel` of this game); the Merkle tree; the verifier's cost; attribution; capacity. `m1Wref` is a count of `H_ref`'s schedule, but that M_4090 runs the schedule at that count (`AdmitsRef`) is not proved: it needs M_4090.

## 7. The `barrier` worker's `Pouw.Dimension` pins (28 Sep 06:00Z and 06:53Z)

The `barrier` worker added these 30 pins; the models, proofs and records are in `internal/pouw/new-crypto/barrier.md`, sections "The mixing lemma and `TT_NCP_of_A1_A2`" and "`A1_cost` in the closed scalar pipe". Its other pins (`Pouw.Barrier`, `Pouw.NCP` and Theorem D's 15 in `Pouw.Dimension`) are described there too. Notation: `D = |U|·m·n·(3k/16 − 1)` is the number of non-final checked words of the units `U` sharing `F₁`; `V₀` is the free values (constants, noise coordinates, every function of `F₁`); "independence" is `CheckpointIndependent k 16 R`; the named assumptions are in `ASSUMPTIONS.md`.

Two later changes apply to these rows, and neither changed a pin record:
- **P9B-1 (08:31Z).** Every A2 hypothesis below takes the target set W = the non-final checked words (`wordSet`), and each A2 witness holds for every W. The 13 definitions that gained W were confirmed by the red team as named statement reviewer (Phase 12).
- **P11-1 (08:29Z).** `A1_cost`, `A1_cost_quad`, `A1_nonquad`, `LiftMinRank` and `LiftMinRankL5e` moved to the assumptions module `Pouw.Dimension.PipeAssumptions`, with the same names and digests, and `liftMinRankWitness` is now stated in `Pipe`.

**06:00Z, 18 pins: AlgM_4090 and the mixing lemma, causal inputs, the lifting node.**

| Pin | Statement |
|---|---|
| `mixingLemma` | Under independence, a program in AlgM_4090 (every priced instruction costs at least 16, or is a product of two free values costing at least `c_s`) that outputs the words has `dim T = D`, cost `≥ 16·#B + c_s·#R`, `#B ≥ D − dim W` and `#R ≥ L(W)`, where `W = T ∩ (span R ⊔ V₀)` |
| `algBound4090` | With A1(c, γ₁), `c·c_s ≥ 16` and `0 ≤ γ₁ ≤ 1`, such a program costs at least `16·(1 − γ₁)·D` |
| `ttNCPOfA1A2` | A2(γ₂) into AlgM_4090, A1(c, γ₁) with `c·c_s ≥ 16`, and `1 − γ₀ ≤ (1 − γ₂)(1 − γ₁)(1 − 16/(3k))` make TT_NCP's event impossible for the machine's program |
| `ttNCPOfA1A2W1` | The same at `c = 2`, `c_s = 8`, with A1 as `A1_W1` (not used by the recommended chain) |
| `alg4090Witness` | For every `k ≥ 1024` with `16 ∣ k`, some admissible independent `R` has an AlgM_4090 program at `c_s = 8` with one product that outputs the words at cost `16·D + 8` |
| `a2Witness4090` | AlgM_4090 itself, as a machine, satisfies A2(0) into AlgM_4090 for every target set (a trivial model) |
| `a1W1Witness` | `A1_W1 γ₁ k R` holds for every `k` and `R` once `γ₁ ≥ 1/2` |
| `minRank2Witness` | For every `k ≥ 1024` with `16 ∣ k`, the shift by 24 is admissible, independent and has MinRank ≥ 2 |
| `algBoundCausal` | Theorem D with causal inputs (P7-1): `A_u` may read `F₁` and the `E₁` of earlier units, and the bound `16·D` is unchanged |
| `causalWitness` | `A_u = E₁` of unit `u − 1` (`A_0 = 0`) is causal, so the hypothesis admits real dependence on earlier noise |
| `algWitnessCausal` | For every causal `A`, some admissible independent `R` has a program costing exactly `16·D` that outputs the causal words |
| `liftMinRankWitness` | `LiftMinRank ρ ε k R` holds at `ε = 1` (trivial; the content is `ε` small) |
| `minRankGeWitness` | For every `k ≥ 1024` with `16 ∣ k`, some admissible independent `R` has `MinRank2` (MinRank ≥ 2) and `MinRankGe k R 1` |
| `liftMinRankL5eWitness` | `LiftMinRankL5e`'s hypotheses hold together (`ρ = G = Λ = 1`), and `epsL5e` is at least 1 at every saving `d ≤ 0` and at most 1 at every `d ≥ 0` |
| `Lifting.card_le_pow_of_sub_mem` | L3: over any field, points with coordinates in a finite set `G` and pairwise differences in a subspace of rank at most `n` number at most `(#G)^n` |
| `Lifting.grid_card` | The noise grid `{−31, …, 32}` has 64 elements |
| `Lifting.solutions_card_le` | L4's counting core: grid solutions of `A·x = y` number at most `64^(#ι − rank A)` |
| `Lifting.slice_card_le_of_subspace` | L2 with L3: grid points on which every functional of a subspace `W` is constant number at most `64^(#ι − dim W)` |

**06:53Z, 12 pins: `A1_cost` in the closed scalar pipe (no free instructions; every priced instruction costs at least 16 or is an FP32 step `a·b + c` on free values and earlier FP32 outputs costing at least `c_s`).**

| Pin | Statement |
|---|---|
| `algBoundPipe` | Under independence and MinRank ≥ 5, a closed-pipe program on inputs in `V₀` that outputs the words costs at least `16·(1 − γ)·D`, given `A1_cost(c, γ)` and `c·c_s ≥ 16` |
| `algBoundQuad` | The same for quadratic pipes, given `A1_cost_quad` |
| `ttNCPOfA1costA2` | A2(γ₂) into the closed pipe at `c_s = 8`, `A1_cost(2, γ₁)`, independence, MinRank ≥ 5 and `1 − γ₀ ≤ (1 − γ₂)(1 − γ₁)(1 − 16/(3k))` make TT_NCP's event impossible |
| `ttNCPOfQuadA2` | The same with A2 into the quadratic pipe and `A1_cost_quad(2, γ₁)`. Theorem 1 is now in Lean (`Forest.a1CostQuadHolds`, §8), and `Forest.ttNCPQuadOfA2` states the form at `γ₁ = 0`, which assumes only A2 |
| `a1CostOfSplit` | `A1_cost_quad` and `A1_nonquad` together give `A1_cost` |
| `minRankGeShift16` | The shift by 24 has MinRank ≥ 16 (the maximum) for every `k ≥ 1024` with `16 ∣ k` |
| `minRankGeFacts` | `MinRankGe` is monotone in `ρ`, and MinRank ≥ 2 in that form gives the older `MinRank2` |
| `pipeWitness` | Some admissible independent `R` with MinRank ≥ 16 has a quadratic-pipe program with one FP32 step that outputs the words at cost `16·D + 8` |
| `a2WitnessPipe` | The closed pipe, as a machine, satisfies A2(0) into itself for every target set (a trivial model) |
| `a2WitnessQuad` | The quadratic pipe, as a machine, satisfies A2(0) into itself for every target set (a trivial model) |
| `a1CostWitness` | `A1_cost`, `A1_cost_quad` and `A1_nonquad` all hold at `c = 2`, `γ = 1/2`, for every `k` and `R` |
| `pipeChainConsistent` | The hypotheses of `ttNCPOfA1costA2` and of `ttNCPOfQuadA2` hold together at every `k ≥ 1024` with `16 ∣ k` (`γ₂ = 0`, `γ₁ = 1/2`, `γ₀ = 3/4`) |

## 8. Theorem 1 in Lean, and A2 on the checked words (28 Sep 07:58Z to 09:07Z)

The `barrier` worker added these 16 pins, in `Pouw.Dimension.Forest` (trusted; proofs in `ForestProofs.lean`), `Pouw.Dimension.A2Words` (trusted; `A2WordsProofs.lean`) and `Pouw.Dimension.Pipe`. The models, proofs and records are in `internal/pouw/new-crypto/barrier.md`, from the section "The audit-tool switch and Theorem 1 in Lean" on. None of them takes an A1 assumption.

**Theorem 1 of `a1-cost` is proved in Lean, in full.** It is proved on the grid, at MinRank ≥ 5, which `A1_cost_quad` already assumes. So `A1_cost_quad 2 0` is proved rather than assumed, and for the quadratic closed pipe TT_NCP follows from A2 alone (`ttNCPQuadOfA2`). The model follows `a1-cost.md` §3.2–3.3, with red-team P8-1 (additions priced) and P8-2 (products of free values). Two terms used below:
- An *atom* is the Q-part of a product of two free values, where a Q-part is a function of the noise modulo `V₀`.
- The *two-atom property* (`TwoAtomFree`) says that no nonzero element of the words' span modulo `V₀` is a sum of two atoms. It is the rank ≥ 3 condition.

**07:58Z, 7 pins (`Forest`; red team: all GRANTED, Phase 11).**

| Pin | Statement |
|---|---|
| `Forest.forestBound` | The forest count, abstract. Take values in a finite-dimensional ℚ-space whose FP32 steps are merge-free and whose other values are priced. If the atoms are closed under scaling and have the two-atom property for a subspace `Z`, then `2·d ≤ 2·#priced + #FP32`, where `d` is the dimension of the values' span in `Z`. With no priced values this is Theorem 1, `#FP32 ≥ 2·d` |
| `Forest.gridTwoAtom` | Under independence and MinRank ≥ 5, the non-final checked words modulo `V₀` have the two-atom property, for every `A = g(F₁)`, `B` and unit set |
| `Forest.a1CostQuadHolds` | `A1_cost_quad 2 0 k R` holds for every `k` and `R`: Theorem 1 on the grid, exactly as the 06:53Z pins use it |
| `Forest.a1CostOfNonquad` | `A1_nonquad 2 0 k R` alone gives `A1_cost 2 0 k R` |
| `Forest.algBoundQuad8` | Theorem D for the quadratic closed pipe at `c_s = 8`, with no A1. Under independence and MinRank ≥ 5, every `QuadPipe 8` program on inputs in `V₀` that outputs the non-final checked words costs at least `16·D` |
| `Forest.ttNCPQuadOfA2` | TT_NCP from A2 alone, into the quadratic closed pipe. A2(γ₂) into `QuadPipe 8` on the words, independence, MinRank ≥ 5 and `1 − γ₀ ≤ (1 − γ₂)(1 − 16/(3k))` make TT_NCP's event fail |
| `Forest.quadChainConsistent` | `ttNCPQuadOfA2`'s hypotheses hold together at every `k ≥ 1024` with `16 ∣ k` (the shift by 24, `quadMachine`, `γ₂ = 0`, `γ₀ = 1/2`). They hold only through the model's own machine, and the pin says nothing about a real one (red-team P11-2) |

**08:31Z, 5 pins: A2 on the checked words (P9B-1), and Theorem 1 for any word family (red team: all GRANTED, Phase 12).**

| Pin | Statement |
|---|---|
| `A2Words.a2ExtraOutputs` | If a machine satisfies A2(γ₂) into a class for the target set `W`, then the same machine with extra outputs outside `W`, at the same cost, satisfies it too |
| `A2Words.a2WitnessExtra` | `extraMachine` is the quadratic-pipe machine with every function outside the words added as an extra output. It satisfies A2(0) into `QuadPipe` for the words. Yet none of its programs has all of its outputs among the slots of any program, of any class and at any cost |
| `Forest.theorem1Family` | Theorem 1 for any word family: if the family's non-final values are linearly independent modulo `V₀` and have the two-atom property, then every quadratic closed pipe that outputs `|S|` of them has at least `2·|S|` steps |
| `Forest.gridNear` | Under independence and MinRank ≥ 5, every family `w` with `w − word ∈ V₀` at each non-final position has both of those properties |
| `Forest.a1CostQuadNear` | Theorem 1 therefore holds for every family within `V₀` of the words. `a1CostQuadHolds` is its instance at `w = word`, and route U's `a1CostQuadUHolds` (§9) is its instance at `wordU` |

**08:53Z and 09:07Z, 4 pins (red team: all GRANTED, Phase 13).**

| Pin | Statement |
|---|---|
| `Forest.quadChainConsistentTight` | `ttNCPQuadOfA2`'s hypotheses hold together at `γ₂ = 0` and the tight `γ₀ = 16/(3k)`, with equality in the arithmetic hypothesis (P11-2) |
| `pipeWordWitness` | For every `k ≥ 1024` with `16 ∣ k` and every unit `u₀`, the shift by 24 (admissible, independent, MinRank ≥ 16) has a `QuadPipe 8` program that outputs the words at cost `16·D + 128`. Its 16-step FP32 chain computes `u₀`'s depth-16 checked word, which lies outside `V₀` (P9B-3) |
| `A2Words.emptyQuadPipe` | The empty program is a `QuadPipe cs` program at every shape and every `cs` |
| `A2Words.a2Separation` | `extraMachine` meets the restricted A2(0) into `QuadPipe cs` on the words, and fails the unrestricted A2 (target `Set.univ`) at every γ₂ and into every class (P12-1). So the restriction is strict |

## 9. Route U (28 Sep 09:21Z; approved (red team, Phase 13))

**The decision.** The coordinator decided at 07:40Z, with the red team (Phase 10), that NCP's checked values are route U's accumulator (`internal/pouw/new-crypto/route-u-checkpoints.md`):
- `C^U_t = c₀ + Σ_{l < 16t} (X + β)·Y mod 2^32`, with `c₀ = −β·colsum(Y)`. The final value is `A·B`.
- The bias β is a parameter, with the hypothesis that `X + β` stays in u8. The first build (ncp-v1) uses β = 128; C2's β = 129 needs a permutation-matrix `R`.
- The named conjecture is `TTNCP_U β` (`Pouw/NCP/RouteUAssumptions.lean`), which is `TTNCP` over route U's checked values.

**The unbiased form is retired but kept.** The unbiased `TTNCP` (`Pouw/NCP/Assumptions.lean`) is retired for NCP's checked values, and it stays in the package. Its pins (`gammaFromTTNCP`, `ttncpWitness`, `leadWitness`, `leadIndWitness`) and the unbiased word floors are the historical form. The unbiased Dimension results remain the base that route U's transfer reads (`wordUSubV0`, `a1CostQuadNear`).

The route-U worker (bc-3647f503) added these 55 pins in `Pouw.NCP.RouteU*` and `Pouw.Dimension.RouteU*`. Its definitions, findings and proposed ledger rows are in `internal/pouw/new-crypto/route-u/README.md`. The `--update` review printout is `route-u/review-integration.txt`: 55 new pins and 77 new definitions, and no existing record or digest changed.

**Every route-U pin below is approved (red team, Phase 13).** The red team granted all 55 as named statement reviewer at 09:50Z (`red-team.md`), and found that nothing existing changed. Every statement holds for every β, and for every forming count `f`, unless it states a range. `wordU β` is route U's checked word as a function of the noise.

**`Pouw.NCP.RouteUProofs`, 17 pins: values, ranges, the int32 reading, protocol and game.**

| Pin | Statement |
|---|---|
| `checkedU_eq` | The shift identity: for `16t ≤ 3k`, `C^U_t = C_t − β·s_t`, where `s_t` is the suffix column sum of `Y` from `16t` |
| `checkedU_final` | With `16 ∣ k`, the last checked value `C^U_{3k/16}` is `A·B` |
| `biasU8Iff` | On the int7 domain, `X + β` stays in u8 exactly for β ∈ {127, 128, 129} when `R` is a permutation matrix, and exactly for β ∈ {127, 128} when `R` is a signed permutation |
| `rangeU` | For `127 ≤ β ≤ 129` and a permutation matrix `R`, with noise in `[−31, 32]` and int7 `A`, `B`, `X + β` is u8 and `Y` is s8 |
| `mmWU_eq` | Route U's int32 accumulator is its running value mod `2^32` at every depth |
| `wrapU` | For int7 `A`, `B`, `16 ∣ k` and `k ≤ 2^19 − 1`, the accumulator at the last checkpoint is `A·B`, and so is the signed reading of the last checked value |
| `int7Int32U` | For `127 ≤ β ≤ 129`, a signed permutation and `k ≤ 2^15`, the running value is int32 at every depth (at most `49,149·k` in magnitude) |
| `int7Int32UUnsigned` | The same for a permutation matrix at `k ≤ 2^16` (at most `29,856·k`) |
| `mmWUExact` | In those two ranges, the int32 accumulator equals the running value over ℤ at every depth `τ ≤ 3k` |
| `leadCompleteU` | Route U's protocol `P.toProtocolU β` is complete on `leadDomain` |
| `yuChecked` | At `d = 16` and `16 ∣ k`, the protocol's checkpoint `t` is `wrap32 (checkedU β (t + 1))` |
| `ttncpUIff` | `TTNCP_U β CM P D γ₀ ε` is exactly `TTNCP CM (P.toProtocolU β) D γ₀ ε` |
| `gammaFromTTNCP_U` | TTNCP_U(γ₀), `W_ref = wrefU f = 3·m·k·n + f·m·k`, `γ₀ < 1` and at least `n₀ > 0` columns per unit on the domain give `Gγ` for route U's protocol at `γ = 1 − (1 − γ₀)/(1 + f/(3n₀))`, `η = ε` |
| `gammaFromTTNCP_U_v1` | The ncp-v1 instance, β = 128 and `f = 24`: `γ = 1 − (1 − γ₀)/(1 + 8/n₀)`, which is 0.995% at `γ₀ = 0.5%` and `n₀ = 1,600` |
| `gammaFromTTNCP_U_C2` | The C2 instance, β = 129 and `f = 20`: `γ = 1 − (1 − γ₀)/(1 + 20/(3n₀))`, which is 0.913% there |
| `ttncpUWitness` | For `0 ≤ γ₀ < 1` and `W_ref ≥ 3·W_mm`, TTNCP_U(γ₀) with error 0 and `AdmitsRef` hold together in the output-priced model at `3·m·k·n` |
| `leadUWitness` | `gammaFromTTNCP_U`'s hypotheses hold together at an `IsLead` instance with `W_ref = wrefU f`, whose `R` is a permutation matrix, so the witness also lies in C2's range |

**`Pouw.NCP.RouteUWordProofs`, 6 pins: the word layer.**

| Pin | Statement |
|---|---|
| `reductionOnlyIfU` | If a rule holds for every noise on route U's values at a position, the unbiased coefficients satisfy `Relation.ReductionOnlyIf`'s conclusion. The shift reads no `E₁`, so the four-point mixed difference drops it |
| `ncpFinalOnlyIndU` | Under independence, each unit has at most `m·n` identity positions on route U's values (the final ones) |
| `ncpWordFloorIndU` | Under independence and `NzNCP` of route U's values (its own hypothesis), `pr(cost/(1 − γ₀) < 16·Σ_{u correct} positions) ≤ N·2^(−mn·(γ₀·3k/16 − 1))` |
| `int7Int32UPos` | For `127 ≤ β ≤ 129` and int7 inputs, every route-U checked value is int32, for a signed permutation at `k ≤ 2^15` or a permutation matrix at `k ≤ 2^16` |
| `wrapFinalOnlyIndU` | `ncpFinalOnlyIndU` for the protocol's wrapped values `wrappedU β`, given that the checked values are int32 |
| `wrapWordFloorIndU` | The floor for `wrappedU β`, given the int32 fact and `NzNCP` of the wrapped values |

**`Pouw.Dimension.RouteUProofs`, 32 pins: the dimension chain on route U, with the same bounds.** The shift `β·s_t` lies in `V₀` whatever β is, so everything proved modulo `V₀` transfers.

| Pin | Statement |
|---|---|
| `wordUSubV0` | At every position, `wordU β − word ∈ V₀` |
| `wordCUSubV0` | The same with causal inputs |
| `combUV0Iff` | A combination of non-final route-U words lies in `V₀` iff the same combination of unbiased words does |
| `indepModShift` | Generic: if `t′ i − t i ∈ V` for every `i`, independence modulo `V` passes from `t` to `t′` |
| `indepModU` | Under independence, route U's words are linearly independent modulo `V₀` |
| `secondDifferenceU` | If a combination of non-final route-U words lies in `V₀`, its coefficients on each entry's checkpoints annihilate the (unbiased) checkpoint matrices |
| `pricedCountU` | `PricedCount` for route-U words |
| `algBoundU` | Theorem D on route U: under independence and H16, a program on inputs in `V₀` that outputs the route-U words costs at least `16·D` |
| `algSharpU` | Theorem D on route U is sharp: below `γ₀ = 16/(3k)` some H16 program outputs the route-U words and TT_NCP's event holds for it |
| `ttNCPAlgU` | TT_NCP in AlgM_16 on route U (`TTNCPAlg` for route-U words) |
| `ttNCPOfA2U` | TT_NCP from A2 into AlgM_16, for a machine program that outputs route-U words, with A2 on the route-U words |
| `algBoundCausalU` | Theorem D with causal inputs on route U |
| `mixingLemmaU` | The mixing lemma on route U, with `T` the span of the route-U words |
| `algBoundWrappedU` | The `16·D` bound for route U's protocol words mod `2^32`, at `127 ≤ β ≤ 129`, a signed permutation and `k ≤ 2^15` |
| `algBoundWrappedUUnsigned` | The same for a permutation matrix at `k ≤ 2^16` |
| `a1U` | A1(c, γ₁) on the unbiased span gives the same inequality for every subspace of the route-U span, because `T ⊔ V₀ = T^U ⊔ V₀` |
| `algBound4090U` | Theorem D in AlgM_4090 on route U, with the same A1 and the same bound |
| `ttNCPOfA1A2U` | `ttNCPOfA1A2` for route-U words |
| `ttNCPOfA1A2W1U` | `ttNCPOfA1A2W1` for route-U words (`A1_W1`; not used by the recommended chain) |
| `algBoundPipeU` | `algBoundPipe` for route-U words, given `A1_cost_U` |
| `algBoundQuadU` | `algBoundQuad` for route-U words, given `A1_cost_quad_U` |
| `ttNCPOfA1costA2U` | `ttNCPOfA1costA2` for route-U words, given `A1_cost_U` |
| `ttNCPOfQuadA2U` | `ttNCPOfQuadA2` for route-U words, given `A1_cost_quad_U` |
| `a1CostQuadUHolds` | Theorem 1 on route U: `A1_cost_quad_U β 2 0 k R` holds for every β, `k` and `R` (from `Forest.a1CostQuadNear` with `wordUSubV0`) |
| `algBoundQuad8U` | Under independence and MinRank ≥ 5, a `QuadPipe 8` program on inputs in `V₀` that outputs the route-U words costs at least `16·D`, with no A1 |
| `ttNCPQuadOfA2U` | TT_NCP from A2 alone, into `QuadPipe 8`, on route U: A2(γ₂) on the route-U words, `16 ∣ k`, independence, MinRank ≥ 5 and `1 − γ₀ ≤ (1 − γ₂)(1 − 16/(3k))` make the event fail |
| `algWitnessU` | For every `k ≥ 1024` with `16 ∣ k`, some admissible independent `R` and some H16 program output the route-U words at cost exactly `16·D` |
| `alg4090WitnessU` | The same in H4090 at `c_s = 8`, with one product, at `16·D + 8` |
| `algWrappedWitnessU` | For `127 ≤ β ≤ 129` and `1024 ≤ k ≤ 2^16`, a permutation-matrix, admissible, independent `R` with int7 inputs attains `algBoundWrappedU`'s bound |
| `a1CostWitnessU` | `A1_cost_U` and `A1_cost_quad_U` hold at `c = 2`, `γ = 1/2` for every `k` and `R` |
| `pipeWitnessU` | Some admissible independent `R` with MinRank ≥ 16 has a quadratic-pipe program with one FP32 step that outputs the route-U words at `16·D + 8` |
| `pipeChainConsistentU` | The hypotheses of `ttNCPOfA1costA2U` and of `ttNCPOfQuadA2U` hold together at every `k ≥ 1024` with `16 ∣ k` |

## 10. The open quadratic pipe (28 Sep, integrated 09:49Z; approved (red team, Phase 14))

The `barrier` worker added these 9 pins in `Pouw.Dimension.OpenPipe` (trusted; proofs in `OpenPipeProofs.lean`), from red-team R11-1. The model, proofs and records are in `internal/pouw/new-crypto/barrier.md`, sections "R11-1: the open quadratic pipe" and "R11-1 integrated". None of the 9 takes a named assumption.

**The model.** `OpenQuadPipe pb cs` has no free instruction. Each priced instruction is one of two kinds:
- **big**: price at least `pb`, computing any function of the noise;
- **an FP32 step**: price at least `cs`, computing `a·b + c` over every earlier priced value.

So the addend, or a factor whose partner is a constant, may be any earlier priced value: a tensor-core word, an INT result, a priced load or an FP32 output. A product of two non-constant factors must still multiply two free values, so the pipe stays quadratic. `openMachine` is the machine of these programs, and W1 is `pb = 16`, `cs = 8`.

The result: FP32 steps may read tensor-core and INT outputs, and Theorem D still gives `16·D` with no A1.

| Pin | Statement |
|---|---|
| `OpenPipe.quadToOpen` | Every `QuadPipe cs` program is an `OpenQuadPipe 16 cs` program |
| `OpenPipe.a2QuadToOpen` | A2 into `QuadPipe cs` gives A2 into `OpenQuadPipe 16 cs`, at the same γ₂ and target set |
| `OpenPipe.theorem1Open` | Take a word family with the two-atom property and independence modulo `V₀`. Every `OpenQuadPipe pb cs` program on inputs in `V₀` whose slots include the family's values at `S` costs at least `min(pb, 2·cs)·|S|` |
| `OpenPipe.algBoundOpenQuad` | Theorem D in the open pipe, with no A1. Under independence and MinRank ≥ 5, an `OpenQuadPipe pb cs` program on inputs in `V₀` that outputs the non-final checked words costs at least `min(pb, 2·cs)·D` |
| `OpenPipe.algBoundOpenQuad8` | The same at W1's prices: `16·D` |
| `OpenPipe.ttNCPOpenQuadOfA2` | TT_NCP from A2 into `OpenQuadPipe 16 8` on the words, with no A1: if `1 − γ₀ ≤ (1 − γ₂)(1 − 16/(3k))`, TT_NCP's event fails |
| `OpenPipe.openQuadChainConsistent` | Its hypotheses hold together at `γ₂ = 0` and `γ₀ = 16/(3k)`, with `openMachine`, for every `k ≥ 1024` with `16 ∣ k` |
| `OpenPipe.openPipeWitness` | For every `k ≥ 1024` with `16 ∣ k` and every unit `u₀`, the shift by 24 comes with an `OpenQuadPipe 16 8` program that is not a `ClosedPipe 8` one. The program is the honest one plus one FFMA, which adds `u₀`'s depth-16 checked word (a tensor-core output) to a product of two noise coordinates. It outputs the words at `16·D + 8` |
| `OpenPipe.a2WordsIff` | Assume independence, MinRank ≥ 5 and `γ₂ ≤ 1`. Then words-only A2(γ₂) into `QuadPipe 8`, and into `OpenQuadPipe 16 8`, are each equivalent to the per-word cost `PerWordCost γ₂ M`: every program of `M` that outputs the checked words at `S` costs at least `(1 − γ₂)·16·|S|` |

## 11. The M4090 embedding (28 Sep 11:15Z to 12:20Z; approved (red team, Phase 15))

The `barrier` worker added these 14 pins, in `Pouw.Dimension.Embed` (trusted; proofs in `EmbedProofs.lean`) and the assumptions module `Pouw.Dimension.EmbedAssumptions`. The sources are `internal/pouw/new-crypto/barrier.md`, from the section "M4090 and the embedding theorem" on, and the design note `internal/pouw/new-crypto/barrier-assets/embed/DESIGN.md`.

**Every pin below is approved (red team, Phase 15)**, as named statement reviewer, together with the definitions they read: `M4090`, `NaNGap`, `CanonicalNaN`, the FP32 class and the pricing table (`red-team.md`, 12:57Z). Every statement is in **draft semantics: S-1 to S-11 are pending Daniel's review** (`DESIGN.md` §5).

**The machine.** `M4090 fpSem` is W1 made precise. It is a straight-line SSA machine on the noise grid:
- registers hold functions of the noise (the int32 reading), every register is an output, and the inputs are the noise coordinates;
- `mma` costs at least 16 per register written and computes any functions;
- `fp32 κ` costs 8 and computes `fpSem κ` of three registers; the FP32 class is exactly FFMA, FADD and FMUL with their operand modifiers;
- `int`, `dd` (H5) and `subword` cost 16 and compute any function; FSEL, SEL, FMNMX, F2FP, I2FP, the half2 family and FSET (measured at 16 in Round 6, `gpu-constants.md` §11) are `int`;
- `move` costs 0 and is a copy;
- `presalt` (1380) and `operand` (0) are values in `V₀`.

The FP32 semantics `fpSem` is a parameter. The rule is that `M4090` may under-price W1 but never over-price it. What it does not cover is listed as named gaps in `DESIGN.md` §6: G-branch, G-wrap, G-grid, G-fp, G-price, G-hash, G-causal, G-concurrency and G-complete, the last being that real SASS maps to `M4090` (an informal claim).

**The residual.** TT_NCP's per-word form for `M4090` is equivalent to `A1_fp` (`embedM4090`, `a1fpIff`), a statement about FP32-only pipes on the checked words (`ASSUMPTIONS.md`). The FP32 pipe `FpPipe fpSem` has no free instruction. Each priced instruction is big (at least 16, any function) or one FP32 operation of free or earlier values (at least 8).

| Pin | Statement |
|---|---|
| `Embed.embedM4090` | Every well-formed `M4090` program on inputs in `V₀` maps to an `OpenQuadPipe 16 8` program whose slots contain every register outside `V₀`, at cost at most the original plus `8·nonQuad`, where `nonQuad` counts the FP32 instructions that are not quadratic steps |
| `Embed.embedFp` | The same into the FP32 pipe `FpPipe fpSem`, with no exception, at no greater cost |
| `Embed.perWordM4090` | Under independence and MinRank ≥ 5, a program whose registers include the checked words at `S` has `16·|S| ≤ cost + 8·nonQuad`. So a program without non-quadratic FP32 instructions pays 16 per word, with no A1 and no A2 |
| `Embed.a1fpIff` | For each instance, `A1_fp(fpSem, γ)` is equivalent to `PerWordCost γ (M4090 fpSem)`, the per-word form of TT_NCP's conclusion for `M4090` |
| `Embed.perWordOfA1fp` | `A1_fp` gives `M4090`'s per-word cost |
| `Embed.ttNCPM4090OfA1fp` | `A1_fp` makes TT_NCP's event fail for `M4090`, through `a2WordsIff` and `ttNCPOpenQuadOfA2` |
| `Embed.a1fpHalf` | `A1_fp fpSem (1/2)` holds for every `fpSem`, because each word is a distinct priced slot costing at least 8 |
| `Embed.a1fpFadd` | `A1_fp faddSem 0`: the γ = 0 witness for FADD-only semantics, since an FADD step is the quadratic step `1·x + y` |
| `Embed.m4090ChainConsistent` | The chain's hypotheses hold together at the tight `γ₂ = 0` and `γ₀ = 16/(3k)`, with `M4090 faddSem` |
| `Embed.canonicalNaNSat` | `CanonicalNaN (canonNaN fpSem)` holds for every `fpSem`, where `canonNaN` maps range-gap outputs to `0x7FFFFFFF` |
| `Embed.a1fpOnRangeGap` | Under independence, if at some grid point each non-final checked word takes a value `fpSem` never outputs, then `A1_fp` holds at γ = 0 on that instance |
| `Embed.perWordM4090Gap` | With the same range gap, every well-formed `M4090` program pays 16 per checked word, with no A1, no A2 and no MinRank |
| `Embed.ttNCPM4090NanGap` | Assume `CanonicalNaN` and independence, on an instance where each non-final checked word takes a `NaNGap` value somewhere on the grid. Then TT_NCP's event fails for every `M4090` program that outputs the words, at `1 − γ₀ ≤ 1 − 16/(3k)`. It needs no `A1_fp`, no A2 and no MinRank |
| `Embed.nanGapConsistent` | Such instances exist at every `k ≥ 1024` with `16 ∣ k`, for every shape and unit set. Take `A = −2` in column 0 and `B = 1` in row 0: every non-final checked word is −2 or −4 at the zero noise. With the shift by 24, `canonNaN fpExact` and a program that outputs the words, all of `ttNCPM4090NanGap`'s hypotheses hold at the tight `γ₀ = 16/(3k)` |

The NaN-gap route is not universal. In the red team's example, int7 `A = B = 63` keeps the first `k/16` checkpoints' words positive, and a miner chooses its workload. On such instances `A1_fp` stays the open residual.

## 12. The FP8 atom model (28 Sep 22:25Z; R1 passed (red team, 29 Sep 00:15Z), its condition F1 closed by Round 11 (04:02Z); `conformance` and `addConformance` revised 29 Sep 01:10Z, granted by R1 (bc-1114588c, 01:39Z))

The Lean worker (bc-5382063c) added these 12 pins in `Pouw.Fp8Atom`, as M1 of `internal/pouw-fp8/lean-atom-plan.md`.
- **Trusted files:** `Pouw/Fp8Atom/E4M3.lean`, `Atom.lean`, `Fp32.lean` and `Pinned.lean`, and the generated vectors `Pouw/Fp8Atom/Vectors*.lean`, which come from `scripts/fp8atom_vectors.py`. `scripts/fp8atom_cover.json` selects which of its vectors the kernel pins.
- **Proofs:** `Proofs.lean`, `Fp32Proofs.lean`, and the generated `Checks*.lean` (`decide +kernel`, no `native_decide`).
- **The bulk test** (compiled evaluation, not a proof): `PouwBulk.lean`, exempt in `lean-audit.json`. `check.sh` checks `conformance/SHA256SUMS`, then runs it on `conformance/steps.txt.gz` (the 10,549 generated steps and R1's 166,000 differential steps) and `conformance/adds.txt.gz` (the 5,000 adds). It evaluates the two pins' own predicates on every line, and `check.sh` fails unless all 176,549 steps and 5,000 adds hold.
- **The model, conformance and findings** are in `internal/pouw-fp8/lean-atom-m1.md`.
- **The `--update` review printout** is `internal/pouw-fp8/lean-atom-m1-review.txt`: 12 new pins with every definition they read. No existing record or digest changed. The 01:10Z revision's printout is `internal/pouw-fp8/lean-atom-check-cost-update.txt`: no pin record changed, but the definitions `conformance` and `addConformance` read did.
- **None of the 12 takes a named assumption.**

**R1 passed the model and all 12 statements** (red team, 29 Sep 00:15Z, `internal/pouw-fp8/lean-atom-r1-review.md`), with one condition, F1: the silicon link for the instruction form H-1T issues (m64n128k32, scale-d = 0, both operands from shared memory, then `add.rn.f32`). **F1 is closed** (Round 11, 29 Sep 04:02Z, run `r20260929-033625-cb6e`; `internal/pouw-fp8/genuine-fp8-interface.md`, 04:02Z): all 4,915,200 captured words (C1, C4, C2) match `verity.ml.tc`. The fixtures are `art:a517c213…` (raw) and `art:5abb7c95…` (decode and golden). R1 reviewed `conformance` and `addConformance` on the 10,549 steps and 5,000 adds. Their 01:10Z covers are R1's F5 with the Lean worker's fine cover added. **R1, their named statement reviewer, granted both changed records** (bc-1114588c, 29 Sep 01:39Z; `lean-atom-r1-review.md`, addendum of 01:40Z): the length floors moved (10,000 to 631, 5,000 to 1,090), and R1 re-derived both covers from the data. R1 also accepted the `PouwBulk` exemption, on one condition: if the package moves into the Verity repository, whose `check` runs `audit.py` but not `check.sh`, the bulk test needs its own runner there.

**The model.**
- **The codec:** `Code = Fin 256` and `decode : Code → Option ℚ` are the OCP E4M3 codec (`verity.ml.tc.term.E4M3`). NaN is `0x7F` and `0xFF`, there are no infinities, and subnormals sit at exponent −9.
- **The step:** `hopperStep acc a b` is one `HOPPER_E4M3_K32` accumulator step, one coordinate of `wgmma.mma_async…m64nNk32.f32.e4m3.e4m3`. It is the FP32 word written from the accumulator word and 32 code pairs, transcribed function by function from `verity.ml.tc.total_fp8.tc_dot_total_e4m3`:
  - exact products;
  - one group of the 32 products and the accumulator on a 14-bit adder;
  - alignment to the largest exponent (floor −139) by truncation, and an exact sum;
  - normalisation to 14 bits by truncation, and denormalisation below `2^−126`;
  - FP32 packing, with `0x7FFFFFFF` for NaN and `+0` for zero.
  `adaStep` is the same adder with two groups of 16 (`ADA_E4M3_M16N8K32`).
- **The FP32 add:** `rnAdd x y = rn (x + y)` is the round-to-nearest-even add of the running words, over ℚ with no exponent range.
  - `rn` rounds to a 24-bit significand at `ulp x = 2^(binade |x| − 23)`.
  - Its conformance vectors lie where the exact sum is zero or normal. R1 (F3) shows it agrees with IEEE binary32 addition on every pair of finite words unless the sum overflows, since word values are multiples of `2^−149`.
  - `Representable x` means a 24-bit significand, and `wordQ w` is a word's finite value.

All 12 pins are `Pouw.Fp8Atom.Proofs.<pin>`, and each proves the `Prop` of the same name, capitalised, in `Pinned.lean`. The last column gives the top-level definitions each statement reads; the review printout lists everything they unfold to.

| Pin | Statement | Reads |
|---|---|---|
| `conformance` | On each of at least 631 vectors, `hopperStep` writes the word that `verity.ml.tc`'s `tc_dot_total_e4m3(HOPPER_E4M3_K32, …)` computes. They are the 49 steps of the repository's `fp8-hopper-wgmma-k32` and `-k1536` model replays, and two greedy branch covers of the 10,549 generated steps (random, mixed, nonzero accumulator, special values, subnormal, saturation, cancellation, wide exponent range), with 15 in common. R1's 450 hit each of its 24 branch outcomes at least 50 times; the fine cover's 147 reach every branch feature the 10,549 reach. The 10,549 run in the bulk test | `hopperStep`, `codes`, `vectors` |
| `adaCaptures` | `adaStep` writes the measured word on each of the 360 RTX 4090 captures of `mma.sync.m16n8k32.e4m3` (`packages/verity/tests/ml/fixtures/golden/ada_e4m3_m16n8k32.json`) | `adaStep`, `codes`, `Vectors.ada` |
| `codeClasses` | NaN is exactly `0x7F` and `0xFF`; `decode` is `none` exactly on NaN, and `some 0` exactly on `0x00` and `0x80`; 254 codes are finite | `Code.isNaN`, `decode` |
| `decodeInjective` | Two finite codes with the same value are equal, or are the two zeros | `decode`, `Code.isNaN`, `Code.isZero` |
| `productExact` | For finite codes, the product term's value is the product of the decoded values | `product`, `Term.value`, `decode` |
| `alignedMono` | The first truncation is monotone. On an adder of at most 24 bits, terms aligned to an exponent at least their own keep the order of their values | `aligned`, `Term.value` |
| `addConformance` | On each of at least 1,090 add vectors, the three words are finite, and `rnAdd` maps the operands' values to the value of the word IEEE binary32 addition writes. They are a greedy cover of the 5,000 generated adds (random, close exponents, cancellation, ties, absorption, `±0 + x`, subnormal operands, the top of the range and binade boundaries). It hits each of 42 features (33 branch features of `rnAdd` and the 9 generator families) at least 75 times, or every time it occurs if fewer. The 5,000 run in the bulk test | `rnAdd`, `wordQ`, `Vectors.add` |
| `rnAddExact` | A representable sum is returned exactly | `rnAdd`, `Representable` |
| `rnAddMono` | `rnAdd` is monotone in the exact sum | `rnAdd` |
| `rnAddAbsorb` | For representable `r ≠ 0`, a summand with `2·\|i\| < ulp r` is absorbed, unless `r` is a power of two and `i` points toward zero | `rnAdd`, `ulp`, `binade`, `Representable` |
| `rnAddMoves` | For representable `r ≠ 0`, a summand with `\|i\| ≥ ulp r` moves `r` | `rnAdd`, `ulp`, `Representable` |
| `wordsRepresentable` | Every finite FP32 word's value is `Representable`. With `rnAddExact` this gives `rnAdd 0 x = x` on word values, which is `C2FirstRunCopy`'s hypothesis | `wordQ`, `Representable` |

**What these pins do not establish:**
- **The H100 semantics, word for word on silicon.** The pins compare the model with `verity.ml.tc` (R1 F1, F2).
  - `verity.ml.tc`'s `HOPPER_E4M3_K32` is itself pinned on H100 silicon by two campaigns with 0 mismatches: QZ, with 144,543,744 words, and tc-probe-fp8, with 25,554,432. Neither measured the instruction form H-1T issues.
  - Round 11's captures measured it (F1, closed above). They are not Lean vectors: `HopperCaptures` and `ChainCaptures`, a kernel-pinned cover of them, are not added.
- **FP32 overflow** (R1 F3). `rnAdd` has no exponent range. For H-1T, `h1tRange` (§14) bounds every running sum of a legal unit below `2^33`, so none overflows.
- **The unreachable branches:** the saturation in `groupStepTotal`, the `mag = 0` exit in `normalize`, and the value of the −139 floor (R1 F4). Conformance cannot test them. For H-1T's steps (accumulator `+0`, finite codes), `h1tAtomValue` (§14) gives the word's value on every input, so neither branch changes it. Its `gridExp` carries the floor, but no value depends on it: a nonzero product of finite codes is at least `2^−18` in magnitude, so its exponent is far above the floor, and with no nonzero product every term is 0. That is argued, not pinned. Steps from a nonzero accumulator are not covered.
- **The second truncation's monotonicity** (`normalize`): for steps from `+0`, `trunc14Mono` with `h1tAtomValue` (§14).
- **Sharp movement,** that a summand of more than half an ulp moves the sum. H-1T's absorption argument was to need it at F = 1/4 with `2^32 ≤ |R| < 2^33` (`internal/pouw-fp8/lean-atom-m2-plan.md`, L5). Pinned since 29 Sep 02:30Z as `rnAddMovesHalf` (§13). §14's proof of absorption does not use it: it uses `rnErr` with L4 (`h1tRange`), so a rounding error of at most 256 (X-M3-2).

## 13. H-1T (M2) (29 Sep 02:30Z; all 16 granted by red team Phase 19d (bc-89770364, 03:27Z))

The Lean worker (bc-5382063c) added these 16 pins in `Pouw.Fp8Atom`, as M2 of `internal/pouw-fp8/lean-atom-m2-plan.md` (§0 there). They apply the 9 changes of red team Phase 19c's statement review (X-H1T-8, `internal/pouw/new-crypto/red-team.md`). **Their named statement reviewer granted all 16 records** (Phase 19d, bc-89770364, 29 Sep 03:27Z; `red-team.md` v2.26): it rebuilt the package and re-ran the audit with `--fresh` (310 pins, the three allowed axioms, no record differs), and asked for no record change. Its notes X-M2-3 to X-M2-5 are applied below. X-M2-2 (widen `free` and `mfree` to any reading of a raw XOF word) waits for the next change of `DistinctLiveH1T`, and X-M2-1 is Track H's (the kernel's docstring says `r0..r15`, but it reads `r0..r14`).
- **Trusted files:** `Pouw/Fp8Atom/H1T.lean` (the map), `H1TVec.lean` (what a vector asserts), `H1TAssumptions.lean`, `H1TPinned.lean`, `H1TGamma.lean`, and the generated `H1TVectors.lean`, which comes from `scripts/h1t_vectors.py` (coverage in `Pouw/Fp8Atom/H1TCoverage.json`).
- **Proofs:** `H1TProofs.lean`, `H1TGammaProofs.lean`, and the generated `H1TChecks.lean` (`decide +kernel`, no `native_decide`). Every H-1T vector is kernel-pinned; none is in the bulk test.
- **The `--update` review printout** is `internal/pouw-fp8/lean-atom-m2-update.txt`: 16 new pins with every definition they read. No existing pin record changed, and no existing module's reads digest changed.
- **The named assumption** is `DistinctLiveH1T` (`H1TAssumptions.lean`, registered in `lean-audit.json`). It is a closed `Prop`, taken as a binder, so the records of `h1tUnitsDistinct` and `h1tGamma` list it. The other 14 pins take none. `HalfApartH1T` is stated beside it, and no pin uses it.

**The map** (`H1T.lean`; `docs/pouw/hardness-shaped-matrices.md` §3.1, as Track H's `h1t_ref`, `tag_tuples` and `chain` compute it):
- **Layout:** `T = ⌈k/29⌉` slices of 29 real lanes and 3 tag lanes, with the row and columns zero-padded to `29·T`.
  - **Lanes 29–31 of the `X_q` tile are zero** (X-M2-4 (b)). The kernel's slice max reads all 32 lanes and the Lean's `sliceMax` reads the 29 real ones, so the two agree only on this layout. It is a condition on the served tile, like R1's F1 and X-H1T-12, and no pin checks it.
- **Salt:** 18 raw XOF words per (row, slice) (`RawSlice`). `extract` reads only the kernel's fields: bits 15 and 31 of `r0..r14` for the 29 real-lane signs, and a sign and 3 mantissa bits per tag lane from `r16` and `r17`.
- **Forming:** `F = max(2^(e(M) − 6), 1/4)`, `μ = max(p/8, F)`, `x1 = enc(x + s·μ)` and `x2 = enc(−s·μ)`, with `x + s·μ` exact over ℚ. `enc` is `cvt.rn.satfinite.e4m3`. Tag lanes get `v = ±32F·(1 + m/8)` and `−v`.
- **B′:** the registered real codes and the fixed tag tuple `(A0[j mod 23], A1[(j/23) mod 62], A1[(j/1426) mod 62])` of column `j`.
- **Chain:** `I_p = hopperStep(+0, x1 or x2, B′)` (block 1 then block 2), with `R_0 = I_0` and `R_(p+1) = rnAdd(R_p, I_(p+1))`. Words are compared as values in ℚ.
- **Credited words** (`Pos T`, 0-based): `I_p` for `p < 2T` and `R_p` for `1 ≤ p ≤ 2T − 3`, which is `4T − 3` per output for `T ≥ 2`. At `T = 1` there are 2 (`I_0` and `I_1`), not 1 (X-M2-3). The useful output `R_(2T−1)` is not credited, and neither is `R_(2T−2)`.
- **A unit** has `m` rows of `X_q` and `n` columns of B′ over `k`, and a salt of its own. `Legal`: `k ≤ 32,768`, `n ≤ 88,412`, every code finite. Its free values are the constants and its raw XOF words (W1).

**The statement** (`DistinctLiveH1T`, Target A per unit): `∀ U, U.Legal → Function.Injective U.word ∧ ∀ c, U.word c ∉ U.free`. On a legal unit no two credited words are equal as functions of the salt, and no credited word is a constant or a raw XOF word. It covers every credited word of the unit, `m·n·|Pos T|` of them, across rows and columns: cross-row and cross-column pairs, O1 among them, are inside it (X-M2-3). The half-salt clause (`HalfApartH1T`, X-H1T-7) is stronger and is not the target. It says two credited words of one row agree on at most half of that row's salts, and a credited word takes one value on at most half of them. It is the input to the lifting and branching arguments: Derived for `I` words, Simulated for `R` words.

All 16 pins are `Pouw.Fp8Atom.H1T.Proofs.<pin>`. Each proves the `Prop` of the same name, capitalised, in `H1TPinned.lean` or `H1TGamma.lean`.

| Pin | Statement | Reads |
|---|---|---|
| `h1tFormTable` | `formTable`'s keys are every finite code, both signs and every `F` in {1/4, 1/2, 1, 2, 4} (2,540 lanes), and on each `formReal` gives the expected codes. A slice of finite codes has `M ≤ 448`, so these are all its `F`. The generator checked each against an exact transcription of §3.1, Track H's `enc`, and (for the 2,236 reachable lanes) a float16 simulation of `h1t_form_xq` | `formReal`, `formTable`, `formKeys`, `fOf`, `codeOf` |
| `h1tTagTable` | Every tag value and its negation encode exactly to the expected codes (80) | `enc`, `tagVal`, `val`, `tagTable`, `tagKeys` |
| `h1tSaltConformance` | On 74 raw salts `extract` reads the expected fields: zero, all ones, 14 single bits in every word, each word alone, and 40 random. The generator checked each against the kernel's masks | `extract`, `packSalt`, `rawOf`, `saltVectors` |
| `h1tChainConformance` | On 31 rows and columns with `T ≤ 3` (128 atoms), at every position, `freshWord` writes `verity.ml.tc`'s word and `runVal` is numpy's float32 running sum. The generator checked each row against Track H's `h1t_ref` and `chain` | `freshWord`, `runVal`, `wordQ`, `rowVectors` |
| `h1tReadsFields` | Two salts with the same `extract` fields give every credited word the same value (change 1) | `Unit.word`, `extract` |
| `h1tNotRawWord` | No credited word is a raw XOF word, since no read bit is below bit 7. This is the XOF half of "no free word", proved unconditionally | `Unit.word` |
| `h1tTupleInjective` | Columns `j, j′ < 88,412` with the same tag tuple are equal | `tuple` |
| `h1tTupleWrap` | `tuple (j + 88,412) = tuple j` | `tuple` |
| `h1tWrapDuplicate` | In one unit, columns 88,412 apart with the same real codes have the same credited words on every salt. So `n ≤ 88,412` per unit is needed, and wider outputs need several units with their own salts (change 4) | `Unit.word` |
| `h1tPosCard` | `4T − 3` credited words per output for `T ≥ 2` (change 2) | `Pos` |
| `h1tNonVacuous` | A legal unit with `m = 1`, `k = 32,768` and `n = 88,412` exists, with `T = 1,130` and 4,517 credited words per output. The proof's witness has every code 1.0 (change 9) | `Unit.Legal`, `Unit.T`, `Pos` |
| `rnErr` | `\|rn y − y\| ≤ ulp y / 2` | `rn`, `ulp` |
| `rnAddMovesHalf` | For representable `r ≠ 0`, `ulp r < 2·\|i\|` gives `rnAdd r i ≠ r`, at `±2^k` too. It was to be X-H1T-3's absorption step: an absorbed summand has `2·\|i\| ≤ ulp r`, where `rnAddMoves` leaves `[960, 1,024)` open. §14's proof of absorption uses `rnErr` with L4 instead, and no other pin uses this one (X-M3-2) | `rnAdd`, `ulp`, `Representable` |
| `halfOfInvolution` | If an involution maps every point where `P` holds to one where it fails, `P` holds on at most half of a finite set. It is the counting step of the half-salt clause's one-flip cases | `Fintype.card` |
| `h1tUnitsDistinct` | Under `DistinctLiveH1T`: on legal units `Us` with independent salts (`MSalt`, change 4 and X-H1T-S7), all their credited words are pairwise distinct functions of the joint salt, and none is a constant or any unit's raw XOF word | `mword`, `mfree`, `Unit.Legal` |
| `h1tGamma` | Under `DistinctLiveH1T` and `H32`: an `MH100w` program (draft semantics) on free inputs whose registers include every credited word of legal units costs at least `32·Σ_u m·n·\|Pos T\|`, which is `32·Σ_u m·n·(4T − 3)` when every unit has `T ≥ 2` (`h1tPosCard`; a unit with `T = 1` has 2 words per output, X-M2-3). It is `distinctLiveMH100` at `ε = 0`. §14's `h1tGammaRunning` proves it under `H1TRunningWords` | `mword`, `mfree`, `regs100`, `cost100`, `Op100.WFw`, `H32` |

**What these pins do not establish:**
- **`DistinctLiveH1T` itself.** Only its raw-XOF half of "no free word" is proved here (`h1tNotRawWord`). Since §14 it is equivalent to the narrower `H1TRunningWords` (`h1tDistinctLive`, `h1tRunningOfDistinct`), which carries O1 and O2 of the M2 plan's §0.4. `I_τ` against `R_τ` and the other one-flip clauses are proved (`h1tOneFlip`).
- **The half-salt clause** for the `Hard` pairs and the block-2 `R` words (§14), and the per-tile count form that the sampled-proofs verifier needs (X-SPC-3; the M2 plan's §0.5).
- **Silicon.** R1's F1 is closed (§12): Round 11's captures match `verity.ml.tc`, whose `HOPPER_E4M3_K32` and `rnAdd` the chain is. The forming map is Track H's `h1t_ref`, checked against a float16 simulation of `h1t_form_xq`, not against the kernel on a GPU. Lanes 29–31 of the `X_q` tile being zero (X-M2-4 (b)) is a layout condition no pin checks.
- **Long chains.** The chain vectors have `T ≤ 3`. `T` up to 1,130 is covered by the definitions and, since §14, by `h1tRange`'s bound on every legal unit, but no vector tests a long chain.
- **`rnAdd` as FP32 on the chain** (X-M2-5). `rnAdd` is IEEE binary32 addition on finite words unless the sum overflows (R1 F3, §12). On the chain every value is a multiple of `2^−18` (products of E4M3 values are, and both truncations and `rn` keep it), so no nonzero value is subnormal, and `h1tRange` rules out overflow. A zero sum is its own case: `binade` means nothing at 0, so the proofs use `rn 0 = 0` there (`rn_err_small` in `H1TSliceProofs.lean`), and `rnAddMovesHalf` and `rnAddAbsorb` take `r ≠ 0`.

## 14. H-1T (M3, M4a) (29 Sep 04:10Z; all 11 and `H1TRunningWords`'s statement granted by red team Phase 19f (bc-89770364, 05:17Z))

The Lean worker (bc-5382063c) added these 11 pins in `Pouw.Fp8Atom`, as M3 and M4a of `internal/pouw-fp8/lean-atom-m2-plan.md` (§0.4, §0.6). **Their named statement reviewer granted all 11 records and the statement of `H1TRunningWords`** (Phase 19f, bc-89770364, 29 Sep 05:17Z; `internal/pouw/new-crypto/red-team.md` v2.28). Its re-run of the audit with `--fresh` passed at 321 pins and left `lean-audit.json` byte-identical. Its notes X-M3-1 to X-M3-3 are applied below.
- **Trusted files:** `Pouw/Fp8Atom/H1TLemmas.lean` (the statements) and `H1TRunningAssumptions.lean` (the named assumption), two new `layers` of `lean-audit.json` that import no proofs.
- **Proofs:** `H1TAtomProofs.lean`, `H1TSliceProofs.lean`, `H1TFlipProofs.lean` and `H1TRunningProofs.lean`.
- **The `--update` review printout** is `internal/pouw-fp8/lean-atom-m3-update.txt`: 11 new pins with every definition they read. No existing pin record changed, and no existing module's reads digest changed. The `reads` entries of 11 modules list the new pins, and that is all that changed in them.
- **The named assumption** is `H1TRunningWords` (`H1TRunningAssumptions.lean`, registered in `lean-audit.json`'s `assumptions`). The records of `h1tDistinctLive` and `h1tGammaRunning` list it, `h1tRunningOfDistinct`'s lists `DistinctLiveH1T`, and the other 8 take none.

**The definitions** (`H1TLemmas.lean`):
- **The two truncations:** `truncTo g y` truncates toward zero to a multiple of `g`, and `trunc14 y` to 14 significant bits (a multiple of `2^(binade |y| − 13)`). `gridExp a b` is a slice's alignment exponent, the largest exponent of a nonzero product (`maxExp`, floor −139). `preSum a b` is the exact sum of the products, each truncated to `2^(gridExp a b − 13)`.
- **The flip:** `negFlip i σ` is the slice salt `σ` with tag lane `29 + i`'s sign bit flipped.
- **The positions the one-flip argument does not cover:** `posIdx` is a credited position's index (`p` for `I_p` and for `R_p`). `Run2 a` holds when `a` is a block-2 running word (`R_p` with `p ≥ T`). `Hard a a′` holds when `a` and `a′` are two block-1 running words at one position (O1), or one of them is `Run2` and the other is not a fresh-step word at a later position (O2). Since §15 (M4b), `Hard` also reads the two words' columns, and it is narrower for pairs of different columns.

All 11 pins are `Pouw.Fp8Atom.H1T.Proofs.<pin>`. The first eight each prove the `Prop` of the same name, capitalised, in `H1TLemmas.lean`. The last three prove the `Prop` their row names.

| Pin | Statement | Reads |
|---|---|---|
| `h1tAtomValue` | On finite codes, `hopperStep 0 a b` writes a finite word whose value is `trunc14 (preSum a b)`. For H-1T's steps this settles R1's F4 (§12) | `hopperStep`, `wordQ`, `trunc14`, `preSum`, `gridExp` |
| `trunc14Mono` | `trunc14` is monotone (L7) | `trunc14` |
| `trunc14Cell` | For `y ≠ 0`, `\|trunc14 y − y\| < 2^(binade \|y\| − 13)`, and `trunc14 y = trunc14 y′` gives `\|y − y′\| < 2^(binade \|y\| − 13)` (L3) | `trunc14`, `binade` |
| `h1tSlice` | For a slice of finite real codes `xs`, salt fields `σ` and a column of finite codes: block 1's sum is at most 6,142,976 and block 2's at most 738,304 in magnitude, both below `2^21·F`. Flipping tag lane `i`'s sign bit keeps both alignment exponents and moves block 1's sum by exactly `−2·v·t` and block 2's by exactly `+2·v·t`, with `v` the lane's tag value and `t` the column's tag code (L1 to L3) | `formSlice`, `colLanes`, `preSum`, `gridExp`, `negFlip`, `tagVal`, `floorF`, `sliceMax`, `tuple` |
| `h1tChainMono` | If every fresh-step word up to `p` is no larger at `σ` than at `σ′`, neither is `R_p` (L7 for the chain) | `freshVal`, `runVal` |
| `h1tRange` | On a legal unit, at every row, column, salt and `p < 2T`: `I_p` is finite, `\|I_p\|` is at most 6,142,976 (block 1) or 738,304 (block 2), and `\|R_p\| < 2^33`, so `ulp(R_p) ≤ 512` and no running sum overflows (L4, R1 F3). It holds at `x = ±448` | `Unit.Legal`, `freshWord`, `freshVal`, `runVal`, `wordQ` |
| `h1tFormCover` | A slice of finite codes has `F = fOf fi` for some `fi ≤ 4`, and each of its codes is below `2^(fi + 5)` in magnitude. So `h1tFormTable`'s five `F` cover every slice (X-M2-4 (a)) | `floorF`, `sliceMax`, `fOf`, `val` |
| `h1tOneFlip` | On every legal unit and row, `HalfApartH1T`'s two clauses for the pairs and words one flip reaches: two distinct credited words of the row (any columns) whose positions are not `Hard` agree on at most half of the row's salts, and a credited word that is not `Run2` takes any one value on at most half of them | `Unit.word`, `Unit.Legal`, `Hard`, `Run2` |
| `h1tDistinctLive` | Under `H1TRunningWords`: `DistinctLiveH1T` | `DistinctLiveH1T`, `H1TRunningWords` |
| `h1tRunningOfDistinct` | Under `DistinctLiveH1T`: `H1TRunningWords`. With `h1tDistinctLive`, the two are equivalent | `DistinctLiveH1T`, `H1TRunningWords` |
| `h1tGammaRunning` | Under `H1TRunningWords`: `H1TGamma` (§13's `h1tGamma` statement, with its `H32` hypothesis) | `H1TGamma`, `H1TRunningWords` |

**The argument** (`H1TFlipProofs.lean`, `H1TRunningProofs.lean`):
- **The flip.** The involution toggles one raw bit of one slice: bit 31 of `r17`, or bit 15 or bit 31 of `r16`. `extract` reads that bit as a tag lane's sign bit and reads nothing else from it. `halfOfInvolution` turns "the flip separates every salt where the pair agrees" into "they agree on at most half".
- **The moves.** A lane-0 flip moves the flipped fresh-step word by at least `4096F − 256F ≥ 960`, in a known direction, and so a block-1 running word by at least `960 − 512 = 448`.
- **The one-flip cases.** `I` against `I`: other slices, the two blocks of one slice, or two columns (`2·|v|·|Δt| ≥ 256F` against cells below `128F`). A block-1 `R_q` against `I_p`: flip slice `q`, or slice `q − 1` when `I_p` is of slice `q`. There, `RN(R_(q−1) + I_q) = I_p` with `|I_p| < 2^23` puts the sum within `1/4` of `I_p`, while `R_(q−1)` moves by at least 448. A block-1 `R_q` against a later block-1 `R_q′`: flip slice `q′`. Absorption (`R_(q−1)` against `R_q`) is this case: it needs `h1tRange`'s rounding error (at most 256), not `rnAddMovesHalf`, which no M4a proof uses. A `Run2` word against a later `I`: the running word moves weakly one way (L7) and the fresh-step word strictly the other.
- **Across rows.** A credited word reads only its own row's salt, so two equal words of different rows are both constant. That, `h1tOneFlip`, `H1TRunningWords` and `h1tNotRawWord` give `DistinctLiveH1T`.

**What is carried as `H1TRunningWords`** (M4b; `∀ U, U.Legal → ∀ i a a′, (a ≠ a′ → Hard a.2 a′.2 → U.word (i, a) ≠ U.word (i, a′)) ∧ (Run2 a.2 → ∀ q, U.word (i, a) ≠ fun _ => q)`). On a legal unit and row: two distinct credited words at `Hard` positions are distinct functions of the salt, and no block-2 running word is constant. These are the positions the one-flip argument does not cover. Per column pair it is wider than that: `Hard` reads positions only, and many column pairs at these positions fall to one flip (X-M3-1).
- **O1:** two columns' block-1 running words at one position. A flip moves their difference by as little as `2·|v|·|Δt| = 64` at `F = 1/4`, against an ulp of 512 (per slice, `256F` against up to `512F` of cell error).
- **O2:** a block-2 running word against every word except a later fresh-step word, and its non-constancy. A block-1 slice `s`'s move reaches `R_p` through the roundings from `R_s` to `R_p`, each of which can absorb up to 512 of it: `2T − 3` of them in the worst case (`s = 0`, `p = 2T − 3`), and `p − T + 2` from the last slice (X-M4-2). §17 uses the last slice near the start of block 2.
- **A several-slice monotone argument** (argued, not pinned) does not close O2 either. It flips all three tag lanes of every block-1 slice after `m`, slices `m + 1` to `T − 1`. Each flipped slice adds at least 3,776 to the difference and its own rounding takes at most 512, so at least 3,264 net. Then the `m + 1` block-2 roundings up to `R_(T+m)` take up to 512 each. So it gives the non-constancy of `R_(T+m)` when `(T − m − 1)·3,264 > (m + 1)·512`, that is for `m` below about `0.86·T − 1`. Near the end of block 2 it gives nothing: `m = T − 3` needs `T ≤ 14`. The plan's §3 first wrote the looser `(T − s)·3,264 > s·512`, which gives `T ≤ 22` there; it counted one slice too many and one rounding too few, and is corrected (X-M3-3).
- **Closing it** needs a rounding lemma that avoids ties and binade changes, with salts chosen across about `T` roundings. That is research. The evidence is the red team's simulation (pair frequencies at most 0.375).

**What these pins do not establish:**
- **`H1TRunningWords`,** above. So `DistinctLiveH1T` and `H1TGamma` are proved only under it.
- **The half-salt clause for the `Hard` pairs and the `Run2` words.** `H1TRunningWords` is function level only, so `HalfApartH1T` itself is not proved.
- **The per-tile count statement** (`TTH1T`, X-SPC-3; the M2 plan's §0.5). It was not stated here; §16 states it, as an assumption. Its "right" event reads only the credited words at fixed output slots, so it does not read the useful output `R_(2T−1)`.
- **X-M2-2:** `free` and `mfree` still list only the raw XOF words themselves, not other readings of them. They are widened at the next change of `DistinctLiveH1T`.

## 15. H-1T (M4b): `Hard` by column (29 Sep 05:40Z; the four changed statements and the narrowed `H1TRunningWords` granted by red team Phase 19h (bc-89770364, 06:42Z); narrowed further in §17)

The Lean worker (bc-5382063c) narrowed `Hard` by column, as X-M3-1 suggested (M4b of `internal/pouw-fp8/lean-atom-m2-plan.md`, §0.7). No pin was added and no pin record changed: the four statements that read `Hard` name their `Prop`s, whose bodies are in `reads`. Those bodies did change: `Hard` and `H1TOneFlip` in `H1TLemmas.lean`, `H1TRunningWords` in `H1TRunningAssumptions.lean`, and the new `FarTags` and `OppLater`. So `h1tOneFlip`, `h1tDistinctLive`, `h1tRunningOfDistinct` and `h1tGammaRunning` now say something else, and their named statement reviewer is the red team, bc-89770364 (named by the coordinator, 05:18Z).
- **The `--update` review printout** is `internal/pouw-fp8/lean-atom-m4b-update.txt`: the three changed definitions as they were (as §14 granted them) and as they are, and the two new ones. Only the `reads` of `Pouw.Fp8Atom.H1TLemmas` and `H1TRunningAssumptions` changed. The policy (`assumptions`, `layers`) is unchanged.

**The definitions** (`H1TLemmas.lean`; `t_j,k` is `val (tuple j k)`, column `j`'s tag value in lane `k`):
- **`FarTags j j′`:** some lane `k` has `|t_j,k − t_j′,k| ≥ 72`.
- **`OppLater j j′ a a′`**, for a block-2 running word `a` of column `j`: `a′` is a block-1 word (`I_q` or `R_q`, `q < T`) of column `j′`, in a slice after `a`'s last block-2 slice (`posIdx a < T + q`), and some lane `k` has `t_j,k·t_j′,k < 0`, with `|t_j′,k| ≥ 36` if `a′` is a running word.
- **`Hard j j′ a a′`** is §14's `Hard a a′` less two sets of cross-column pairs: O1 when `FarTags j j′`, and O2 when `OppLater` holds. For `j = j′` it is §14's, since `FarTags j j` and `OppLater j j a a′` are false.
- **`H1TOneFlip` and `H1TRunningWords`** now read `Hard a.1.val a′.1.val a.2 a′.2`, the two words' columns and then their positions, and are otherwise as in §14.

| Pin | What it says now |
|---|---|
| `h1tOneFlip` | The half-salt clause for every pair that is not `Hard` in the new sense. That adds the O1 pairs of `FarTags` columns and the O2 pairs that `OppLater` names, so it is stronger than §14's |
| `h1tDistinctLive`, `h1tRunningOfDistinct` | The narrower `H1TRunningWords` is still equivalent to `DistinctLiveH1T` |
| `h1tGammaRunning` | `H1TGamma` under the narrower `H1TRunningWords` |

**The argument** (`H1TFlipProofs.lean`; it uses only L1 to L4, L7 and `rnErr`, through `h1tSlice`, `trunc14Cell`, `trunc14Mono`, `h1tChainMono` and `rn_err_small`). Flip lane `k` of slice `q`.
- **O1 for `FarTags` columns** (`sep_run_columns`). The two columns' `R_q` have `q ≥ 1`, since a credited `R_p` has `p ≥ 1`, and both `R_(q−1)` stay. If `RN(Y) = RN(Z)` at both salts, each pair of sums is within 512, because the rounding error is at most 256 (L4). So the two sums' moves differ by at most 1,024. But they differ by `2v(t′ − t)` plus four cell errors, each strictly below `128F` (L3), and `|2v(t − t′)| ≥ 64F·72 = 4608F`. So they differ by more than `4096F ≥ 1024`.
- **O2 for `OppLater`** (`sep_opp_fresh`, `sep_opp_run`).
  - `R_p` with `p < T + q` reads slice `q` only through `I_q`, since slice `q`'s block 2 is position `T + q > p`. So it moves weakly by the sign of `−v·t` (L7).
  - The other column's `I_q` moves strictly the other way, by more than `2048F − 256F`, since every tag value is at least 32 in magnitude (`tuple_abs_ge`).
  - Its `R_q` (`q ≥ 1`) also moves strictly if `|t′| ≥ 36`. Then `I_q` moves by more than `2304F − 256F ≥ 512`, `R_(q−1)` stays, and each rounding takes at most 256. At `|t′| = 32`, `I_q` may move by as little as `1792F`, which is 448 at `F = 1/4`, and rounding can absorb that.
  - Lane 0's values are all positive (`[64, 448]`), so only lanes 1 and 2 can have opposite signs.
- **`pair_sep`** splits §14's `Hard` cases on `FarTags` and `OppLater`. The other cases are as in §14.

**What `H1TRunningWords` now carries.** On a legal unit and row, take two distinct credited words, `a` of column `j` and `a′` of column `j′`. They are distinct functions of the salt:
- **O1:** if they are block-1 running words at one position, of columns whose tuples are less than 72 apart in every lane. The red team counts 98.6% of the column pairs of a full unit as `FarTags`. The rest are nearby columns: 84,568 of the 88,411 adjacent pairs.
- **O2:** if `a` is a block-2 running word `R_p` and `a′` is one of the following:
  - another block-2 running word;
  - a block-2 fresh-step word at a position up to `p`;
  - a block-1 word of a slice up to `p − T`;
  - a block-1 word of a later slice whose column has no lane of opposite sign, or, if `a′` is a running word, none in which `|t_j′,k| ≥ 36`. This includes every such pair within one column.

  About 3/4 of column pairs have opposite signs in lane 1 or lane 2 (the red team's figure).
- **Non-constancy:** no block-2 running word is constant, as before.

The several-slice argument of §14 is unchanged. It is not pinned, and it does not close the within-column O2 pairs or the non-constancy near the end of block 2.

**What M4b does not establish:** everything §14 lists, less the `FarTags` and `OppLater` pairs. `HalfApartH1T` is proved for those pairs (`h1tOneFlip`), and for the rest of `Hard` it is not.

## 16. H-1T: the per-tile count statement `TTH1T` (29 Sep 06:05Z; `tth1tAllRight` and `tth1tSat` granted by red team Phase 19h (bc-89770364, 06:42Z); `TTH1T`'s statement not granted as stated (X-M4-4), and restated in §17)

The Lean worker (bc-5382063c) stated `TTH1T` (X-SPC-3; the M2 plan's §0.5), for sampled proofs' layout A, as a named assumption, with two pins that check its form (323 pins). It is Assumed: the lifting from pointwise-right tiles to a cost bound is research.
- **Trusted files:** `Pouw/Fp8Atom/H1TTile.lean` (the tiles, the output slots and the sanity statement) and `H1TTileAssumptions.lean` (`TTH1T`), two new `layers` of `lean-audit.json` that import no proofs. `H1TTileAssumptions` is registered in `assumptions`.
- **Proofs:** `H1TTileProofs.lean`.
- **The `--update` review printout** is `internal/pouw-fp8/lean-atom-tth1t-update.txt`.

**The definitions** (`H1TTile.lean`, over §13's `MSalt`, `Idx`, `mword` and `mfree`):
- **`Tiling Us C`:** each output `(i, j)` of unit `u` lies in tile `tile u i j : C`. Every tile holds an output (`onto`), lies in one unit (`unit`), and is a block of that unit's rows and columns (`block`: holding `(i, j)` and `(i′, j′)`, it holds `(i, j′)`). `tl.of x` is credited word `x`'s tile, its output's.
- **`slotVal rs slot x`:** register `slot x` of the program's registers `rs`, or `0` past the last one. Each credited word has one fixed output slot, which the verifier reads.
- **`TileRight rs slot tl c G`:** every credited word `x` of tile `c` has `slotVal rs slot x G = mword Us x G`.
- **`rightWords rs slot tl G`:** the number of credited words whose tile is right at `G`. So `32·rightWords` is `Σ_{c right at G} W c`, with `W c = 32·|credited words of c|`. The useful output `R_(2T−1)` and `R_(2T−2)` are not credited (`Pos`), so "right" does not read them.

**The assumption** (`H1TTileAssumptions.lean`): `TTH1T γ η`, for `γ : ℚ` and `η : ℕ → ℚ`. Take prices `pr` with `H32`, legal units `Us`, a tiling `tl` by the tiles `C`, and a well-formed `MH100w` program `P` (draft semantics) on free inputs `L` with output slots `slot`. Then

`|{G : (1 − γ)·32·rightWords (regs100 fpSem P L) slot tl G > cost100 pr P}| ≤ η (Nat.card C)·|MSalt Us|`.

For tiles of `w` credited words each, this says that except with probability `η`, at most `cost/((1 − γ)·32·w)` tiles are right. `η` reads the number of tiles, as `TTNCP_U`'s `ε` reads the number of units, and `onto` keeps empty tiles from inflating it. The universally quantified tiling is restricted to blocks of one unit, which makes the assumption weaker, not stronger. `MH100w` is straight-line, so branching is outside it (X-H1T-2).

| Pin | Statement | Reads |
|---|---|---|
| `tth1tAllRight` | Under `H1TRunningWords`: `TTH1TAllRight`. Under `H32`, a well-formed `MH100w` program on free inputs that is right on every tile at every salt is never in `TTH1T`'s event at `γ = 0`: `cost ≥ 32·rightWords` at every salt. It is `h1tGammaRunning`: a slot past the last register would make a credited word the constant `0`, which is free (`h1tUnitsDistinct`), and every credited word is in a right tile | `Tiling`, `TileRight`, `slotVal`, `rightWords`, `mword`, `mfree`, `regs100`, `cost100`, `Op100.WFw`, `H32`, `H1TRunningWords` |
| `tth1tSat` | `TTH1T 1 (fun _ => 0)`: at `γ = 1` the event is `cost < 0`, which never holds. So the family is not contradictory in form | `TTH1T` and what it reads |

**What these pins do not establish:** `TTH1T` at any `γ < 1` and useful `η`. That is the lifting (research), whose input is `HalfApartH1T`, which is itself proved only off `Hard` (§15). No pin reads `TTH1T` as a hypothesis yet.

## 17. H-1T: `TTH1T`'s domain (X-M4-4), and M4c (29 Sep 07:20Z; the restated `TTH1T`, `tth1tSat`'s record, the narrowed `H1TRunningWords` and the five pins `tth1tAllRight`, `h1tOneFlip`, `h1tDistinctLive`, `h1tRunningOfDistinct` and `h1tGammaRunning` granted by red team Phase 19j (bc-89770364, 08:14Z, v2.32); X-M4c-1 applied in §17.1)

Red team Phase 19h (bc-89770364, 06:42Z; `internal/pouw/new-crypto/red-team.md` v2.30) granted §15's four changed statements, the narrowed `H1TRunningWords`, and §16's two pins. It did not grant `TTH1T`'s statement as stated (X-M4-4, medium). The Lean worker (bc-5382063c) gave `TTH1T` a domain of tilings, and narrowed `Hard` further (M4c: X-M4-1 and X-M4-2, both optional). One pin record changed, `tth1tSat`'s. The `reads` of `H1TLemmas`, `H1TRunningAssumptions`, `H1TTile` and `H1TTileAssumptions` changed, and the policy (`assumptions`, `layers`) did not. The named statement reviewer is the red team, bc-89770364.
- **The `--update` review printout** is `internal/pouw-fp8/lean-atom-m4c-update.txt`: the changed record before and after, the changed and new definitions as they are now, and the changed ones as Phase 19h reviewed them (§15's granted `Hard`, `H1TOneFlip` and `H1TRunningWords`, and §16's `TTH1T`).

### 17.1 `TTH1T`'s domain

**The definition** (`H1TTile.lean`): `Tiling.AtLeast r c` says every tile holds an `r × c` block of its unit's outputs, `r` rows and `c` columns all of whose outputs lie in the tile. Since every tile holds an output, `AtLeast 1 1` always holds.

**The assumption** (`H1TTileAssumptions.lean`): `TTH1T r c γ η` is §16's statement for the tilings with `AtLeast r c`, so `TTH1T 1 1 γ η` is §16's. Sampled proofs' layout A takes `r = c = 16`: its tile is 16 activation rows by 16 weight rows at full depth (`docs/pouw/sampled-proofs-circuit.md`, "Tile"), and in a unit the activation rows are the rows `i` and the weight rows the columns `j`. Every credited word of an output is in its tile, so full depth is built in.

**Why a domain**, of the red team's three options:
- **It is what layout A has.** Layout A fixes its tile shape before the salt, and its tiles lie in one unit (X-M4-5). So its tilings have `AtLeast 16 16`, and the assumption need hold for nothing else. That is how `TTNCP_U`'s domain `D` works for NCP.
- **Rows are what bound a lucky guess.** A free constant is right on a tile at the salts where the tile's credited words take that value. Rows have independent salts, and a row's columns share its salt. In X-M4-4's example, a zero-coded unit at `k = 1` (`T = 1`), one row's words in column 0 are `(0, 0)` at 64 of 4,096 tag settings. That is column 0's count, and the domain allows any columns (X-M4c-1). In the same family, 16 columns with tag tuples `(x, x, x)` let the best constant be right on a row with probability 9/256, the maximum over tiles of at least 16 columns. So a tile of `r` rows is right with probability at most `(9/256)^r`, about `2^(−77.3)` at `r = 16`, and the program with no instructions is in the event with probability at most about `N·2^(−77.3)`, not `1 − (63/64)^N`. Layout A's aligned blocks give at most 1/256 per row, so `2^(−128)` per tile. These figures are computed. What Lean proves is 1/2 per row, since a fresh-step word is never `Stuck` and `h1tOneFlip`'s second clause applies, so `2^(−16)` per tile. Either way the floor falls geometrically in the rows and is negligible at `r = 16`.
- **`η` reading the smallest tile's credited words would not fix it.** A one-row tile with many columns has many credited words and still one row's salt, so guessing it gets no harder with the columns. `η` reading the rows and `T` would fix it, but it would claim one `η` for every tile shape at once, including one-row tiles. That is a stronger assumption than layout A needs.
- **A slack for lucky guesses** would itself be a random count, so it would need its own tail bound. That bound is `η` again.

**The two pins**, checked again:

| Pin | Statement | Reads |
|---|---|---|
| `tth1tAllRight` | Unchanged: `TTH1TAllRight` under `H1TRunningWords`, over every tiling, so it covers every domain. It now takes §17.2's narrower `H1TRunningWords`, so it is stronger | as §16, and `Stuck`, `Early`, `SkipsLast` through `H1TRunningWords` |
| `tth1tSat` | **Changed record:** `tth1tSat (r c : ℕ) : TTH1T r c 1 (fun _ => 0)`. At `γ = 1` the event is `cost < 0`, which never holds, in every domain | `TTH1T`, `Tiling.AtLeast` and what §16 lists |

**No witness at `γ < 1` is pinned** (X-M4-5). `TTH1T r c γ (fun _ => 1)` holds at every `γ`, because the event is a set of salts, and it says nothing. A witness with `η < 1` at some `γ < 1` would bound, on every legal unit, how often any cheap program makes a whole `r × c` tile right. That is the lifting itself, with `HalfApartH1T` as its input. §0.5 of the M2 plan promised such a witness, and it is not met.

### 17.2 M4c: `Hard` narrowed further

**The definitions** (`H1TLemmas.lean`; `t_j,k` is `val (tuple j k)`):
- **`Early j a`,** for column `j`'s block-2 running word `a = R_p`: some lane has `|t_j,k| ≥ 32·(p − T + 2) + 4`.
- **`SkipsLast a`:** word `a` does not read slice `T − 1`. That is `posIdx a + 1 < T`, or `a` is a block-2 fresh-step word before `I_(2T−1)`.
- **`Stuck j a`:** `Run2 a` and not `Early j a`.
- **`Hard`:** O1 gains `¬ OppLater j j′ a a′ ∧ ¬ OppLater j′ j a′ a` (X-M4-1), and each O2 disjunct gains `¬ (Early ∧ SkipsLast)` of its running word and the other word (X-M4-2).
- **`H1TOneFlip`'s second clause** reads `¬ Stuck` (it read `¬ Run2`), and **`H1TRunningWords`'s** reads `Stuck` (it read `Run2`). `OppLater`'s docstring now allows a block-1 running word as its first word; its body did not change.

| Pin | What it says now |
|---|---|
| `h1tOneFlip` | Stronger. It adds the half-salt clause for the O1 pairs with opposite signs in a lane where one column is at least 36, for an `Early` block-2 running word against every word that skips slice `T − 1`, and non-constancy on half the salts for every `Early` word |
| `h1tDistinctLive`, `h1tRunningOfDistinct` | The narrower `H1TRunningWords` is still equivalent to `DistinctLiveH1T` |
| `h1tGammaRunning` | `H1TGamma` under the narrower `H1TRunningWords` |
| `tth1tAllRight` | As in §17.1 |

**The argument** (`H1TFlipProofs.lean`; only L1 to L4, L7 and `rnErr`, through `h1tSlice`, `trunc14Cell`, `trunc14Mono`, `h1tChainMono`, `run_bound` and `rn_err_small`):
- **X-M4-1** (`pair_sep`'s O1 branch). At one position `q`, `OppLater` either way round is `sep_opp_run` with `p = q`: the column whose lane is at least 36 moves `R_q` strictly, and the other moves weakly the other way.
- **X-M4-2** (`run_last_chain`, `run_early_moves`, `sep_early`). Flip lane `k` of slice `T − 1`.
  - `I_(T−1)` moves by more than `64F·|t| − 256F` (`fresh1_flip`, `tv_move_ge`).
  - For `T − 1 ≤ p ≤ 2T − 2`, `R_p` reads slice `T − 1` only through `I_(T−1)`, since `I_T` to `I_p` read slices 0 to `p − T`.
  - Each of the `p − T + 2` roundings from `R_(T−1)` to `R_p` takes at most 512 of the move (L4 through `rn_sep`; `run_sum_lt` puts block 2's sums below `2^33`).
  - With `|t| ≥ 32·(p − T + 2) + 4` and `F ≥ 1/4`, `64F·|t| − 256F ≥ 2048F·(p − T + 2) ≥ 512·(p − T + 2)`. So `R_p` moves strictly, and a word that skips slice `T − 1` stays.

**The shares** (exact over the 88,412 tuples; they match the red team's):
- **O1:** 55,657,938 unordered column pairs (1.424%) before M4c, and 55,066,938 (1.409%) after, so 591,000 fewer.
- **`Early`:** from 0 to 12 block-2 positions per column, 6.98 on average. That is 99.6% of the block-2 running positions at `T = 3`, 58% at `T = 14`, 5.0% at `T = 142`, and 2.5% at `T = 283` (`k = 8,192`).

**What `H1TRunningWords` now carries.** On a legal unit and row, take two distinct credited words, `a` of column `j` and `a′` of column `j′`. They are distinct functions of the salt in these cases:
- **O1:** they are block-1 running words at one position, of columns whose tuples are less than 72 apart in every lane and have opposite signs only where both are 32 in magnitude.
- **O2:** `a` is a block-2 running word `R_p` and `a′` is one of §15's list.
  - If `R_p` is `Early`, only the entries of that list that read slice `T − 1` remain. Those are the block-2 running words, and `I_(T−1)` and `R_(T−1)` of a column without an opposite-signed lane (for `R_(T−1)`, without one where it is at least 36).
- **Non-constancy:** no `Stuck` word is constant. That is a block-2 running word `R_p` whose column's largest lane is below `32·(p − T + 2) + 4`.

**What M4c does not establish:** the rest of `Hard` and `Stuck`. `HalfApartH1T` for those pairs and words, and `TTH1T` at any `γ < 1` with useful `η`, are also not established. X-M4-3 stands: `Hard` reads neither the row nor `F`, so 72, 36 and `32·(p − T + 2) + 4` are the `F = 1/4` worst case.

## 18. H-1T: the cross-column late pairs in the exact-512 regime (29 Sep 13:45Z; the five theorems and their ten definitions granted by red team Phase 19p (bc-89770364, 13:26Z, v2.37); granted, not pinned (14:29Z): pin when used)

The Lean worker (bc-5382063c) proved `H1TCrossLate` (the staged statement of `H1TGapStaging`) in one regime, `Exact512`, in five theorems. **Their named statement reviewer granted the five records and the ten definitions they add** (Phase 19p, bc-89770364; `internal/pouw/new-crypto/red-team.md` v2.37, §19p.6, which records the hashes). **They are granted, not pinned; pin when used.** The requester's correction (13:27Z) pins them only when the k-bounded `DistinctLiveH1T` proof or a 32,768³ γ claim uses them, and neither does: the bounded target is a blocker (`internal/pouw-fp8/h1t-running-words-blocker.md` §7), and no 32,768³ claim rests on them.
- **Trusted file:** `Pouw/Fp8Atom/H1TCrossLate.lean`, the ten definitions, text and namespace unchanged from `H1TCrossLateStaging` (X-CL-2). It is a `layers` entry of `lean-audit.json` that imports only `H1TLemmas` (and through it `H1T` and `H1TVec`), and it is built and audited.
- **Proofs:** `H1TCrossLateStaging.lean`.
- **When pinned,** `--update` writes the records 19p.6 granted. At 13:45Z it did: the five type hashes, the ten definition hashes, the module digest `2e2b3520…` and the reads counts (7, 115, 115, 108, 112) all matched (`internal/pouw-fp8/lean-atom-crosslate-update.txt`). Those records were then dropped. `lean-audit.json` has 323 pins, and its 323 earlier records are byte-identical to before 13:45Z.
- None of the five takes an assumption.

**The definitions** (`H1TCrossLate.lean`, namespace `Pouw.Fp8Atom.H1T.CrossLate`):
- **The finite model.** `TagSalt` is one slice's tag fields: three sign bits and three mantissas. `tagMul n m = ±(8 + m)` is a tag lane's value over `32F` at `F = 1/4`, and `q32 c σ` is a quiet slice's block-1 word over 32, for tag values `32·c`. `rnd512 p u` is the number of 512-steps one rounding adds to `512·a` for an increment `32·u` (`p`: `a` odd), and `two512` the number two roundings add. `cross512 p p′ c c′ s` is the difference of two columns' 512-steps over the two slices with tag fields `s`.
- **`CrossLateResidue512`:** for `c ≠ c′` with `|c_k| ≤ 14` and either parities, `cross512` is not constant in the two slices' tag fields.
- **`Exact512 U i j`:** `T ≥ 3`; the row's and column `j`'s real codes are 0 from `29(T − 2)` on; column `j`'s tag values are multiples of 32; at the zero salt `R_(T−3) = 512·a` with `2^23 + 2^9 ≤ a ≤ 2^24 − 2^9`; and every block-2 word of slices `0..T−3` is a multiple of 512.
- **`H1TCrossLate512`:** on a legal unit, two running words of row `i` of different columns, both at positions from `T − 1` on and both columns in `Exact512`, are different functions of the salt.
- **`absorbUnit`:** §4 of the blocker's unit: `k = 32,768` (`T = 1,130`), `x = b = 448` on slices `0..1127` and 0 on slices 1128 and 1129, 23 columns.

All five are `Pouw.Fp8Atom.H1T.CrossLate.<theorem>`.

| Theorem | Statement | Reads |
|---|---|---|
| `crossLateResidue512` | `CrossLateResidue512`. Tag sums at least 2 apart are separated by the salt with mantissa 7 and signs against the difference, against all its signs flipped; the rest by a kernel `decide` over 1,032 cases | the finite model |
| `h1tCrossLate512` | `H1TCrossLate512` | `Exact512`, `Unit.word`, `Unit.Legal`, `posIdx` |
| `crossLate_of_exact512` | `H1TCrossLate`'s conclusion for its pairs with both columns in `Exact512`, without its `¬ OppLater` | `Exact512`, `Run2`, `posIdx`, `Unit.word`, `Unit.Legal` |
| `absorb_exact512` | columns 21 and 22 of `absorbUnit` are in `Exact512` | `Exact512`, `absorbUnit` |
| `absorb_distinct` | `absorbUnit`'s `R_2257` of columns 21 and 22, equal on every salt with the blocker's tag fields, are two different functions | `absorbUnit`, `Unit.word` |

**What these theorems do not establish.** The regime is thin: it is **empty for `k ≤ 19,430`** (Phase 19p, X-CL-4), which covers both γ shapes (8,192³ and 16,384³), so it discharges none of their pairs and moves no γ figure. `H1TCrossLate` outside the regime, `RnMonoChainGap`, `H1TLastSliceSplit` and the reduction of `H1TRunningWords` to them are not established. `H1TRunningWords` and `DistinctLiveH1T` stay named assumptions, and γ₀ = 1/400 stays.
