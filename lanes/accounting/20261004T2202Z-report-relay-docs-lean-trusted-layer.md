---
id: 20261004T2202Z-report-relay-docs-lean-trusted-layer
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/lean-trusted-layer.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/lean-trusted-layer.md`, sha256 `a0e9f9426d9515e494c4659e39f4343d67530d3c2ce03eeb12e2ce978759a7c4`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Lean trusted layer for POUS: reviewer guide

Code: [lean/pous](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/lean/pous/README.md). It uses Lean `v4.34.0` with Mathlib `5ed2965`, the same pin as Verity's Flock packages. The trusted statements are 1,877 lines: `Pous/Game`, `Pous/Model`, `Pous/Accounting/{Params,LemmaA}.lean`, `Pous/Assumptions.lean` and `Pous/Pinned.lean`. There are 49 pinned statements, of which thirteen were added on 28 Sep 2026 (ten for P2 and M1, and three for P3 with a concrete `H`) and three on 29 Sep 2026: P2's margin rows, pinned under the P2 v1 freeze (default, Daniel deferred, 2026-09-29). Six of the thirteen, plus the model files `Pous/Model/M1p.lean` and `Pous/Model/P3Chain.lean`, were added after the snapshot synced to the repo in PRs #162/#183; see the table below. **Accepted on 29 Sep 2026** (red team GO; Daniel deferred review to coordinator, 2026-09-29), and landed in Verity's `protocols/pous/lean` by [PR #428](https://github.com/danielreuter/verity/pull/428) with their proofs in `PousProofs`: the three concrete-`H` P3 pins, the nine band pins (with `Pous/Model/BandChain.lean`, `Pous/Model/PubEncoder.lean` and `Pous/Accounting/PubMeets.lean`), and the dense deployment re-pinned from `k = 107` to `k = 111` (`ChainDenseMeets111`). This store's `lean/pous` does not carry the band pins, the public-encoder pins or `ChainDenseMeets111`; their code home is Verity's. Review the statements; the proofs are checked by machine.

Checks:

- `check.sh` passes: 13 audited theorems using only Lean's three axioms, a from-scratch kernel replay (`leanchecker --fresh`), the grader's positive control, and rejection of all 9 negative controls. The red team's two exploits are among those controls.
- Verity's `tools/lean/audit.sh` with its kernel replay passes too. That needed two local fixes to its PR #112 branch; see the reply to the coordinator.

The [red-team review](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/lean-trusted-layer-review.md) returned NOT GRANTED. F1 is fixed, F2 and F3 are fixed provisionally, and F4 and F5 are documented below.

## Framework

- **Verity's Flock-soundness conventions**, since Verity is the likely code home:
  - the same toolchain and Mathlib pin, with `autoImplicit` off;
  - no `axiom` anywhere: an assumption is a named `Prop` hypothesis (`Pous/Assumptions.lean`: Lemma A as a hypothesis and Conjecture B1′; the invertible-labels assumption was retracted when N10 was refuted);
  - `CheckAxioms.lean`, with one `#print axioms` line per headline theorem;
  - the Game/Model/Accounting split, with `sorry` targets kept out of the default build;
  - probabilities as exact uniform fractions over finite types in `ℝ≥0∞`, as in Flock's `prCoin`.
- **No VCVio.** Its oracle computations issue queries one at a time; `Prog` counts parallel rounds, in about 30 lines.
- **From `proofs-harness`:** pinned statements, a grader, and negative controls. The differences:
  - the allowed axioms are Lean's three only, compiled into the grader;
  - Lean `v4.34.0` instead of `4.32.2`;
  - several pinned `Prop`s, and submissions may import `Mathlib.*`;
  - a `TRUSTED.sha256` manifest;
  - a structural trust boundary around the grader, described next.
- **The grader boundary (F1).** The red team showed that compile-time IO in a submission could rewrite the grader's inputs or the grader itself, then restore them. Now:
  1. `grade.sh` first checks that unprivileged user namespaces exist; if not, it exits 2 as an environment error. It then builds the trusted layer and the grader, and records hashes of the grader binary, `lean`, the trusted sources and every `.olean` on the grader's `LEAN_PATH`, Mathlib and the toolchain's core included (second-pass findings G1 and G2).
  2. It compiles the submission with `lean` in a scratch directory, inside user, mount, PID and network namespaces where every other mount is read-only, so compile-time IO can write nothing else, and every process it starts dies with the namespace.
  3. It re-checks the hashes.
  4. The grader loads the submission's `.olean` as data, without running its code, and rejects anything that asks the kernel to run compiled code. It replays every new constant through the kernel, checks `solution` against the pinned constant with the kernel's `isDefEq`, and collects axioms from the replayed environment.

## Definitions

| Lean | Models |
|---|---|
| `Bits n`, `pr P` | sizes in bits; `Pr` is the fraction of a finite uniform space |
| `IdealModel` (`Ω`, `answer`), `plain`, `randomOracle` | a primitive drawn uniformly from `Ω` at setup; the public reaches it only by queries. `plain` has no primitive, so games there are information-theoretic |
| `Prog`, `Bounded D Q`, `RoundBounded D q` | a parallel oracle machine: rounds of simultaneous queries, with free local computation and memory. Bounds: `D` rounds and `Q` queries in total, or `q` per round, on every primitive |
| `Scheme` (`n t B ℓ`, `Coins`, `enc`, `dec`), `Correct`, `SpaceBound X`, `CodeHoldsW` | `enc` is trusted, sees the whole primitive, and has its coins erased. `dec` is public (queries only) and bit-exact. `B·ℓ + t ≤ X·n`, and `n ≤ B·ℓ` |
| `Preprocessor`, `SimResponder`, `SeqResponder`, `simAccepts`, `seqAccepts`, `AuditSecure` | the timed audit game with perfect isolation |
| `INC`, `TimedINC`, `ProdResponder`, `p₀` | the report's §2–3 names |
| `Params`, `stateBound ρ = ⌊ρ·B·ℓ⌋`, `Meets` | ρ = 18/19, δ = 1/100, X = 21/20, `εMax = 2^-128`. `Meets` = `ε ≤ εMax`, correct, `CodeHoldsW`, the space bound, and `AuditSecure` at `⌊ρ|C|⌋` bits with bound `δ + ε` |
| `perms`, `m1`, `codeEquiv` (`Model/M1.lean`) | model M1: `B` independent ideal permutations of `Bits ℓ`, forward queries only; block `j` is `Π_j⁻¹(W_j)`, no `pp`, no coins |
| `bitsEquiv`, `bitsVal`, `bitsOfNat`, `permAct`, `permsp`, `m1p` (`Model/M1p.lean`; **added after the snapshot in PRs #162/#183, pending Daniel's review**) | model M1 on `[0, p)`: `B` independent uniform permutations of `Fin p` acting on `Bits w` by numeric value (bit `i` has weight `2^i`), with values `≥ p` fixed; each block's `b` payload bits are zero-extended to `w` bits, block `j` is `Π_j⁻¹(W_j)`, and the decoder reduces mod `2^b` |
| `Pous.Sponge.{iv, padBlk, Tweak, domP3, parentsDesc, ovR, ovH, ovStep, ovAbsorb, ovKey, P3COmega, p3ChainModel, keyP3c, c1c, c2c, topLabelC}`, `Pous.ColumnAware.basePath`, `Pous.P3Column.{bandExtra, bandGraph}`, `Pous.P3Meets.{tagR, WlabW, WbitsW, WsegW}`, `Pous.P3Concrete.{pi2Of, pInvOf, decodeC, p3SchemeC, p3SchemeNC}` (`Model/P3Chain.lean`; **added after the snapshot in PRs #162/#183, pending Daniel's review**) | P3 with a concrete `H`, in the two-permutation model `p3ChainModel`: a tweakable ideal permutation `P` of labels (an independent uniform permutation per tweak `(tag, layer, node)`) and an untweaked ideal permutation `Π₂` of `2m + 512` bits, both queried both ways. `H` is the overwrite chain on `Π₂` (`ovKey`): each call `(r, h) = Π₂(block ‖ h)` drops `r` and chains `h`, and the key is the pad call's `r`. Labels are P3's two layers (`c1c`, `c2c`) on the band graph `bandGraph n k`; segment `s` is keyed by `salt ‖ u64(s)` (`tagR`). The copies are verbatim, with each source namespace `PousX` renamed `Pous.X` (the `Pous.Dense` precedent). `P3COmega`'s `Fintype` and `Nonempty` instances are a definition and a theorem, local instances for `p3ChainModel` only |
| `histCount`, `gammaM1`, `logHistGammaM1/M2`, `A7Row` (`Accounting/LemmaA.lean`) | `|Hist| = Σ_{j<k} B^j`; Lemma A's bound `2^S·C(B,g)·Σ_{h≤g} C((g+1)T,h)/M^g` (M2: identity factor `g!/(g−h)!`, pool `(M−g)!/M!`); A7′'s certified log form |
| `Assumptions.LemmaA sch S D Q g Γ G` | Lemma A per run, as a hypothesis: on the good setups `G` (`True` in M1, `Dist` in M2/M3), every `S`-bit state and per-block `(D, Q)` responder is right on `≥ g` blocks with probability `≤ Γ`. A2 proves it for M1 |
| `Assumptions.B1Prime sch Mdom S D Q k` | Conjecture B1′: `sch`'s sequential audit obeys M1's completion bound with an `Mdom`-point domain. For `m1` at `Mdom = 2^ℓ` it follows from A2 and A3′; proved for all parameters on 28 Sep (`PousA2M1.b1prime_m1`, `lean/submissions/efficient-crypto/a2/`) |
| `HashChain.chain` | B3's tweaked chain `x_{i+1} = H(i, x_i)` |
| `DRG.*` (`Model/Pebbling.lean`) | Fisch's stacked DRGs: `DepthRobust`, `StackedEdge`, `DisjointPaths` (the superconcentrator, as its disjoint-path property), `Unpebbled`, and the white/green game `Available`, `IsPebbling` |
| `Labelling.*` (`Model/Labelling.lean`) | Pietrzak's one-way data-carrying labels `ℓ_i = H(i, ℓ_par(i)) ⊕ d_i` on a `TopoDAG`, greedy pebbling `reach`, `PebblingHard` |
| `Invertible.*` (`Model/Invertible.lean`) | P3's two-layer invertible labels: `p3Model` (an `H`-oracle and one ideal permutation `P` of `m`-bit labels, with `P` and `P⁻¹` queryable), `c¹ = P(W ⊕ H(0, ·))`, `c² = P(transpose(c¹) ⊕ H(1, ·))`, `topLabel`, the `K_{n,n}` connector, and `WhiteGreenHard` (white/green pebbling hardness, black pebbles only) |
| `Dense.*` (`Model/Dense.lean`) | the dense single-layer scheme S1: the complete DAG, the label-shaped random oracle, `denseScheme` with `C_i = H(i, C_{<i}) ⊕ W_i`, `t = 0`, no coins, rate 1 |
| `Sampled.seqState` (`Model/SampledAudit.lean`) | the state a sequential responder reaches after a history of indices |
| `Pinned.*` | the graded statements (below). `KFloor` (k = 86) is the grader's positive control |

## Quantifier order

- **`AuditSecure`, simultaneous:** ∀ `W`, ∀ `A₁ : (W, pp, C, ω) → {0,1}^S`, ∀ `(D, Q)`-bounded `A₂(W, pp, σ, I)`: `Pr_{ω, r, I}[A₂ returns C_I] ≤ δ + ε`.
- **`AuditSecure`, sequential:** the same, except that each round is its own `(D, Q)`-bounded `step(W, pp, j, σ_{j−1}, i_j) ↦ (block, σ_j)`, and every `σ_j` has `S` bits.
- **`INC(β, π)`:** ∀ `W`, ∀ `Cmp(W, pp, C, ω) → {0,1}^β`, ∀ `Exp(W, pp, w, ω)`: `Pr_{ω, r}[Exp = C] ≤ π`. In `TimedINC D Q`, `Exp` is `B` programs `Exp(W, pp, w, i)`, each `(D, Q)`-bounded.
- **`Theorem1ii(Timed)`:** ∀ model, scheme, `D Q β S k π`, if `(Timed)INC` holds, then ∀ `W A₁ A₂′`: `Pr_{ω, r, I}[∀ j, A₂′(σ, i_j) = c_{i_j}] ≤ π + max(p₀, 0)^k`.
- **`A3Prime` (A3′):** ∀ model, scheme, `S D Q k g Γ G`, if `LemmaA sch S D Q g Γ G`, then ∀ `W A₁` and sequential `A₂`: `Pr_{ω, r, I}[pass] ≤ ((g−1)/B)^k + |Hist|·Γ + Pr[¬G W]`. `A3PrimeLam` replaces `|Hist|·Γ` by `2^-λ'` under `|Hist|·Γ ≤ 2^-λ'`.
- **`B2Stacking`, `FischClaim13`:** the graph, depth robustness and connectors first; then ∀ black and red pebbles within budget; then ∃ the path (Claim 13: ∃ a set `E` of `≥ εn/2` endpoints).
- **`B5ExPostFacto(Bounded)`:** ∀ graph, challenges, data `d` (fixed before the oracle), hardness; ∀ `A₁ : H → {0,1}^m`, ∀ bounded `A₂(σ, c)`: `Pr_H[A₂ answers ≥ k challenges] ≤ N·2^m·(Q_tot²/2^w)^{s+1}`.
- **What the order implies.** `W` is fixed before the primitive and the coins. Strategies may depend on `W` but are fixed functions before setup, and deterministic adversaries suffice.

## Waiting on Daniel (provisional in the Lean)

- **F2, `pp` accounting.** `pp` is free at the audit, so under `|C| + |pp| ≤ 1.05|W|` alone, a scheme can park `W` in `pp`, decode from `pp` and fill `C` with noise. The red team's `junk` does exactly this and met the old `Meets`. `Meets` now also requires `|C| ≥ |W|`, i.e. `|pp| ≤ 0.05|W|`, and `junk_not_meets` confirms `junk` fails. The alternative is to charge `pp` into the state bound.
- **F3, `ε_crypto`.** Any `ε ≥ 1 − δ` made the audit clause vacuous. `Meets` now requires `ε ≤ 2^-λ` with λ = 128 (`not_meets_eps_one`); the problem statement doesn't fix this bound.
- **F5, reveal semantics.** Simultaneous reveal gives one `(D, Q)` budget for all `k` answers, while sequential gives `(D, Q)` per answer. So a construction could pick `.simultaneous` to look more secure. Which `Reveal` a graded `Meets` may use waits on the per-answer versus shared deadline decision.

## Choices that could be wrong

1. **`W` is independent of the primitive.** A real adversary knows the concrete hash, so constructions need a salt drawn after `W`.
2. **Preprocessing is unbounded and sees all of `ω`**; the `2^λ` work bound isn't modeled. This is conservative in ideal models, but it means standard-model schemes can't be proved secure here (`plain_short_coins_insecure`); their assumptions would enter as named `Prop`s.
3. **Only queries cost.** The layer covers attacks that go through the primitive.
4. **There is no `vk`.** A block is accepted iff it equals the true block, i.e. tags are ideal. Digest responses aren't modeled; they need an extraction step.
5. **Under sequential reveal** the next index arrives when the answer returns, so any real gap must be charged to `(D, Q)`, and the round index comes free.
6. **`TimedINC` is per block.** A whole-expander `(D, Q)` bound would make `Theorem1iiTimed` false: the bridge's expander has depth `D` but work `B·Q`.
7. **F4: `Theorem1ii` (untimed) can't be instantiated.** For a correct scheme, `fibre_count` forces `β ≲ 0.05·n`, so `INC` can't hold at the operating point in this model. The reduction is sound, but only the timed form applies to a scheme.
8. **`dec`'s cost and block-locality are unconstrained.** Names: the report's `B` blocks of `ℓ` bits are the problem statement's `N` blocks of `b` bits.
9. **Locality (deferred)** would add a query interface that reads a preprocessed string, with a budget of `βΔ` bits per answer, plus digest responses.
10. **Every model is single-segment.** Each pinned statement plays one segment against a fresh uniform primitive drawn after `W`, which idealizes a fresh per-segment salt. None of the models puts a salt or segment index in its oracle queries; they tag only the node or step. So under one shared hash, segments with equal `W` (all-zero weights, say) get identical codewords, which an adversary stores once. A deployment must therefore salt every segment, with the salt and segment index in every oracle query, and any multi-segment statement must model that. This applies to:
   - `denseModel` (`DenseMeets`);
   - `Labelling` (B5 and the stacked audits);
   - M1 (`perms`/`m1`, and so A2, A3′ in M1, A7′ and `M1Meets`);
   - `HashChain` (B3), where the start `x₀` can act as the salt.

   The one-segment statements stay true.
11. **H is a monolithic random oracle (narrow-state H).** Every result that models the hash H as a random oracle with `m`-bit outputs holds only in that model:
   - B3's chain (`HashChain`);
   - B5 and the stacked audits (`Labelling`);
   - `DenseMeets` (`denseModel`);
   - P3's labels (`p3Model`), N10′ included. The band certificate itself is pure combinatorics over the column game, so it is unaffected.

   A real hash whose `m`-bit output comes from a narrower internal state breaks the instantiation. The adversary stores each label's pre-squeeze state and regenerates the labels from those states alone: with SHAKE's 1600-bit state, Dense in one round from about 20% of `C`, and P3 in three rounds from about 39% ([p3-cryptanalysis](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-cryptanalysis.md), "Narrow-state H"). This is the Ristenpart–Shacham–Shrimpton limit: indifferentiability does not carry over to storage games, so no ideal-hash result transfers to a concrete hash by citation. So **"no named assumption" for `DenseMeets` means within the ideal-hash model only.** The planned fix is H as a wide sponge (state at least `m` bits) over an ideal permutation, re-proved in the ideal-permutation model; a pilot has started. The Lean statements are unchanged.

## Pinned statements (`Pous/Pinned.lean`)

"As drafted" means the binders and conclusion are the draft's, verbatim; this was checked textually, and every graded proof below also proves the draft by kernel `isDefEq`. `PousTargets.lean` restates each as a `sorry` target under its draft name.

| Pinned | Source | Status (grader) |
|---|---|---|
| `KFloor` | `k = 86` | PASS (positive control) |
| `Theorem1ii`, `Theorem1iiTimed` | report Theorem 1(ii) | PASS, PASS |
| `Theorem1iTimed`, `Theorem1iiSeq`, `Theorem1iiiTimed` | as drafted | PASS, PASS, PASS |
| `FibreCount`, `A1CompressionCard`, `A1CompressionPr`, `A6RederiveUntimed`, `A6RederiveTimed` | as drafted | PASS ×5 |
| `A2LemmaAM1` | as drafted | PASS (28 Sep; `lean/submissions/efficient-crypto/a2/`) |
| `A5RabinGcd` | as drafted | open |
| `A3Prime`, `A3PrimeLam` | the prover's A3′ (`track-a/A3Prime.lean`), superseding the A3 draft | PASS, PASS |
| `A7Params` | A7′, certified log form | open |
| `M1Meets` | `m1_meets`, conditional on B1′ | PASS (28 Sep; B1′ now holds for `m1`) |
| `M1MeetsUncond` | `M1Meets`'s conclusion, **unconditional** | PASS (28 Sep) |
| `P2MeetsM1`, `P2MeetsM1W8192` | P2 parameters in abstract M1, **conditional** on `A2LemmaAM1` (`efficient-crypto/p2/`) | PASS, PASS (28 Sep) |
| `P2MeetsM1Uncond`, `P2MeetsM1W8192Uncond` | the same two conclusions, **unconditional** (`efficient-crypto/a2/`) | PASS, PASS (28 Sep) |
| `P2MeetsM1B19Uncond`, `P2MeetsM1FamilyUncond` | 16,448 bits at the POUS MVP's `2^19` blocks, and at every block count from `2^8` to `2^23`, **unconditional** (`efficient-crypto/a2/P2Rows.lean`) | PASS, PASS (28 Sep) |
| `P2MeetsM1pB19Uncond`, `P2MeetsM1pFamilyUncond`, `P2MeetsM1pW8192Uncond` | the same rows on P2's exact domain `[0, p)` (`Model/M1p.lean`), for every payload width in range, **unconditional** (`efficient-crypto/p2-domain/`). **Added after the snapshot in PRs #162/#183; pending Daniel's review** | PASS ×3 (28 Sep) |
| `P2SlackB19Uncond`, `P2SlackFamilyUncond`, `P2ErrorSplitB19Uncond` | P2's exact-domain rows against an adversary with `λ·B` extra state bits (λ = 64, 128, 256; k = 95/104/127 at `2^19`, 96/105/128 over `2^8`–`2^23`), and the error split with the ideal-model ε at most `2^-129` (`efficient-crypto/p2-margin/`). **Pinned 29 Sep under the P2 v1 freeze (default, Daniel deferred); after the snapshot in PRs #162/#183** | PASS ×3 (29 Sep) |
| `P3ConcreteMeets64`, `P3ConcreteMeets14GB`, `P3ConcreteMeets64D12` | P3 with a concrete `H` (`Model/P3Chain.lean`), 64 KB labels, `k = 106`: one segment and 971 segments (14.005 GB) on `B(220, 12)` at `D = 10`, and the `D = 12` fallback on `B(220, 16)`, **unconditional** (`p3-concrete-multi/grading/`). **Accepted**; reviewer: red team GO; Daniel deferred review to coordinator, 2026-09-29. In Verity by [PR #428](https://github.com/danielreuter/verity/pull/428) (`PousProofs.P3Concrete*`) | PASS ×3 (28 Sep); accepted; audited in Verity (PR #428) |
| `BandChainMeets64`, `BandChainMeets64D5`, `BandChainMeets64D12` | the band chain on `2^9` blocks of 64 KB labels, `k = 111`, `D = 5`: every in-degree `d ≥ 5`, and `d = 5`, `d = 12`, **unconditional** (`sponge-dense/ChainEPFV6FinalBand64.lean`: `band_meets_64_final`, `band_meets_64_d5_final`, `band_meets_64_d12_final`). **Accepted**; reviewer: red team GO; Daniel deferred review to coordinator, 2026-09-29. In Verity by [PR #428](https://github.com/danielreuter/verity/pull/428) (`PousProofs.BandChainMeets64*`) | graded: PASS ×3 (28 Sep; `sponge-dense/trusted-draft/install/band-grading/GRADE.txt`); accepted; audited in Verity (PR #428) |
| `BandMultiMeets14`, `BandMultiMeets14K106` | the band on 448 segments (229,376 blocks of 64 KB, 14 GiB), every `d ≥ 5`: `k = 111` with per-segment and with global salts, and `k = 106` per segment, **unconditional** (`sponge-dense/ChainEPFV6FinalBand14.lean`: `band_meets_14_final`, `band_meets_14_k106_final`). **Accepted**; reviewer: red team GO; Daniel deferred review to coordinator, 2026-09-29. In Verity by PR #428 (`PousProofs.BandMultiMeets14*`) | graded: PASS ×2 (28 Sep), as above; accepted; audited in Verity (PR #428) |
| `BandMultiMeetsFamily` | the band at every segment count `N` with `1 ≤ N ≤ 2^64` (`N·512` blocks of 64 KB), every `d ≥ 5`, `k = 111`, with per-segment and with global salts; `BandMultiMeets14` at `N = 448`, **unconditional** (`band-multi/BandMultiFamilyFinal.lean`: `band_meets_family_final`). **Proposed** 29 Sep 2026 (A14); reviewer: the statement red team (`bc-22298e90`) GO (§58), on a red-team read GO (`internal/p3-instantiation/band-family-pin-redteam-verdict.md`); pending acceptance. For Verity: [PR #431](https://github.com/danielreuter/verity/pull/431), stacked on PR #428 (`PousProofs.BandMultiMeetsFamily`) | graded: PASS (29 Sep; `band-multi/family-pin/GRADE.txt`); proposed |
| `ChainDenseMeets64` | the overwrite-chain dense scheme on `2^9` blocks of 64 KB, `k = 111`, `D = 5`, **unconditional** (`sponge-dense/ChainEPFV6FinalDense.lean`: `chain_meets_64_final`). Not the `DenseMeets` pin. **Accepted**; reviewer: red team GO; Daniel deferred review to coordinator, 2026-09-29. In Verity by PR #428 (`PousProofs.ChainDenseMeets64`) | graded: PASS (28 Sep), as above; accepted; audited in Verity (PR #428) |
| `ChainDenseMeets111` | **the dense deployment, re-pinned from `k = 107` to `k = 111`**: the overwrite-chain dense scheme at the deployment point, `2^16` blocks of 1 KiB, `D = 64`, `Q = 2^20`, `k = 111`, **unconditional** (`sponge-dense/ChainEPFV6FinalDense111.lean`: `chainDenseMeets111_final`). The `k = 107` target (`SpongeDense`'s `ChainDenseMeetsPinned`) stays open; the argument does not reach it. Strictly weaker than it by four challenges. **Accepted**; reviewer: red team GO (§§53–54); Daniel deferred review to coordinator, 2026-09-29. In Verity by PR #428 (`PousProofs.ChainDenseMeets111`) | accepted; audited in Verity (PR #428) |
| `BandPubMeets64`, `BandPubMeets14`, `BandPubMeets14Global` | the public-encoder forms of the 64 KB and 14 GiB band rows, **unconditional** (`sponge-dense/ChainEPFV6FinalPub.lean`), under the four deployment conditions of the review's §48. `PubMeets` and `exactCheck` enter the trusted layer (`Pous/Model/PubEncoder.lean`, `Pous/Accounting/PubMeets.lean`), with bc-c0ee31ee's lane change (`trusted-draft/install/pub-lane/`). **Accepted**; reviewer: red team GO (§§53, 55); Daniel deferred review to coordinator, 2026-09-29. In Verity by PR #428 (`PousProofs.BandPub*`) | accepted; audited in Verity (PR #428) |
| `B1IndepSet`, `B3Chain` | as drafted | PASS, PASS |
| `B2Stacking` | the prover's draft (Fisch Claim 12, strengthened) | PASS |
| `FischClaim13`, `FischClaim14` | as drafted (Claim 14 with the white/green game) | PASS, PASS |
| `B5ExPostFactoBounded`, `B5ExPostFacto` | as drafted (Pietrzak Thm 10 + §8) | PASS, PASS |
| `TransposeMixing`, `ReverseNeedsAllChildren` | as drafted (N10's two core lemmas) | PASS, PASS |
| `N10Refuted` | `¬ InvExPostFactoTwoLayer`, N10 as drafted (`p3-forward/Refutation.lean`) | PASS: **N10 is false** |
| `SampledAuditProd`, `SampledAuditSeq`, `SampledAuditSim` | as drafted (`b5/SampledAudit.lean`) | PASS, PASS, PASS |
| `StackedAuditSeq` | as drafted | PASS |
| `StackedAuditOnePercent` | as drafted; **conditional** on a concrete depth-robust graph, audit clause only | PASS |
| `DenseMeets` | as drafted (`dense/DenseMeetsDraft.lean`; `PousDense` renamed to `Pous.Dense`) | PASS |

Notes on individual statements:

- **`Theorem1iiSeq`** keeps the union over histories, `(Σ_{j<k} B^j)·π`. The tighter `k·π` (a stopped-process argument) is plausible but unproved: a possible later strengthening.
- **`Theorem1iiiTimed`** drops the report's `−λ` from `p_η`: each seed value gives its own deterministic `(cmp, exp)`, and the seed is averaged only in the analysis. Two caveats: the draft's `lam` is the report's miss parameter `λ'`, not the seed length; and the argument uses that `TimedINC` puts no bound on the compressor, so if `INC` ever limited compressor size, a built-in seed would count as non-uniform advice.
- **`A3Prime`, `A3PrimeLam`** are class (b), the target game (`S` bits at every challenge, `T := Q`), with Lemma A as the named hypothesis `Assumptions.LemmaA` and its good event `G` charged once (`Pr[¬G]`, not `|Hist|·Pr[¬G]`). In M1, `G = True`, and A2 supplies `LemmaA`.
- **`A7Params`** states each row as ∃ `g` rather than at the review's exact `g`. Those `g` are witnesses, but they are the least workable ones, and the review's float solver loses about 10⁴–10⁵ bits at `T = 2^34`. Recomputed with a series expansion, each row has 5,700–45,500 blocks of room below the `((g−1)/B)^k ≤ 1/100` limit. The domain hypothesis `M ≥ 2^2048 − 2^2029` is met by `φ(N)` of a 2048-bit `N` with its top 20 bits set. `S` counts 2056-bit RW–SMS records.
- **`M1Meets`** is about the ideal permutation model M1, with B1′ as a named hypothesis (in M1 it follows from A2 and A3′). A2 was proved on 28 Sep, so B1′ now holds for `m1` at all parameters, `M1Meets` grades PASS, and `M1MeetsUncond` pins its conclusion without the hypothesis. It does **not** transfer to RW–SMS at `λ = 128`: a 2048-bit `N` factors in about `2^112 < 2^128` preprocessing (sms5 F1).
- **The P2 and A2 pins (28 Sep 2026).** Seven pins, plus the proof of `A2LemmaAM1`. The statement reviewer for the seven pins was `statement-review-p2 / bc-d1405c07-5e8a-5efb-8b66-087d4bf697fe`. It gave GO on `P2MeetsM1B19Uncond` and GO WITH CONDITIONS on the other six, with its conditions carried in the docstrings. The same reviewer checked the A2 proof (GO). In plain terms:
  - `A2LemmaAM1` (now proved): a responder that can only evaluate M1's permutations forward, holding an `S`-bit state, gets `g` or more blocks right with probability at most `2^S·C(B, g)·Σ_{h ≤ g} C((g+1)Q, h) / 2^(ℓ·g)`.
  - `P2MeetsM1`: if A2 holds, `2^23` independent forward-only permutations on 16,448-bit blocks (17.2 GB) meet the requirement with 88 sequential challenges and `2^20` queries per answer, at any depth.
  - `P2MeetsM1W8192`: the same with `2^24` blocks of 8,192 bits and 90 challenges (the near-zero-round-trip row).
  - `P2MeetsM1Uncond`, `P2MeetsM1W8192Uncond`: the same two conclusions, with no hypothesis.
  - `M1MeetsUncond`: `M1Meets`'s conclusion (`2^28` blocks of 2,048 bits, 117 challenges), with no hypothesis.
  - `P2MeetsM1B19Uncond`: the POUS MVP's configuration, `2^19` blocks of 16,448 bits, meets the requirement with 88
    challenges and no hypothesis. Storing blocks raw already breaks it at 85.
  - `P2MeetsM1FamilyUncond`: every block count from `2^8` to `2^23` at 16,448 bits (about 0.5 MB to 17.2 GB) meets
    it with 88 challenges and no hypothesis. The proof makes no claim below `2^8`.
- **The exact-domain pins (28 Sep 2026): added after the snapshot synced to the repo in PRs #162/#183, pending
  Daniel's review.** Three pins, plus one new trusted model file, `Pous/Model/M1p.lean`.
  - **Not yet in the repo.** The sync follows once those PRs merge.
  - **Review.** The statement reviewer was `statement-review-p2 / bc-d1405c07-5e8a-5efb-8b66-087d4bf697fe`. It gave
    GO on the model, and GO on the three pins after its docstring fixes, which are applied.
  - **Proofs.** `lean/submissions/efficient-crypto/p2-domain/P2Domain.lean`, by the A2 prover. They use only Lean's
    three axioms, and the rows pay one extra state bit for the domain.

  In plain terms:
  - `m1p B w p b` is model M1 on P2's real domain. `B` independent uniform permutations of the numbers
    `0, …, p − 1` act on `w`-bit strings, and values `p` and above stay fixed. Each block carries `b` payload bits,
    and the code block is the permutation's inverse applied to the payload.
  - `P2MeetsM1pB19Uncond`: the POUS MVP's `2^19` blocks at `p = 2^16448 − 21065` meet the requirement with 88
    challenges and no hypothesis. This holds for every payload width `b` the space bound allows, up to 16,447 bits,
    including the MVP's 16,432 (2,054 bytes). Storing blocks raw breaks it at 85.
  - `P2MeetsM1pFamilyUncond`: the same for every block count from `2^8` to `2^23`.
  - `P2MeetsM1pW8192Uncond`: `2^24` blocks at `p = 2^8192 − 9345`, with 90 challenges, for payload widths up to
    8,191 bits.
  - Primality is never used: `p` enters only as the size of the domain.
- **P2's margin pins (29 Sep 2026): pinned under the P2 v1 freeze** (default, Daniel deferred, 2026-09-29), after the
  snapshot in PRs #162/#183. There are three pins and no new model file.
  - **Review.** The statement reviewer was `statement-review-p2`. It gave GO after its docstring fixes, which are
    applied, and all three grade PASS.
  - **Proofs.** `lean/submissions/efficient-crypto/p2-margin/P2Margin.lean`, by the A2 prover.

  In plain terms:
  - `P2SlackB19Uncond`: at `2^19` blocks, the exact-domain row still holds against an adversary with `λ` extra bits
    of state per block, at k = 95, 104 and 127 for λ = 64, 128 and 256.
  - `P2SlackFamilyUncond`: the same over `2^8` to `2^23` blocks, at k = 96, 105 and 128 (95, 104 and 127 above small
    B). The frozen spec's k = 105 is the 128-bit row.
  - `P2ErrorSplitB19Uncond`: the k = 88 row and the slack rows hold with the ideal-model error at most `2^-129`.
  - What `λ` covers: only leakage that reduces to bounded, reusable per-block advice.
- **The concrete-`H` P3 pins (28 Sep 2026): accepted on 29 Sep 2026** (red team GO; Daniel deferred review to
  coordinator, 2026-09-29). Three pins, plus one new trusted model file, `Pous/Model/P3Chain.lean`.
  - **In the repo:** [PR #428](https://github.com/danielreuter/verity/pull/428), with the proofs in `PousProofs`
    (`PousProofs/Chain/Flat.lean`, generated from the graded P3 solution by `trusted-draft/install/flatten_chain.py`).
  - **Review.** The statement red team (`bc-22298e90-fd61-5062-a836-0b7a423cab8a`) gave GO on the closure and on the
    three statements (`docs/lean-trusted-layer-review.md` §50).
  - **The model file.** It holds verbatim copies of the 27 definitions and one lemma that the three statements read,
    and nothing else. Each source namespace `PousX` becomes `Pous.X`. The graded submissions make the same renaming,
    so the proof is about these constants, and no other part of it is trusted. The lanes' own files keep their `PousX`
    definitions and build unchanged against this layer.
  - **Proofs.** `lean/submissions/p3-concrete-multi/grading/Solution-*.lean`, one per pin. `flatten.py` generates them
    from the 115 modules of the combined chain: bc-58ec406e's `p3-concrete` and bc-4b3abaed's `p3-concrete-multi`,
    with freshness, pebbling, p3-meets, p3-column, thm1-family, sponge-dense and lazy-perm. They use only Lean's
    three axioms, and the closure has no `sorry`. The same finals are audited in their own package
    (`p3-concrete-multi/finals/`), and `leanchecker --fresh` passes over the whole closure.

  In plain terms:
  - `P3ConcreteMeets64`: P3 on 220 labels of 64 KB (one 14.4 MB segment), with `H` the overwrite chain on an ideal
    permutation and a tweakable ideal permutation `P` per label, meets the requirement with 106 sequential challenges,
    10 rounds and `2^20` queries per answer, with no hypothesis.
  - `P3ConcreteMeets14GB`: the same at 971 segments (14.005 GB), with one advice string for the whole store. Security
    is joint over all segments: segment-by-segment bounds do not combine to this.
  - `P3ConcreteMeets64D12`: the fallback, 12 rounds on the band graph `B(220, 16)`, one segment.
  - Scope: the ideal two-permutation model only. Lean proves nothing about a concrete permutation (no Keccak or other
    instantiation of `P` or `Π₂`), decode cost, the wall-clock-to-`Q` calibration, authentication, accounting or fresh
    setup. As for every `Meets` here, `W` is fixed before the primitives are drawn.
- **The band pins (28 Sep 2026): accepted on 29 Sep 2026** (red team GO; Daniel deferred review to coordinator,
  2026-09-29). Nine statements, in Verity's `Pous/Pinned.lean` by [PR #428](https://github.com/danielreuter/verity/pull/428)
  with their proofs in `PousProofs` (`PousProofs.Band*`, `PousProofs.ChainDense*`), beside the dense deployment
  re-pinned at `k = 111` (`ChainDenseMeets111`, §§53–54). Not in this store's `lean/pous`.
  - **Review.** The statement red team (`bc-22298e90-fd61-5062-a836-0b7a423cab8a`) gave GO on the proof closure and on
    six pins: `BandChainMeets64`, `BandChainMeets64D5`, `BandChainMeets64D12`, `BandMultiMeets14`,
    `BandMultiMeets14K106` and `ChainDenseMeets64`. The three `BandPub*` pins are GO only if `PubMeets` and
    `exactCheck` enter the trusted layer, with the four deployment conditions of the review's §48 in their docstrings;
    otherwise they are cited unpinned, through `band_pub_iff_*`. The verdict (about 20:05Z) is in
    `internal/p3-instantiation/band-v6-design-rereview-redteam-verdict.md`.
  - **The trusted model.** `Pous/Model/BandChain.lean` (`fc149e43`, drafted in `sponge-dense/trusted-draft/`), after
    the `P3Chain` precedent: verbatim copies of the definitions the six statements read, each namespace `PousX` renamed
    `Pous.X`, reusing `Pous.Sponge`'s overwrite chain. From `SpongeDense.lean`: `idealPerm`, `dom`, `parentsNF`,
    `absorbed`, `labelOv`, `chainDense`; from `DenseReCert.lean`: `u64`, `tag`; from `BandChainModel.lean`: `bandDAG`,
    `labelG`, `absorbedG`, `chainScheme`, `chainBand`; from `BandMultiModel.lean`: `bandSegDAG`, `segDom`,
    `chainBandSeg`. The pins spell their statements out over these. GO in the review's §53, and in the second review
    (§55). The `BandPub*` pins add `Pous/Model/PubEncoder.lean` and `Pous/Accounting/PubMeets.lean` (drafted beside
    it), with bc-c0ee31ee's lane change (`trusted-draft/install/pub-lane/`), which the proofs in PR #428 use.
  - **The install.** GO in the review's §54, with the grader hardening GO in §57. Landed in Verity by PR #428: the
    model files, the pins, the grader hardening, and the proofs in `PousProofs` in place of the graded solutions. The
    store-side parts of `sponge-dense/trusted-draft/install/INSTALL.txt` (the patch to this store's `lean/pous`, P3's
    re-flatten there) are not applied.
  - **Grading.** All six are graded: `flatten_band.py` flattens the v6 chain into one submission per pin, and each grades
    PASS on a scratch `lean/pous` with the patch applied (`trusted-draft/install/band-grading/GRADE.txt`).
  - **Proofs.** `lean/submissions/sponge-dense/ChainEPFV6Final{Band64,Band14,Dense,Pub}.lean`. Each applies a reviewed
    conditional theorem to the now-proved ex post facto bound (`chainExPostFactoG_v6`, proved in the (c′) band chain
    `ChainEPFV6*.lean`), so its statement is that theorem's conclusion unchanged. They use only Lean's three axioms,
    the closure has no `sorry`, and `leanchecker --fresh` passes over it. `ChainEPFV6FinalBand64Key.lean` proves the
    64 KB statements a second way, through the key-rule form `ChainExPostFactoG'`.
  - **Not proposed as pins.** The bound itself (`chainExPostFactoG_v6`, `chainExPostFacto_v6`) and the band chain's
    internal results (`bandFreshTail_v6`, `v6_pattern_fibers`). They stay graded theorems that the pins cite: pinning
    them would freeze proof-internal definitions into the trusted layer. If the ex post facto bound should be a
    headline, the red team suggests pinning only `ChainExPostFactoG`, with `ChainHard` copied and reviewed.

  In plain terms:
  - `BandChainMeets64`: the band scheme on 512 blocks of 64 KB labels meets the requirement with 111 sequential
    challenges, 5 rounds and `2^20` queries per answer, for every in-degree `d ≥ 5`, with no hypothesis.
    `BandChainMeets64D5` and `BandChainMeets64D12` are the deployment point and the recommended in-degree.
  - `BandMultiMeets14`: the same on 448 segments (14 GiB), both with per-segment salts and with one global salt.
    `BandMultiMeets14K106` needs only 106 challenges, with per-segment salts.
  - `BandMultiMeetsFamily` (proposed): the `k = 111` row at every segment count from 1 to `2^64`.
  - `ChainDenseMeets64`: the overwrite-chain dense scheme on 512 blocks of 64 KB meets the requirement with 111
    sequential challenges, 5 rounds and `2^20` queries, with no hypothesis.
  - `BandPubMeets*`: the same band rows for the public-encoder form of the scheme.
  - Standing conditions: `d ≥ D` (one round more than the in-degree breaks hardness), the ideal two-permutation model,
    and `W` fixed before setup. Lean proves nothing about a concrete permutation, decode cost or the wall-clock-to-`Q`
    calibration.
- **Scope of the P2 and M1 pins, in plain words.** These are results about the abstract M1 model: each block is an ideal permutation that anyone can evaluate forward and no one can invert. They do not cover:
  - physical time: that one square root takes longer than the deadline (SeqRoot), and how many queries fit in the deadline;
  - the prime domain `[0, p)` that the real P2 map works in, as opposed to `2^w` bit strings. The three `m1p` pins
    below now cover it in the abstract model; the M1 pins above do not;
  - concrete accounting: per-block keys and tweaks, tags, packing;
  - the step from the concrete square–mask–square map to independent ideal permutations, which needs fresh keys and tweaks per block (a shared mask with linear tweaks is model M2 and is not covered).

  All of these sit outside Lean, as the band's Feistel-SHAKE instantiation does. The 2048-bit `M1MeetsUncond` row has no concrete scheme behind it: RW–SMS at that size factors within the preprocessing budget, and P2 needs at least about 8,000 bits.
- **`B2Stacking`** is the prover's strengthened form of Claim 12: unpebbled green paths, which Claims 13–14 use.
- **`B5ExPostFacto(Bounded)`** is scoped to **one-way labels**, the standard forward-only pebbling game. It gives no bound for P3's invertible, locally decodable labels (decoding is Fisch's reverse move, Claim 14). A P3 bound with local decoding needs a new reduction, and B5 still needs a bridge from B2's graph model to `TopoDAG`.
- **`DenseMeets` is the first `Meets` with no named assumption, within the ideal-hash model** (choice 11; contrast `M1Meets`, which carried B1′ until A2 was proved on 28 Sep): the dense scheme on `2^16` blocks of 1 KB meets the requirement with sequential reveal, `D = 64`, `Q = 2^20`, `k = 107` and `ε = 2^-128`. Its scope is **security, correctness and rate only, not decode cost**: decoding hashes every earlier block, `Θ(B)` per byte, far from the 2× cost target. It carries the framework's standing ideal-model caveats (label-shaped random oracle; `W` fixed before `H`, so a deployment needs a salt drawn after `W`).
- **The sampled-audit lemmas** turn "except with probability `p`, fewer than `k` blocks are answerable" into an audit bound `((k−1)/B)^t + p` (product), `((k−1)/B)^t + |Hist|·p` (sequential, per history) or `p + ((k−1)/B)^t + t·η` (general simultaneous). `StackedAuditSeq` chains the stacked one-way bound (`b5_stacked`) through the sequential form.
- **`StackedAuditOnePercent` is conditional** on a concrete depth-robust stacked graph (its `hdr`, `hsc` hypotheses; construction path N4, not yet proved) and covers the **audit clause only** of the stacked one-way scheme, not a full `Meets`: at `n = 2^16`, `w = 8192`, `N = 2^17`, `Q = 2^20`, 210 sequential challenges pass with probability at most `1% + 2^-128`. Its `ε = 1/23` is the stacked graph's pebbling deficit, distinct from `ρ`'s `1/19`.
- **N10 is false** (`N10Refuted`, PASS). `InvExPostFactoTwoLayer` was PIEs (ePrint 2018/684) Conjecture 1 at `L = 2`: B5's bound for P3's invertible two-layer labels, with `WhiteGreenHard` in place of `PebblingHard`, width `m = n·wc` and `Q_tot = n(Q + 1) + 2n`. It stays in `Pinned.lean` only as the statement `N10Refuted` negates, and the named assumption `InvertibleLabels` is retracted (`ASSUMPTIONS.md`). The attack is column storage across the transpose ([p3-cryptanalysis](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-cryptanalysis.md) §1). Top label `u` reads only component `u` of each lower label, so the adversary can hold a lower label one column at a time, paying `|U|/n` of a label where white/green pebbling charges a whole pebble. On a graph that meets every hypothesis of Theorem P3 on paper (40% sources plus a complete core), 82% of `C` answers every challenge in 3 rounds. The graded Lean proof (`lean/submissions/p3-forward/Refutation.lean`) uses a smaller counterexample with the same root cause: on an 8-node chain it guesses the missing components, winning with probability `2^-448` against the bound's `≈ 2^-485.8`. Neither attack queries `P⁻¹`, so no inverse-query accounting can rescue the statement. A column-aware restatement, N10′, is being drafted: its game prices lower-label components at `1/n`, and its hypothesis bounds the column saving `X(G, D)` in place of white/green hardness. `TransposeMixing` and `ReverseNeedsAllChildren` stay pinned and proved; they are about decoding lower labels from top labels (the reverse move), which the attack never does.
- **B3 as the construction-paths memo states it, `(D+1)q/M`, is false** (at `q = 0`, and for untweaked chains); `B3Chain` uses the tweaked chain and `(D·q + 1)/M`.
- **Not stated yet:** A2 in M2/M3 (A3′ already takes its `Dist` event as `G`; A7′ has the M2 numbers); B4; N10′ (being drafted); P3 bounds beyond two layers; report Theorem 2.
