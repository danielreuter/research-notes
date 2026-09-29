---
id: 20260929T0120Z-handoff-from-pous-pouw-sampled-proofs-addendum-3
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Addendum 3 to `20260929T0050Z-handoff-from-pous-pouw-sampled-proofs-questions`: row blocks drawn with replacement

The red team's second pass on the draw bound found that a fixed count of distinct row blocks per stratum fails when a
stratum needs more draws than it has row blocks (the LM-head stratum of a one-forward 70B model, or on purpose by the
prover). The design now draws with replacement: each stratum makes k_s independent draws of a uniform row block with
one uniform tile each; a block drawn twice is replayed once and checked at two tiles. The escape probability is then
exactly Π_s (1 − σ_s)^{k_s} ≤ (1 − σ)^t, with no cap. Headline: 4,605 draws over (k, n) strata give ε_s = 0.09998%.
Questions 7 and 9 change; their full current text follows, changes marked *After the second pass*.

7. **Pinned interiors: may the profile count proof units?** *(addendum)*
   - In layout B, each row block's committed output includes a Merkle root over its tiles' digests. The interiors
     committed after the RU draw must match that root, and each tile's inputs (A rows, weights, derived noise) are
     committed at serving. So whether a tile is correct is fixed before the first draw.
   - `IntegrityProfile` allows a profile of several levels when "its checked level is committed before the first draw
     (… two-stage with every intermediate committed up front)". Here that would be Bernoulli(p) over row blocks and
     Subset(k) over tiles, counting wrong tiles.
   - May a two-stage audit emit that profile when its interiors are pinned this way? `TwoStageLaw.profile` today emits
     only the per-RU form, 1 − p·k/n_v, which would make layout B n_v/k times worse (§3.3).
   - *After the review* (X-SPC-2, X-SPC-9), the draw is a fixed count per template stratum (question 9). Each stratum
     draws k_s = ⌈t·W_s/W⌉ row blocks, then one tile in each.
     - `IntegrityProfile` allows a `Subset` only at the checked level, so it can't express this two-level draw.
     - The exact `Stratified` law over tiles does not bound it (a counterexample is in §3.3).
     - What does bound it is the with-replacement form, Π_s (1 − σ_s)^{k_s} ≤ (1 − σ)^t (§3.3, **Derived**).
     - The question becomes: may a two-stage audit emit that profile, as a new profile form?
   - *After the red team's second pass* (X-SPC-13, X-SPC-14; addendum 3):
     - Row blocks are now drawn with replacement, one uniform tile per draw. The escape probability is then exactly
       Π_s (1 − σ_s)^{k_s} ≤ (1 − σ)^t.
     - The conditions are H1 (the rounded-up sizes), H2 (equal work per tile in a stratum), H3 (equal tiles per block in
       a stratum), H5 (tile correctness fixed before the first key), and an abort counting as a rejection, with one
       registration per salt.
     - The profile form that is expressible today, a profile per stratum at δ/5, costs 6.7× the draws (31,033 against
       4,605 for 0.1%).
     - The question is unchanged: may `verity.proofs.profile` gain this profile form (with-replacement, fixed-count,
       stratified, two levels), with those conditions stated?
9. **k RUs, or each RU with probability p?** *(addendum)* Daniel's description draws k RUs. `law.py` draws each RU
   independently with probability p (`select_replay_units`), and `IntegrityProfile` allows a fixed-size `Subset` only at
   the checked level. Which is intended? This design assumes the repo's Bernoulli form; a fixed count changes only the
   constants.
   - *After the review,* the design takes the fixed count: per template stratum, k_s = ⌈t·W_s/W⌉ draws of a uniform row
     block. It fits Daniel's "k RUs" and the red team's rule (X-SPC-9).
     - *After the second pass* (addendum 3), the draws are with replacement. A block drawn twice is replayed once and
       checked at two tiles. This removes the need for k_s ≤ N_s, which the LM-head stratum of a one-forward 70B model
       breaks, and which a prover could break on purpose.
     - The sampler differs from `select_replay_units`, so it needs a domain of its own, not `ru-sample` (X-SPC-2).
     - The rule is registered, not the numbers, since n_s is known only at the run root.
     - Is a fixed-count stratified RU draw with replacement acceptable in `protocols/sampled_proofs`?

Reply in `lanes/pous/`.
