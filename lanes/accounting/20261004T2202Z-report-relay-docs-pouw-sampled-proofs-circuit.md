---
id: 20261004T2202Z-report-relay-docs-pouw-sampled-proofs-circuit
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pouw/sampled-proofs-circuit.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pouw/sampled-proofs-circuit.md`, sha256 `ab8ef8756e4584293c98031d33a62f2d39d7530ecc29f978136b97585815244f`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Verifying PoUW with sampled proofs: the circuit, the replay units and the draw

29 Sep 2026. Design only: no code, no GPU.

**Revision history.**
- 00:45Z: first version.
- 01:00Z and 01:15Z: reframed under the two-stage protocol.
- 01:40Z and 02:00Z: two red-team passes.
- 02:20Z: rebased on the protocol owner's first answers.
- 02:45Z: reconciled with the owner's full answers (research-notes `lanes/pous/20260929T0145Z-handoff-from-verity-root.md`,
  D1–D7).
- 03:05Z:
  - costs Daniel's 02:12Z proposal (seed expansion inside the circuit, proved by sampled proofs) as a candidate for
    F4/D3, and recommends it in a tile-local form (§5);
  - folds in the red team's re-review of layout A (X-SPC-15 to X-SPC-22, with `redteam-sampled-proofs-circuit-costs.py`),
    whose C-Flock row counts replace the earlier cost estimates.
- 03:30Z:
  - folds in Verity root's answer on the partition query (research-notes `lanes/pous/20260929T0210Z-handoff-from-verity-root.md`);
  - drafts the `ncp-linear` part of that query (§2.6);
  - moves y's dequantization out of the tile, to narrow the width-rule exception;
  - consolidates §10 into one list for Daniel, linked to the
    [deployment-requirements audit](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/deployment-requirements-audit.md)'s
    rows A19–A24.
- 03:45Z: folds in the red team's verdicts on D3–D5 (X-SPC-23 to X-SPC-28), all confirmed with conditions:
  - D4 is an informal reduction that needs a short simulation lemma;
  - grinding buys only E₁, and TT_NCP_U's error term ε(q, N) is unpinned;
  - two gaps predate this design (a layout chosen after the salt, and a prover opening several runs);
  - D5's separate units cost +43–50%, and only with forming strata per (k, n) site;
  - D3's wording holds within one run and one fixed layout.

  The seed-expansion review of §5, §2.5 and §2.6 is still running.
- 04:00Z: answers Daniel's 02:36Z question, whether the recompute exception can be avoided at all, with every
  exception-free route found (§2.7) and §10 decision 3.
- 04:15Z: folds in the red team's verdicts on the seed-expansion revision (X-SPC-29 to X-SPC-35), all confirmed with
  conditions:
  - each tile binds its position (constants), and the forward index becomes an anchored input;
  - TT_NCP_U is assumed afresh for `ncp-v2` under the per-strip key (the two-level key keeps the existing instance;
    05:45Z);
  - the window is quoted at 17.5 T;
  - forming strata are keyed per (k, n);
  - the query draft gains the four missing specifications;
  - work-based sizing gets an integrity floor.
- 04:30Z: folds in the FP8 red team's verdict on §9's weight-noise caveat (`genuine-fp8-red-team-round9.md`, "Sampled
  proofs: the per-strip weight-noise caveat", X-SPW-1 to 6).
  - Per-strip weight noise is ruinous for NCP-FP8. The fix is a two-level key: the noise is keyed on a call-level root
    D_A over the strip digests, and each tile checks its own digest's path to D_A (§5.4).
  - The two-level key is now recommended for NCP-INT's E₁ as well, because it keeps TT_NCP_U's existing per-call
    instance. The call-wide hash of A before the GEMM (A23) comes back, and the recompute exception must also name the
    call's tree unit.
  - This changes decisions 2, 3, 4 and 9.
- 04:45Z: costs Daniel's 02:57Z question, proving the strip-building units outright once rather than drawing them
  (§2.7, route 6; §10 decision 3).
- 05:00Z: **Daniel ruled, at 03:03Z, that there is no recompute exception.** Strip generation becomes its own proof units,
  sampled like the tiles. §12 gives the theorem, the optimal allocation and the costs. It supersedes the exception
  recommended in §2.5 and §2.7, and §10 decision 3 is closed.
- 05:15Z: **Daniel decided, at 03:16Z: δ = 2⁻⁴⁰ for now, and ε = 0.1%.** §12.4 and §10 decisions 3 and 7 quote the exact
  cost.
- 05:30Z: **Daniel's 03:22Z rulings** are recorded in §10: decisions 1, 2, 5, 6, 8 and 9 decided, and decision 10
  answered (the layout gap is closed by the registered circuit; the many-salts gap survives). §12.5 adds the
  joint-objective width analysis for decision 4, the only one still open.
- 05:45Z: folds in the layout-A red team's review of the two-level key (X-SPC-36 to X-SPC-42). Everything is confirmed
  with conditions except the path check, which was a recompute across units (X-SPC-39, high):
  - X units commit their strip digest D_s, each tree node is its own unit (`ncp-node`), and a proved X unit's path nodes
    are proved with it, so the key needs no recompute (§5.4, §12.1);
  - TT_NCP_U keeps its per-call instance once `qAct` gets the unit's shape and the tree's shape is pinned;
  - the X and Y units carry the layer, site and global indices;
  - D_s is pinned in a per-row form so that it fuses into quantization, and its decode latency is **Assumed**;
  - the first form's tree unit cost 87–302 G rows per draw, not 43 G. The decided window is now ≈ 150 T (§12.4).
- 06:00Z: folds in the layout-A red team's verdict on §12 and §12.5 (X-SPC-43 to X-SPC-56). §12.2 holds, with
  conditions:
  - §12.2 gains three assumptions: A9, anchored inputs; A10, named hash assumptions for the key; and A11, no call index
    registered twice. It states the closure law as its own statement, (2′), which covers undrawn node units. A2's "no
    exception" clause is marked as policy, and A4 as cost-only.
  - §12.2 is proved in Lean, against `main`'s `Stratified`, `stratified_escape` and audit profile
    ([`/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/lean/submissions/pouw-accountable-compute`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/lean/submissions/pouw-accountable-compute/NOTES.md)).
  - §12.3 and §12.4 take the checked costs: 25.0–25.5 T at δ = 1%, 147–150 T at 2⁻⁴⁰ and 450–459 T at 2⁻¹²⁸. Closure
    is cheaper than strata. Y proofs can be reused across a run's windows.
  - §12.5 and decision 4 are revised. The served output caps leakage in every feasible design, and PoUW's count may need
    to keep Z. The recommendation is now to keep Z in the tile's checked words and certify the served Z with narrow
    units.
- 06:15Z: **Daniel, 04:23Z and 04:25Z: keep the strict partition unless a recompute is genuinely better.** §12.5 and
  decision 4 weigh the strict partitions for the served Z: (a) Z in the tile, (b) the final block split out, and (c) a
  restated `checkIdx` with Z computed once from A and B. They use the Lean worker's 04:26Z input per scheme.
  - The recommendation is (a): the partition as it stands, with Z in the tile under a width exception. It adds no cost
    and depends on nothing in Lean.
  - `ncp-z` is withdrawn. There is no compelling reason for it.
- 06:30Z: **Daniel, 04:35Z: the matmul outputs separate the tiles from the replay unit's outputs, which caps their
  influence.** Confirmed against the design. The theorem is the downstream-cut bound of his Notion draft
  ([Draft 2](https://app.notion.com/p/Draft-2-Computational-integrity-via-zero-knowledge-spot-checks-3d2399515d9e80d18797d8ebb674b676), Lemma 4.7 and Theorem 5.4). §12.5 and decision 4 now settle the width rule by that bound: no
  unit behind the Z separator needs a width exception.
- 06:45Z: **Decision 4 is decided: option (a)** (Daniel, 04:35Z: "If so, then this is fine"; the "if" confirmed at
  06:30Z). Z stays in the tile and is the separator, by Lemma 4.7 and Theorem 5.4 of Draft 2. (c) stays as an optional
  integrity upgrade and is not adopted. Every decision in §10 is now decided.
- 07:00Z: **Built, and red-teamed again.**
  - The circuit is in [PR #364](https://github.com/danielreuter/verity/pull/364) (`verity_pouw.circuit`: NCP-INT at small
    shapes). Four things changed on contact with the IR; §12.1 lists them.
  - The layout-A red team's review of the Z comparison is folded in (X-SPC-57 to X-SPC-68):
    - the separator port is pinned by the protocol, and the build enforces it;
    - the safety argument is stated as the separator topology;
    - (b)'s bound is the larger term, not the sum;
    - (c) is for NCP-INT only, on per-row leaves;
    - the integrity and cost figures are corrected.
- 07:15Z: **The draw budget is root's K = 27,713** (Verity root, 05:06Z). Its work law (draft
  [PR #362](https://github.com/danielreuter/verity/pull/362), `Flock/Draw.lean`) draws min(n_s, max(1, ⌈K·W_s/W⌉)) per
  stratum, and Lean proves the escape at most (1 − ε)^K, which meets 2⁻⁴⁰ first at K = 27,713 (27,712 misses).
  - The window's draws are now 27,715 after the per-stratum ceilings, and its rows 147.0–150.2 T. §12.3, §12.4 and
    decision 7 are recounted with the red team's cost script, and every row of the table moves only in its last digit.
  - #364's `WorkLaw` is root's rule at K = 27,713 (`plan.RECORD_K`).
- 07:30Z: §12.5 and decision 4 cite the separator result as **Theorem 5.4 at replay-unit granularity** (the
  influence-pin review): that is the form that is pinned, and the one layout A meets.
- 07:45Z: **NCP-FP8 is built** ([PR #380](https://github.com/danielreuter/verity/pull/380), stacked on #295 and #364),
  under the same layout (a). §9 says what changed on contact with #295's scheme.
- 08:20Z: **§9's FP8 proving cost corrected** (the red team's X-SPC-91 on #380): a 16 × 16 draw is 9.0–15.3 G rows,
  8–11× below a 64 × 64 one, not 16×, because the forming doesn't shrink with the tile. At the decided δ a window is
  249–424 T. The choice of 16 × 16 tiles stands. #295's leaf becomes two-level (SHAKE256 per 16 × 16 subtile, then over
  the 16 sub-digests).
- 09:30Z: **#380's fixes** (the red team's X-SPC-89 and 90). The verifier builds every id input from the shape. A
  weight's h and amplitudes are formed once per run and weight strip (`NcpFp8Amp`), and the call-wide units' gates over
  the salt and the weight id alone are the verifier's own native evaluation, read as an anchored prefix. So calls on
  one weight compose with no recomputed value, and §9's per-run amplitude unit is built.
- 12:30Z: **#295's two-level leaf is its production default** (`f76cf2ab`, its byte layout pinned by the vector
  `leaf-64-d3s-f16`). #380's tiles give its sub-digests and leaf bit for bit (`fp8.subtile_digest`, `fp8.leaf_digest`),
  against the vector and end to end on a 64 × 128 × 64 call. §9's leaf cost is #295's corrected figure.
- 12:45Z: **X-SPC-84 is decided (Verity root, 12:06Z): one stratum per template of the call's partition**, as `verify`
  derives them, each with its work and floor from the verifier's work table (the tile template its W_ref, every other 0,
  floors 1 unless POUS sets them). The two-strata form fails U2 and no pin covers it. #364, #380, #391 and #372 follow it,
  and each one's law equals `flock-verify draw --work`'s on `main`.

**The baseline:**
- one verifier, drawing from its own randomness (D6);
- drawn tiles are proved, and the verifier never recomputes them (D7);
- the noise as §5 recommends.

It answers Daniel's 00:15Z question, "how should we choose the proof units?", under his rulings: PoUW runs beside sampled
proofs with its own modeled circuit, and sampled proofs' draw replaces PoUW's own audit draw. Scope: NCP-INT, scheme
`ncp-v1` ([PR #218](https://github.com/danielreuter/verity/pull/218)), composed in vLLM by
[PR #311](https://github.com/danielreuter/verity/pull/311). §9 covers FP8.

Status tags: **Proved** (Lean, audited), **Derived** (a calculation; its inputs are stated), **Assumed** (an estimate
not yet measured), **Open**.

Sources:
- **The protocol owner's answers:** research-notes `lanes/pous/20260929T0145Z-handoff-from-verity-root.md`.
- **The red team:** [`redteam-sampled-proofs-circuit.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw-fp8/redteam-sampled-proofs-circuit.md),
  with `redteam-sampled-proofs-circuit-bound.py` and `redteam-sampled-proofs-circuit-costs.py`. The second script counts
  C-Flock rows with the repo's `verity_flock.gf2` and `sha512_circuit`.
- **The red team on bindings:** [`redteam-transcript-binding.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw-fp8/redteam-transcript-binding.md).
- **PoUW and composition notes:**
  - [NCP](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/new-crypto.md);
  - the [composition plan](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/vllm-protocol-composition.md);
  - the sparse verification note ([`internal/pouw/sparse-verification-note.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/sparse-verification-note.md));
  - the [FP8 hashing decision note](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw-fp8/fp8-hashing-decision.md).
- **C-Flock's rates,** from research-notes `kb/flock-prover.md` and the flock-netlist lane:
  - 1.4–4.6 G AND/s on an L40S for elementwise templates;
  - 69 M unit-AND/s for the one measured GEMM template, bound by host witness generation.
- **The repo** (origin/main `b4fd93e9`):
  - `protocols/sampled_proofs/`;
  - `verity.proofs.profile` (`Stratified`), with Lean `Audit/Stratified.lean` and `Flock/Draw.lean` (#167);
  - `verity.ir.partition` (`INPUT_UNIT`);
  - `verity/commitments/vllm_v1/PROTOCOL.md`;
  - `backends/flock/`;
  - #311's `protocol_options/` and `commit/challenge.py`;
  - #218's `protocols/pouw/`.

## The owner's answers, as they apply to layout A

The owner's D1–D7 are recommendations awaiting Daniel's approval, and nothing depending on them gets built before he
approves.

| Item | What the owner recommends | Under layout A (this design) |
|---|---|---|
| D1 (Q7) | count tiles under pinning, in layout B | **Not needed.** Each tile is its own replay unit, so the profile is one-stage over tiles (Q2) |
| D2 (Q7, Q9) | the existing fixed-size stratified law over tiles, without replacement; only work-proportional sizes need approval | **Adopted.** The cap is k_s ≤ T_s tiles, and a capped stratum is proved whole, escaping with probability 0 (`stratified_escape`). The one departure: #167's Lean sampler and one_stage accept only count-proportional sizes, so work-proportional sizes need a new law version (§10, decision 1) |
| D3 (Q4) | a narrow derived-input class for protocol randomness | **Superseded as the recommendation** by Daniel's proposal in its tile-local form (§5), which needs no derived-input class and no evaluation by the verifier. D3 stays the fallback. Its grinding condition holds only within one run and one fixed layout (X-SPC-28; §6.1) |
| D4 (Q8) | new leaf and tree kinds through the commitments owner; prefer salts from one per-run seed | **Adopted.** Salted A rows are fine for PoUW, so no privacy exception is needed. The red team confirms it as an informal reduction (X-SPC-23). Under `ncp-v2` the leaves' salts no longer reach the noise, so no simulation lemma is needed on the noise path (X-SPC-29; §6.1) |
| D5 (Q10) | the query fits `verity/partition/v1`; try forming as its own unit before a recompute exception | **Both costed** (§2.5). The exception is still recommended, and one named exception covers both forming and §5's noise expansion. Separate units cost +43–50%, only with forming strata per (k, n) site; their harm-weighted sizes are mandatory and need the Lean sampler change (X-SPC-26, 27) |
| Q10 (0210Z) | a generic new query, for example `Q_nested_instances` v0, if its cut passes `validate_unit_cut` and `Flock.Partition` unchanged; it must define the stratum key; per-tile forming is a recompute (option (b)); tile units need a width-rule exception. Owners: cross-call-check writes the spec, evaluator and vectors, POUS drafts the `ncp-linear` part, red-team-flock-3 reviews, flock-verifier ports it to Lean | **Adopted.** The `ncp-linear` part is drafted in §2.6. The recompute exception and the width rule go to Daniel (§10). Verity root's "unchanged per tile" for separate forming units is reconciled in §2.5 |
| D6 (Q2, Q9) | the verifier's own randomness after the registration receipt | **Adopted** (§6) |
| D7 (Q1, Q7) | drawn tiles are proved, not recomputed | **Adopted** (§4) |
| Q1, Q3, Q5 | words as tile outputs in one leaf per tile; one `Stratified` profile; bit-exact regeneration only | **Adopted** |
| Q7–Q9, parts that concern only layout B | the tile-counting profile under pinning, the two-part reveal, the with-replacement form, the fixed-count RU draw, H3 | **Not needed under A** |

## Why each tile's checked words are committed at serving

Under the two-stage protocol, serving commits only the replay units' inputs and outputs, and the verifier then draws
replay units. Anything committed after the draw was produced knowing which units would be checked.

PoUW's useful output y is the same whether or not the noised work was done, because the noise cancels exactly. If the
evidence of work came after the draw, the prover would serve y from a plain int7 GEMM and do the noised work only for
the tiles it knows are drawn. That proves no work.

So each tile's checked words are outputs of the tile, committed at serving as one leaf. That leaf is hashed in the
kernel, and no word is written to memory. A drawn tile is then proved, and its proof covers the words and the leaf.

## Recommendations in brief

**Superseded in part by Daniel's 03:03Z ruling (no recompute exception):** see §12. X and Y strips, and the nodes of the
two-level key's tree, are their own units. The draw is `Stratified` over tiles with closure: each drawn tile is proved
with the strips it reads, and each X strip with its path's nodes. A window costs 25.0–25.6 T at ε = 0.1%, δ = 1%, and
147–150 T at the decided δ = 2⁻⁴⁰.

1. **The circuit models the whole noised computation** (§2).
   - Each tile's outputs are its checked words, committed as one leaf per tile (Q1), and its final checkpoint Z = A·Bᵀ,
     committed in a narrow leaf.
   - y is dequantized from Z by width-rule units, so the only wide units are the tiles (§2.4).
   - The tile forms its own operands, checks that A is int7, and derives its own noise (item 3).
   - The partition is a generic new query, `Q_nested_instances` v0, whose `ncp-linear` part is drafted in §2.6.
2. **Layout A: each tile is a replay unit and its only proof unit** (§3).
   - `main`'s fixed-size stratified law over tiles, without replacement, from the verifier's own randomness after the
     registration receipt (D2, D6).
   - One `Stratified` profile, one δ, with work read through `harm_bound`.
3. **The noise: Daniel's proposal, tile-local** (§5).
   - The salt is one more committed Input, anchored to the registration record the way weights are.
   - **Keyed two-level** (§5.4): the noise is keyed on D_A, a Merkle root over the call's strip digests. Under §12 each
     X unit commits its strip digest, each tree node is its own unit, and a proved X unit's path nodes are proved with
     it. This keeps TT_NCP_U's per-call instance, and it is the only in-circuit key that works for NCP-FP8.
   - Each tile derives, in gates, the noise it uses: its 16 E₁ rows from the salt, the call index, a digest of its own
     16 A rows and the weight id; its 16 F₁ columns from the salt and the weight id.
   - This needs no derived-input class, no public input, and no evaluation by the verifier. One named recompute exception
     covers it and strip forming together (§2.5).
   - Because the noise is bound to A inside the Program, root_A no longer has to be fixed mid-forward. What remains of
     A23's serialization point is each strip hashing its own 16 rows (§6).
   - Each tile also binds its position: its layer, site and global row and column indices as constants, and the
     forward index as an anchored input like the salt. Otherwise identical strips get identical noise and are credited
     twice (X-SPC-30).
   - It costs about 17.5 T C-Flock rows per window (16.6 T if a real Keccak lowering reaches its AND count), against
     15.7 T plus 2.04 GB of native derivation for option (i).
     Option (ii), committing all the noise, adds 3.9–5.1 G rows per served token.
4. **The cost is proving the drawn tiles** (§4).
   - About 2.2 G rows per tile at k = 8,192, and 17 T rows per window for ε_s = 0.1% under the work rule.
   - That is 4.7 L40S-hours at 1 G AND/s, or 69 hours at the one measured GEMM-template rate. The count rule doubles
     both, to 9.8 and 143 hours.
5. **Salted A rows are fine** (§6.1).
   - Grinding buys only E₁, never the draw. It is bounded by TT_NCP_U's error term, not by grinding's cost, and that term
     ε(q, N) is not yet pinned.
   - Two gaps predate this design and apply to every option: a batch layout chosen after the salt, and a prover opening
     several runs.
6. **Hashing:** the word leaf is per-word hashing, and it is 46% of each tile's proof. Sampled proofs' commitment is not
   the binding that fits FP8's 5× (§7).

## 1. Terms

- **Program, Definition, subcircuit template, port, value:** as in the repo's Glossary. A **transition unit** is one
  16-deep accumulator step.
- **Replay unit (RU):** a part of the Program the prover replays. Its **boundary** is its inputs and outputs; its
  **interiors** are the values inside it.
- **Proof unit:** one part of an RU, proved on its own. It is *incorrect* when its committed outputs differ from its
  gates applied to its inputs.
- **The two-stage protocol:**
  1. serving commits the RUs' boundaries and registers them;
  2. the verifier draws RUs;
  3. the prover replays them and commits their interiors;
  4. the verifier draws proof units inside them;
  5. those are proved.

  With n_v = 1, steps 3 and 4 are skipped, and the audit is one-stage over the RUs (Q2).
- **The verifier:** it issues the coins and checks proofs, and every value is private (D7).
- **The input unit:** holds every Input gate: weights, request inputs and randomness. It certifies each input root
  against its external anchor (the declared weights root, the client's request commitment, the randomness source) on
  every audit, and is never drawn (`verity.ir.partition.INPUT_UNIT`).
- **Integrity profile:** the audit's output. Here it is one `Stratified` profile.
- **C-Flock rows:** the unit C-Flock's prover counts, and its rates are quoted in it. Rows are AND gates plus the
  committed carries that the repo's lowerings add. For example, SHA-512 costs 640 rows per byte, against 453 pure ANDs.

PoUW (`ncp-v1`):
- **GEMM call:** one linear layer's matmul in one forward, m × k → n.
- **Tile:** 16 activation rows × 16 weight rows at full depth.
- **Strip:** the 16 A rows shared by one row of tiles, or the 16 weight columns shared by one column of tiles.
- **Checked words:** route U's accumulator after every 16-deep step, C_t for t = 1 … 3k/16, mod 2^32. All but the last
  are *credited*.
- **Word leaf:** the commitment's leaf over one tile's 256 × 3k/16 checked words, hashed in the kernel.
- **Salt:** issued by the verifier after the weights' registration receipt, one per run.
- **E₁, F₁:** the activation-side and weight-side noise.
- **γ, ε_s:** PoUW's work gap under TT_NCP_U(0.5%), 0.60% at 8,192³; and the share of work in wrong tiles that an
  accepted audit still admits at δ. End to end, Pr[accept and T < (1 − γ)(1 − ε_s)·W] ≤ δ + η.

## 2. The circuit (question 1)

### 2.1 What the tile computes (with §5's noise)

Under Daniel's no-exception ruling (§12.1), each value below is computed in one unit: the X unit computes D_s, E₁ and X;
the node units compute D_A; the Y unit computes F₁ and Y; and the tile computes the checked words from committed X and Y.

~~~text
x (BF16, m × k)  →  A (int7 rows), s (row scales)                 pinned quantizer (+ H2 rotation for branch E)
salt                                                               a committed Input, anchored to the registration record
D_s = H(r_1 … r_16),  r_i = H(A row i)                             per strip, in gates: computed and committed by its X unit (§5.4)
D_A = MerkleRoot(D_1 … D_{m/16})                                   per call: one ncp-node unit per tree node; the root is
                                                                   committed once, and the X units read only D_A (§5.4)
E₁[i] = XOF(salt, forward, layer, site, D_A, weight id, i)        row i (global), in gates, inside the X unit
                                                                   (per-strip alternative: D_s in place of D_A)
F₁[:, j] = XOF(salt, weight id, j)                                 column j (global), in gates, inside the Y unit
                                                                   forward: an anchored Input; layer, site, i, j: constants
E₂ = E₁·P,  E₃ = E₁ + E₂,  F₂ = −P·F₁,  F₃ = F₁ + F₂                P: the pinned word-granular permutation v1.1
X = [A + E₁ | A + E₂ | −(A + E₃)] + β      Y = [B + F₁ ; B + F₂ ; B + F₃]      β = 128
C_t = c₀ + Σ_{l < 16t} X[:, l]·Y[l, :]  mod 2^32,  t = 1 … 3k/16 − 1    the credited words (tile output, word leaf)
Z = C_{3k/16} = A·Bᵀ exactly, for every noise draw                 tile output (narrow leaf); Lean cancel, stacked, checkedU_final, wrapU
y = bf16(fp32(s_i)·fp32(t_j)·Z[i][j]) + bias_j                      the useful output, in width-rule units that read Z
~~~

**This changes `ncp-v1`'s derivation.** `ncp-v1` derives E₁ from root_A, the commitment root of all the call's A rows.
root_A is a commitment artifact and can't be a Program value (Sep 27: modeling commitments is out of scope). The Program
instead uses D_A, a Program-computed Merkle root over the call's strip digests D_s (the two-level key, §5.4).
- In the random-oracle model this is the same security condition: the noise is unknown until a hash query on the
  committed inputs.
- It is a new scheme version (call it `ncp-v2`), with new vectors.
- The Lean reductions are parametric in the noise's parameters, so the theorems are unchanged. The *assumption* carries
  over too. D_A is a function of the call's whole A, so any edit to A re-rolls the whole call's E₁, as under `ncp-v1`,
  and TT_NCP_U keeps its per-call instance (X-SPC-36). Under the per-strip alternative (D_s in place of D_A) it would be
  a new instance, assumed afresh, because the prover could grind strip by strip (X-SPC-29).
- `ncp-v2` is an exact instance of the game's query points (the salt, the unit, the call's whole A through D_A, the
  weight id, the row index), up to D_A collisions, on two conditions (X-SPC-36):
  - `qAct` gets the unit's shape, since D_A hashes only the entries inside it. That is a change to PoUW's `Params`,
    whose record needs a statement reviewer. Otherwise the instance is stated per layout;
  - the tree's shape is pinned (§5.4), so no padding leaf or direction bit can serve as a free nonce.

  Given both, the leaves' hiding salts and root_A no longer reach the noise, and no simulation lemma is needed.
- **Each tile must bind its position** (X-SPC-30). If the tile read only its 16 A rows, its weight rows and the salt,
  two identical strips would get identical E₁, and on the same weight columns identical words. The prover controls
  both kinds of duplicate: padding rows, or a request batched twice. One computation would then be credited twice.
  Likewise for F₁ on identical weight column strips, such as zero-padded columns. So:
  - the layer, the site and the global row and column indices are constant arguments of each tile instance. Constants
    are structure, never committed, and they leave the template's descriptor id and its stratum unchanged;
  - the forward index is dynamic, so it is an anchored Input like the salt, carrying the verifier's enumeration.
    X-SPC-18's refusal of a repeated call index only helps because the index is in the gates;
  - under §12 the noise is derived in the X and Y units, so they carry these constants: the X unit the layer, the site
    and its strip's global row indices, and the Y unit the weight id and its strip's global column indices (X-SPC-40);
  - one key per GEMM launch. If serving ever splits one logical call, for instance into tensor-parallel shards that
    read one A, the shard index, or a weight id per shard, goes into the key.

### 2.2 The choice

- **(a) The declared int7 linear only.** Sampled proofs checks y, but y is identical with or without the noised work, so
  there is no work claim: at A = 0, γ ≥ 1 − c₀/W_ref, about 100% (Theorem B0, **Proved**).
- **(b) The noised computation, with the checked words as tile outputs** (Q1). This is what TT_NCP_U counts.

**Recommendation: (b).**

### 2.3 What γ needs the proofs to establish

| A drawn tile's proof establishes | Why PoUW's argument needs it |
|---|---|
| Every checked word of the tile, and its final checkpoint Z, equal its gates applied to its committed A rows, weight rows and salt, and match the committed word leaf and Z | TT_NCP_U counts tiles whose running sums are all correct |
| The noise it uses is the XOF of (salt, call index, D_A, weight id) with its global indices; its strip's D_s is the hash of the same 16 A rows, and D_A is the root over the strip digests. Under §12 its X unit and the node units on that strip's path establish this, proved with the tile by closure (§5.4, §12.3) | The noise must be random-oracle-derived from committed inputs. Otherwise A = −E₁ zeroes a block |
| The salt it reads is the registered one (the input unit, R5) | The noise must be unpredictable before the run |
| The useful product is Z, the final checked word. y is Z dequantized by width-rule units, which sampled proofs checks for integrity | No decode is left to skip: Z is exactly A·Bᵀ, and dequantization is glue outside W_ref |
| The word leaf and the A rows were registered before the draw, and no call index was registered twice | Work counts only before the draw, and only once (X-SPC-18) |
| A's entries are int7, and the shape is in the domain | The certificate holds only on the domain (X-SPC-5, X-SPC-16) |

What stays outside: the commitment's hashing, which the statement certifies; P's certification, done offline;
TT_NCP_U, W1 and γ, which are the certificate; the kernel's schedule; and work outside the PoUW linears.

### 2.4 The Definitions

- **`quantize-int7-rowmax`:** the pinned quantizer.
- **`ncp-tile(k, P, β)`,** the tile template (under §12, with no exception):
  - *arguments:* its committed X strip and Y strip;
  - *body:* c₀ and 3k/16 exact-integer transition units;
  - *returns:* the credited words C_1 … C_{3k/16 − 1} (one word leaf, a Program output) and Z (256 int32, a narrow
    leaf).

  In the exception's form (§2.5, superseded), the tile took the A rows, the weight rows, the salt and the forward
  index, with its position as constants, and computed D_s, the noise and the forming itself.
- **`ncp-form-x(k, n)`,** one per call and 16-row strip:
  - *arguments:* 16 A rows (typed `Value<7>` or range-checked), the salt and the forward index (both anchored Inputs),
    and the call's committed D_A;
  - *constants* (structure, never committed): the layer, the site and the strip's global row indices (X-SPC-40);
  - *body:* D_s in the per-row form (§5.4), 16 E₁ rows, and forming X;
  - *returns:* D_s and the X strip (16 rows × 3k), both committed.
- **`ncp-node`,** one per node of a call's tree. It reads its two committed children and returns the parent, committed;
  the root is D_A. The tree's shape is Program structure (§5.4), so the template carries neither m nor k.
- **`ncp-form-y(k, n)`,** one per run, weight and 16-column strip:
  - *arguments:* 16 weight columns and the salt;
  - *constants:* the weight id and the strip's global column indices (X-SPC-40);
  - *body:* 16 F₁ columns, and forming Y;
  - *returns:* the Y strip (3k × 16), committed.
- **`ncp-dequant`:** y = bf16(fp32(s_i)·fp32(t_j)·Z_ij) + bias_j, per output, reading Z, the row scales, the column
  scales and the bias. It is a width-rule unit under `Q_word`.
- **`ncp-linear(m, k, n)`:** per row the quantizer, per strip one X unit, per tree node one node unit, per 16 × 16
  block one tile, and per output one dequantization; the Y units are per run. It returns y to the model and the word
  leaves to the Program's outputs (Q1).
- **The shape domain:** 16 | m; 64 | k and n; 1,088 ≤ k ≤ 2¹⁶; and 1,600 ≤ n ≤ 2¹⁶ (X-SPC-16).
  - *At 70B* the mix relies on vLLM's fused calls, qkv (n = 10,240) and gate_up (n = 57,344). Separate k and v
    projections (n = 1,024) are out of domain.
  - *The LM head* (n = 128,256) is out of domain at TP 1, so it runs outside PoUW, and its work counts in f. There is no
    LM-head stratum. At TP 2 or TP 4 its shards (n = 64,128 or 32,064) are in domain.
  - *At TP 8,* per-rank qkv (n = 1,280) and o (k = 1,024) are out of domain.
- **`circuit-check`:** each Definition needs `circuit-check` and a binding with at least 2 tiles per strip (X-SPC-6). A
  property test checks that y equals the plain int7 linear.
- **Hash Definitions:** SHA-512 for D_s and the tree's nodes, which the repo has (`sha512_circuit`), and SHAKE256 for
  the XOF; decision 6 keeps this conservative family. The repo has no Keccak circuit, so SHAKE256 also needs a C-Flock
  lowering.
- **The partition query:** `Q_nested_instances` v0, drafted in §2.6.
- **Evaluation is per drawn instance.** The words never exist outside a drawn tile's proof: they come to 412 GB per call
  at 8,192³.
- **A C-Flock lowering of the tile.**
- **#311:** `traced_as("ncp-v1")` names `ncp-linear`. #311's refusal of PoUW beside sampled proofs lifts once it is
  registered.

### 2.5 Recomputes inside the tile: the exception, or separate units (D5)

Each tile computes some values that other tiles of the same template also compute:
- **X strips:** forming X for its 16 rows, which the n/16 tiles of that row share;
- **Y strips:** forming Y for its 16 columns, which every tile of that column shares, in every call of the run on that
  weight;
- **under §5,** the strip digest D_s and the noise slices (16 E₁ rows and 16 F₁ columns), shared the same way.

`validate_unit_cut`, and Lean's `Flock.Partition`, refuse any two gates in different units that compute the same
function of the same values (`gate-recomputed`). This holds however the Program is written, because the query tooling
finds the duplicates across instances (Verity root, 0210Z §2). Committed A rows don't help: they cover the *inputs* of
forming, not its gates, and X can't sit under root_A because X depends on E₁.

**One named exception covers all of these.** All three are the same kind of recompute:
- the value is a function of the tile's own inputs (its A rows, its weight rows, the salt);
- it is recomputed across instances of one tile template;
- it stays inside each tile, is never committed, and is certified by that tile's own proof.

So one exception can name them all: "recomputes across instances of `ncp-tile`, and between them and the call's
`ncp-tree` unit, of values computed from committed inputs: strip forming, the strip digest, its Merkle path to D_A, and
the noise slices". It is reported on its own line with its gate count, in both `validate_unit_cut` and
`Flock.Partition`.

The path nodes are recomputes of the same kind. Under the two-level key (§5.4), the tiles of sibling strips, and the tree
unit that commits D_A, all hash the same nodes. They add 7–10 compressions (448–640 bytes) per tile. Opening D_A and
the siblings adds 11–30 M rows per tile, so 0.5–1.4% of a tile's proof in all (X-SPC-37). The red team also found this
wording exceeded Verity root's limit, and neither checker has an allowance for it (X-SPC-39).

**Its size per drawn tile** (**Derived**, C-Flock rows at k = 8,192; §4's prices):
- strip forming, c₀ and the rest: 0.02 G, about 1% (Verity root estimates 2–3% of gates);
- the noise XOF, 32·k bytes: 0.07–0.15 G;
- the strip digest, 16·k bytes: 0.04–0.08 G.

In total the recomputed values are about 6–12% of a tile's 2.2 G rows. Daniel's Sep 26 invariant anticipates this case:
"recomputation, if ever wanted, is an explicit, measured optimization reported on its own line".

**The alternative, option (a), is separate units whose outputs are committed:**
- an X-forming unit per call and 16-row strip, which computes D_s, the E₁ rows and X;
- a Y-forming unit per run, weight and 16-column strip, which computes the F₁ columns and Y.

These units recompute nothing, and they need no exception.

**The cost of option (a)** (**Derived**; 70B, ε_s = 0.1%, work rule):

| | (b) the named exception | (a) separate forming units |
|---|---|---|
| New committed values at serving | none | X at 3 bytes per A byte, about 12.8 MB per token; Y at 3 bytes per weight per run, about 207 GB per run (Verity root's figures). E₁ and F₁ stay inside the forming units, so they aren't committed |
| Harm of a wrong unit | its own work | every tile it feeds. X = 0, or noise that isn't the XOF output, lets those tiles be correct and cheap. That is a row of up to n/16 tiles, or a column across every call of the run |
| Sizing | the tile strata, by either rule | the forming strata must be sized by the work they feed: about t draws each for X and for Y. They must be keyed per (k, n) site, because an X unit's harm, n/16 tiles, varies 7× across the k = 8,192 sites. With one stratum per forming template the extra roughly doubles, to +92% (X-SPC-26). Under the count rule they get about 1/513 of the tiles' draws, which is unsafe. So harm-weighted sizes are mandatory, and they need a new law in `Flock/Draw.lean` and one_stage, since #167 refuses them (X-SPC-27) |
| A tile's own proof | 2.15–2.27 G rows at k = 8,192 | about 2.34 G. The arithmetic is unchanged, but the tile opens X and Y, which are 3× the size of A and B |
| Drawn forming units | none | X units at 0.69–0.83 G each, Y units at 0.62–0.69 G, about 4,600 draws of each: +6.1–7.0 T |
| **Proving per window** | **≈ 17.5 T** (16.6 T with Keccak at its AND count) | **≈ 24.5–25.4 T, about +45–47%**, with forming strata per (k, n). Keyed by k alone, as §2.6's first draft had it, it is 32.0–34.1 T, **+93%** (X-SPC-33) |

The red team measured the same gap against the tiles of option (i), which open only A and B: +43% in the design's unit
(SHA-512 at 453 ANDs per byte), and +50% in C-Flock rows. That is 15.7 T for option (i)'s tiles, against 18.2 T for tiles
opening X and Y, plus 5.4 T of forming draws (X-SPC-26). It holds only with forming strata per (k, n) site.

**Why this differs from Verity root's "unchanged per tile".** That figure counts a tile's own gates, which are indeed
about unchanged: forming moves out. It leaves out two costs:
- each tile then opens X and Y instead of A and B, which is 3× the bytes;
- the forming units must be drawn and proved too, sized by the work they feed.

The second is most of the difference: 5.4 T of the red team's 7.9 T.

**Two conditions if option (a) is chosen** (X-SPC-27):
- **Y's scope.** Y is per run and feeds every window. Either every window's partition includes the run's Y units, drawn
  afresh and each charged that window's share of work, or Y is audited once per run and charged the whole run's work.
- **The per-tile lifting** must say that a tile counts only when its X and Y strips are also correct, because the game
  has no X or Y.

**Superseded (Daniel, 03:03Z: no exception; §12).** The original recommendation was the named exception (b). It keeps every harm local to its tile, works under either size rule, and
costs about 6–12% of a tile. Option (a) is the fallback that keeps Daniel's rule. It costs about +40–50% proving and
207 GB per run of new committed values, and it needs per-site harm-weighted strata with a new law in the Lean sampler.

### 2.6 Draft: the `ncp-linear` part of the partition query

For the cross-call-check lane to fold into its spec, evaluator and vectors. Red-team-flock-3 reviews it, and
flock-verifier ports it to Lean (Verity root, 0210Z §3). It follows Daniel's no-exception ruling (§12.1), with the
two-level key's tree in node units (X-SPC-39).

~~~text
partition object (standard shape):
  {"format": "verity/partition/v1", "program": <SHA-512 of the program>,
   "query": {"name": "Q_nested_instances", "version": 0,
             "params": {"templates": [<descriptor ids of ncp-tile(k, P, β) for each k, ncp-form-x(k, n) and
                                       ncp-form-y(k, n) for each site, and ncp-node>],     # non-empty, distinct
                        "rest": {"name": "Q_word", "version": 1, "params": {"X": 16, "W": 32}}}}}

units:
  - every instance of a listed template is one unit, found through call, batch and scan:
    each batch member and each scan iteration is its own instance (v0 of the template queries refuses scan;
    a layer scan would otherwise hide every tile)
  - canonical numbering: instances in the program's canonical gate order (strata are ranges of unit numbers)
  - every other gate is partitioned by "rest" applied to the residual graph (below)

the residual graph ("the rest"):
  - carving the template instances out of a Call leaves a residual: the A rows become its returned values, Z its inputs
  - the spec fixes the residual's input numbering and target order (Q_word's packing depends on return order),
    with vectors in the qword_vectors.json style, so the Python and Lean evaluators agree
  - every enclosing Definition returns the word leaves up to the root, so they are program outputs, not committed-unread

ncp-linear(m, k, n), as the Program writes it:
  quantize-int7-rowmax   per row                        -> A rows, s                     rest
  ncp-form-x(k, n)       per 16-row strip               -> D_s, X strip                  one unit each
  ncp-node               per node of the call's tree    -> the parent (the root: D_A)    one unit each
  ncp-tile(k, P, β)      per 16 × 16 block              -> word leaf, Z                  one unit each
  ncp-dequant            per output                     -> y                             rest
and once per run, read by every call on that weight:
  ncp-form-y(k, n)       per weight and 16-column strip -> Y strip                       one unit each

one X unit:
  reads      16 A rows (committed), salt and forward index (input unit, anchored), the call's D_A (committed)
  constants  layer, site, the strip's global row indices
  computes   D_s (the per-row form, §5.4), 16 E₁ rows, X (16 rows × 3k)
  writes     D_s and the X strip (committed)

one node unit:
  reads      its two children (committed: D_s from X units at the bottom level, a node unit's parent above it)
  structure  the tree's shape: RFC 6962 (unbalanced, no padding), children wired by the constant strip index,
             the node hash domain-separated from the leaf hash (§5.4)
  computes   one node hash
  writes     the parent (committed). The root is D_A, one per call, read by every X unit of the call

one Y unit:
  reads      16 weight columns (input unit), salt (input unit, anchored)
  constants  weight id, the strip's global column indices
  computes   16 F₁ columns, Y (3k × 16)
  writes     the Y strip (committed)

one tile unit:
  reads      its X strip and its Y strip (committed)
  computes   c₀, 3k/16 transition units
  writes     the credited words C_1 … C_{3k/16−1}  (one word leaf; a program output, read by no unit)
             Z = C_{3k/16}                          (256 int32 in a narrow leaf; read by ncp-dequant)

stratum key (new: core, one_stage and #167's strataOf define strata only for the template queries today):
  tile units   -> the tile template's descriptor id (it carries k): one stratum per k, 2 at 70B; drawn by work
  X, Y units   -> their descriptor ids, which carry (k, n); proved by closure with each drawn tile (§12.3)
  node units   -> one stratum (ncp-node carries neither m nor k); proved by closure with each proved X unit's path
  rest units   -> a key the spec must define, for example the Q_word unit class; new in all three
~~~

- **What must still hold.** The cut passes `validate_unit_cut` and `Flock.Partition` unchanged, with no exception:
  - every gate is certified by exactly one unit;
  - the committed set is exactly the boundary set;
  - every read across units goes through a committed value.
- **The units read each other in a cycle** (an X unit's D_s feeds the tree, whose root feeds the X unit), but the gate
  graph has none. Both checkers check gates, not an order on units, so this is allowed; the spec should say so.
- **The shape domain,** 1,600 ≤ n ≤ 2¹⁶ and the rest, is checked when the Program is registered. An `ncp-linear` outside
  it isn't PoUW: its tiles are ordinary `Q_word` units, and its work counts in f.
- **Width.** A tile unit outputs 256·(3k/16 − 1) words plus 256 words of Z, far above the width rule's 16 or 32 bits. The
  X and Y units output whole strips, and a node unit a 512-bit digest. Decision 4 settles this by the Z separator (§12.5):
  no unit behind Z needs a width exception, and the tiles' Z bits are the only departure from the Sep 26 rule. Moving the
  dequantization out keeps y, and everything downstream, under the width rule.

### 2.7 Can the recompute exception be avoided? Every exception-free route found

Daniel's question (02:36Z). All figures are **Derived**, per 70B window at ε_s = 0.1% under the work rule, in C-Flock
rows, and none is red-teamed yet. The recommended design, with the exception, costs about 17.5 T and keeps γ at 0.60%.

**The exception affects only proofs.** Serving computes each strip's operands, its digest and its noise once, and each
weight's noise once per forward, whichever route is chosen. The "recompute" exists only in how the Program is cut into
proof units: a drawn tile's proof re-derives its strip's share, about 6–12% of that proof. So the exception costs
nothing at serving.

**What would have to change.** To avoid the exception, no two units may compute the same function of the same values.
The shared values are the X strip, D_s and the E₁ rows (shared by a row of tiles), and the Y strip and F₁ columns
(shared by a column of tiles, across calls).

| Route | Serving cost | Proving per window | Security effect | Verdict |
|---|---|---|---|---|
| **1. Separate forming and noise units** (§2.5, option (a)) | X committed at 12.8 MB per token; Y committed at about 207 GB per run | ≈ 24.5–25.4 T (+45–47%), with forming strata keyed per (k, n); +93% keyed by k alone | γ unchanged. But a wrong unit taints every tile it feeds, so harm-weighted strata per (k, n) site are mandatory, needing a new law in the Lean sampler (#167). Y's scope across windows must be chosen | **Viable, and the only exception-free route that keeps γ.** Costly |
| **2. Noise per tile** (E, F, or both, derived with the tile's coordinates, so each tile's operands differ) | per-tile E adds 1/16 B of XOF per useful MAC (one byte per noise entry; 3/64 packed), +8% on the word hashing at every batch size. Per-tile F costs 1/16 B per MAC at every batch size, against 1/m today: 512× more at m = 8,192, and the same at m = 16. Per-tile D_s adds a strip hash per tile, a further 1/16 B per MAC | about unchanged (each drawn tile already derives its own noise) | **It breaks γ.** Unique operands mean unique forming: each tile forms its own 16 rows (and columns) at 24 W1 units per position, uncredited honest work equal to half the tile's MACs, where today it is shared n/16 ways (8/n). Ω* rises from 1 + 8/n to about 1.5 with per-tile E, or about 2 with both, so γ goes from 0.60% to about 34% or about 50%. Removing every recompute needs both. It also changes the noise distribution, so TT_NCP_U needs restating, and F stops being per run and weight | **Fails γ** |
| **3. Larger units: a row strip per unit** (all n/16 tiles of 16 rows) | none extra for X, D_s and E₁, which are shared inside the unit. Y and F₁ are still shared across row strips and calls, so it needs route 1's committed Y (207 GB per run) or the exception | each draw proves a whole strip, 512 to 3,584 tiles at 70B: about 5.6 T rows per draw on the work-weighted mix. The number of draws doesn't shrink with unit size, so ≈ 26 P rows per window, about 1,600× the tile layout (about 7,000 L40S-hours at 1 G AND/s) | γ unchanged | **Infeasible** |
| **4. The strip digest as its own small committed unit** (32 B per strip; about 0.6 KB per token) | negligible | removes the digest from each tile (−0.29–0.65 T), but adds harm-weighted digest draws (a wrong D_s taints its strip's tiles) | it removes only D_s's recompute. The E₁ expansion, X and Y are still recomputed | **Not enough on its own.** It is part of route 1's X units |
| **5a. Forming units at word size,** under `Q_word`'s width rule | X and Y at word granularity, plus the XOF's inner state. A Keccak permutation can only satisfy the 32-bit width rule if every round's 1,600-bit state is committed: about 35× the noise bytes, roughly 150 MB per token for E₁ and 2.4 TB per run for F₁ | small per draw, but the tiles still open X and Y (≈ 18.2 T) | γ unchanged | **Not better.** It trades the recompute exception for a width exception on hash units, or a heavy commitment |
| **5b. A one-sided construction** (no weight-side noise, like FP8's H-1T) | Y = B, the committed weights, so nothing is formed on the weight side. X would go to per-strip units (12.8 MB per token), with no per-run 207 GB | about route 1's X half | a different PoUW construction for NCP-INT, with its own γ and conjecture | **Research, not available now** |

**Route 6. Prove the strip-building outright instead of drawing it** (Daniel, 02:57Z; **Derived**, C-Flock rows at the
red team's prices, not red-teamed).

*What a run and a window are in the current design.*
- **A run** has one salt, issued by the verifier after the weights' receipt. Its F₁, and so Y, is fixed for its lifetime,
  and its call indices are enumerated within it.
- **A window** is the audit unit. At its end every root is registered with a receipt, the verifier draws about 4,600
  tiles, and the window gets its own profile at its own ε_s.
- A run holds one or more windows. The simplest choice so far has been one window per run (§5.2).

*The weight side, outright once per run.* One proof covers every weight's F₁ derivation and commits Y = [B + F₁; B + F₂;
B + F₃]:
- F₁'s XOF: 68.5 GB × 282–565 rows per byte, 19–39 T;
- opening B (68.5 GB × 640): 44 T;
- committing Y (205.5 GB × 640): 132 T;
- the forming arithmetic: a few T.

That is **≈ 200–220 T rows per run**, about 56–61 L40S-hours at 1 G AND/s, or 800–890 h at the measured GEMM-template
rate. Hashing Y dominates.
- Y's correctness is then established exhaustively, so the question of Y's scope across windows disappears.
- The prover regenerates Y slices bit-exactly from B and the salt, so nothing is retained.
- But the tiles then open Y (16·3k bytes) instead of B (16·k) plus in-tile F₁: +0.7–1.0 T per window.

*The activation side, outright per window.* One proof covers every X strip of the window: the A rows opened, D_s, E₁'s
XOF, and X committed.
- That is 4.26 MB × (640 + 282–640 + 282–565) plus 12.8 MB × 640 rows per token: **≈ 13–16 G rows per served token.**
- It scales with tokens, like option (ii) (3.9–5.1 G per token), but about 3× worse, because X is 3× A. It overtakes the
  whole tile budget (17.5 T) past about 1,100–1,300 tokens per window, and it never amortizes. Your guess is confirmed.

*The comparison, per 70B window at ε_s = 0.1%:*

| Option | Per window | Per run | Break-even windows per run, against route 1 | Against the exception |
|---|---:|---:|---:|---|
| The exception (recommended) | ≈ 17.5 T | 0 | — | — |
| Route 1: X and Y as drawn, harm-weighted units | ≈ 24.5–25.4 T | 0 | — | never better |
| 6(c1): Y outright per run, X under a smaller exception (recomputes within one call only) | ≈ 18.2–18.5 T | ≈ 200–220 T | ≈ 30–35 | never: +0.7–1.0 T per window, plus the per-run proof |
| 6(c2): Y outright per run, X as drawn units (fan-out n/16), no exception | ≈ 21.4–22.0 T | ≈ 200–220 T | ≈ 63–76 | never |
| 6(b): X outright per window | 17.5 T + 13–16 G per served token | — | — | never |

- **Against route 1,** the outright weight side pays off only for long runs: above about 70 windows per run with no
  exception (c2), or above about 30 with the smaller exception (c1).
- **Against the exception,** it never pays: every per-window term is already higher, before the per-run proof.
- **FP8 can't amortize at all.** Its weight noise is per call (r = 1), so an outright weight-side proof would recur every
  forward. Committing F₁ alone is 63–82 T rows per forward (X-SPW-6), and Y would add about 132 T more.

**Verdict on route 6:** the weight-side proof is a real alternative to route 1 only if runs span tens of windows. The
activation-side proof is ruled out. None of it beats the exception. If Daniel declines the exception but accepts runs of
70 or more windows, 6(c2) is the cheapest exception-free route; with shorter runs, route 1 is.

**Superseded (Daniel, 03:03Z: no exception; §12).** The original recommendation was to keep the exception.
- The only exception-free route that preserves γ is route 1. It costs 40–50% more proving, 207 GB per run of committed Y,
  and per-site harm-weighted strata that need a Lean sampler change.
- Per-tile noise looks cheap at serving but breaks γ, because it destroys the sharing that makes forming nearly free.
- Larger units multiply the proving by about 1,600.
- The exception changes nothing at serving and costs about 6–12% of each drawn tile's proof.

## 3. Replay units and proof units: layout A against layout B

**Layout A: each tile is a replay unit and its only proof unit (n_v = 1).**
- *Boundary:* in, its A rows, weight rows and the salt; out, the word leaf and Z. y comes from width-rule dequantization units that read Z.
- *Draw:*
  - k_s tiles uniformly without replacement per stratum, from the verifier's own randomness after the receipt, sent in
    the clear;
  - strata are per template, one `ncp-tile(k)` per k, which gives 2 strata at 70B. W_ref per tile varies with n by at
    most 0.5%, and `harm_bound`'s (harm, units) pairs keep the profile exact (X-SPC-15);
  - a stratum whose k_s would exceed its T_s is proved whole, and escapes with probability 0 (`stratified_escape`).
- *Profile:* one `Stratified` profile with one δ, and work as `harm_bound({template: W_ref per tile})`.

**Layout B** (a row block as the replay unit, tiles as proof units): the same draws and proving, but it needs D1 and
B's root tree kind.

**Recommendation: layout A.** It is the two-stage protocol with n_v = 1, which involves no capture of replay-unit
interiors. It uses `main`'s law and profile as they are, except for the size rule under decision 1.

**What the prover keeps:**
- word leaves are rebuilt by rerunning the drawn tile's row block of NCP, which is deterministic integer arithmetic;
- A rows of drawn tiles are kept (about 4.3 MB per token at 70B, int8), or regenerated bit-exactly on a batch-invariant
  path (Q5);
- the A-row salt seed is kept until the openings are done.

Noise needs no retention, because the tile derives it.

## 4. The cost of proving drawn tiles

The inputs are the red team's C-Flock row counts (X-SPC-19 to X-SPC-21, **Derived** with the repo's lowerings):
- **An int8 multiply-add:** 132 rows in a fused lowering (one carry-save tree per 16-deep step), or 151 unfused.
- **The in-circuit hash, per byte:**

  | Hash | Rows per byte |
  |---|---:|
  | SHA-512 | 640 (the repo's `sha512_circuit`) |
  | SHAKE256 | 282–565 (38,400 ANDs per 136 B, up to double if the state is committed each round; the repo has no Keccak circuit) |
  | TurboSHAKE128 | 114–229 |

**Per drawn tile** (SHA-512 leaves; noise opened as committed inputs, as the red team counted it):

| Part | k = 8,192 | k = 28,672 |
|---|---:|---:|
| Checked-word arithmetic | 0.83 G | 2.91 G |
| Hashing the words (1.57 MB; 5.5 MB) | 1.01 G | 3.52 G |
| Opening the inputs (4·16·k bytes, plus paths) | 0.35 G | 1.19 G |
| Forming, c₀ and dequantization (dequantization now runs in width-rule units) | 0.02 G | 0.06 G |
| **Total** | **2.20 G** | **7.68 G** |

- Hashing is the largest part, at 46%. TurboSHAKE128 for the words cuts the tile 30–38%, and for the inputs too, 39–50%.
- With §5's design the tile opens only A and the weights, and derives its noise. The per-window totals for that design
  are in §5's table.

**Per window, ε_s = 0.1% at δ = 1%, 70B with fused in-domain calls, m = 8,192:**

| Size rule | Draws | Total | L40S time at 1 G AND/s | at 69 M/s (the measured GEMM-template rate) |
|---|---:|---:|---:|---:|
| Work-proportional, ⌈t·W_s/W⌉ | 4,604 | 17.1 T rows | 4.7 h | 69 h |
| Count-proportional, max(1, round(K·n_s/N)) (#167 today) | 12,942 | 35.4 T rows | 9.8 h | 143 h |

**These totals count the noise opened as committed inputs,** as under option (ii). The window, in C-Flock rows at 4,604
draws, depends on how the noise is handled:
- 15.7 T when the verifier derives the noise (option (i));
- about 17.5 T when each tile derives it, the recommendation. That is 16.6 T if a Keccak lowering reaches its AND count; no
  repo lowering shows that yet, so quote 17.5 T (X-SPC-32);
- 17.1 T when the noise is committed.

Earlier versions' 14 T was in the design's own unit (SHA-512 at 453 ANDs per byte). In C-Flock rows, option (i)'s window
is 15.7 T (X-SPC-21, X-SPC-26).

1 G AND/s is an elementwise-template rate. The only GEMM-template measurement is 69 M/s, until witness generation moves
to the GPU. So the honest range for a window is **4.7–9.8 L40S-hours at 1 G AND/s, and 69–143 hours at the measured
GEMM rate**. The number of draws depends on ε_s and δ, not on how much was served.

**Integrity floor** (X-SPC-35).
- Under work-based sizing, every non-tile stratum has W_ref = 0, so ⌈t·W_s/W⌉ gives it zero draws. The dequantization
  units, and so y, would never be checked, and neither would the quantizer or the rest of the model.
- The sizing rule therefore needs an integrity floor for the non-tile strata: at least #167's max(1, ·), or better, a
  count budget sized for the integrity guarantee sampled proofs gives the rest of the Program today.
- The floor adds draws of small units, so it changes little in rows. It is part of decision 1.

### 4.1 Serving-side costs (per token at 70B, fused in-domain calls)

| What serving computes or commits | Size | Note |
|---|---:|---|
| Word leaves: every credited word hashed in the kernel | 51.3 GB hashed per token (0.75 B per useful MAC) | the dominant serving cost. Daniel's 394× acceptance was priced with SHAKE256 on the 4090; SHA-512 on a GPU is unpriced (audit A22, §10 decision 6) |
| Z's narrow leaf: 256 int32 per tile | 26.9 MB committed per token (4 B per PoUW output × 6.72 M outputs) | about 2× y's BF16 and 1/1,900 of the word hashing. It adds no retention: Z = A·Bᵀ regenerates bit-exactly from A and the weights with a plain int7 GEMM |
| A rows, committed with hiding leaves | 4.26 MB per token | retention: §3, decision 8 |
| Strip digests D_s, and the call's root D_A | 4.26 MB hashed per token, plus about 1.3 KB per token of tree nodes, hashed and committed (X-SPC-41) | computed once in the kernel, fused into the quantization pass with D_s in the per-row form (§5.4). This is the call-wide barrier (A23; §6 step 3) |
| E₁, derived per call | 4.26 MB of XOF per token | row by row, from D_A, once the call's last strip is hashed |
| **F₁, re-derived per forward** | **about 69 GB of XOF per 70B forward** (1 B per weight) | see below |
| Y = B + F, formed per forward | transient, formed in chunks (#315's `per-forward` mode, about 146 MiB) | no resident copy |
| X strips, committed (no exception, §12) | 12.8 MB per token (3 bytes per A byte) | about 1/4,000 of the word hashing; regenerable bit-exactly |
| Y strips, committed once per run (no exception, §12) | about 207 GB per run (3 bytes per weight) | about 4 tokens' worth of word hashing; regenerable from the weights and the salt, so nothing is retained |

**F₁ is re-derived every forward, by design.**
- F₁ is per run and weight: one byte per weight parameter. Keeping it, or Y, across forwards would be a resident
  weight-derived copy, which Daniel has closed (00:15Z; composition decision 3). #315's default, `per-forward`,
  already re-derives it.
- That costs about 69 GB of XOF per 70B forward: about 0.14 s of H100 SHAKE256 time at about 0.5 TB/s (audit A6's
  rate), or less with TurboSHAKE128.
- It is small at prefill-sized batches: 1/6,000 of the word hashing at m = 8,192. It isn't small at the domain's smallest
  batch, m = 16, where it is about 8%.
- **`ncp-v2` changes nothing about F₁.** Only E₁'s derivation changes (D_A, the Program's root over the strip digests, in place of root_A). F₁ still reads only the
  salt and the weight id, as in `ncp-v1`, so the serving cost and the no-copy constraint are the same under both.

## 5. The noise

### 5.1 The options

- **(i) The derived-input class (D3).** The verifier derives each drawn tile's noise from registered fields, and the
  values go into the statement. This makes the noise a public input, and has the verifier run the XOF.
- **(ii) Committed in full.** The prover commits E₁ and F₁, and the input unit proves on every audit that all of it
  matches its derivation.
- **The middle form (iii).** Each drawn tile's proof derives its noise from root_A as a statement value. That is
  modeling commitments, which is out of scope.
- **Daniel's proposal (02:12Z).** Seed expansion inside the circuit, proved by sampled proofs, with the verifier's
  randomness as one more circuit input. This is worked out below, in two partitions:
  - *(a)* the expansion inside each tile;
  - *(b)* the expansion in its own units.

### 5.2 Daniel's proposal, worked out

**Item 1. The salt as one more Input, anchored like the weights.**
- The prover commits the salt under an input root. The registration record carries the salt's anchor. The input unit
  certifies it on every audit by R5, a native comparison of roots, the way the weights root is checked.
- **It fits `main` as-is.**
  - `INPUT_UNIT` already names "randomness" inputs anchored to "the randomness source".
  - `IntegrityProfile.prescribed` is a free-form set, so "salt" is one more family.
  - The `Stratified` law and profile are untouched.
  - There is no public input, and the verifier computes only the salt's commitment root from a value it issued itself,
    not any part of the Program.
- **What it needs:** the registration record carries the salt anchor, the owner's condition "the salt in the
  registration record". It also needs a claim id in `verity.claims` for the salt's unpredictability: a PRF claim on
  `derive` keyed by the verifier's secret (X-SPC-17).

**Item 2. The XOF expansion as Program gates.**
- **(a) Inside each tile's unit.**
  - The tile expands its own 16 E₁ rows and 16 F₁ columns, 32·k bytes of XOF, at 282–565 rows per byte.
  - The same rows are expanded again in every tile that uses them. Each E₁ row is expanded in all n/16 tiles of its
    strip: 512 at n = 8,192, and 3,584 for gate_up at n = 57,344. Each F₁ column is expanded in all m/16 tiles of its
    column, in every call of the run on that weight.
  - That is the D5 recompute exception again, and the same named exception covers it.
  - Only drawn tiles pay: 0.57–1.15 T rows per window.
- **(b) In its own units.**
  - An E₁ unit per strip and call, and an F₁ unit per column strip and run, each committing its output. The tiles open
    their noise, as in the 17.1 T baseline.
  - A wrong expansion unit taints every tile it feeds: a strip of up to n/16 tiles, or a column across every call of the
    run. So these units need harm-weighted sizes, about t draws per kind:
    - E₁ units, including the strip digest of item 3: about 1.9–2.5 T rows;
    - F₁ units: about 0.94–1.23 T rows.
  - **Do the per-run F₁ units need proving whole?** Not at 70B: there are about 420,000 column-strip units per run,
    against about 4,600 draws. They would only if a stratum's harm-weighted k_s exceeded its size, as in a tiny model or
    window. But F₁ units feed every window of the run, so either each window's draw includes them again, charged the
    work they feed in that window, or a run is one window.
  - Under count-proportional sizes these strata get about 1/513 of the tiles' draws, which is unsafe, so (b) needs
    decision 1's new law version.
  - **(b) pays off only if forming moves out too.** If the recompute exception is declined, forming has to leave the
    tile anyway (§2.5). The noise then sits inside the forming units, since X-forming needs E₁ and Y-forming needs F₁,
    and E₁ and F₁ need not be committed. That combined layout is §2.5's option (a): about 24.3–25.2 T rows per window.
    With the exception granted, (a) of this item is cheaper. So separate noise units without separate forming units
    are never the best choice.

**Item 3. Binding the noise to A without root_A as a Program value.** The salt is known before serving, so the noise
must depend on A. Otherwise the prover sets A = −E₁, which zeroes one of the three blocks, about a third of the tile's
work.
- **(a) A digest of the call's A, computed in gates in its own units** (a Merkle tree over the strips).
  - A wrong digest unit lets the prover choose the A rows beneath it after seeing E₁. For a leaf unit that is one strip;
    for the root, the whole call.
  - That is a wrong proof unit, not grinding, so TT_NCP_U's ε does not cover it. Only the sampling bound does, with
    harm-weighted sizes: about t draws per tree level, with the top levels proved whole, about 1.3 T rows in all.
  - TT_NCP_U's ε covers only re-rolling a *correct* digest by editing A, within one run and one layout. Its size is not
    pinned yet (§6.1).
- **(a′) A digest of each strip, computed inside each tile** (recommended).
  - The tile hashes its own 16 A rows into D_s and derives its E₁ rows from D_s. This is still noise derived by a random
    oracle from the unit's committed inputs, which is exactly the sufficiency condition.
  - A wrong D_s makes that tile wrong, charged only its own work, so no harm weighting is needed. It rides on the same
    recompute exception.
  - Cost: 16·k bytes at 282–640 rows per byte, 0.29–0.65 T rows per window.
  - It needs the derivation change of §2.1 (`ncp-v2`).
- **(b) A digest of something smaller that determines A,** such as the request tokens.
  - Hashing them is nearly free. But E₁ then becomes predictable before the forward.
  - Every unit upstream of A (the quantizer, norms, attention, earlier layers, the KV cache) becomes a lever: a wrong
    upstream unit can steer A toward −E₁. So all of them would need PoUW harm charges on top of their integrity role.
  - **Not recommended.**
- **(c) Other ways.**
  - A live salt per call, issued after each call's A is committed, costs a verifier round trip per linear call:
    impractical.
  - Restricting A was refuted (≥ 6.2%, NCP §3).
  - root_A as a Program value is out of scope.

  So (a′) was the one to use. The two-level key (§5.4) replaces it: (a)'s tree, in node units proved by closure with
  each proved X unit rather than by harm-weighted strata, which binds E₁ to the whole call's A.

### 5.3 The comparison

Proving per window, 70B, ε_s = 0.1%, work rule, C-Flock rows (**Derived**). Without noise openings, the tile proofs are
15.7 T; with them, 17.1 T.

| Option | Proving per window | Other cost | What it needs |
|---|---:|---|---|
| **Daniel's proposal, (2a) + (3a′): tile-local** | **≈ 17.5 T** (4.9 h at 1 G AND/s; 71 h at 69 M/s) | the salt anchor (R5) | the recompute exception (shared with forming), `ncp-v2`'s derivation, and a hash Definition with its C-Flock lowering. No public input, no evaluation by the verifier |
| Daniel's proposal with no exception: noise and forming in separate units (§2.5, option (a)) | ≈ 24.3–25.2 T | commits X (12.8 MB per token) and Y (about 207 GB per run) at serving | harm-weighted sizes, so a new law version for safety; no recompute exception |
| Daniel's proposal, (2a) + (3a): a call digest in its own units | ≈ 17.6–18.2 T | none | the recompute exception, and harm-weighted sizes for the digest strata |
| (i) Derived-input class (D3) | ≈ 15.7 T | the verifier derives 2.04 GB of XOF natively per window | the partition invariant's "no public inputs" and the "verifier evaluates nothing" rule both change, for protocol randomness |
| Middle form (iii) | ≈ 16.3–16.9 T | none | root_A as a statement value: out of scope |
| (ii) Committed in full | 17.1 T, plus 3.9–5.1 G rows per served token (E₁) and 63–82 T per run (F₁) | none | nothing new; it overtakes the tile proofs past 3,300–4,400 tokens per window |

**Recommendation: Daniel's proposal in its tile-local form, (2a) + (3a′).**
- It keeps both standing rules (no public inputs, and a verifier that evaluates nothing).
- It keeps every harm local, so it works under either size rule.
- It costs 6–12% more proving than (i), and a small fraction of (ii) at any real window.
- Its one exception is the recompute exception that forming needs anyway.
- If Daniel declines that exception, noise and forming move together into separate units (§2.5's option (a)). That keeps
  his rule at about +40–50% more proving, and needs per-site harm-weighted sizes with the Lean sampler change. If he
  prefers the cheapest proving, (i) is 6–12% cheaper, but changes two rules.

### 5.4 The two-level key (the FP8 red team's X-SPW-4), and why NCP-INT uses it too

**The key, with no recompute** (Daniel's 03:03Z ruling; the layout-A red team's X-SPC-39).
- Each X unit hashes its 16 A rows into its strip digest D_s, and commits it.
- One `ncp-node` unit per node of the call's tree reads its two committed children and commits the parent. The root is
  D_A = MerkleRoot(D_1 … D_{m/16}), and there is one committed D_A per call.
- Each X unit reads only D_A, and derives its E₁ rows from it with the global indices. For NCP-FP8 both streams are keyed
  on D_A: E₁ with the row index, F₁ with (call, weight id, j). For NCP-INT, E₁ uses D_A, and F₁ stays per run and
  weight, since NCP-INT's weight noise doesn't read A.
- **Path closure.** When an X unit is proved, the node units on its strip's path to D_A are proved with it, each node
  once (§12.3). That is a small addition to the draw law, for its owner to review.
- No gate is computed in two units: D_s only in its X unit, and each node only in its node unit.
- The first form of the key had each reader (a tile, or later an X unit) recompute D_s and check its path, against a
  monolithic tree unit that also hashed every strip. That was a recompute across units. `validate_unit_cut` and
  `Flock.Partition` both refuse it (`gate-recomputed`), and no allowance covers it (X-SPC-39).

**Why it binds.** Under the ROM and collision resistance, E₁ is unknown until D_A is queried. A proved path from a proved
D_s fixes that strip's A rows before E₁, so A = −E₁ needs a preimage. Two proved paths that meet must agree above the
meeting point, or the prover has found a collision (X-SPC-38).

**What it doesn't guarantee, and why that is enough.**
- A strip with no proved reader can hang a junk leaf, and a wrong node off every proved path can hang junk beneath it.
  Either way the prover sacrifices the strips beneath to re-roll the call's noise. The per-call game covers that: the
  sacrificed strips play edited strips, and the simulation is exact on every other strip (X-SPC-36, X-SPC-38).
- Under the closure, harm stays local. A tile counts as sound only when its X unit and that unit's path nodes are right,
  and a drawn tile's proof covers all of them.
- With node strata instead of the closure, a level-ℓ node would carry the work of the 2^ℓ strips beneath it. That needs
  about t draws per level (about 27,800 node draws, 0.25 T at δ = 1%) and the harm-weighted law (X-SPC-39).

**The tree's shape is pinned** (X-SPC-36, X-SPC-38). Each of these, left free, would be a nonce even with every tile
right:
- the RFC 6962 shape: an unbalanced tree with no padding leaves. A fixed depth of 13 for m ≤ 2^17, with padding siblings
  as constants, also works;
- direction bits from the constant global strip index. Node units give this by construction: the tree is Program
  structure, so each node's children are fixed wires;
- leaf and node hashes domain-separated;
- digests of at least 256 bits, since q ≤ 2^64 (SHA-512 gives 512);
- one committed D_A per call, read by every X unit in the call. Readers with their own D_A would have free siblings, a
  nonce per strip, and per-strip grinding would return.

Because the shape is Program structure, `ncp-node` carries neither m nor k: one node template serves every call, and
there are no per-m strata (X-SPC-37).

**D_s's byte format** (X-SPC-41).
- D_s = SHA-512(strip domain ‖ r_1 ‖ … ‖ r_16), with r_i = SHA-512(row domain ‖ row i's int7 encoding), the rows in
  order, pinned with vectors.
- A row-wise quantization kernel then hashes each row as it writes it, and a strip's digest is 16 short hashes. One sponge
  over 16 rows would be serial: about 1,024 SHA-512 compressions per strip at k = 8,192 (964 SHAKE256 permutations).
- A tree mode such as KangarooTwelve's would also fuse, but it is TurboSHAKE-based, which decision 6 excludes.
- The circuit hashes the same bytes, plus 16 small hashes.

**Proving cost** (**Derived**, from the red team's script section 10b, in C-Flock rows).
- A node unit is 8.9 M rows: one SHA-512 compression, two children opened, the parent committed.
- An X unit commits D_s and opens D_A, about 5.9 M rows, and no longer checks a path itself.
- At δ = 1% (4,606 draws) the closure proves about 24,000 distinct node units, 0.22–0.37 T. That is −0.29 to +0.06 T
  against the first form.
- At the decided δ = 2⁻⁴⁰ (27,715 draws) it proves 69,667 of the window's 163,520 node units in expectation, 0.62 T
  (the red team's recount, X-SPC-49, at root's K = 27,713).
  With D_s's commitment and D_A's opening, that adds about 0.8 T to the window (§12.4).
- **The first form, correctly counted** (X-SPC-37):
  - Its path was 7–10 compressions per reader, 0.57–0.82 M rows, as stated.
  - It left out opening D_A and the siblings, 11–30 M rows per reader.
  - Its tree unit opens all m A rows as well as hashing them. It costs 87–302 G rows per draw (87 G at k = 8,192, 302 G
    at k = 28,672), not 43 G.
  - In all that is 0.3–0.5 T per window at δ = 1%, including opening D_A and its siblings, and 0.6–1.2 T at the decided
    point.

**For NCP-FP8 it is the fix** (FP8 red team, X-SPW-3 to 6).
- Per-(strip, column) weight noise, as §9's caveat had it, moves the weight-side forming from once per call to once per
  strip.
  - That is 21.9 units per MAC at 16-row strips, and 5.5 at 64-row strips, against a 1% budget of about 0.06.
  - γ rises to 78.6% or 48%, and the slowdown to about 27× or 11× (281× or 74× with the XOF).
  - Any F₁ key must cover at least 14,596 of a call's rows at 16,384³.
- The two-level key keeps the weight noise per call, at #295's serving cost, with root_A := D_A. It keeps A16's call-wide
  barrier for FP8. It needs an FP8 scheme version with new vectors, and X-R9-2's regression test re-keyed to D_A.
- Committing F₁ in full isn't viable: NCP-FP8's F₁ is per call, so it costs 63–82 T rows every forward.
- Option (i), the derived-input class with #295's root_A as is, also works, but changes two rules.
- H-1T pays nothing extra. Its salts are already per (unit, row, slice), so keying them on D_s changes no byte, and it
  needs only the strip index, or the global row index, in its key (X-SPW-5).

**For NCP-INT it is used too, for E₁.**
- *What it keeps.* D_A is a Program hash of the call's A, so E₁'s query points are a function of (salt, call, A, weight
  id), the same per-call granularity as `ncp-v1`'s root_A. TT_NCP_U's existing instance carries over. The red team
  confirmed this, on the shape conditions above and with `qAct` given the unit's shape (§2.1; X-SPC-36). The per-strip
  key would need TT_NCP_U assumed afresh, because the prover could grind strip by strip (X-SPC-29).
- *What it costs.* The call-wide hash of A before the GEMM (A23) comes back. It hashes the same 4.26 MB per token as the
  per-strip key, plus 1.3 KB per token of tree and one barrier per call (X-SPC-41). The barrier forbids fusing
  quantization into the GEMM's prologue, and forbids starting any strip's tiles before the call's last strip is
  hashed.
- *Decode latency is only estimated* (**Assumed**, X-SPC-41).
  - A serial sponge over 16 rows would take a few hundred µs to a few ms per call, over 320 calls per forward.
  - The per-row form cuts that to one row's hash: about 65 SHA-512 compressions at k = 8,192, and 225 at k = 28,672.
  - It is small next to the word hashing, but not next to a plain decode step. It must be measured at decode.
- *For F₁* it buys nothing, because NCP-INT's F₁ reads only the salt and the weight id.
- *Decided* (Daniel, 03:22Z; §10 decisions 2 and 9). The per-strip key stays the alternative, if the call-wide barrier
  matters more than one key shape for NCP-INT and NCP-FP8.

## 6. Commitment ordering and the draw (layout A)

0. **Registration, before serving:**
   - the Program with the Definitions and the scheme's parameters (`ncp-v2`);
   - the partition;
   - the law as a rule: one stratum per `ncp-tile(k)` template, the size rule, the cap k_s ≤ T_s, and the closure
     (each drawn tile with its X and Y strips, and each X strip with its path's node units; §12.3);
   - δ and the commitment scheme.
1. **Weights.** The int7 B, scales and biases, under one root, which is also PoUW's `weights_root`. Registered, with a
   receipt.
2. **Salt.**
   - The verifier issues it after the weights' receipt, as `derive(secret, <salt domain>, {weights root, run id})`
     (X-SPC-17).
   - The prover commits it as an Input, and its anchor goes into the registration record (§5.2, item 1).
   - One salt per run.
3. **Serving, per linear call.** The index is the call's position in the run: forward, layer, site.
   1. Quantize x to A and s.
   2. Commit A's rows as ordinary committed values with hiding leaves (D4).
      - The noise is bound to A inside the Program, so root_A no longer has to be fixed before the GEMM, and the
        mid-forward commitment tree kind is not needed (X-SPC-11).
      - Under the two-level key, the call's A is still hashed before its GEMM: every strip digest, then D_A, which is
        A23's serialization point. The hash can be fused into the quantization pass that precedes the GEMM anyway, at
        1 B hashed per A element. The kernel computes each D_s once, in the per-row form (§5.4), and the Program
        computes it once too, in the strip's X unit.
      - Under the per-strip alternative, only each strip's 16 rows are hashed before that strip's tiles, with no barrier
        across the call.
   3. In the kernel, for each tile: compute E₁ and F₁; run NCP; hash the credited words into the word leaf (a new leaf
      kind, Q1, D4); write Z to its narrow leaf.
   4. Dequantize y from Z, and commit y.
4. **Registration** of every root at the end of the window, and the verifier's receipt.
   - The verifier assigns run ids, and refuses any call index already registered in an earlier window of the run
     (X-SPC-18). Otherwise the same forward registered twice would have identical noise and leaves, and be credited
     twice.
5. **Draw.**
   - The verifier draws k_s tiles uniformly without replacement per stratum, from `derive(secret, <tile-draw domain>,
     {receipt digest, law digest, program digest, run id, window})`, and sends the draw in the clear.
   - It is never keyed from a root; under `LEGACY = True` a root-keyed draw gives no guarantee.
   - An abort is a rejection, and a window is never re-registered (R6).
6. **Proofs.** One C-Flock session proves the drawn tiles. The prover opens A rows from kept copies or bit-exact
   regeneration.
7. **Profile.** `Stratified`, one δ. PoUW's consumer reads `harm_bound({template: W_ref per tile})` for ε_s·W, and
   combines it with γ.

**For a record third parties can replay,** the verifier commits to its secret before serving and reveals it after the
audit. Anyone can then recompute the salt and the draw, but not check that the secret stayed private (X-SPC-17).

### 6.1 Grinding, and why salted A rows are fine (D4)

The red team confirmed this with conditions (X-SPC-23 to 25, 28). The game referred to is PoUW's Lean game
(`Game/Defs.lean`, `NCP/RouteUAssumptions.lean`).

- **What grinding buys: only E₁.**
  - Re-rolling A gives a fresh E₁ for the whole call, under `ncp-v2`'s two-level key as under `ncp-v1`. Editing many
    strips still re-rolls it once, so the prover can't keep one strip's good noise while re-rolling another
    (X-SPC-36). Under the per-strip alternative a re-roll would be one strip's.
  - It never buys the draw, which comes from the verifier's secret after the receipt and depends on no root. The one
    exception is #311's `LEGACY` draw, which §6 excludes.
  - Within a run it never buys F₁, which reads only the salt and the weight id.
- **Grinding is always cheap.** A prover can re-roll by editing one entry of A, by changing the batch composition, or
  by changing the row order. Each costs a strip hash and its path to the root, however the leaves are salted.
- **PoUW never relied on grinding's cost.**
  - Editing A is inside the game: the online adversary sees the salt and may commit any activations, and E₁'s query
    points are a function of the committed A.
  - q counts the noise XOF's query points: per re-roll, 16 for each strip the prover inspects, and m for the whole
    call. Re-rolls are joint across the call, not per strip. It does not count leaf hashes (those enter
    only through ε_bind), salts, or verifier keys.
  - Grinding toward any event of per-query probability p succeeds with probability at most q·p. On one strip, E₁ = −A has
    probability 64^(−16k), and rank below 16 at most 16·64^(−(k−15)). Both are below 2^(−6,000) for every k ≥ 1,088.
    At q up to 2^64 that term is negligible, and so is ε_bind (about q²/2^257).
- **But "covered by the error term" has no number yet.** `TTNCP_U` and `gammaFromTTNCP_U` take ε(q, N) as a free
  parameter, and nothing pins it. Grinding is not the weak point; the unpinned ε is.
- **Under `ncp-v2`, no simulation lemma is needed on the noise path** (X-SPC-36). The noise reads D_A, a Program hash
  of the call's A with no salt. That is an exact instance of the game's query points once `qAct` gets the unit's shape
  and the tree's shape is pinned (§2.1, §5.4).
  - If D_A is modeled as a fixed collision-resistant function (`cr/sha-512`), the instance is exact.
  - If the tree hash is itself the random oracle, add the textbook domain-extension step, whose loss is the collision
    term.

  The following bullet matters only if `ncp-v1` stays.
- **Under `ncp-v1`, salted leaves need a short simulation lemma** (X-SPC-23). With per-leaf salts, the query points depend on (A,
  salts), and the game's query function has no salt argument.
  - The reduction: simulate a salt re-roll by editing one entry in a row outside the target strip. The simulation is
    exact on every other strip when m ≥ 32.
  - This needs writing down, as a lemma or a `STATEMENTS.md` bridge.
  - The seeded option, with its seed fixed before the salt, makes root_A a function of A alone, which is closest to the
    formal game. Under `ncp-v2` the noise reads D_A, a Program hash of A with no salt, so the leaves' salts don't reach
    the noise at all.
- **Binding** is the unformalized commitment bridge: the game's commitments are ideal, and ε_bind enters the bound.
  Salts don't weaken it.
- **Two gaps that predate this design** (X-SPC-25). Every noise option inherits them, and #218 has both:
  - *The layout is chosen after the salt.* The game fixes the layout (shapes, calls, batch composition) before the
    salt. Serving picks m, the number of calls and the batches afterwards, and choosing a batch re-rolls A while also
    changing the layout. The fix: register each run's shape schedule before the salt is issued, which A4's pre-declared
    workload allows, or restate the game for a layout the adversary picks after the salt, within the domain.
  - *Many salts.* A prover that opens r runs and serves only on a favourable salt gets r·ε(q, N). The fix: count an
    abandoned run against the prover, as R6 does for windows, cap runs per weights root, or state the bound as r·ε.
- **With no beacon,** the uniform salt becomes a PRF claim on `derive` keyed by the verifier's secret, which has no claim
  id yet. "Preprocessing never sees the salt", and the independence of the audit coins, then hold computationally, and
  only against a verifier that doesn't collude.
- **The wording for D3's condition** (X-SPC-28): *the fields are fixed before the draw. Any grinding over them (A, the
  layout, the choice of run) must be bounded by the consumer's security statement. For PoUW, TT_NCP_U's ε(q, N), with q
  counting the derivation's XOF queries, bounds re-rolls within one run and one fixed layout. The layout and the run are
  bounded once the two gaps above are closed.*
- **So salted A rows are fine, and no privacy exception is needed.** The red team's "unsalted" (X-SPC-11) is withdrawn.

**What moves in code and Lean:**
- `verity_pouw` gains `ncp-v2`, with its two-level derivation (D_s in the per-row form, the pinned tree, D_A) and
  vectors. Its transcript tree, its draws and `verity/pouw/audit/v1` retire.
- Lean: PoUW's `Params` gives `qAct` the unit's shape, a changed record that needs a named statement reviewer
  (X-SPC-36).
- Lean: PoUW's `endToEnd` must be composed with `Audit/Stratified.lean`, which is a new pin with a named statement
  reviewer. **Open.**

## 7. Transcript hashing

**Does sampled proofs' commitment force each credited word to be written? Only through the word leaf, and the word leaf
is a per-word hash.**
- Committing only y, or a fold, binds a function of the words: the barrier or the exact-sum shortcut.
- Committing words after the draw proves nothing.
- Committing every word verbatim under a random-oracle leaf forces the writes. PoUW's certificate must name the
  random-oracle claim, which `verity.claims` doesn't yet have (X-SPC-17).

**Under D7 it is paid twice:**
- at serving, 0.75 B hashed per useful MAC;
- in each drawn tile's proof, where hashing the words is 1.01 G of the tile's 2.20 G rows.

TurboSHAKE128 is about 2.5× cheaper on a GPU (X-A6-7), and 2.8–5.6× cheaper than SHA-512 in C-Flock rows.

**It is not the binding that fits FP8's 5×.** The cheapest per-word hash costs about 3,300 units per word, against a
budget of 4–8 units for H-1T. A6's verdict stands.

## 8. `vllm-v1`, what is not yet in the repo, and what changes elsewhere

**`vllm-v1` is two-stage in its law, degenerate in its lifecycle.** Every stratum is one RU at p = 1, with one draw
keyed from the run root while `LEGACY = True`. PoUW needs a stratified tile draw from the verifier's randomness (D2,
D6, #132).

**Not yet in the repo (layout A with §5's noise):**
1. **The tile draw and its `Stratified` profile in the Commit** (`commit/challenge.py`, the proof step, #311's adapter).
2. **The verifier's own draw and salt,** keyed as in §6, with the cross-window index check (X-SPC-17, X-SPC-18).
3. **A new law version for work-proportional sizes,** in `Flock/Draw.lean` (`stratumK`, #167) and one_stage's
   `stratum_k`. Their check U2 refuses any other k today. This is a change to the Lean verifier (X-SPC-15).
4. **The word leaf and Z's narrow leaf:** `vllm-v1` leaf kinds, through the commitments owner (Q1, D4). A rows are
   committed as ordinary values with hiding leaves, so no mid-forward tree kind is needed under `ncp-v2`.
5. **The salt as an anchored Input:** the anchor in the registration record, and "salt" as a prescribed family.
6. **The partition query `Q_nested_instances` v0** (§2.6), with its stratum key. It needs no recompute exception
   (§12.1).
   - Cross-call-check writes the spec, the canonical evaluator, vectors and the `PROTOCOL.md` entry.
   - POUS (this lane) drafts the `ncp-linear` part.
   - Red-team-flock-3 reviews it.
   - Flock-verifier ports it to Lean, along with the stratum key for #167's `strataOf`.
7. **PoUW's Definitions** (`ncp-v2`'s tile, `ncp-form-x`, `ncp-form-y` and `ncp-node`; §2.4) and the hash
   Definitions (SHA-512 for D_s and the nodes, which the repo has; Keccak for the XOF), with `circuit-check` bindings of
   at least 2 tiles per strip.
8. **C-Flock lowerings** of the tile and of Keccak.
9. **Claim ids** in `verity.claims`: the PRF claim on the verifier-keyed `derive`, and the word leaf's random-oracle
   claim (X-SPC-17).
10. **PoUW's consumer and Lean:** harms of W_ref per tile, and the composition with `Audit/Stratified.lean`.
11. **TT_NCP_U for `ncp-v2`:** the existing per-call instance, with `qAct` given the unit's shape (X-SPC-36), and a
    pinned ε(q, N) (X-SPC-24). The salted-leaf simulation lemma (X-SPC-23) is needed only if `ncp-v1` stays.
12. **The two statement gaps** (X-SPC-25):
    - a shape schedule registered before the salt, or G_γ restated for layouts chosen after it;
    - an abandoned run counted against the prover, a cap on runs per weights root, or the bound stated as r·ε.
13. **The per-tile count statement** (X-SPC-3, X-SPC-35): except with probability η, the number of fully correct tiles is
    at most cost/((1 − γ)·W_tile). The game's unit is a whole call, so today one wrong tile spoils its call, and γ over
    tiles waits on this statement. Under §12 it must also say that a tile counts only when its X and Y strips, and
    the node units on its X strip's path, are correct (X-SPC-27, X-SPC-39).
14. **The query's four specifications** (X-SPC-34):
    - the residual graph for "the rest", with vectors;
    - instance discovery through call, batch and scan, with canonical numbering;
    - a stratum key for the non-tile units, in core, one_stage and #167;
    - the standard {name, version, params} shape.
15. **The forward index as an anchored Input,** and the tile's position constants (X-SPC-30).
16. **An integrity floor in the sizing law** for the non-tile strata (X-SPC-35).
17. **The closure in the draw law:** each drawn tile with its X and Y strips, and each X strip with its path's node units
    (§12.3), for the draw-law owner's review (X-SPC-39).

**Not needed under layout A:** D1, B's root and tree kind, the with-replacement form, the fixed-count RU draw, H3, and
the derived-input class (unless it is the chosen noise option).

**Elsewhere:**
- #311's refusal lifts once items 1–8 exist.
- #218's "not here yet" Definition becomes §2.4.
- Audit item A7 (retention) becomes §3. Audit item A8 (serving restrictions) now applies to PoUW rows.

## 9. FP8 (NCP-FP8 and H-1T)

- **The same structure:** tile replay units, the words as outputs, and noise derived in the tile. For H-1T's tag lanes,
  that means tag signs from the salt.
- **Semantics.** The H100 FP8 atom (e4m3, validated in `verity.ml.tc`), and FP32 adds.
- **The work bound per tile** (X-SPC-3). Except with probability η, the number of tiles with every word right is at most
  cost/((1 − γ)·W_tile). FP8's lifting is **Assumed** and must be stated in that form.
- **The useful output depends on the salt,** so regenerating A needs the noised GEMM.
- **Proving an FP8 tile** (**Derived**, corrected by the red team's X-SPC-91 on #380; the atom is C-Flock's pinned count,
  and the f16 forming is **Assumed** until its pieces land).
  - *The atom* is 7,147 ANDs from +0 and the running FP32 add 854: 250 ANDs per lane-MAC, 750 per useful MAC, the low
    end of the 200–540 per MAC this section first assumed.
  - *A 16 × 16 draw at k = 16,384:* the tile's arithmetic 3.15 G, its words 2.0 G at 640 rows per byte, its digest
    0.09 G, and its closure's forming 3.8–10.1 G (16 rows and 16 columns of k elements at 7.2–19.2 k ANDs each, with f16
    sums). That is **9.0–15.3 G rows**; the forming is 1.2–3.2× the tile's own arithmetic.
  - *A 64 × 64 draw* is 98–123 G, the forming 15–33% of it. So 16 × 16 tiles cut a draw **8–11×, not 16×**: the forming
    doesn't shrink with the tile. This section's first 16 × 16 figure, (70–140 G)/16, was about 2× low.
  - *A window:* 4,600 draws (δ = 1%) come to 41–70 T, 11.6–19.6 L40S-hours at 1 G AND/s. At the decided δ = 2⁻⁴⁰, 27,715
    draws come to **249–424 T, 69–118 hours**, 1.7–2.8× NCP-INT's 147.0–150.2 T.
  - **Does the conclusion change?** The choice doesn't: 16 × 16 tiles still cut a draw 8–11×, and the tile-local noise
    is still the precondition. The figure does: FP8 is about 2× this section's first estimate, and at the decided δ it is
    above NCP-INT's window. The forming dominates, so the levers are the f16 C-Flock pieces (which narrow the range) and
    X-SPC-90's per-run amplitude unit (built in #380), which makes the weight-only 35–39% of the Y forming a per-run
    proof, reusable across the run's windows.
  - *#295's leaf at 16 × 16* (X-SPC-92). The circuit's tile is 16 × 16, and #295's production leaf was one SHAKE256
    over a 64 × 64 tile's words. Decided (08:20Z, with #295's owner): a **two-level leaf**, a SHAKE256 per 16 × 16 subtile
    and SHAKE256 over the 16 sub-digests as the 64 × 64 Merkle leaf. It keeps the kernel, the words, W_ref, γ and the
    64 × 64 tree. #295's cost (11:55Z): the SHAKE256 combine is 0.046× a plain GEMM at 8,192³ and 0.023× at 16,384³,
    and the sub-digests' own padding adds 0.046× and 0.084× (the earlier 0.013× assumed SHA-256 and left out that
    padding). A proof opens one sub-digest with its 15 siblings as committed inputs
    (+480 B). SHAKE256 as the combining hash keeps the leaf on the one hash FP8's certificate names; in the circuit it is
    about 4 Keccak-f per opening, the same as SHA-256's cost.
- **Noise.** NCP-FP8's weight noise is per call (r = 1). Derived in the tile, a drawn tile's closure derives (16 + 16)·2k
  bytes of XOF: 1.05 MB for a 16 × 16 tile at k = 16,384, and 4.2 MB for a 64 × 64 one. Committed in full, it is about one byte per weight per call: 67 MB per call at 8,192², and 69 GB per 70B
  forward. So the tile-local derivation, or (i), is a precondition for FP8.
  - NCP-FP8's weight noise must also read the activations (X-R9-2).
    - The per-(strip, column) form this section first suggested is ruinous: γ goes to 78.6% (48% at 64-row strips),
      and the slowdown to about 27× (11×).
    - The fix is the two-level key of §5.4. Both streams are keyed on D_A, the call's root over its strip digests,
      with the X units committing their digests and the tree in node units, proved by closure. The noise stays per call, harm stays local, there is no new public input, and the
      serving cost is #295's. FP8 keeps the call-wide barrier.
    - Committing F₁ in full would cost 63–82 T rows every forward.
    - H-1T pays nothing extra and needs only the strip index in its key (FP8 red team, X-SPW-1 to 6).
- **Hashing:** §7 applies, and A6's verdict stands.
- **Built** ([PR #380](https://github.com/danielreuter/verity/pull/380), `verity_pouw.circuit.fp8`): #295's D-3s cells
  `fp8-is-h100-d3s-v0-f16` and `-d3s-v0` as a Program under layout (a), with Z = R_T in the tile. It evaluates to #295's
  scheme bit for bit, passes `validate_unit_cut` over the whole call, and every PoUW unit is behind the pinned Z (8,192
  bits per tile). Three things changed on contact with #295's scheme; none needed a change to #295's test instance.
  Production needs #295's leaf at 16 × 16 subtiles (the two-level leaf, above).
  - **The call-wide prefixes are hoisted.** #295's streams hash (salt, index, root_A, weight id) before each row's line,
    and its commitment hashes the domain before each leaf and node. Computed per row, those gates recompute across units.
    So each per-row function is split once, its call-wide gates run in one per-call unit, which commits the frontier, and
    its row gates read that. This is `ncp-v2`'s per-call key K in general form, for a message format the circuit doesn't
    choose.
  - **root_A is the protocol's own commitment:** `verity.commitments.merkle`'s SHA-256 tree with one leaf per row, padded
    to a power of two. The strips are its aligned 16-leaf subtrees. The padding adds a **pad cone** (the pad strips and
    the all-pad nodes) to every closure, because a wrong pad has no tile beneath it to be charged to.
  - **Minimal integer encodings** make byte lengths template parameters: the index's, the owner's (index + 2) and the
    weight id's per call; a strip's ranks, its nodes' indices and a row's or column's stream line per binding. Past 255
    they take two bytes, so strips are batched in runs of one byte-length signature.
  - **A row's rank and its stream line are separate anchored inputs,** though equal. Read as one input, the leaf and the X
    row place its two bytes by the same gate once it passes 255, which is one value computed in two units. The cut at
    272 rows found this; 48 rows had passed only because the one-byte placements differed.

## 10. Decisions for Daniel (one consolidated list)

Daniel ruled on this list at 03:03Z, 03:16Z, 03:22Z and 04:35Z, and every decision is now decided. The matching rows of the
[deployment-requirements audit](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/deployment-requirements-audit.md)
(A19–A24) carry the same rulings.

1. **Draw sizing: decided, by work** (Daniel, 03:22Z; audit A19).
   - Tile draws are sized by work, ⌈t·W_s/W⌉, with closure draws: each drawn tile is proved with the X and Y strips it
     reads.
   - Units that do no PoUW work (quantizer, dequantization, the rest of the model) get an integrity floor. The key's
     node units are proved by closure with each proved X strip (§12.3).
   - Still to do: a new law version in `Flock/Draw.lean` and one_stage, whose check U2 refuses non-count sizes today,
     and the draw-law owner's review of closure.
2. **The noise: decided, in-circuit, tile-local, with the two-level key** (Daniel, 03:22Z; §5, §5.4; audit A21).
   - The salt is a committed Input anchored like the weights, and so is the forward index.
   - The noise is keyed on D_A, the call's root over its strip digests, with no recompute (X-SPC-39):
     - each X unit commits its strip digest D_s and reads only D_A;
     - each tree node is its own unit (`ncp-node`), which commits its parent;
     - a proved X unit's path nodes are proved with it.
   - The X and Y units bind their position: the layer, the site and the global indices, as constants (X-SPC-30,
     X-SPC-40).
   - TT_NCP_U's existing per-call instance carries over. The red team confirmed it (X-SPC-36) on two conditions:
     - `qAct` gets the unit's shape. That is a `Params` change needing a statement reviewer; otherwise the instance is
       stated per layout;
     - the tree's shape is pinned: the RFC 6962 shape, direction bits from the constant strip index, domain-separated
       leaf and node hashes, 512-bit digests, and one committed D_A per call (§5.4).
3. **The recompute exception: decided, none** (Daniel, 03:03Z; §12). Strip generation is its own proof units, sampled by
   closure.
4. **The width rule: decided, option (a): Z stays in the tile, and Z is the separator** (Daniel, 04:35Z: "If so, then
   this is fine"; §12.5).
   - *Why it holds:* every PoUW unit (the strips, the noise, D_s, the node units, the tiles' checked words) reaches the
     served output only through the matmul outputs Z → y. So the Z values are a downstream cut between them and the
     replay unit's delivered output.
     - Per tile, what crosses is its 256 Z values (8,192 bits). Per call, it is the m·n Z values at 32 bits each.
     - No X, Y, noise, D_s, D_A, node value or checked word crosses.
   - *The theorem:* Lemma 4.7, and Theorem 5.4 at replay-unit granularity, of Daniel's Notion draft ([Draft 2](https://app.notion.com/p/Draft-2-Computational-integrity-via-zero-knowledge-spot-checks-3d2399515d9e80d18797d8ebb674b676)). The values at a downstream
     cut determine the delivered output, so a fault set's influence is at most the cut's width in bits,
     U = log₂ Σ_(E : a(E) > ε) 2^(w(K_E)).
   - *What that settles:*
     - no unit behind the separator needs a width exception;
     - the only departure from the Sep 26 rule is the tiles' 8,192 Z bits each, which enter U as a faulty tile's cut
       width, and the served output (about 17 bits per token) caps what can leave, through the output space itself
       rather than through U (X-SPC-66);
     - everything else keeps the Sep 26 rule.
   - *The conditions:*
     - the word leaves and every other commitment count as committed to the verifier, not delivered;
     - the separator port is the tile's Z, pinned by the protocol and never registrant-chosen (X-SPC-66). The build
       enforces this by reachability from the served outputs (`partition.width_rule`).
   - *Cost:* none. The window stays at 147–150 T at ε = 0.1% and δ = 2⁻⁴⁰, y's integrity is 1.24 × 10⁻³ of outputs,
     and nothing depends on the Lean question.
   - *Not adopted, kept as an option:* (c), an integrity upgrade for y (+0.61 T net for 1.0 × 10⁻³, +5.15 T for
     1.26 × 10⁻⁴, on a leaf per row; 6.1 T and 48 T on flat 16-row leaves). It is the only part that would depend on
     the Lean question: it needs NCP-INT's `checkIdx` restated. It is NCP-INT-only: H-1T's useful output depends on the
     salt through rounding, so H-1T and NCP-FP8 stay on (a) (X-SPC-68).
5. **The online verifier: decided, accepted** (Daniel, 03:22Z: standard in our setting; audit A24).
   - The credit is the verifier's own.
   - An online verifier issues salts, receipts and draws on every run and window.
   - Re-served work earns no credit, and an abort rejects the window.
6. **The leaf hash: decided, keep it conservative** (Daniel, 03:22Z: "keep it secure, don't care about efficiency yet";
   audit A22).
   - The current family stays: SHA-512 word and strip leaves, and SHAKE256 for the noise XOF. There is no TurboSHAKE128
     switch.
   - Round 11's GPU pricing of SHA-512 leaves is still wanted, since Daniel's 394× acceptance was priced with SHAKE256.
7. **The proving budget: target decided** (Daniel, 03:16Z: ε = 0.1%, δ = 2⁻⁴⁰ for now; §12.4; audit A19).
   - 27,715 tile draws: root's work law (#362) at K = 27,713, the smallest K whose Lean-proved escape (1 − ε)^K meets
     2⁻⁴⁰, plus two from the per-stratum ceilings. Each is proved with its two strips, and each X strip with its path's
     node units. (`harm_bound` alone would certify t = 27,707, but it is not proved in Lean.)
   - 147–150 T rows per window (147.0–150.2 T, the red team's recount): 41–42 L40S-hours at 1 G AND/s, or about 590–605 hours at the
     measured 69 M/s GEMM-template rate.
   - Over a long run, reusing proved Y units across windows brings a window to about 134 T (X-SPC-51).
   - No stratum hits its cap at an 8,192-token window. Activation-strip strata are proved whole only below about 3,000
     tokens per window (gate_up first).
   - Open engineering: moving witness generation to the GPU, which takes this from about 600 hours to about 40.
8. **A rows: decided, regenerate on a batch-invariant serving path, not retain** (Daniel, 03:22Z; audit A20).
   - *What that requires of the serving path:*
     - every op upstream of a PoUW linear (GEMMs, attention, norms, activations, the quantizer) must be batch-invariant,
       so a row's values don't depend on batch size, composition or order: fixed reduction orders, no atomics, and no
       split-K that varies with the batch;
     - the batch schedule and request inputs (tokens, sampling seeds) are recorded, which the registered circuit
       supplies (decision 10);
     - the KV cache is regenerated deterministically, with prefix caching off or deterministic, and chunked prefill off
       or recorded, as audit item A8 already requires for sampled proofs;
     - the replay runs on the same hardware class (compute capability; `num_sms` is baked into the GEMM);
     - replay is bit-exact, because a mismatch rejects an honest prover.
   - *For NCP-INT,* the replay's PoUW linears can run the plain int7 GEMM, since y doesn't depend on the noise. For FP8,
     y does depend on the salt, so the replay needs the noised GEMM.
   - *Cost:* at most one forward-prefix replay per distinct drawn forward (at most 27,715 per window). Nothing is
     retained but request inputs, the registration and the leaves' salt seed.
9. **The serialization point: decided, fused quantize-and-hash** (Daniel, 03:22Z: "whatever is most elegant"; audit
   A23).
   - The quantization kernel writes each strip's A rows and its digest D_s in the same pass, and a small tree reduction
     in the same launch gives D_A before the GEMM.
   - Why: it adds no extra pass over memory, since quantization already reads every row before the GEMM, and it gives
     NCP-INT and NCP-FP8 one key shape.
   - D_s is pinned in the per-row form, a SHA-512 hash of its 16 row digests, so a row-wise kernel can fuse it. A tree
     mode such as KangarooTwelve's is TurboSHAKE-based, which decision 6 excludes (§5.4; X-SPC-41).
   - The barrier forbids fusing quantization into the GEMM's prologue.
   - The decode latency is only estimated so far (**Assumed**): a few hundred µs to a few ms per call for a serial
     sponge, down to one row's hash in the per-row form. It must be measured at decode.
10. **Two gaps in PoUW's own statement: one is closed by the registered circuit, one survives.**
    - *Daniel asked: "Is this even true? I thought you committed to the circuit ahead of time."* Partly true.
    - *The layout gap is closed.* The circuit, including every call's batch shape and which request rows it holds, is
      registered before the salt is issued (§6 step 0). That fixes the layout before the salt. It reopens only if
      batches are formed live after the salt; the pre-declared workload (audit A4) doesn't.
    - *The many-salts gap survives.* Committing the circuit doesn't stop registering the same circuit several times and
      keeping the run with the luckiest salt. It closes with one registration per circuit, an abandoned registration
      counting as a rejection as R6 already does for windows, or with the bound stated as r·ε.
    - *A third gap, for the Lean lane:* the theorem counts correct calls, not correct tiles, so γ over tiles waits on a
      per-tile count statement of TT_NCP_U. TT_NCP_U's error term ε(q, N) also still needs pinning.
    - *Recommendation:* adopt "one registration per circuit" as a protocol rule, and ask the Lean lane for the per-tile
      statement and the pinned ε.

**Settled without Daniel:**
- salted A rows are fine for PoUW, so no privacy exception is needed (§6.1);
- D1 and the other layout-B items aren't needed under layout A;
- the query's form, its owners and its stratum key are ordinary engineering (Verity root);
- the Lean pin composing PoUW's theorem with `Audit/Stratified.lean` needs only a named statement reviewer.

## 11. Red-team findings, and where they stand

| Finding | Status |
|---|---|
| X-SPC-1: no query yields nested tiles | a new query in `verity/partition/v1` (D5; §2.4) |
| X-SPC-2: `TwoStageLaw.profile` can't produce the tile profile | resolved: `Stratified` over tiles (Q3, D2) |
| X-SPC-3: FP8's pins don't compose over tiles | §9: state the lifting per tile |
| X-SPC-4, X-SPC-18: the salt and indices bound to one run | §6 steps 2 and 4, with the cross-window index check |
| X-SPC-5: the tile must enforce int7 | §2.4 |
| X-SPC-6: per-tile forming fails `circuit-check` | §2.5: the named exception, or separate units |
| X-SPC-7: the noise and the words don't fit the committed set | words: tile outputs. Noise: derived in the tile (§5) |
| X-SPC-8: an FP8 tile is costly | now proving costs, §9 |
| X-SPC-9, X-SPC-15: the size rule; #167 is count-only | §10 decision 1; §8 item 3 |
| X-SPC-10, X-SPC-17: keys, and what third parties get | §6: key derivations and commit-and-reveal; §10 decision 7; §8 item 9 |
| X-SPC-11: a `vllm-v1` tree kind; unsalted | the mid-forward tree kind is no longer needed under `ncp-v2`, since the noise binds to A through D_A; unsalted withdrawn (§6.1) |
| X-SPC-23: D4 is an informal reduction | §6.1; the simulation lemma, §8 item 11 |
| X-SPC-24: grinding buys only E₁; ε(q, N) unpinned | §6.1; §8 item 11 |
| X-SPC-25: the layout after the salt, and many salts | §6.1; §8 item 12; §10 decision 10 |
| X-SPC-26: D5 +43–50% only with per-site forming strata | §2.5; §10 decision 3 |
| X-SPC-27: the separate commitment; harm-weighted sizes need #167 changed; Y's scope | §2.5; §10 decision 3; §8 item 13 |
| X-SPC-28: D3's wording, within one run and one layout | §6.1 |
| X-SPC-29: `ncp-v2` stops A = −E₁; TT_NCP_U(`ncp-v2`) is a new assumption instance | §2.1; §6.1; §8 item 11 |
| X-SPC-30: bind the call index and positions, or duplicates are credited twice | §2.1; §2.4; §2.6; §8 item 15 |
| X-SPC-31: a wrong digest spoils only its own tile | §5.2 (unchanged) |
| X-SPC-32: 16.6–17.5 T; quote 17.5 T until a Keccak lowering | §4; §5.3 |
| X-SPC-33: +45–47% with (k, n) forming strata, +93% by k alone | §2.5; §2.6; §2.7; §10 decision 3 |
| X-SPC-34: the query's four specifications | §2.6; §8 item 14 |
| X-SPC-35: an integrity floor; γ over tiles waits on the per-tile statement | §4; §8 items 13 and 16; §10 decisions 1 and 10 |
| X-SPC-36: the two-level key restores TT_NCP_U's per-call instance, exact once `qAct` gets the unit's shape and the tree's shape is pinned | §2.1; §5.4; §6.1; §8 item 11; §10 decision 2 |
| X-SPC-37: the path costs what was said, but opening D_A and its siblings (11–30 M per reader) and the tree unit (87–302 G per draw, not 43 G) were left out: 0.3–0.5 T per window at δ = 1% | §5.4; §12.4 |
| X-SPC-38: floor draws are right for the tree; the path check proves less than "D_A is the root of A"; the tree's shape must be pinned | §5.4 (the shape conditions); node units need no draws of their own (§12.3) |
| X-SPC-39 (high): the path check is a recompute across units, in the exception and in §12.1 alike | fixed: X units commit D_s, one `ncp-node` unit per tree node, path closure (§2.4; §2.6; §5.4; §12.1 to §12.4) |
| X-SPC-40: §12's X and Y units must carry the position constants; one key per GEMM launch | §2.1; §2.4; §2.6; §12.1 |
| X-SPC-41: the call-wide hash costs the per-strip key's bytes, plus 1.3 KB per token of tree and one barrier per call; pin D_s's format; measure decode latency | §4.1; §5.4 (the per-row form; latency **Assumed**); §10 decision 9 |
| X-SPC-42: passages still stating the per-strip key | restated for D_A, or marked as the per-strip alternative: §2.1, §2.4, §4.1, §6.1, §8, §11 |
| X-SPC-43: (1) and (2) hold, by proof and by exact enumeration | §12.2; proved in Lean |
| X-SPC-44: the decided law is the closure, and §12.2 stated the stratified one | §12.2: (2′) stated and proved (`audit_closure`, `closureLaw_escape`), covering undrawn node units |
| X-SPC-45: (3) needs anchored inputs, named hash assumptions for the key, and no call index registered twice | §12.2: A9, A10 and A11; in Lean, named hypotheses of `compute_used` |
| X-SPC-46: which assumptions are needed | §12.2: A2's "no exception" clause is policy, A4 is cost-only, A5 is well-formedness |
| X-SPC-47: harm-proportional sizing is optimal for the relaxation, 15% above the exact optimum at heavy sampling | §12.3; ln(1/δ)/ε is an upper bound |
| X-SPC-48: the closure gives the same bound at a lower cost (−3.7 T on strips; nodes 0.62 T against about 2.2 T) | §12.3 |
| X-SPC-49: §12.4 recounted | §12.4 uses it: 25.0–25.5 T, 147–150 T, 450–459 T |
| X-SPC-50: the scaling is sublinear | §12.4: 5.9× and 18.0×; the linearly scaled rows dropped |
| X-SPC-51: Y proofs can be reused across a run's windows | §12.4: about 134 T per window over 100 windows; §10 decision 7 |
| X-SPC-52, X-SPC-56: only the served output leaks values, under four conditions; every feasible design sits above its floor | §12.5; §10 decision 4 |
| X-SPC-53: about 2.2 × 10⁹ bits is right; a gate_up X strip carries 29.4 M bits | §12.5 |
| X-SPC-54: moving Z out rests on restating `checkIdx`; otherwise about +167 T | §12.5: option (a), Z in the tile, needs no answer; the upgrade (c) needs the restatement for NCP-INT; §10 decision 4 |
| X-SPC-55: the 220,000 floor costs +3.5% with openings, and bounds only the Z strata | §12.5; §10 decision 4 |
| X-SPC-57: the Z costs hold on a leaf per row; on a flat 16-row leaf they are about 9× higher | §12.5 (c); the build commits a leaf per row |
| X-SPC-58, X-SPC-63: today's integrity is 1.244 × 10⁻³ at every δ, a window share; the Z-sized boost costs +15.1–15.4 T | §12.5 (a) |
| X-SPC-59, X-SPC-64: window totals; (c) net of the tile's last block, and per site | §12.5 (c) |
| X-SPC-60, X-SPC-66: the limit must be enforced by reachability, with the separator ports pinned by the protocol | §12.5; §10 decision 4; enforced in the build (`partition.width_rule`) |
| X-SPC-61, X-SPC-62, X-SPC-67: cost is independent of `checkIdx`; γ 0.597% → 0.662% under the restatement, a strictly stronger assumption | §12.5 (c) |
| X-SPC-65: (b)'s bound is the larger of the two terms, not their sum | §12.5 (b) |
| X-SPC-68: (c) isn't available to H-1T, whose useful output depends on the salt | §12.5 (c); §10 decision 4 |
| X-SPW-1 to 6 (FP8 red team): per-strip weight noise is ruinous for NCP-FP8; the two-level key fixes it; H-1T pays nothing extra | §5.4; §9; §10 decisions 2, 3, 4 and 9 |
| Q10 (Verity root, 0210Z) | `Q_nested_instances` v0 drafted (§2.6); the recompute exception and width rule go to Daniel (§10); "unchanged per tile" reconciled (§2.5) |
| X-SPC-12 to 14: layout B | not needed under A |
| X-SPC-16: the cap and the domain; no LM-head stratum | §3 (`stratified_escape`); §2.4 (the n bound, fused calls) |
| X-SPC-19 to 21: C-Flock rows, 640 per SHA-512 byte | §4 uses them |
| X-SPC-22: the sizes and cost of noise under (ii) | §5.3 uses them |

## 12. Without the recompute exception: the theorem, the allocation and the cost (Daniel, 03:03Z)

**Daniel's ruling (03:03Z): no recompute exception.** Strip generation, for both weight strips and activation strips
and including the noise, becomes its own proof units. Only a small random sample is proved, like the tiles. This
section supersedes the exception recommended in §2.5 and §2.7. The partition is §2.6's, keyed per site, with the
two-level key's tree in node units (X-SPC-39). All figures are **Derived**, in C-Flock rows at the red team's prices,
and not red-teamed.

### 12.1 The units

| Class | One unit | Reads | Writes (committed) | Harm: the matmul compute a wrong unit can spoil |
|---|---|---|---|---|
| Tile | one 16 × 16 block of one call | the X strip and the Y strip it multiplies | the word leaf and Z | its own W_ref |
| X strip | one call's 16 A rows (template `ncp-form-x(k, n)`) | A rows, salt, forward index, the call's committed D_A; constants: layer, site, global row indices | the X strip (16 rows × 3k), 3 bytes per A byte, and the strip digest D_s | the W_ref of the n/16 tiles that read it |
| Y strip | one run's 16 weight columns (template `ncp-form-y(k, n)`) | weight columns, salt; constants: weight id, global column indices | the Y strip (3k × 16), 3 bytes per weight | the W_ref of the tiles in this window that read it |
| Node | one node of a call's tree (template `ncp-node`, carrying neither m nor k) | its two committed children: D_s at the bottom level, a parent above it | the parent; the root is D_A | the W_ref of the tiles beneath it (2^ℓ strips at level ℓ). Under the closure it needs no stratum: it is proved with every proved X unit whose path it is on |
| Rest | quantizer, dequantization, and the rest of the model (`Q_word`) | as today | as today | 0 for work; their own integrity floor |

- The X unit computes D_s (the per-row form, §5.4), reads the committed D_A, derives E₁ and forms X.
- Each node unit hashes its two children into the parent. The tree's shape is Program structure, pinned as §5.4 says.
- The Y unit derives F₁ and forms Y.
- No gate is computed in two units: the tile reads only committed X and Y, the X unit only the committed D_A, and each
  node unit only its committed children (X-SPC-39).
- **What the build changed** ([PR #364](https://github.com/danielreuter/verity/pull/364); `protocols/pouw/PROTOCOL.md`
  §`ncp-v2`). In `verity.ir`, each unit is a template instance and each root node is one call placed after its
  arguments. Four things follow, and each has a test.
  - **D_s is its own unit (`NcpDigest`).** One call can't both write D_s and read D_A, which depends on it. The X unit
    becomes a digest unit and a forming unit. Both read the committed A rows, and they compute different functions. The
    tile's closure gains the digest unit. D_s could instead fuse into a modeled quantizer unit (decision 9).
  - **E₁ is keyed through a per-call key unit (`NcpKey`).** It computes K = SHAKE256(salt, forward, position, weight id,
    D_A) once per call. Each row's E₁ is SHAKE256 over the row's index, repeated in the first lane of all five Keccak
    columns, then the tag, then K.
    - With the call-wide fields in every row's XOF, round 1 computes the same function of the same values in every X
      unit. That is a recompute across units: 3,456 pairs at 32 × 64 × 32.
    - F₁ carries its column index the same way. In the ROM this is the two-level key composed with one more hash.
    - The key unit is in every tile's closure.
  - **c₀ is the Y unit's.** Otherwise every tile of a column computes −β·Σ Y[:, j] again.
  - **The index binding is anchored inputs, not constants.** `Q_template_instances` admits no constant node at the root,
    so the forward index, the position, the weight id and the global row and column indices are inputs, anchored like
    the salt.
  - The Program evaluates bit for bit to a reference built from `hashlib` and the MVP's own arithmetic. The whole
    call's cut passes `validate_unit_cut` with no value computed in two units. The Z separator's width is 8,192 bits per
    tile, and `circuit-check` passes for every template.

### 12.2 The theorem

**Definitions, all fixed at registration:**
- the partition's units U, and the tiles among them, each with its work W_ref;
- a tile's *closure*: its own unit, the X and Y strips it reads, and the node units on its X strip's path to D_A;
- a stratum σ(u) for each unit: tile(k), X-strip(k, n), Y-strip(k, n), node, and the rest classes;
- stratum sizes N_s;
- draw sizes k_s ≤ N_s;
- harms h(u) ≥ 0 as in 12.1, computed from the Program, the partition and the registered shape schedule only.

**The transcript τ** is the committed values, fixed at registration.
- wrong(τ) ⊆ U is the set of units whose committed outputs differ from their gates applied to their committed inputs.
- A tile is *sound* when its closure holds no wrong unit.
- unsound(τ) is the total W_ref of tiles that are not sound.

**The draw.**
- *Decided: closure draws.* Each tile stratum draws a uniform k_s-subset without replacement, independently of the
  others. Each drawn tile is proved with its closure, and each unit is proved once. The rest's floor strata are drawn
  independently beside them. The coins are the verifier's, drawn after the registration receipt.
- *The alternative:* every stratum, strips and nodes included, draws its own k_s-subset.
- Acceptance means every proved unit's proof verifies.

**Statements, proved in Lean** against `main`'s `Law.stratified`, `stratified_escape` and `audit_profile`
([`lean/submissions/pouw-accountable-compute`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/lean/submissions/pouw-accountable-compute/NOTES.md); names as there):

~~~lean
-- the decided law: draw tiles by Lt (main's Law.stratified over the tile strata), prove each drawn tile's closure cl t
def closureLaw (Lt : Law nT) (cl : Fin nT → Finset (Fin n)) : Law n where
  Ω := Lt.Ω
  draw ω := (Lt.draw ω).biUnion cl

-- harm_bound's specification: every set escaping with probability at least δ has harm at most H
def IsHarmBound (L : Law n) (h : Fin n → ℝ) (δ : ℝ≥0∞) (H : ℝ) : Prop :=
  ∀ B, δ ≤ L.escape B → ∑ u ∈ B, h u ≤ H

-- the closure's escape is the tile law's escape of the unsound tiles; node units have no stratum
theorem closureLaw_escape : (closureLaw Lt cl).escape B = Lt.escape (unsoundTiles cl B)
theorem mem_closureLaw_draw : u ∈ (closureLaw Lt cl).draw ω ↔ ∃ t ∈ Lt.draw ω, u ∈ cl t
-- a wrong unit's whole harm is counted, whether or not any draw reaches it
theorem harm_le_unsoundWork (hw : ∀ t, 0 ≤ w t) (hu : u ∈ B) : harm cl w u ≤ unsoundWork cl w B

-- (1) coverage
theorem unsoundWork_le_harm (hw : ∀ t, 0 ≤ w t) (B) : unsoundWork cl w B ≤ ∑ u ∈ B, harm cl w u

-- (2′) the decided law, pinned: the tiles' own harm bound, each tile's work as its harm
theorem audit_closure (hdom : ∀ B, L.escape B ≤ (closureLaw Lt cl).escape B) (hH : IsHarmBound Lt w δ H)
    (A : Analysis L Reg session) (hks : A.KnowledgeSound εks) (hlink : A.LinkSound δlink) (σ' : Strategy _) :
    prob (fun o => o.1 = true ∧ H < unsoundWork cl w (A.wrong (A.committedOf σ'))) (audit L Reg session) σ'
      ≤ δ + εks + δlink

-- (2) the alternative law: any law, each unit charged `harm cl w`
theorem audit_strata (hw) (hH : IsHarmBound L (harm cl w) δ H) … : (the same conclusion)

-- the conclusion: tile strata proved whole or sized so that N_s · wmax_s · ln(1/δ) ≤ ε · W · k_s
theorem accountable_compute … :
    prob (fun o => o.1 = true ∧ soundWork cl w (A.wrong (A.committedOf σ')) < (1 - ε) * totalWork w) …
      ≤ ENNReal.ofReal δ + εks + δlink

-- (3) the γ step, in any game: A8 with A10 (PerTileCount), A9 (AnchoredInputs), A11 (UniqueCallIndices)
theorem compute_used … : prob (fun o => accept o ∧ cost o < (1 - γ) * (W - H)) g s ≤ a + δin + δidx + (ηTT + εcr)
~~~

- **(2′) in words:** except with probability δ + ε_proof, an accepted window has at least W − H*_tiles(δ) = (1 − ε)·W of
  its matmul compute in sound tiles. H*_tiles is the tile law's harm bound, with each tile's work as its harm, and
  ε_proof = ε_ks + δ_link is `main`'s two per-unit terms. The probability is joint with acceptance: it is not
  conditional on acceptance.
- **It covers undrawn node units.**
  - A node unit beneath no drawn tile is never proved, and has no stratum (`mem_closureLaw_draw`).
  - If such a node is wrong, every tile beneath it is unsound and counted in unsound(τ) (`harm_le_unsoundWork`). That
    set escapes exactly when the tile draw misses those tiles (`closureLaw_escape`).
  - The stratified statement over every class is true for the closure but vacuous: with the node stratum at k = 0,
    H* absorbs every node's harm, at least W per level of the tree (X-SPC-44). So (2′) is the one to pin.
- **(3) in words:** with PoUW's per-tile count statement (A8), in the random-oracle model with the key's collision term
  (A10), the prover's online cost is at least (1 − γ)(1 − ε)·W. This holds except with probability
  δ + ε_proof + δ_in + δ_idx + η_TT + ε_cr, where δ_in is A9's term and δ_idx is A11's.

**Why (2′) follows.** A drawn unsound tile has a wrong unit in its closure, and every unit of the closure is proved. So
the audit accepts with probability at most the tile law's escape of the unsound tiles, plus ε_proof. If unsound(τ)
exceeds H*_tiles, that escape is below δ. The draw is independent of τ (A1). No union bound over classes is needed.
(2) follows the same way through (1), and the adversary gets the joint supremum over the product escape (X-SPC-43).

**Why (1) holds.** A sound tile's words are the correct running sums for the noise derived from committed A and B,
because its X and Y strips are correct, and its strip's path to D_A is right, so its A rows were fixed before E₁. Each
unsound tile is charged at least once: to itself if it is wrong; otherwise to the wrong strip it reads, whose harm counts
every tile reading it; otherwise to a wrong node on its strip's path, whose harm counts every tile beneath it. Overlaps
only overcount. The red team's exact enumeration of all 2¹⁷ wrong-unit sets of a small call finds no counterexample.

**The exact assumptions** (X-SPC-45 and X-SPC-46 say which are needed):
- **A1, pinning** (needed). τ is fixed at registration, and the draw comes from the verifier's secret after the receipt
  (a PRF claim, no id yet). An abort is a rejection. A window is registered once (R6).
- **A2, the partition** (needed, as: each gate is certified by one unit, and every cross-unit read goes through a
  committed value; without committed reads wrong(τ) is undefined).
  - The partition passes `validate_unit_cut` and `Flock.Partition`, and with the key's tree in node units it has no
    exception (X-SPC-39).
  - **"No exception" is policy, not soundness.** The exception form satisfies the same theorems, with the strips
    inside the tile.
- **A3, harms from the layout** (needed for (1) with a fixed h). h depends only on the registered Program, partition and
  shape schedule, not on τ.
  - Y units are per run but feed every window. Each window's partition includes the run's Y units, each charged the
    W_ref of that window's tiles that read it. A Y unit already proved in the run needs no second proof (§12.4).
- **A4, uniform harm per stratum** (**cost only**). No statement needs it: `harm_bound` takes (harm, count) pairs, and
  the Lean sizing rule uses each stratum's largest harm. It sets only the harm-weighted strip strata's cost: keyed by k
  alone, the strip cost doubles (X-SPC-33). Under closure the tile strata are uniform up to the 0.5% spread of W_ref
  with n.
- **A5, the cap** (only for the law to be well formed). k_s ≤ N_s. A stratum whose rule asks for more is proved whole,
  and then escapes with probability 0 for any wrong unit in it (`stratified_escape`).
- **A6, independence** (needed for the product form; under closure, only among the tile strata). A law whose X and Y
  draws share one index has uniform marginals, yet can fail (2) (X-SPC-46).
- **A7, proofs** (needed). ε_proof = ε_ks + δ_link is the proof system's per-unit error for the session.
- **A8, for (3) only.** TT_NCP_U for the two-level key, stated per tile (count form), with `qAct` given the unit's shape
  and the tree's shape pinned (X-SPC-36). The two statement gaps must be closed: the layout before the salt, and one
  salt per prover (§6.1, decision 10).
- **A9, anchored inputs, for (3).** The salt, the forward index and the weights that the X and Y units read equal their
  registration anchors, on every audit (§2.3's R5).
  - Without it, every unit can be correct while the prover picks the salt, or commits weights chosen after F₁. Both
    are outside TT_NCP_U's game.
  - The input unit's harm is W, so it is proved whole, which is cheap.
- **A10, the key's named hash assumptions, for (3).** `cr/sha-512` for D_s and the node hashes, with its collision term
  ε_cr, about q²/2^257 for digests of at least 256 bits. `random-oracle` for the Program's SHA-512 and SHAKE256, which
  stand in for TT_NCP_U's oracle. A1's PRF still has no claim id.
- **A11, no call index registered twice, for (3).** This is the verifier's refusal of a repeated index (X-SPC-18). R6
  doesn't imply it, and (3) summed over windows needs it.

**Lean status.** Every statement above is proved: no `sorry`, only `propext`, `Classical.choice` and `Quot.sound`, and
Verity's Lean audit passes with 21 pins and a kernel replay. The pins await a named statement reviewer.
- A8 with A10 (`PerTileCount`), A9 (`AnchoredInputs`) and A11 (`UniqueCallIndices`) are named hypotheses.
- The Lean statements differ from the draft above in six ways; the package's `NOTES.md` gives each:
  - (2′) is stated separately from (2);
  - the probability is joint with acceptance;
  - H* is any bound meeting `harm_bound`'s specification;
  - the closed-form sizing uses ln(1/δ)/ε, an upper bound;
  - (3) takes A9 and A11 as acceptance events;
  - (3) is stated for any game, because `main`'s audit game has no salt.
- Not formalized: `harm_bound`'s implementation, PoUW's per-tile count statement, and the composed serving-and-audit
  game.

### 12.3 The optimal allocation

**The optimization.** Minimize the proving cost Σ_s k_s·c_s, where c_s is the rows to prove one unit of stratum s,
subject to H*(δ) ≤ εW.

**Its solution** (**Derived**). For small wrong fractions, a stratum's escape is about exp(−k_s·m_s/N_s). The adversary
puts its whole risk budget ln(1/δ) into the stratum with the most harm per unit of risk, so
H*(δ) ≈ ln(1/δ) · max_s H_s/k_s, where H_s = N_s·h_s is the stratum's total harm.
- The max means no stratum can lend draws to another, so the cheapest allocation meets every constraint separately:
  k_s = min(N_s, ⌈ln(1/δ)·H_s/(εW)⌉). That is **harm-proportional sizing**.
- **In what sense it is optimal** (X-SPC-47). It is optimal for this relaxed constraint, among independent stratified
  laws, against an adversary who fixes τ before the draw. The relaxed constraint bounds the exact one from above: term
  by term, a stratum's exact risk is at least k·m/N. So the rule is feasible, and ln(1/δ)/ε is an upper bound.
- **Exactly, it overshoots where a stratum is sampled heavily:** by 15% above the exact optimum in the red team's
  brute-force case.
  - At 70B, only the strip strata are sampled heavily: gate_up's X stratum samples 37%.
  - The tile strata sample about 10⁻⁴, so the tile rule is essentially exact.
- The exact hypergeometric bound (`harm_bound`) certifies t = 4,601 at δ = 1% and 27,707 at 2⁻⁴⁰, but only numerically.
- **The budget of record is root's** (draft #362, `Flock/Draw.lean`): the work law draws min(n_s, max(1, ⌈K·W_s/W⌉))
  per stratum, and Lean proves its escape is at most (1 − ε)^K. That meets δ first at K = 4,603 (δ = 1%) and
  K = 27,713 (2⁻⁴⁰; 27,712 misses), which is 4,606 and 27,715 draws after the per-stratum ceilings.
- The closed form ln(1/δ)/ε (Lean, `stratified_isHarmBound`) gives 27,726 at 2⁻⁴⁰, an upper bound.

**What that means for each class.** Every tile reads exactly one X strip and one Y strip, so H_tiles = H_X = H_Y = W.
- As harm-weighted strata, each class needs **at most about t = ln(1/δ)/ε draws**, whatever the fan-out. It is an upper
  bound: caps and the exact risk only lower it. The fan-out changes only each strip's harm, which is why strip strata
  must be keyed per site.
- Under closure, fewer strips are proved as the fan-out grows: a fraction 1 − (1 − p)^f of each stratum. At 2⁻⁴⁰ that
  is 24,398 X strips and 26,522 Y strips, and gate_up proves 12,704 X strips from its 15,207 tile draws.
- Rest units need only their integrity floor. Node units need no draws of their own: the closure proves them, and a
  wrong node matters only through the tiles beneath it, and not at all to y.

**Unit sizes.**
- A draw's cost grows with its unit's size, while t per class is fixed, so the smallest units whose harm is charged
  exactly are optimal: 16 × 16 tiles, and 16-row and 16-column strips.
- Finer strips, a single row say, charged conservatively (the full work of every tile they touch) cost the same in total.
  Charged exactly (a wrong row spoils only its own row of each tile), they would cost 16× less, but that needs a
  per-output count form of TT_NCP_U.
- Larger strips only cost more.

**A simpler way to run the same law: closure draws.**
- Draw only tiles, by work (`Stratified` over the tile strata). Prove each drawn tile together with the X and Y units it
  reads, each strip once, and each X unit with the node units on its strip's path to D_A, each node once.
- A drawn tile that is unsound is then caught, whether the tile itself, one of its strips, or a node on its X strip's
  path is wrong. So the escape is exactly `Stratified` over tiles, with the wrong set being the unsound tiles, and
  unsound(τ) is bounded by the tiles' own harm bound.
- A strip is proved exactly when one of its tiles is drawn, with probability about fan-out × the per-tile rate. That is
  "weighted by the compute it can spoil" by construction.
- **It gives the same bound at a lower cost** (X-SPC-48).
  - At 2⁻⁴⁰ the bound is identical to five digits.
  - Strips cost 39.8 T by closure, against 43.5 T as strata at t each, a saving of 3.7 T.
  - Nodes cost 0.62 T by closure, against about 2.2 T as strata keyed per (site, level).
  - It needs no strip or node strata, no harm weighting, and no per-site keys.
  - It beats every stratified law. In the red team's brute-force case it costs 24.43, against the exact stratified
    optimum's 24.8.
- It is a small addition to the draw law ("prove what a drawn unit reads, and for an X unit the node units on its
  path"), which needs the owner's review.

**Are strip draws nearly free? No.** Work-weighted means per draw, SHA-512 leaves:

| Per draw | k = 8,192 | k = 28,672 | Mean on the 70B mix |
|---|---:|---:|---:|
| Tile reading committed X and Y (arithmetic, words, X and Y openings) | 2.36 G | 8.25 G | 3.95 G |
| X-strip unit (A opening, D_s, D_A's opening, E₁'s XOF, commit X and D_s) | 0.42–0.50 G | 1.47–1.75 G | ≈ 0.77 G |
| Node units by closure, per X-strip draw (9 on a path, the upper ones shared: 3–5 new ones, 8.9 M each) | 0.03–0.05 G | 0.03–0.05 G | ≈ 0.03–0.05 G |
| Y-strip unit (weight opening, F₁'s XOF, commit Y) | 0.37–0.41 G | 1.30–1.44 G | ≈ 0.66 G |
| The exception's tile, for comparison (A and B openings, in-tile XOF, digest, path) | | | 3.80 G |

- A strip draw costs about 17–19% of a tile draw. Under closure each class needs somewhat fewer strips than tile draws,
  so strips add 34–37% on top of the tiles (checked, X-SPC-49).
- The tiles themselves cost about 4% more than the exception's, because they open X and Y, which are 3× A and B.
- About 60% of a strip unit's cost is committing its output in the circuit (48k bytes at 640 rows per byte). A leaner
  leaf hash (decision 6) helps strips most.
- In total the no-exception window is **1.41–1.43× the exception's at moderate t:** 25.0–25.6 T against 17.4–18.1 T
  at ε = 0.1%, δ = 1% (checked, X-SPC-49).

### 12.4 Costs per 70B window

The window has 8,192 tokens and fused in-domain calls. It holds 163,840 X units, 163,520 node units and 215 M tiles;
the run holds 419,840 Y units. The table is in C-Flock rows; the L40S hours in brackets are at 1 G AND/s (×14.5 at the
measured 69 M/s GEMM-template rate).

| δ | ε | K (draws) | No exception (strip units) | With the exception | Ratio |
|---|---:|---:|---:|---:|---:|
| 1% | 0.1% | 4,603 (4,606) | 25.0–25.6 T (6.9–7.1 h) | 17.4–18.1 T (4.8–5.0 h) | 1.41–1.43 |
| **2⁻⁴⁰ (decided)** | **0.1% (decided)** | **27,713 (27,715)** | **147.0–150.2 T; 41–42 h at 1 G AND/s; about 590–605 h at 69 M/s** | 102.9–106.9 T (29–30 h) | 1.41–1.43 |
| 2⁻¹²⁸ | 0.1% | 88,679 (88,681) | 450–459 T (125–128 h) | 328–341 T | 1.35–1.37 |
| 2⁻⁴⁰ | 0.01% | 277,246 (277,248) | 1.30–1.32 P (X capped) | 1.03–1.07 P | 1.24–1.27 |

- **These are the red team's recount** (X-SPC-49, cost script section 11), at root's K: the smallest K with
  (1 − ε)^K ≤ δ, drawn by root's work law (#362). `harm_bound` alone certifies 4,601, 27,707, 88,654 and 277,095, a few
  draws fewer, but only numerically.
  - SHA-512 leaves at 640 rows per byte, and D_s in SHA-512's per-row form.
  - E₁'s and F₁'s SHAKE256 at 282 rows per byte (low end) or 565 (high end).
  - Strips and nodes counted in expectation by closure.
  - The exception column is the first form of the key: the tile with its in-tile XOF, digest and path, D_A's openings,
    and one tree unit per k at the floor.
- **The rows scaled linearly before are dropped until recounted.** δ = 1% at ε = 0.01% and 0.001%, 2⁻⁴⁰ at 0.001%, and
  2⁻¹²⁸ at 0.01% were linear scalings of the δ = 1% row. The scaling is sublinear, so they were high (X-SPC-50).
- **The cost grows sublinearly in ln(1/δ).** δ = 2⁻⁴⁰ costs 5.9× δ = 1%, and 2⁻¹²⁸ costs 18.0× (not 6× and 19×). As t
  grows, closure shares strips and nodes more: at 2⁻¹²⁸, gate_up proves 28,475 X strips from 48,656 tile draws.
- **At very small ε the strip strata hit their caps** and are proved whole. Proving every X unit of the window (about
  126 T) and every Y unit of the run (about 277 T) is a fixed cost, so the no-exception penalty shrinks toward the tiles'
  4%. This is route 6's outright proof, reached naturally by the cap.
- **Where ε stops mattering.** The accountable compute is at least (1 − γ)(1 − ε)·W, with γ = 0.60% at 8,192³:

  | ε | Accountable fraction |
  |---:|---:|
  | 0.1% | 99.30% |
  | 0.01% | 99.39% |
  | 0.001% | 99.40% |

  Below about ε = 0.05%, each 10× in proving buys under 0.05 points, because γ dominates. The useful lever is δ: a
  cryptographic δ costs 5.9× (2⁻⁴⁰) to 18.0× (2⁻¹²⁸) at ε = 0.1%.
- **Decided (Daniel, 03:16Z): ε = 0.1%, δ = 2⁻⁴⁰ for now.** Closure draws remain the recommendation. They are cheaper
  than strata, and if strip strata are used instead they need per-site keys.

**The decided operating point, exactly** (**Derived**: 70B, fused in-domain calls, 8,192-token window, C-Flock rows,
SHA-512 leaves, the work rule, no exception):
- **Draws.** Root's work law (#362) at K = 27,713, the smallest K whose Lean-proved escape (1 − ε)^K meets 2⁻⁴⁰: 27,715
  draws after the per-stratum ceilings (2,718 qkv, 2,175 o, 15,210 gate_up and 7,612 down). `harm_bound` alone certifies
  27,707, and the closed form ln(1/δ)/ε gives 27,726. Closure then proves 24,402 X strips, 26,528 Y strips and 69,667
  node units in expectation.
- **Rows per window:** 147–150 T (147.0–150.2 T).
  - Tiles are 109.7 T, X strips 19.7–21.3 T, Y strips 16.9–18.5 T, and node units 0.62 T.
  - That is 5.9× the δ = 1% window, and 1.41–1.43× the exception's 102.9–106.9 T.
- **Time:** 41–42 L40S-hours at 1 G AND/s (the elementwise-template rate). At the one measured GEMM-template rate
  (69 M AND/s), it is about 590–605 L40S-hours, until witness generation moves to the GPU.
- **Reusing Y proofs across a run's windows** (new, X-SPC-51).
  - A Y unit's statement reads only the run's salt, the weight columns and constants, so once proved it holds for
    every later window of the run.
  - If the verifier keeps the run's set of proved Y units, a later draw that lands on one costs nothing.
  - At 2⁻⁴⁰ the Y strips then fall from 18.5 T per window to 11.7 T (the mean over a 10-window run) and 2.2 T (over
    100 windows). The whole run's Y is 277 T, proved at most once.
  - A long run's window is then about 134 T rather than 150 T.
  - The per-window law, and (2′), are unchanged. It needs a new piece of verifier state (the run's proved-Y set), and
    the draw-law owner's agreement that a proof from an earlier window of the run counts in a later one.
- **Caps.** At the 8,192-token window no class hits its cap:
  - *Activation strips:* 163,840 units in all. As strata, gate_up's would draw 15,207 of its 40,960 (37%); by
    closure, its 15,207 tile draws prove 12,704 of them.
  - *Weight strips:* every per-site stratum holds at least 40,960 units per run, against at most about 15,200 draws.
  - *Node units:* the closure proves 69,662 of the window's 163,520 in expectation, and they have no draw of their own
    to cap.
  - *When the caps bind:* the activation-strip strata hit their caps, and are proved whole, only in shorter windows:
    gate_up below about 3,000 tokens, down below about 1,500, qkv below about 540, and o below about 430. The
    weight-strip strata don't cap at 70B.

### 12.5 The width rule under the joint objective: free compute and exfiltration (decision 4)

Daniel's framing: "we're optimizing for a joint objective of minimizing both free compute and exfiltration capacity." The
figures are for a 70B, 8,192-token window at ε = 0.1% and δ = 2⁻⁴⁰ (Λ = ln 2⁴⁰ ≈ 27.7), in C-Flock rows. They are the
red team's checked figures (X-SPC-52 to X-SPC-56) unless marked otherwise.

**Two bounds from one draw.**
- One draw gives both bounds, with two harm functions (`audit_damage` and `exfiltration` in Lean).
- *Free compute:* a unit's harm is the matmul compute it can spoil (§12.2). The bound is H*_W(δ) = εW.
- *Internal exfiltration bound:* a unit's harm is the number of its output bits that can reach an observable output.
  The bound is H*_B(δ) bits.
- For a stratum of total harm H drawn k times, the bound is about Λ·H/k, whatever the unit size.

**What actually caps leakage: the served output** (X-SPC-52, X-SPC-56).
- Only values that reach the served output can leak through values. That is log₂ 128,256 = 16.97 bits per token, or
  1.39 × 10⁵ bits per 8,192-token window if every token is served.
- The four conditions:
  - *The verifier's view isn't published.* Openings, the leaves' hiding salts and proofs hold prover-chosen values.
    Registered roots carry only what grinding buys, about log₂ of the prover's hash budget per root.
  - *Sampling randomness is pinned* by a verifier-supplied seed. Otherwise a run with every unit correct still leaks up
    to 17 bits per token through its choice of sample.
  - *The served output is only the tokens.* Logprobs, top-k lists or several samples per prompt widen it.
  - *Timing is a separate channel,* unbounded here. Wide units don't change it, because the prover controls latency
    with every unit correct.
- **Every feasible design's internal bound sits far above that floor.**
  - With Z inside the tile it is 2.19 × 10⁹ bits, about 16,000× the floor.
  - With 220,000 narrow Z draws it is 2.2 × 10⁸, 1,600× the floor.
  - Even at 2.2 M narrow Z draws it is 2.2 × 10⁷, 160× the floor.
  - Reaching the floor itself would take 3.5 × 10⁸ Z draws, 8.3 P rows with their openings.
- **So realized leakage is the output channel's in every feasible design.** The width rule doesn't change it, and the
  joint objective's exfiltration term is the same across designs. It drops out of the choice. What lowers leakage is the
  output channel's four conditions, not the partition.

**Strict partitions for the served Z** (Daniel, 04:23Z and 04:25Z: "I want a compelling reason why we would need to
change our clean conceptual picture of the partition").
- *The constraint:* every value is computed in exactly one unit.
- *Where Z's value can be computed.* It can be computed in the tile, which is (a). It can be computed in a unit that
  reads the tile's state, which is (b). Or it can be computed from A and B in a unit that the tile's count doesn't
  depend on, which is (c).
- `ncp-z` (the tile keeps C_{3k/16}, and a narrow unit computes A·Bᵀ again) computes Z's value twice. It is weighed
  last.
- The costs below are **Derived** at ε = 0.1% and δ = 2⁻⁴⁰, on the red team's recount of 147–150 T. The new figures
  are not red-teamed.

**(a) Keep Z in the tile, under a width exception, with no extra units.**
- *Cost:* none. The window stays at 147–150 T.
- *y's integrity under the decided tile draws.* Except with probability δ + ε_proof, at most **1.24 × 10⁻³** of a
  window's Z outputs are wrong: 1.2440 × 10⁻³ exactly, at every δ. That is 1.244ε (0.902/0.725): the tiles are drawn
  by work, and the k = 8,192 tiles hold 90.2% of Z but only 72.5% of the draws (X-SPC-53, X-SPC-63). It is a window
  share. Per site it is 1.0 × 10⁻² (qkv), 1.3 × 10⁻² (o), 1.8 × 10⁻³ (gate_up) and 3.6 × 10⁻³ (down).
  - In Lean this is `audit_closure`, with each tile's weight set to its 256 outputs instead of its work.
- *Would a small tile-floor boost fix it?* Not a small one.
  - Sizing the k = 8,192 tile stratum by Z as well as by work (25,008 draws instead of 20,100) brings the share to
    1.0 × 10⁻³.
  - That costs **+15.1–15.4 T (+10%)** with the closure's strips and nodes (X-SPC-63).
  - Nothing needs it to match another option: `ncp-z` at its matching 22,000 draws gives 1.26 × 10⁻³.
- *Width.* The tiles are wide units that reach the output, through their Z and nothing else. Leakage is capped by the
  served output in every design, so this costs no leakage. What it costs is integrity granularity: a wrong tile spoils
  256 outputs. The bound above already counts that.
- *The separator port is pinned by the protocol* (X-SPC-66). The width exception is sound only if the port is the
  tile's Z, fixed by the protocol and not chosen by the registrant.
  - A registrant-chosen port would let any wide unit call its output a separator and skip the width rule.
  - A floor-drawn wide unit on the served path would then break y's bound, because the floor's count sizing assumes
    32-bit units.
  - The build enforces it (`partition.width_rule`). It removes the pinned Z ports, then width-checks every unit from
    which y is still reachable. Only the dequantization units are, at 16 bits each.
  - A Program whose y reads a credited word fails: the tile, and every PoUW unit upstream of it, becomes reachable and
    too wide.
  - The permanent home is `Q_nested_instances` v0: a served-output designation and the pinned ports, in its spec,
    evaluator, vectors and Lean port.
- *Lean:* nothing, in either scheme. The per-tile count keeps Z where TT_NCP_U has it.

**(b) Split the tile: its final block becomes narrow Z units that read the tile's committed pre-final state.**
- *The unit.* One Z unit per output. It reads C_{3k/16−1} (the tile's last credited word, committed in a leaf that
  opens word by word), 16 entries of X and 16 of Y. It does 16 MACs and commits Z.
  - This is a strict partition: the last block's gates move from the tile into the Z units.
  - A unit costs about 12 M rows, mostly its openings.
- *But the tile stays on the output path.* Z = C_{3k/16−1} + the last block, so a wrong tile corrupts y through its
  pre-final state.
  - The tile still carries 8,192 observable bits.
  - y's integrity is still bounded by the tile draws (1.24 × 10⁻³). Under one law over the tiles and the Z units, the
    bound is the larger of the two terms, not their sum: `harm_bound`'s supremum sits at a vertex, with all the fault in
    one class (X-SPC-65). So (b) ties (a) at 22,274 Z draws or more, and is worse below.
- *NCP-INT, if the count keeps Z.* A tile counts only if its 256 Z units are right, so they carry its work harm, and
  closure proves them with each drawn tile.
  - That costs about +0.4 T if a tile's Z units share their openings in one session.
  - It costs up to about +84 T if each unit opens its own leaves and paths.
- *NCP-INT with a restated count, and H-1T.* For H-1T, Z isn't credited, so certifying it in separate units needs no
  change (the Lean worker, 04:26Z). The Z units then carry no work harm. The tie with (a) costs 0.27–0.35 T of Z
  units.
- *Verdict:* **dominated by (a) in every case.** It adds units and cost, and gains neither the width rule nor any
  integrity.

**(c) Restate `checkIdx` so the count doesn't need Z, then compute Z once, in narrow units from A and B. For NCP-INT
only.**
- *The partition.*
  - The tile stops after block 3k/16 − 1 and no longer computes Z.
  - Narrow Z units compute A·Bᵀ from the committed A row and weight row, and dequantization reads them.
  - Z's value is computed once, so this is a strict partition: the original §12.5 move.
  - Serving is unchanged. The kernel's C_{3k/16} is the Z units' witness.
- *What it buys.*
  - The tiles are off the output path, so there is one width rule.
  - y's integrity is set by k_Z: 1.0 × 10⁻³ at 27,700 draws (+0.65 T), and 1.26 × 10⁻⁴ at 220,000 (+5.19 T, +3.5%).
    Net of the tile's saved last block (0.042 T), that is +0.61 T and +5.15 T.
  - These are window shares. At 27,700 draws the down projections are 2.8× looser than (a). Being at least as tight as
    (a) at every site, and at 1.0 × 10⁻³ over the window, takes 32,618 draws, 0.90 T (X-SPC-64).
  - **The costs assume one Merkle leaf per A row and per weight row.** On one flat 16-row leaf, a Z unit hashes 16 rows
    to read one, and (c) costs 6.1 T and 48 T. The build commits a leaf per row (`plan.openings`), which costs the X and
    Y units about 11 compressions each (X-SPC-57).
- *What it asks of the Lean, for NCP-INT.*
  - Restate `checkIdx` without the last block. That is a change to `Params`, so it needs a statement reviewer, and the
    restated TT_NCP_U is a new instance of the conjecture.
  - Justify the credit: each tile's credit drops by the last block's share, exactly d/(3k) = 16/(3k). That is 0.065%
    at k = 8,192 and 0.019% at 28,672, and γ goes from 0.597% to 0.662% at the worst unit (X-SPC-67).
  - The restated TT_NCP_U is strictly stronger than today's: it counts calls correct on fewer words, a superset of
    today's correct calls. The statement reviewer should see that direction.
- *Not for FP8* (X-SPC-68). H-1T's count needs no change, because Z isn't credited (the Lean worker). But no unit
  computes H-1T's useful output from A and B alone: it depends on the salt through x1's rounding and the FP32 chain.
  - A unit that reads the salt and recomputes the chain recomputes the tile.
  - A unit that reads the tile's pre-final word is (b).
  - So H-1T keeps (a), and so does NCP-FP8, whose useful output also depends on the salt (§9). (c) is an NCP-INT-only
    option.

**`ncp-z`, weighed against these.**
- *What it would gain.* Over (a): one width rule, and y's integrity tunable cheaply (10× for +5.2 T) with no Lean
  change. Over (c): no restatement.
- *Is there a compelling reason for it? No.*
  - Leakage is the same in every design.
  - At matching integrity it costs 0.52 T more than (a) and delivers what (a) already gives (1.26 against
    1.24 × 10⁻³).
  - Its one real edge is cheap extra integrity for y, which no requirement asks for yet. And (c) delivers that within
    the partition once `checkIdx` is restated.
- So there is no concrete gain the partition can't match, and it is withdrawn.

**The separator argument** (Daniel, 04:35Z: "the matmul outputs are a separator between the tile and the RU outputs
… this caps the influence of the RU outputs").
- **The theorem** is in Daniel's Notion draft, [Draft 2: Computational integrity via zero-knowledge spot checks](https://app.notion.com/p/Draft-2-Computational-integrity-via-zero-knowledge-spot-checks-3d2399515d9e80d18797d8ebb674b676)
  (a stale draft; its extraction is going to `docs/sampled-proofs-notion-extraction.md`).
  - *Definition 4.6 (downstream cut):* "A set K ⊆ G is a downstream cut for E if every directed path from a gate in E to
    a designated output contains a gate in K. … The cut's width is w(K) = Σ_(i∈K) log₂|D_i|."
  - *Lemma 4.7 (a cut determines the output):* "Among the transcripts defining 𝒪_C(E), the values at K determine the
    delivered output. Consequently, |𝒪_C(E)| ≤ 2^(w(K))."
  - *Theorem 5.4 (two-stage integrity):* for each possible faulty-unit set E, choose a downstream cut K_E of the
    coarsened computation. Protocol 2 then has (U, ε)-integrity with U = log₂ Σ_(E : a(E) > ε) 2^(w(K_E)). By its
    Remark 3.2, U bounds the prover's influence over the output in bits, and by Corollary 3.3 it bounds exfiltration.
  - Its §6 applies it to replay units: "For each replay unit, all its exported scalars form a downstream cut for every
    verification unit it contains … This can be much smaller than the sum of all internal unit-output widths."
  - **This design cites it as Theorem 5.4 at replay-unit granularity.** That is the form that is pinned (the
    influence-pin review), and the one layout A meets: a tile is its own replay unit, and its exported Z is the cut.
  - **What "RU" means** (its §5.2, and `protocols/sampled_proofs`): a replay unit, "a subcircuit together with its
    incoming and outgoing boundary edges; fixing its incoming boundary values determines its correct interior and
    outgoing values". The "RU outputs" are the request replay unit's delivered outputs, meaning the served tokens.
  - Nothing in the repo states it. `verity.ir.partition`, `verity.ir.cut` and `harm_bound` have the width rule but no
    cut-based influence bound. Flock's Lean `compose_cone` (`Audit/Circuit.lean`) is the determination half: a
    consumer's committed wires are right when no unit of its cone is wrong. The research-notes quote the Sep 26 rule
    only in `lanes/pous/20260929T0210Z-handoff-from-verity-root.md`: "the largest units whose output width is at most
    16 or 32 bits, plus small fixed extras, so that corrupting the transcript meaningfully takes many wrong units".
- **The topology: confirmed.** In the quotient DAG, every path from a PoUW unit to the served output passes through a
  tile's Z port:
  - an X strip reaches the served output only through the tiles that read it, and those only through their Z;
  - so does a Y strip, and so does the noise, which lives inside the strip units;
  - D_s and the node units reach it only through D_A, then the X units, then the tiles' Z;
  - the tiles' checked words have no consumer at all;
  - the salt and the forward index are prescribed inputs, which carry no freedom of their own (the draft's input
    linkage).
- **What crosses the separator.**
  - *Per tile:* its 256 Z values, 32 bits each, 8,192 bits, produced by the tile itself.
  - *Per call:* the matmul's m·n Z values at 32 bits each (for gate_up at m = 8,192, 1.5 × 10¹⁰ bits), 1.76 × 10¹²
    bits per window.
  - *Nothing else:* no X, Y, noise, D_s, D_A, node value or checked word.
  - Downstream, y's BF16 (16 bits per output) is a narrower cut, and the served tokens are narrower still.
  - **The cap binds through the output space, not through U** (X-SPC-66). Theorem 5.4's U at replay-unit granularity for (a) is 2.19 × 10⁹ bits,
    and its fault-set term alone, log₂ of the number of escaping fault sets, is 2.9 × 10⁶ bits, 21× the cap. The cap
    comes from the trivial fact that everything the prover can cause is a delivered output: at most 16.97 bits per
    served token, 1.39 × 10⁵ per window.
- **One condition.** The theorem's "designated output" must be the delivered output only.
  - In the IR the word leaves are Program outputs (§2.6), so that they aren't committed-unread.
  - The query must therefore mark them, and every commitment, as committed to the verifier but not delivered. That is
    X-SPC-52's first condition: the verifier's view isn't published.
- **The safety argument is the separator topology.** It is not "no wide unit reaches an observable output": the tile
  does reach it, through Z. What holds is that every other PoUW unit reaches the output only through the tiles' Z, and
  the tiles only through Z, a port the protocol pins (X-SPC-66).
- **So the width rule is settled by the cut, not by an exception.**
  - A unit behind the separator enters U only through the Z values behind it, whatever its own width. That covers the
    strips, the noise, D_s, the node units and the tiles' checked words.
  - The tiles produce the separator. A faulty tile's cut is its 256 Z words (8,192 bits), or its 256 y values
    (4,096 bits). That is simply the width it adds to U, and U is capped by the served output in any case.
  - What remains is a choice of certificate for PoUW's units: Theorem 5.4's downstream cuts at replay-unit granularity,
    in place of the baseline's 32-bit outgoing interface. The draft says the baseline alone doesn't allow it: "a narrower downstream cut does not
    permit a wider baseline VU". Daniel's 04:35Z message gives the go-ahead.

**The joint optimum, re-derived.** Leakage is the output floor in every design, so the optimum minimizes proving at
ε = 0.1% subject to the integrity wanted for y.

| y's integrity target (wrong-Z share) | Cheapest strict partition | Extra proving | Depends on the Lean question? |
|---|---|---:|---|
| ≈ 1.2 × 10⁻³ (what the decided tile draws give) | (a) | 0 | no |
| 1.0 × 10⁻³ | (c) at 27,700 Z draws; or (a) with the Z-sized tile boost | +0.65 T; or +15 T | (c): yes, for NCP-INT |
| 1.3 × 10⁻⁴ | (c) at 220,000 Z draws; (a) would need about 10× the tile draws | +5.2 T | yes, for NCP-INT |

**Decision 4: decided, option (a)** (Daniel, 04:35Z: "If so, then this is fine").
- **Adopted: (a), the partition as it stands, with Z in the tile.** The window stays at 147–150 T at ε = 0.1% and
  δ = 2⁻⁴⁰, y's integrity is 1.24 × 10⁻³ of outputs, and nothing depends on the Lean question.
- **The width rule is settled by the Z separator (Theorem 5.4 at replay-unit granularity):**
  - no unit behind the separator needs a width exception;
  - the only departure from the Sep 26 rule is the tiles' 8,192 Z bits each, which enter U as a faulty tile's cut width,
    and the served output caps what can leave;
  - everything else keeps the Sep 26 rule.
- **The separator port is the protocol's:** the tile's Z, pinned, never registrant-chosen. The build enforces it with a
  reachability check from the served outputs (`partition.width_rule`).
- **The condition:** the word leaves and every other commitment count as committed, not delivered, so that the
  delivered output in the theorem is the served tokens.
- **What lowers leakage** is the output channel's four conditions, not the partition.
- **(c) is kept as an optional integrity upgrade, not adopted.** It would only move the separator from the tiles' Z to
  narrow Z units, so its one gain is y's integrity, tunable cheaply (+0.61 T net for 1.0 × 10⁻³, +5.15 T for
  1.26 × 10⁻⁴, on per-row leaves). That is the only part that depends on the Lean question: it needs NCP-INT's
  `checkIdx` restated. It is NCP-INT-only: H-1T and NCP-FP8 stay on (a).

**Design changes:** none. The partition is §12.1's, with the tile outputting its word leaf and Z's narrow
leaf, and dequantization reading Z. The Lean theorems are width-abstract and don't change.
