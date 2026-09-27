---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: draft · status: open, for review before formalizing · repo: danielreuter/verity · follows PR #110 (`table_sound_compiled`, proved)

# Knowledge soundness: the extraction analysis, on paper first

`DESIGN.md` §3 asks for this analysis, written out and reviewed, before any Lean. It revises the estimate in
`note:20260926T2330Z-finding-knowledge-soundness` §2. That estimate (`t/ε ≤ 2^99`) is not rigorous: it assumes the
extractor sees about 99% of level 0, and a prover can refuse to open some positions. The fix below removes the coverage
requirement and gives a much better hash term. One case is still open (§5).

## 1. What the compiled proof already gives

For a deterministic compiled prover `P*`, let `σ₁` be its strategy after its level-0 cap, and `q_p` the probability
that a run opens position `p` with a verifying path. `table_sound_compiled`'s proof uses only that `C0star` is a
plurality table (`bad_le`, the `hpl` step). At a position no run ever opens (`q_p = 0`), every row is a plurality, so
the theorem holds **for every completion** of the plurality table there. For any table `T` at all, the same proof
bounds the level-0 bad term by

> `Pr[a run opens a level-0 position off T] ≤ √(N₀·2Q₀·Adv₀) + Σ_{p : T(p) ≠ T*(p)} q_p`,

by the union bound on top of `Rewinding.expect_bad_le`. So:

> **(A)** `Pr[acc ∧ ¬Committed(T)] ≤ ε_c + Σ_{p : T(p) ≠ T*(p)} q_p`, where `ε_c` is the right side of
> `table_sound_compiled`.

## 2. The extractor

`E` runs `σ₁` on `K` independent coin draws. Level 0 is committed first, so every run opens under the same cap. `E`
collects every verifying level-0 opening, from rejected runs too.
- If two openings of one position differ, `E` outputs the SHA-512 collision (`opOf_conflict_collision`).
- Otherwise `E` has one row per observed position (the set `O`); the unobserved set is `U`. `E` list-decodes the
  interleaved code punctured to `O`, unpacks each candidate and outputs one whose witness satisfies the statement.
  Satisfaction is decidable.

## 3. Unobserved positions are erasures that count against the prover

Take `T_z`: `T*` on `O`, and `z` on `U`. By (A), `Committed(T_z)` fails with probability at most
`(Σ_{p ∈ U} q_p) / (ε − ε_c)` over `E`'s runs, by Markov. Here `ε = Pr[acc]`, and
`E[Σ_{p ∈ U} q_p] = Σ_p q_p (1 − q_p)^K ≤ N₀/(eK)`. So

> `K = N₀ / (e·τ·(ε − ε_c))` runs make `Pr[¬Committed(T_z)] ≤ τ`, **with no coverage requirement**.

If `z` disagrees at every point of `U` with every codeword close to `T*` on `O`, a committed codeword `c*` satisfies
`dist_O(c*, T*) ≤ δN₀ − |U|`. The error fraction on `O` is then at most `(δN₀ − u + W)/(N₀ − u)`, which decreases in
`u`. Here `W` is the number of wrong-but-consistent positions (§4), and `δ = 1 − √ρ − η`. The worst case is `u = 0`:
decode at relative radius `δ + W/N₀` against the Johnson radius `1 − √ρ`. The margin is `η = 1/50`, with no erasure
penalty. The earlier "coverage must be 99%" concern goes away.

## 4. Wrong-but-consistent positions

`p ∈ W` needs some run to open `p` off the plurality, so `Pr[p ∈ W] ≤ K·b_p`, where `b_p` is one run's off-plurality
mass at `p`. The rewinding lemma's core, whose proof already bounds the sum, gives
`Σ_p b_p ≤ √(N₀·2Q₀·Adv₀)`. By Markov, `Pr[W ≥ ζ'N₀] ≤ K·√(2Q₀·Adv₀/N₀)/ζ'`. With `K` from §3,
`Adv₀ ≤ (2t)²/2^513`, `τ = 1/4` and `ζ' = 1/100` (below `η`):

> `Pr[W ≥ ζ'N₀] ≤ t·2^-232.9 / (ε − ε_c)` at m = 33.

**The candidate theorem:** if `ε > ε_c`, then `E` makes `K ≈ 2^21.6/(ε − ε_c)` runs and outputs a satisfying witness
or a SHA-512 collision with probability at least `1 − τ − t·2^-232.9/(ε − ε_c)`. The knowledge error is `ε_c`
itself, and the hash term is negligible unless `t/(ε − ε_c)` approaches `2^230`.

## 5. The open case: many unobserved positions

§3 needs a completion `z` that avoids every codeword close to `T*` on `O`. With the random-completion argument, that
needs the list `M = {c : dist_O(c, T*) ≤ δN₀}` to be smaller than `|Σ|/N₀`, where `|Σ| = |F|^lanes` is the
alphabet. That holds while `δ/(1 − u/N₀)` is below the punctured Johnson radius, so for `u ≲ 1%` of `N₀`. For larger
`u`, `M` is not bounded, and the argument must change. Two routes, for review:
- **Poisoned oracle.** Prove oracle-model soundness for tables with `⊥` at `U`: a query to `⊥` rejects, and `⊥`
  counts as a disagreement in `Committed`. `table_sound`'s proof should carry over, since `⊥` is just a row no
  codeword has. Then (A) holds with `Committed_U`, and §3 needs no avoidance.
- **Threshold.** Complete adversarially only where `q_p < θ`, which costs `≤ θN₀` in (A). Then `K ≥ ln(N₀/β)/θ`
  covers the rest, with `θ = τ(ε − ε_c)/N₀`. That costs a `ln` factor in `K`, and brings the coverage term back only
  for positions `E` should have seen.

## 6. Lean plan (after review)

1. `table_sound_compiled_of_table`: the compiled bound for any table `T`, with the deviation term. This is a refactor
   of `bad_le`.
2. `expect_offmass_le`: `Σ_p b_p ≤ √(N·Q·c)`, the sum form of `Rewinding.expect_bad_le`.
3. The `K`-run experiment as an expectation over `K` independent strategy runs, with `E`'s observation table and the
   Markov steps of §3–§4.
4. Decoding: per-row Guruswami–Sudan (CompPoly) plus a pruned interleaved search, bounded by ArkLib's Johnson bound.
   This is the largest piece. Until it lands, the extractor could state its decoding step as the list of codewords
   within the radius. That is computable, but not efficient.
5. `table_knowledge_sound`. `registered_weights` waits for the SHA-512 leaf layout.
