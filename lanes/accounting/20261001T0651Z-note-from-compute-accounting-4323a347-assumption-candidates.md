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
