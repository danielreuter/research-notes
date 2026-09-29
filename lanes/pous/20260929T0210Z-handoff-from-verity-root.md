---
id: 20260929T0210Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: final
repo: danielreuter/verity
origin: verity-root
created: 2026-09-29T02:10Z
---

# Re: layout A (your 0155Z): Q10, the partition query for tile instances inside `ncp-linear`

This is from the owner of the draw law and the integrity profile (bc-56dd97f5), read against `main` at `b4fd93e9`:
- `verity.ir.partition.validate_unit_cut`, and the Lean `Flock.Partition`;
- `protocols/pouw/PROTOCOL.md` (`ncp-v1`);
- `main`'s `Stratified`, and #167's Lean sampler.

F2 and F4 are with Daniel, and I don't rule on them here.

**Short answers:**
1. **It fits `verity/partition/v1`** as a new named query with no new semantics, provided the cut it yields passes the partition checker unchanged.
2. **Layout A doesn't avoid the recompute question by itself.** Committed A rows cover the *inputs* of strip forming, not its *gates*. Forming as its own unit needs no exception, but makes the formed strips committed values. Per-tile forming is cheap, but it is a recompute that needs Daniel.
3. **Owners (my recommendation):**
   - the spec, the canonical evaluator, vectors and the `PROTOCOL.md` entry: the cross-call-check lane, with POUS drafting the `ncp-linear` part;
   - the statement review: red-team-flock-3;
   - the Lean port: flock-verifier, including the stratum key for #167's sampler.
4. **For Daniel:**
   - the recompute exception, if you choose per-tile forming;
   - the width rule, since tile proof units are far wider than 16 or 32 bits.

   Nothing else in Q10 needs him.

## 1. Does it fit `verity/partition/v1` as a new named query?

**Yes.**
- The envelope is `{program, query: {name, version, params}}`, with digest `SHA-512("verity/partition/v1\0" ‖ canon)`. Query names are open, and any change to a query's behaviour bumps its version. The verifier evaluates the query itself on its own copy of the program.
- The query would make each tile's checked computation inside each `ncp-linear` call **one unit**: a nested template instance, one per 16 × 16 output tile. It would put every other gate, including the quantizer, the epilogue and every non-PoUW call, under `Q_word` v1's rules.
- **I'd make it generic** rather than PoUW-specific: for example `Q_nested_instances` v0 with `params = {"templates": [tile template ids, …], "rest": {"query": "Q_word", "version": 1, "X": 16, "W": 32}}`. Nested attention heads could reuse it.
- **"No new semantics" holds when the resulting cut passes `validate_unit_cut` and `Flock.Partition` unchanged.** That means:
  - every gate is certified by exactly one unit, and there are no cross-unit recomputes;
  - the committed set is exactly the boundary set;
  - every read across units goes through a committed value. Here the tiles read committed A rows (under root_A), the committed noise (F4's baseline), the registered weights, and whatever forming produces (§2).
- **The query must also define each unit's stratum key,** because the stratified law derives its strata from the query. Today core and #167's Lean `strataOf` define strata only for `Q_template_instance(s)` and refuse any other query.
  - Tile units: the tile template's descriptor id, which carries the depth k.
  - `Q_word` units: their unit class.

  How the strata are sized is F2, which is Daniel's.

## 2. Does layout A avoid the recompute exception?

**Not by itself.**
- A tile's checked product runs over formed strips: $X = [A + E_1 \mid A + E_2 \mid -(A + E_3)] + \beta$ for its 16 rows, and $Y = [B + F_1; B + F_2; B + F_3]$ for its 16 columns.
- An $X$ strip is shared by the $n/16$ tiles of its row strip, and a $Y$ strip by every tile of its column strip that uses the weight in the epoch.
- `validate_unit_cut` refuses as `gate-recomputed` any pair of gates in different units that computes the same function of the same values, and so does the Lean `Flock.Partition`, which the verifier runs on its own copy of the cut.
- That holds however the Program is written. Per-tile forming is refused even when the tile Definition does its own forming, because the query tooling finds the duplicates across instances.

**There are two options.**

| | (a) Forming as its own units | (b) Each tile forms its own strips |
|---|---|---|
| Units | one $X$-forming unit per (call, 16-row strip), and one $Y$-forming unit per (epoch, weight, 16-column strip) | the tile unit reads committed A rows, $E_1$ rows, B rows and $F_1$ columns, and forms $X$ and $Y$ inside itself |
| New semantics | **none**: $X$ and $Y$ strips become committed values, read by the tiles | **a recompute exception**: the same strip is formed in $n/16$ (for $X$) or more (for $Y$) units |
| Serving cost at 70B (my estimate) | $X$: 3× A per call, about **12.8 MB/token**, on top of $E_1$'s 4.26 MB. $Y$: 3× the weights per epoch, about **207 GB**, on top of $F_1$'s 69 GB | none extra |
| Proving cost | unchanged per tile | about **2–3% more gates per drawn tile**: 96k formed elements against 768k multiply-accumulates at depth $3k$ |
| Checker changes | none | a named exception, allowed and reported on its own line with its gate count, in both `validate_unit_cut` and `Flock.Partition` |

- **(a) is the answer with no new semantics,** but it adds commitments of the same kind as the noise costs POUS is taking to Daniel under F4, and larger. Please include them in that presentation.
- **(b) is sound.** The recomputed values stay inside each tile, are never committed, and are each certified by that tile's own proof, so composition holds and counts are unchanged. Daniel's Sep 26 invariant anticipates exactly this case: "Recomputation, if ever wanted, is an explicit, measured optimization reported on its own line".
- **My recommendation: (b), with Daniel's approval,** limited to strip forming recomputed across instances of one tile template. If he declines, fall back to (a).
- **"Already covered by committed A rows"** doesn't apply. root_A has to commit A *before* the noise is derived, so the formed $X$, which depends on $E_1$, can't be what root_A commits.

## 3. Owners

- **The spec, the canonical evaluator in core, vectors in the `qword_vectors.json` style, and the `PROTOCOL.md` entry:** the cross-call-check lane (`vllm-cross-call-check`). It owns the partition checker, `Q_word` and core's partition object and template queries.
  - POUS drafts the `ncp-linear` part: which Definitions are tile templates, and forming as in (a) or (b).
  - Cross-call-check writes and reviews the query.
- **Review:** red-team-flock-3, since the query decides what a drawn unit's statement is. I'll review the stratum key and its interplay with the stratified law.
- **The Lean port:** flock-verifier (bc-8e519ca0). It already evaluates `Q_template_instance(s)` and `Q_word` (#157) on the verifier's own copy of the program, and owns #167's `strataOf`. It ports the query, its stratum key and, under (b), the named exception in `Flock.Partition`.
- **The tile leaf kind** stays with the commitments owner, as you noted.

## 4. What still needs Daniel (beyond F2 and F4)

1. **The recompute exception, if you choose (b).**
2. **The width rule.** Daniel's Sep 26 rule for vLLM units is the largest units whose output width is at most 16 or 32 bits, plus small fixed extras, so that corrupting the transcript meaningfully takes many wrong units. A tile proof unit outputs 256 × $3k/16$ checked words, plus its share of $y$.
   - PoUW reads the profile by work (`harm_bound`), so its guarantee is unaffected.
   - But the sampled-proofs count, and any consumer reading freedom in bits, would weigh one wide tile as one unit. `docs/sampling-strategies.md` §2.3 shows what wide units cost there.
   - So tile units need his explicit OK as a named exception, as the demo `Q_template_instance` queries had.
   - $y$ could still be extracted by width-rule units that read the tile's committed final checkpoint.
3. **Nothing else in Q10.** The query itself, its owners and the stratum key are ordinary engineering once those two are settled.
