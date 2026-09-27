---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: finding · status: open · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# Knowledge soundness for Flock: statement, proof plan, effort

The long form of `backends/flock/verifier/lean/soundness/DESIGN.md` §3; the statements are `ASSUMPTIONS.md` §1.3 (the
coordinator's request, 2026-09-26; older references to ASSUMPTIONS.md §4.3, §12 and §13 are now `DESIGN.md` §2, §9 and
§10). It is needed for two claims:
- "these proofs used the registered weights" (ASSUMPTIONS.md §13). Hiding leaves open to essentially any row, so the
  committed witness must be extracted and then compared with the registrant's opening.
- The recursion track (`docs/circuit-privacy.md`), whose outer proof must be a proof of knowledge.

## 1. Statements (targets)

- **`table_knowledge_sound`.**
  - **The extractor.** `E` gets black-box access to any classical prover `P*`, deterministic without loss of
    generality, which is accepted with probability ε. It reruns `P*` from the start `K` times on fresh coins. Level 0 is
    committed in the first message, so every run opens the same cap, and `E` collects the verified level-0 openings.
    - If two runs open one position to different columns, `E` outputs that SHA-512 collision (`Merkle.opening_binding`).
    - Otherwise `E` has a consistent partial table. It list-decodes it, treating unobserved columns as erasures, unpacks
      each candidate and outputs one that satisfies the statement.
  - **The claim:** `Pr[E outputs a satisfying witness or a collision] ≥ ε − κ`.
  - `K ≈ (N₀/Q₀)·ln(1/(ζβ))/ε`. At m = 33, `N₀/Q₀ = 2^21/436 ≈ 2^12.2`.
- **`registered_weights`.** Given the registrant's opening `(W, R)` of the weights root, the extracted witness's rows at
  every position linked to that root equal `W`, or `E` together with `(W, R)` yields a SHA-512 collision. Tree binding
  of the commit strings comes first, then Halevi–Micali binding: a leaf, salt or inner-digest collision (hm96
  PROTOCOL.md §4). So `Pr[accepted ∧ extracted rows ≠ W] ≤ κ + Adv_CR^{SHA-512}(B_link)`, where `B_link` is `E` plus
  a comparison.
- **For recursion:** the same theorem, applied to the outer statement, extracts `C`, the openings and the inner
  transcript. The composed error is the outer `κ` plus the inner soundness error. If the recursion's composition proof
  needs witness-extended emulation (Lindell 2003), it follows from knowledge soundness for public-coin arguments by the
  standard transformation. That is one more small theorem.

## 2. Why the extraction is mostly straight-line

- **Only level 0 matters,** since the witness lives there. It is committed before any coin, so `E` never forks
  mid-protocol.
- **`E` sees conflicts directly.** Two runs opening one position differently are a collision found by `E` itself, which
  costs only a quadratic term, `(K·t)²/2^513`. That is negligible for SHA-512.
- **What still needs rewinding-style analysis:** positions where `E` observed only non-plurality values without a
  conflict. Their expected number is at most `K·Q·Pr[a run opens off the plurality]`, which is at most
  `K·Q·√(N·Q·c)` by `Rewinding.prBad_le`, where `c` is the conflict probability of two runs. They act as extra decoding
  errors, and Markov's inequality bounds the chance that they exceed the decoding slack.
- **Decoding margin, deterministic.** Compiled soundness says `P*`'s plurality table `T*` is δ-close to a codeword that
  packs a satisfying witness, with `δ = 1 − √ρ − η` (`ρ = 1/2`, `η = 1/50`, so `δ = 0.2729` at level 0). On the observed
  columns the error fraction is at most `(δ + ζ')/(1 − ζ)`, where `ζ` is the fraction unobserved and `ζ'` the fraction
  wrong. It must stay below the punctured code's Johnson radius, `1 − √(ρ/(1 − ζ))`. At `ζ = 1%`, `ζ' = 0.5%` that is
  0.2807 against 0.2893: a thin margin, so coverage must be about 99%.
- **Coverage** needs no tail bound: `E[#unobserved] = Σ_p (1 − q_p)^K ≤ N·e^{−KQ/N}`, then Markov.
- **A first estimate of the extraction term** is `ln(1/(ζβ))·2^15.4·t/(ε·ζ'·2^256)`, about `t·2^-227/ε`. So a 2^-128
  total needs `t/ε ≤ 2^99`, which is to be sharpened.
  - The generic interactive-BCS analysis (Chiesa–Dall'Agnol–Gur–Spooner 2023) pays `L/ϵ` in the reduction. With SHA-512
    it gives only about 2^-100 to 2^-111 at `t = 2^64` to `2^80`.
  - The Flock-specific plurality argument is why we can do better, as it did for soundness (§4.3).

## 3. What exists to build on

- **`Merkle.opening_binding`, `Rewinding.prBad_le`, `Compiled.*`** (this lane, proved).
- **CompPoly's Guruswami–Sudan decoder**, in our pinned dependency: executable, with interpolation (dense,
  Lee–O'Sullivan, approximant basis), root finding (Roth–Ruckenstein, Alekhnovich) and filtering. It has correctness
  theorems (`gsCore_sound`, `gsCore_complete_of_enough_matches`, `gsFilteredCore_*`) and no `sorry` in
  `CompPoly/Bivariate/GuruswamiSudan`. So the decoding step can be proved, not assumed.
- **ArkLib's Johnson list bound** for interleaved Reed–Solomon codes (`irs_lambda_le_johnson_mds`). Applied to the
  punctured code, it bounds the pruned search below.
- **ArkLib's rewinding knowledge-soundness definitions** (`OracleReduction/Security/Rewinding.lean`) are marked "under
  development" and are for its own oracle-reduction framework, so they are not usable here.

## 4. Effort, by component

Sizes are rough Lean line counts. For comparison, the whole development today is about 3,350 lines.

| Id | Component | Lean (lines) | Depends on |
|---|---|---|---|
| K1 | The extractor as an experiment in the `Game` framework: `K` independent runs, collecting verified level-0 openings, conflict detection | 150–250 | the compiled game (openings at the end of the proof) |
| K2 | Conflict gives collision | 20–40 | `Merkle.opening_binding` |
| K3 | Coverage: `K` runs observe at least `(1 − ζ)N₀` columns, except with probability β, for the stratified query law | 120–200 | `Model.positions`; the query-balance fact in `Arith.Correct` |
| K4 | Wrong-but-consistent positions: a `K`-sample extension of the rewinding lemma, with Markov | 150–250 | `Rewinding.prBad_le` |
| K5 | Decoding the punctured interleaved code: per-row Guruswami–Sudan (CompPoly), then a pruned search over row candidates. Its completeness comes from the Johnson bound on row prefixes, and it bridges CompPoly polynomials, ArkLib codes and `Model.encode` | 400–650 | CompPoly GS; ArkLib Johnson bound; `Arith.Correct` (`xhat_poly`) |
| K6 | Unpack and check the candidates (`Model.unpack`, a decidable `Satisfies`) | 50–100 | `Model` |
| K7 | `table_knowledge_sound`: assembly, with `κ` = the compiled soundness error plus the K3 and K4 terms | 150–200 | `table_sound_compiled` |
| K8 | Halevi–Micali binding for the SHA-512 leaf (leaf, salt or inner-digest collision) | 80–120 | the SHA-512 hm96 byte layout (commitments lane, re-baseline) |
| K9 | `registered_weights`: data-tree binding (vllm framing, a second Merkle lemma), then K8, then K7 | 120–200 | K7, K8 |
| K10 | For recursion, if needed: witness-extended emulation, and unpacking a masked witness | 200–350 | the M1/M2 masking spec |

- **Total:** about 1,250–2,000 lines for K1–K9, plus 200–350 for K10. That is roughly half the size of the development
  so far. K5 is the largest single piece, and K4 holds the mathematics that sets the concrete error.
- **Paper first:** the extraction analysis (K3–K5, with its concrete bound) should be written out and reviewed by a
  cryptographer before it is formalized.
- **Order:** K1–K7 follow `table_sound_compiled`, and can be stated and proved from it the way `rep_sound` is proved from
  its phase lemmas, so they needn't wait for every phase lemma. K8–K9 wait for the SHA-512 leaf layout, and K10 for
  M1/M2.

## 5. Risks

- **The concrete knowledge error** (section 2). The first estimate needs `t/ε ≤ 2^99` for 2^-128. A sharper analysis
  is part of the work, and the generic bounds are worse.
- **The decoding margin.** `fast100`'s η = 1/50 leaves under 1% slack at level 0 after erasures. So coverage must be
  about 99% (more runs), and Guruswami–Sudan needs a high multiplicity near the Johnson radius. That affects the proof's
  parameters, not the protocol, but a future profile with larger η would ease it.
- **Bridging representations:** CompPoly's executable polynomials, ArkLib's codes and our `Model`.
- **Recursion** may need stronger extraction notions (witness-extended emulation; state preservation, if quantum ever
  matters).
- **It is classical only.** Post-quantum knowledge soundness follows asymptotically from CDDGS25's Theorem 1, as for
  soundness (§12).
