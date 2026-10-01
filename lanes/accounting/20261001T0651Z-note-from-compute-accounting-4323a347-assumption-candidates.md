---
id: 20261001T0651Z-note-from-compute-accounting-4323a347-assumption-candidates
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-4323a347 (the assumptions table): add the candidate-assumption rankings as a section of the table

From compute accounting, 11:57 PM PDT. Daniel wants the most plausible named security assumption found, since no design will
be conjecture-free (11:49 PM PDT). Two lists from the old store (`art:8bd64630…`) belong in your table, `docs/pouw/assumptions.md`
in the Project store:
- **`docs/pouw/milder-assumptions.md`:** NCP's ranked candidates. Theorem D + IndepRule(P), H_16, A1(2), A1(4), A2,
  MinRank(P) + a lifting lemma, TT_NCP⁰ and TT_NCP(0.5%), plus the classes it rules out.
- **`docs/pouw/cheap-binding.md` §2:** each design's named assumption, from TT_OUT(1/400) and TT_OUT_D through I-O, NCP-INT
  low-byte, H-1T byte targets, counting and Pearl's Assumption 1.

Add a short section, "Candidate assumptions, ranked by plausibility", that cites both documents and links to them, and cites
`art:8bd64630…`. The pouw-design worker (bc-c5d0d68e) is extending the ranking tonight, and its result goes into the same
section.


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
