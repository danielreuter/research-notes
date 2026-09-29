---
cursor:
  subagentId: "bc-e7e2bf3a-f0d8-5b5a-9714-9de87eb030a8"
---

# Influence through a separator, on `main`'s audit law (draft, unpinned)

The influence-cap theorem of Daniel's Notion Draft 2 (Definition 4.6, Lemma 4.7) and its uses (Theorem 4.8,
Theorem 5.4 at replay-unit granularity, Corollary 3.3), stated and proved over `main`'s Boolean `Circuit`, `Partition`,
`Law` and audits. The extraction that motivates it is
[`docs/sampled-proofs-notion-extraction.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/sampled-proofs-notion-extraction.md).

**Status.** Every declaration is proved: no `sorry`, `axiom` or `native_decide`, and only `propext`, `Classical.choice`
and `Quot.sound` (AXIOMS.txt, from `lake env lean Check.lean`). Built with Lean v4.34.0 and Mathlib `5ed2965`, the
revision Verity's soundness package pins.

**Verity's Lean audit passes** (2026-09-29, `tools/lean/audit.py` at origin/main b4fd93e9): 713 declarations in 12
modules, only the standard axioms, 12 pinned theorems, and a clean kernel replay. It flagged nothing, so no source
changed.
- `lean-audit.json` holds the roots (every module; `Check` is exempt), a layer rule keeping the vendored code
  independent of this package, the 12 pins (the table below) and their `reads`, recorded with `--update`.
- A second run without `--update` passes against those records, and `check.sh` prints ALL CHECKS PASSED.
- The pins are new, so the merge handoff must name a statement reviewer. `review.txt` lists every pinned signature and
  every definition the pins read. The reviewer should check that `Separates` quantifies over every gate of every unit
  in `B`, that `D` is the delivered wires only, and that `K` is committed.

~~~text
lake exe cache get && lake build && lake env lean Check.lean
VERITY_CHECKOUT=<a Verity checkout at b4fd93e9 or later> ./check.sh     # ALL CHECKS PASSED
~~~

- `FlockSoundness/`: `main`'s audit law at b4fd93e9, byte for byte, with `Audit/TwoStage.lean` added to the set the
  pouw-accountable-compute submission vendors (digests in VENDORED-FROM).
- `PouwAccountable/HarmBound.lean`: `IsHarmBound`, `harm_bound`'s specification, from that submission.
- `Influence/Separator.lean`: the new module, 15 theorems (the table's results plus two helper lemmas). Its intended home on `main` is
  `backends/flock/verifier/lean/soundness/FlockSoundness/Audit/Influence.lean`.

`D` is the set of delivered wires (the served tokens). Commitments and leaves are circuit outputs that nobody is
delivered, so they stay out of `D`; this is the condition PoUW's decision 4 names.

| Theorem | Statement |
|---|---|
| `outputs_eq_of_separates` | Lemma 4.7: two transcripts with the anchors' inputs, wrong only in `B`, agreeing on a committed separator `K` of `B` from `D`, agree on `D` |
| `card_delivered_le` | they deliver at most `2^|K|` values on `D` |
| `separates_exits` | the committed wires of `B`'s units separate `B` (a replay unit's exports) |
| `Separates.mono`, `Separates.union` | wider cuts and smaller unit sets stay separators; unions of separators separate unions |
| `card_influenceSet_le` | Theorem 4.8's count: `|influenceSet| ≤ ∑_{B : δ ≤ e B} 2^|K B|` |
| `audit_influence` | Theorem 4.8 on the one-stage audit: `Pr[accept ∧ out ∉ influenceSet] ≤ δ + ε_ks + δ_link + δ_in` |
| `Refines.twoStage_influence` | the same on the two-stage audit, over replay units, with `effEscape` |
| `card_influenceSet_le_harm` | `|influenceSet| ≤ 2^H · #{B : δ ≤ escape B}` for a harm bound `H` of the separator widths |
| `card_admissible_le` | `#{B : δ ≤ escape B} ≤ ∑_{j ≤ K} C(n, j)` when `miss (K + 1) < δ` |
| `card_guess_le`, `audit_exfiltration` | Corollary 3.3: `avg_m Pr[accept ∧ g(out) = m] ≤ |influenceSet|/|M| + δ + ε_ks + δ_link + δ_in` |
