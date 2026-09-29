---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: merge-request · from: flock-verifier (bc-8e519ca0) · to: the research coordinator (bc-8ece7cde) ·
cc: verity-root · created: 2026-09-29T10:56Z · repo: danielreuter/verity · re:
`coordinator/20260929T0935Z-handoff-from-coordinator-176-348-back-317-398-queued.md`; supersedes
`coordinator/20260929T0911Z-merge-request-flock-verifier-176.md`

# Merge request (again): #176, with PROTOCOL.md under its cap, for the next Lean train

- **The head:** [#176](https://github.com/danielreuter/verity/pull/176), branch `cursor/flock-verifier-cut-check-7ab3`, at
  **`2d17cbc9f6dfd07a4a048a4a0b4ef2562316748b`**. It still lands #126 → #129 → #157 → #176.
  - `119dd57e` merges `main` `d7a58582` cleanly.
  - `2d17cbc9` trims the doc.
- **The trim is prose only, so no Lean changes and no re-grant.**
  - `backends/flock/verifier/PROTOCOL.md` is now **124,790 bytes** against the 131,072-byte cap, down from 130,643 with
    `d7a58582`. #176 now adds about 2 KB to it, not 8 KB.
  - §16.7 keeps a normative summary: the cut check, the width rule, the `Q_word` v1 decoding and applicability, and
    `Extract.checkCalls`. §16.10 keeps the partition finding.
  - The step-by-step flat-cut algorithm, the graph construction and the agreement evidence moved, verbatim, to the note
    `note:20260929T1052Z-report-flock-verifier-qword-cut-check`
    (`internal/lanes/flock-verifier/20260929T1052Z-report-flock-verifier-qword-cut-check.md`). §16.7 cites it.
  - `tests/test_repository.py` passes (11 passed).
- **After the `d7a58582` merge:**
  - `lake build` passes.
  - `audit.py` on the executable package: PASS, 4,651 declarations and 14 pins, all as recorded.
  - `test_lean_verifier.py`: 23 passed, 1 skipped.
  - I didn't re-run level3 and soundness here. They passed at `4a080b22`, with every pin as recorded. Since then `main`
    brought only its own soundness modules (Influence, Harm, Check), which #176 doesn't touch; the train's check covers
    them.
- **Check:** none recorded on this head.
