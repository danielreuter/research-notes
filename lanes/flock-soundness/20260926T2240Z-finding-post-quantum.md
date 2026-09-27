---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: finding · status: open · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# Flock interactive soundness against quantum provers and verifiers (full analysis)

The long form of `backends/flock/verifier/lean/soundness/DESIGN.md` §9. The section references below use the numbering
before the 2026-09-26 split of `ASSUMPTIONS.md`: §4.3 is now `DESIGN.md` §2, §8 is `DESIGN.md` §6, §11 is `DESIGN.md` §8. Sources checked
2026-09-26: CMSZ21 (ePrint 2021/334), CDDGS25 (ePrint 2025/947, TCC 2025; Theorem 6.1, Definition 3.5, Equation 1),
CMS19 (ePrint 2019/834), Unruh 2016 (ePrint 2016/508), Fehr 2018 (ePrint 2018/887), Czajkowski et al. (ePrint
2017/771), LMS22 (arXiv 2111.12257), CCLY21 (arXiv 2103.11244), EasyPQC (ePrint 2021/1253), qrhl-tool, Lean-QIT
(arXiv 2607.09632), QICLean.

## Numbers behind the loss estimate (m = 33)

- Level lengths `2^21, 2^19, 2^17, 2^15, 2^13, 2^11`, queries per rep `218, 106, 71, 53, 43, 36` (`Accounting/Schedule.lean`).
- `Σ_i L_i·(q_i + 5)`: level 0 (both reps) `2^21 × 441 = 2^29.8`; levels 1–5 in both reps add `2^26.8 + 2^24.3 + …`;
  total `≈ 2^30.0`.
- CDDGS25 set `N = 2k·L_max/ϵ` rewinds and call the rewinding procedure with slack `ϵ/2k`, of size
  `poly(N/(ϵ/2k))·(t_V + t) = poly(4k²·L_max/ϵ²)·(t_V + t)`. With `k ≈ 2^7.4`, `L_max = 2^21`, `ϵ = 2^-128`, the
  number of rewinds alone is `2^157.4`.

## The analysis

**The theorem is classical, and only its compiled layer needs to change.**

- **The oracle layer already holds against quantum provers.** `table_sound` is statistical, and every message and coin
  is classical. Whatever a quantum prover does, its next message given the history follows some classical randomized
  strategy, and `table_sound` bounds every strategy. So 2^-195.5 per table is a post-quantum statement at the oracle
  layer.
- **The compiled layer does not carry over.** §4.3 rewinds `P*`: it runs the continuation twice from a snapshot taken at
  the commitment.
  - A quantum prover's state cannot be copied (no-cloning), and measuring the first run's openings disturbs it. So
    there is no second independent run, and no well-defined plurality table.
  - Collision resistance is also the wrong property against quantum provers. Relative to an oracle, there are hash
    functions that are collision resistant against quantum adversaries but whose commitments do not bind them
    (Ambainis–Rosmanis–Unruh, FOCS 2014). The quantum replacement is **collapsing** (Unruh, Eurocrypt 2016): given a
    hash value, measuring a superposition of its preimages must be undetectable.
  - Our Lean framework, like VCVio, EasyCrypt and CryptHOL, reasons about classical adversaries only. Unruh gave a
    protocol that such frameworks prove secure but quantum adversaries break. So no compiled-layer proof here transfers.

**What is known.**

- **Kilian's protocol, from PCPs.** Chiesa–Ma–Spooner–Zhandry (FOCS 2021, ePrint 2021/334): Kilian's four-message
  argument with any PCP and any collapsing hash is post-quantum sound in the standard model. It introduced the first
  quantum rewinding that can collect arbitrarily many accepting transcripts. Lombardi–Ma–Spooner (FOCS 2022) tightened
  the reduction. Lai–Malavolta–Spooner (TCC 2022) rewind across many rounds, but only for tree-special-sound protocols,
  which interactive BCS is not.
- **Interactive compilation of IOPs, which is our setting.** Chiesa–Dall'Agnol–Di–Guan–Spooner (TCC 2025, ePrint
  2025/947) study interactive BCS: the prover commits each IOP message with a vector commitment, the verifier answers
  with public coins, and the openings come at the end. It is post-quantum sound in the standard model for every
  public-coin **semi-adaptive** IOP with a **collapse-position-binding** vector commitment. Their Theorem 6.1 gives
  `ε_ARG ≤ ε_IOP + Σ_i L_i·(q_i + 5)·ε_collapse + ϵ`, where `L_i` is the i-th message's length, `q_i` its queries,
  and `ϵ` the rewinding slack. Hash trees over a collapsing hash are collapsing vector commitments.
- **Fiat–Shamir.** In the quantum random-oracle model, BCS applied to an IOP with round-by-round soundness `ε_rbr` has
  error `O(t²·ε_rbr + t³/2^λ)` (Chiesa–Manohar–Spooner, TCC 2019). That is the reference for a future non-interactive
  variant (§11), not for live coins.

**Does it apply to Flock with live coins?** Structurally, yes.

- **Flock's table is interactive BCS.** The coins are public, oracles are committed by Merkle trees (caps instead of
  roots, still a vector commitment), and openings come at the end of the proof. The two reps sharing level 0 are one
  IOP whose first oracle both reps query.
- **It is non-adaptive, hence semi-adaptive.** Ligerito's query positions depend only on the query coins (spec §13.5,
  including stratification, A11), never on earlier answers.
- **`ε_IOP` is our oracle-layer bound**, valid against quantum IOP provers, as argued above.
- **The kept round bytes** fix every message before its coins, which is exactly the interactive model.
- **Merkle trees over SHA-512 are collapse-position-binding if SHA-512 is collapsing.**

So, **if SHA-512 is collapsing, Flock's interactive protocol is post-quantum sound with error `tableError + negl(λ)`.**
This is a paper-level corollary of CDDGS25. It is not yet written out, and not in Lean.

**Is SHA-512 collapsing?** It is conjectured, not proved.

- A random oracle is collapsing (Unruh 2016).
- Merkle–Damgård preserves collapsing when the compression function is collapsing: Unruh (Asiacrypt 2016), under a
  padding condition that SHA-2's length padding meets, and Fehr (TCC 2018), with simpler proofs. So SHA-512 is
  collapsing if its compression function is, which is what modeling that function as random suggests.
- No attack on collapsing SHA-512 is known. The generic ones go through collisions (table below).
- Table 1 would need a new property for it (`collapsing/sha-512`); `verity.claims` has none today.

**The loss in the bound: the corollary is asymptotic only.** CDDGS25's reduction rewinds the quantum prover about
`2k·L_max/ϵ` times, and its collapse adversary costs `poly(k·L_max/ϵ)` prover runs. The collapsing advantage is also
multiplied by `Σ_i L_i·(q_i + 5)`. At m = 33:

- `L_max = 2^21` (level 0's columns), and `Σ_i L_i·(q_i + 5) ≈ 2^30`, level 0's 2^21 × 441 dominating;
- `k` is 150–200 rounds for a table;
- a 2^-128 target needs `ϵ ≤ 2^-128`, so the collapse adversary makes at least `2^157` prover runs;
- any 512-bit hash stops being collision resistant, and hence collapsing, at about 2^171 quantum queries (BHT);
- even at `2^157` queries, the generic quantum collision probability `q³/2^512 = 2^-41`, times `2^30`, is `2^-11`.

**So the known theorem gives no concrete post-quantum bound at our parameters, for any prover size.** Classical
rewinding costs a square root (§4.2a). Quantum rewinding costs polynomial factors in `L/ϵ`, and closing that gap is open
(CDDGS25 list it as such).

**What could give a number:**

- **The quantum random-oracle model.** Model SHA-512 as a quantum-accessible random oracle. Merkle commitments can then
  be extracted straight-line, with no rewinding, by Zhandry's compressed oracle (as in CMS19). With live coins the
  natural target is `ε_stat + O(t³/2^512)`, CMS19's collision term, which is at most 2^-128 up to `t ≈ 2^128`. No paper
  proves the interactive case with concrete terms, and the model is heuristic, like the classical random-oracle remark
  (§4.3).
- **A standard-model analysis with small enough polynomial factors.** That is open research.

**Grover and BHT margins for SHA-512** (n = 512):

| Attack | Quantum cost | Where it would hit |
|---|---|---|
| Preimage or second preimage (Grover) | 2^256 sequential queries; `P` machines in parallel gain only `√P` | opening a given leaf or node to other contents |
| Collision (Brassard–Høyer–Tapp 1998) | 2^170.7 queries, with 2^170.7 quantum-accessible memory | Merkle binding; collapsing |
| Collision with small quantum memory (Chailloux–Naya-Plasencia–Schrottenloher, Asiacrypt 2017) | 2^204.8 time, 2^102.4 classical memory | the same |
| Collision, generic limit (Zhandry 2015) | success at most `O(q³/2^512)` with `q` queries | the `t³` term above |

- **For comparison,** SHA-256 collisions cost 2^85.3 by BHT, below 2^128.
- **NIST's reference points:** post-quantum category 2 is SHA-256 collision search and category 4 is SHA-384; SHA-512
  collision search is above category 4.
- **Cost models make these margins more conservative still.** Bernstein (SHARCS 2009) argues quantum collision search
  is no cheaper than parallel classical search once hardware cost is counted.
- **So the hash has ample quantum margin.** What blocks a post-quantum number is the reduction's loss, not SHA-512.

**Other components against quantum provers.**

- **`os` coins**, and the kept round bytes, are unaffected.
- **`seed` coins** (PR #83) rely on the prover not learning the seed. Grover on a 256-bit seed and on SHA-256 as a PRF
  both cost 2^128: the 128-bit post-quantum level, with no margin.

**Zero knowledge against quantum verifiers.**

- **Honest-verifier ZK (§8, target 1) carries over unchanged.** The verifier's view is classical and statistically close
  to the simulator's output, and statistical distance bounds every distinguisher, quantum ones included. Leaf hiding
  (Halevi–Micali) and uniform masks and padding are statistical too.
- **Malicious-verifier ZK (§8, target 2) is where quantum verifiers bite.** The simulator must learn the committed coins
  and then rewind a verifier whose state, including its auxiliary input, may be quantum.
  - Lombardi–Ma–Spooner (FOCS 2022) prove the closest analogue, Goldreich–Kahan, post-quantum zero knowledge. In it the
    verifier commits to its challenges first. Their proof uses a black-box simulator in coherent-runtime expected
    quantum polynomial time, and needs the verifier's commitment to be collapse-binding and statistically hiding.
  - Chia–Chung–Liu–Yamakawa (FOCS 2021) rule out constant-round black-box post-quantum zero knowledge for NP with
    measured expected-polynomial-time simulation. Our protocol has 150–200 rounds, so their result does not apply
    directly, but it shows the simulation notion matters.
  - Adapting LMS22 to our many rounds, with coins revealed round by round, is research.
- **One design consequence:** a post-quantum malicious-verifier claim needs the coin-seed commitment
  (`coin-commit/sha256/v1`) to be collapse-binding with a 128-bit quantum margin. SHA-256 (BHT 2^85.3) is not enough;
  SHA-384 or SHA-512 would be. LMS22's template also wants it statistically hiding.

**What a post-quantum statement would take:**

1. **The asymptotic corollary, on paper (small).** Write out that Flock's table is interactive BCS over a public-coin,
   non-adaptive IOP, and apply CDDGS25's Theorem 6.1 under "SHA-512 is collapsing". It needs a quantum-cryptography
   reviewer. It yields `tableError + negl(λ)`, not a number.
2. **A concrete number (research).** Either prove interactive BCS in the quantum random-oracle model with concrete terms,
   adapting CMS19 (the interactive case is simpler than Fiat–Shamir), or find a tighter standard-model quantum
   rewinding (open).
3. **Lean.**
   - **What exists:** finite-dimensional quantum information libraries in Lean 4, such as Lean-QIT (2026) and QICLean.
     They provide states, channels, measurements, trace distance and entropy, with some QKD security. They are not in
     Mathlib, and not pinned to our Mathlib.
   - **What is missing in every proof assistant:**
     - quantum adversaries with superposition oracle access, and a game model for them (the counterpart of our `Game`
       or VCVio's `OracleComp`);
     - collapsing and collapse position binding;
     - the engine of CMSZ21's rewinding (value estimation and state repair, on Jordan's lemma and Marriott–Watrous
       amplification);
     - CDDGS25's multi-round argument;
     - for the random-oracle route, Zhandry's compressed oracle.

     The closest tools are outside Lean: qrhl-tool (Isabelle; the Fujisaki–Okamoto transform in the quantum
     random-oracle model) and EasyPQC (EasyCrypt; Full Domain Hash, GPV identity-based encryption and PRF-MAC).
     Neither has quantum rewinding, and no proof assistant has a post-quantum proof of any succinct argument.
   - **A full Lean statement** means building that quantum-adversary layer and then formalizing a quantum rewinding
     proof far longer than this lane's classical one. It is a research formalization program, larger than the whole
     classical development, and not plannable now.
   - **A cheap intermediate:** state CDDGS25's theorem as a named `Prop`, like A1, and prove only the application: Flock
     is public-coin and non-adaptive, with `ε_IOP = tableError`. It is honest, but adds little while the conclusion is
     asymptotic.

**Recommendation.** Keep the theorem classical (§4.3), and do not claim a post-quantum number in Table 1. A fair
statement is: the statistical layer holds against quantum provers; the compiled protocol is post-quantum sound
asymptotically if SHA-512 is collapsing (CDDGS25); no concrete post-quantum bound is known at these parameters.
