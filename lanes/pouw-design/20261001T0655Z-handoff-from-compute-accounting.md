---
id: 20261001T0655Z-handoff-from-compute-accounting
campaign: verity
lane: pouw-design
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-c5d0d68e (pouw-design): re-aim. The target is the most plausible named security assumption, not "no conjecture"

From compute accounting, 11:55 PM PDT. Daniel, 11:49 PM PDT, verbatim: "I don't think there's ever going to be a conjecture-free
bet... I think the goal would just be to find a really plausible security assumption!"

**The new deliverable** (item 4 of `docs/overnight-gpu-plan.md`, reworded) has two parts:
- **A ranking of candidate security assumptions by plausibility:** how well studied each is, how falsifiable, how minimal,
  and what attack would break it.
- **The non-Pearl design that needs the best one,** at close to Pearl-C's cost, with its γ argument resting on that named
  assumption.

Drop "no new conjecture" as a requirement. Plausibility is the measure.

**Start from what Daniel and the old coordinator already walked through.** Both documents are in the old store, preserved in
`art:8bd64630bc06c23d5095996d2f198ce4bd557413722ad94bd3ca3c1a949e42e9`. Fetch them with
`research data fetch art:8bd64630… --to <dir> --path 'docs/pouw/milder-assumptions.md'` and the same for the second path:
- **`docs/pouw/milder-assumptions.md`** (28 Sep, a research note for Daniel). "Milder assumptions for PoUW: can TT and TT_NCP be
  reduced to something chiller?"
  - It ranks Theorem D + IndepRule(P), H_16, A1(2), A1(4), A2, MinRank(P) + a lifting lemma, TT_NCP⁰ and TT_NCP(0.5%).
  - It proves, class by class, that standard cryptography, I/O and pebbling, asymptotic fine-grained conjectures and
    operation-count models can't replace TT or TT_NCP.
- **`docs/pouw/cheap-binding.md` §2, "Ranked alternatives".**
  - Each design is listed with its named assumption: TT_OUT(1/400), TT_OUT_D (depth-scoped, testable exhaustively), I-O, NCP-INT
    low-byte, H-1T byte targets, counting, and Pearl's Assumption 1.
  - It derives the bound that no design inside 5× total can have its γ proved by counting. That's why Daniel says a conjecture is
    unavoidable.

I've asked @old-accounting whether a later list exists, in a note, in Notion or in a transcript, and I'll forward anything it
finds. Rank against these first, and add new candidates where your designs need them.

The assumptions table you should rate against is the Project store's `docs/pouw/assumptions.md` (bc-4323a347's).


**Addendum, 11:58 PM PDT, from @old-accounting.** Daniel's walk-through was in the old coordinator's chat on 27–28 Sep, with no
notes id and no Notion page. Its written form is in the same old-store art (`art:8bd64630…`):
- **`docs/pouw/problem-statement.md`, the primary source:**
  - §4, "Assumption landscape": §4.1 covers what standard assumptions prove, §4.3 the options, and §4.4 the TT(0.5%)
    recommendation.
  - §6, "Candidate directions, tagged by assumption": D1–D7, with NCP under TT_NCP.
- **`docs/pouw/milder-assumptions.md`** is Daniel's next ask, for even milder assumptions.
- **The living superset** is `docs/pouw/assumptions.md`, also preserved as `art:a707728e…`. It came from Daniel's 30 Sep ask
  for "a table of possible precise security assumptions with monikers / parameters". The Project store's copy is bc-4323a347's.
- `cheap-binding.md` §2 lists designs, not that walk-through. It's still useful context.

Rank against `problem-statement.md` §4 and §6 first.
