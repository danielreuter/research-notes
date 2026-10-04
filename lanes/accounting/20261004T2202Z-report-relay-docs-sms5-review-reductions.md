---
id: 20261004T2202Z-report-relay-docs-sms5-review-reductions
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/sms5-review-reductions.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/sms5-review-reductions.md`, sha256 `0ea64d6f3ed2416c37eb98b8cd88a773b0f3116270c517acdc05cc49c275e176`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# sms5 reductions and redesign: adversarial review

27 Sep 2026. Scope: `sms5/reduction/reduction.md` Theorem 2, and `sms5/redesign/redesign.md` Prop. 1, Theorem A, the design-(a) ⇔ two-root-game (2RG) lemma and §5. The target is the [problem statement](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/problem-statement.md) (λ = 128, preprocessing ≤ 2^λ work). All five checkers, rerun on a scratch copy, reproduce the quoted output (the longest, `rwsms_toy.py`, takes 108 s).

**Bottom line.** The proofs mostly hold; the parameters don't match the problem statement. At w = 2048 the problem statement's preprocessor (2^128 work) can factor N, whose number field sieve cost is about 2^104–2^117. Prop. 1's own adversary then passes every audit from a 1024-bit state. P1 needs w ≥ 3072, which is at the edge, and about 3300–3500 for margin. At 3072, design (a) costs 190 int32/B, above the 150 int32/B prefill budget, so P1's prefill fallback fails as costed. Theorem 2 and Theorem A stand after small repairs. The equivalence of design (a) with 2RG is not exact, and 2RG-C has to be restated.

## Verdicts

| Claim | Verdict | Condition |
|---|---|---|
| Theorem 2 (no fully black-box reduction to a single-stage assumption) | GRANTED WITH CONDITIONS | Only under the convention that R must work for oracles of any running time, which makes T vacuous (F5). It reaches design (a) only with gated tags (F6). |
| Prop. 1 (no information-theoretic theorem for short-secret encoders) | GRANTED | Read "output the secret" as "output a secret consistent with the view". Its corollary, that A₁ must not be able to factor, is exactly what F1 violates. |
| Theorem A (blocks recovered without an inverse hit are B1-bounded) | GRANTED WITH CONDITIONS | Recount the constants (F7); p* moves by less than 10⁻³. |
| Design (a) ⇔ 2RG lemma | GRANTED WITH CONDITIONS | Holds only with a permutation oracle shared by both stages (or a λ-bit PRP key in σ) and a work bound on A₂. It is then neither "perfect" nor permutation-free (F3). |
| §5 residual assumptions of the deployable candidate (w = 2048) | NOT GRANTED | They omit factoring against a 2^128 preprocessor, which fails (F1). |
| §5 cryptanalysis questions | GRANTED WITH CONDITIONS | Right questions; add F1 and F4 (notes below). |

## Findings

| # | Severity | Location | Finding | Witness |
|---|---|---|---|---|
| F1 | Critical | redesign §4 row "store trapdoor … outside the computational model", §5; 2RG-C (A₁ ≤ 2^100); tradeoff §5 RW-IC (A₁ < 2^112 at 2048); construction-paths P1; problem statement "Moduli … 2048–3072" | w = 2048 lies inside the 2^λ preprocessing budget. | The number field sieve estimate L[1/3] gives 2^116.9, or 2^104 cycles anchored on RSA-250. A₁ factors N and keeps p (1024 bits). A₂ computes RWInv, E⁻¹, RWInv in about 4096 squarings per block (`params.py`: "far inside Δ"). 3072 bits: 2^126–2^139 (edge); 3500 bits: 2^134–2^147. |
| F2 | High | reduction §4 RW-IC, with Def. 1's "A₁ unbounded" | RW-IC as written is false at every w, by the same adversary. The usable form is tradeoff §5's (A₁ below the factoring cost); the two statements disagree. | `toy_two_round.py` [0]: a 128-bit state recomputes c exactly. |
| F3 | Medium | redesign §3.3 Lemma and Game 2RG | (i) Design (a) ⇒ 2RG: σ may depend on E at unprogrammed points that A₂ later queries, and 2RG's stages share only σ, so "lazily sampled by whoever needs it" breaks across the stage boundary. (ii) 2RG bounds A₂'s oracle calls but not its work; an unbounded A₂ wins with one Open per block. | A₁ masks its state with E(x₀) at a fixed unprogrammed x₀, and A₂ unmasks it by querying E(x₀): this works in the real game and gives garbage in the simulation. Fix: a shared public permutation patched through Open and Test (≤ 3 calls per E-query), or a PRP key in σ (likely the "+λ"). |
| F4 | Medium (if stacking exists) | redesign §3.3 table, §4 kangaroo rows; `params.py` L_I+ | The kangaroo cost counts only online work. N is shared, so an offline Bernstein–Lange table of 2^s entries (about 1–8 bits/block) raises the per-root shift saving to s + 2 log T. Construction-paths §1.1 already applies this to RSA. | `params.gstar_frac` at w = 3072, T = 2^20, s = 24: L goes 100 → 148, p* 0.982 → 0.998 and k(1%) 254 → 2411, against "survives at T = 2^20 either way". The per-block shift search costs B·2^t = 2^92–2^112, inside the budget. |
| F5 | Low | reduction §2.3 statement | A_F's responder enumerates a Rabin fibre, which amounts to factoring, so it does not break (s, T, ε)-hardness as Def. 2 bounds it. The proof holds only if R must work for oracles of any running time (Wichs 2013). "For every T" is then vacuous and the theorem is MW20 8.1 untimed: it says nothing about reductions that use the deadline. | Def. 2 bounds A₂ by T decodes. Nits: ε < 1 − O(B/√N) − 2^−λ; a ⊥ symbol. |
| F6 | Low | reduction §2.3 Remark (ii); redesign §1.3, §5 Q5 | "Covers every redesign" overclaims for design (a). Enumerating the fibre queries E⁻¹ at all four roots of y_j, so an R that embeds y* = a·x² learns a root ≠ ±x and factors, which M cannot simulate. | Repair: A₁ also tags r_j, and A₂ queries E⁻¹(r_can) only after that tag matches. M can then simulate, since it decodes its table entry to r. |
| F7 | Low | redesign §3.2 bound; §3.3 ℓ(T); `params.py` | Hit identities "among unmatched blocks" cost about log₂ e per block beyond log T + log B, or log₂3·B for ternary labels in place of B. `params.py` charges log₂ C(B, g) rather than B. ℓ(T) is defined as the bits needed but used as the bits droppable. | Recount of the encoding: p* changes by less than 10⁻³. The ℓ formulas are consistent only with the "droppable" reading. |
| F8 | Low | construction-paths §1.3(b) | "Only dimension ≤ 6 lattices run in 1 ms" contradicts `frontier.py`'s cost model. The "400-bit margin" shrinks to about 128; Lemma 3's saving stays negative, so no verdict changes. | `frontier.py` δ = 64 row: dimension 32 costs 2^27 decodes, under T = 2^30. |

## Conjectures

**What P1 depends on.** P1 needs exactly one of two conjectures: RW-IC for a public XOR or ARX mixer (the M2 bound transferred), or 2RG-C for design (a), where the middle layer is a public permutation. On top of that it needs:

- factoring to be hard for the 2^λ preprocessor. This is false at 2048 (F1). A5 is correct, but at 2048 the regeneration leg it supports is void.
- for a 2-round Feistel E, the heuristic that it acts as an ideal permutation.

B1′-M2 is not load-bearing at τ = 0, because the proved M2 bound already gives k = 196–278 at 1%. It only lowers k. It becomes necessary only with the τ = 0.025 tiering allowance (M2 is vacuous there at 2048) or with narrower blocks. Using construction-paths' M1 losses (21–35 bits) for the real map needs the stronger concrete B1′, not B1′-M2.

| Conjecture | Needed by | Plausibility | Cheapest test |
|---|---|---|---|
| RW-IC (tradeoff §5 form) | P1 with an XOR/ARX mixer | Moderate (about 0.6 at λ_dev ≤ 20). Every toy route collapses to Lemma 3. The weight rests on H2 (XOR between two squarings), which has had no dedicated cryptanalysis, and the RSA-IC precedent was refuted. | Extend `rwsms_toy.py` Exp. B to masks K of weight 1…w/2 at w = 128–160. Record the largest weight at which the lattice (or a bit-linearised variant) still recovers bits: an empirical H2 margin, in CPU-minutes. |
| 2RG-C (restated per F1, F3) | P1 with design (a) | Moderate-low (about 0.5). It bundles three unproved parts: single-root Coppersmith optimality against arbitrary leakage (the BBS gap), multi-instance joint leakage, and "sum not max". If kangaroo stacks, it is vacuous at 2048 and near-vacuous at 3072 with tables (F4). | Toy at w = 64–96, t = 8–12 in `toy_two_round.py`. Confirm that a shift j plus a truncated r′ costs 2^t·T_C, since the kangaroo needs the full r′ and Coppersmith needs a known multiplier. Any sub-2^t method is the stacking attack; otherwise §5 Q1 reduces to that crisp question. |
| B1′-M2 | Nothing at τ = 0; it only reduces k | High (about 0.85). It is pure ideal-model combinatorics, and the best known other-hitting strategy saves log T − 2.4. | Implement R3's refined encoding in `tradeoff.py` and search for strategies that maximise other-hits at \|D\| = 2^12, B = 2^6, T ≤ 2^4. Anything above log T + 2 per block refutes it. |

**Notes on the §5 questions.**

- Q1 should include the table variant (F4).
- Q4: a 2-round Feistel gives v_R = r_lo ⊕ F₂(r_hi), a known-mask XOR on half of each value. Partial information therefore crosses E bitwise, which is an H2-type question that neither ideal E nor 2RG-C can see.
- Q5 is answerable, but not verbatim (F6).
- Add Q6: fix w against the preprocessing bound (F1) before doing any other parameter work.
