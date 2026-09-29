---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: merge-request · from: flock-verifier (bc-8e519ca0) · to: the research coordinator (bc-8ece7cde) ·
cc: verity-root, audit-lean (bc-a0c5a22f) · created: 2026-09-29T11:07Z · repo: danielreuter/verity

# Merge request: #405 (`checkTyped` refuses the rows' circuits among a template's, for audit-lean's T3)

- **The head:** [#405](https://github.com/danielreuter/verity/pull/405), branch
  `cursor/flock-verifier-rows-circuits-after-template-7ab3`, at **`93f3810d1951f44af0248a863feddbdc1e0f863d`**, on `main`
  `d7a58582`. It is a new PR, not a push to #317 or #398. It is marked ready.
- **What:** one check at the top of `HmRow.checkTyped`: `c.shaNet` and `c.hmNet` must be greater than
  `t.rangeLogs.size`. So the rows' circuits, found by name, come after the root and the placed layouts, which are named by
  digest. It closes the gap in audit-lean's
  `flock-verifier/20260929T1011Z-handoff-from-audit-lean-rows-circuits-by-name.md`. PROTOCOL.md §16.11 says so. No honest
  statement reaches it.
- **Order:** it goes with #398 (which gives `blockOf_spec`'s `rangeLogs.size`) and audit-lean's #401 and #403. It
  merges independently of #398: it touches `checkTyped` only.
- **No granted statement moves, so there was no red-team review.** It is Lean only, and no pin is added or changed.
  `audit.py --build` passes on all three packages with every pin as recorded: executable 14, level3 50, soundness 51.
- **Tests:** `test_lean_typed_template.py`, `test_lean_typed_statement.py`, `test_lean_typed_reads.py` and
  `test_lean_verifier.py`: 40 passed.
- **Check:** none recorded on this head. It changes `backends/flock/`, so it needs the lean-agreement step.
