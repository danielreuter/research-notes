---
id: 20260929T0110Z-handoff-from-pous-pouw-sampled-proofs-addendum-2
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Addendum 2 to `20260929T0050Z-handoff-from-pous-pouw-sampled-proofs-questions`: after the red-team review

A red team reviewed the PoUW-under-sampled-proofs design and accepted its recommendations with changes. Applied to the
recommended layout (row block = replay unit with a root over its tiles' digests; tiles = proof units), they change
questions 3, 4, 7, 8 and 9 and add question 10. Each item below is the full current text; the changes are marked
*After the review*. Questions 1, 2, 5 and 6 stand as sent (with the layout notes in addendum 1).

Other changes you may care about:
- **Draw:** a fixed count per template stratum, k_s = ⌈t·W_s/W⌉ row blocks drawn uniformly without replacement, then
  one tile in each, under its own draw domain. The rule is registered, not the numbers.
- **Salt:** one per run, so a batch served twice isn't credited twice.
- **Noise:** derived by the verifier; nobody commits it.
- **Verifier time:** about 30 CPU-seconds on a 70B layer mix (4,604 draws give 0.1007%).

## Questions (current text)

3. **One δ across RU classes.** `TwoStageLaw.profile` returns one profile per class. PoUW needs one class per template,
   because units at different depths k do different work, with draw rates proportional to that work.
   - How should a consumer combine several classes' profiles under one δ: by a union bound, or through a joint profile
     over the classes?
   - Or may one class carry a rate per RU?
   - *After the review:* the design now draws a fixed count per template stratum under one stratified law (question 9).
     That gives one profile and one δ, and this question falls away if that law is accepted.
4. **An input derived from a serving-time root.** A tile's noise E₁ is derived from (salt, call index, root_A, weight
   id). root_A, the Merkle root of the call's A rows, is a commitment artifact, not a Program value. How does a
   two-stage RU take such an input?
   - (i) As a prescribed "noise" family that the verifier derives for each drawn RU and the prover never commits?
   - (ii) Committed by the prover, and checked against the derivation by a plan class?
   - (iii) Derived inside the Definition, with root_A as a Program value?

   `IntegrityProfile` lists "noise" among its prescribed families, which it says are checked exhaustively. Does that mean
   (ii) at p = 1?
   - *After the review* (X-SPC-7), (ii) is ruled out by size. The committed-set rule would commit E₁, which is as large
     as A, and Y, which is 3k × n per weight and epoch, or per call for FP8: about 200 MB per call at 8,192².
   - So the question narrows: can the IR and `vllm-v1` have an Input class that the verifier derives and nobody
     commits, exempt from the committed-set rule? No such class exists today.
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
8. **A replay unit whose output commits to its own interiors.** *(addendum)* Does the two-stage lifecycle support an RU
   output that is a root over some of its interior values, with step 3 checking that the committed interiors hash to it?
   Is that a leaf layout `vllm-v1` would add, and whose check is it (the protocol's, or the consumer's)?
   - *After the review* (X-SPC-11), `vllm-v1` also needs a tree kind for PoUW's A rows.
     - root_A must be fixed mid-forward, before E₁ is derived, while the Commit builds its trees at the end of the row.
     - The proposed form: the PoUW row subtree is lifted verbatim under the run root, and left unsalted, because an
       `hm96` leaf would let the prover regrind root_A for one path recompute.
     - Is that acceptable in `vllm-v1`?
9. **k RUs, or each RU with probability p?** *(addendum)* Daniel's description draws k RUs. `law.py` draws each RU
   independently with probability p (`select_replay_units`), and `IntegrityProfile` allows a fixed-size `Subset` only at
   the checked level. Which is intended? This design assumes the repo's Bernoulli form; a fixed count changes only the
   constants.
   - *After the review,* the design takes the fixed count: per template stratum, k_s = ⌈t·W_s/W⌉ row blocks, drawn
     uniformly without replacement. It fits Daniel's "k RUs" and the red team's rule (X-SPC-9).
     - The sampler differs from `select_replay_units`, so it needs a domain of its own, not `ru-sample` (X-SPC-2).
     - The rule is registered, not the numbers, since n_s is known only at the run root.
     - Is a fixed-count stratified RU draw acceptable in `protocols/sampled_proofs`?
10. **The partition query.** *(addendum 2; X-SPC-1, X-SPC-6)*
    - `Q_template_instances` v0 applies only when every root node is an instance of a listed template. Row blocks and
      tiles sit inside `ncp-linear`, beside the quantizer and every non-PoUW call, so the query refuses the Program.
    - Per-tile forming also recomputes each strip's gates in n/16 units, which `Q_word` v1 and `validate_unit_cut`
      refuse (`gate-recomputed`, pinned by `qword_vectors.json`).
    - Proposed: a new query version with nested template instances (row blocks and their tiles), the rest of the Program
      under `Q_word`, and a named exception for recomputes across instances of one template, with vectors and a
      `PROTOCOL.md` entry.
    - Is that acceptable, and who owns it?

Reply in `lanes/pous/`.
