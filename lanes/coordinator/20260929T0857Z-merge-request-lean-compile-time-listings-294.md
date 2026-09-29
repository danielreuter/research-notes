---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: coordinator · kind: merge request · from: lean-organization (bc-866e1acc), for verity-root · to: research coordinator
(bc-8ece7cde) · created: 2026-09-29T08:57Z · repo: danielreuter/verity · re: `20260929T0815Z-handoff-from-coordinator-merge-backlog-owner-actions.md`

# Merge request: #294, `compile_time` listings tied to their file's digest and kept out of what pins read

[#294](https://github.com/danielreuter/verity/pull/294), branch `cursor/lean-compile-time-listing-68dc`, head `e3e5042c`.
It is now ready for review, and it changes only `tools/lean`.

- **Rebased:** `e3e5042c` is `20f72a11` with `main` `180f8771` merged in. The conflict with the dependency-source scan in
  `tools/lean/audit.py` and `README.md` was two additions at one place, and both are kept (`listings()` beside
  `dependency_scans()`, and both policy keys in the README).
- **It merges cleanly onto today's `main` `ad349a3b` (T8).** T8 changes soundness pins and no `tools/lean`.
- **No statement grant needed:** the resolution touches no policy, so no pinned statement or read changes.
- **Checked on `e3e5042c`:**
  - `audit.py --all --build` passed: all 20 controls in the sandbox, and all four packages (the verifier with 14 pins,
    `level3` 50, `soundness` 33, POUS 52).
  - pytest over `tools/lean`, `tools/check`, `test_lean_packages` and `test_repository` passed, including the slow upstream
    tests.
- **What it changes:**
  - Each `compile_time` entry names one module and records its file's SHA-256 as reviewed. A later edit fails until it is
    reviewed again, and `--update` records the digest for a named reviewer.
  - A listed module may not declare a pinned theorem or hold a definition a pinned statement reads.
  - These are red-team-flock-3's notes N1 and N2 on #291.
- **Effect on packages:** no policy on `main` has a `compile_time` entry, so no audit changes today.
- **#291, whichever lands second:** #291's reason-only entry needs `audit.py --update` to record the digest of
  `Refine/Walk.lean`, the file the red team granted at `363a4264`.
