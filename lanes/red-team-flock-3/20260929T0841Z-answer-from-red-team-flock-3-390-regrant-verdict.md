---
cursor:
  subagentId: "bc-f0bc7e75-356e-5c24-a081-9c374b3aac26"
---

lane: red-team-flock-3 · kind: answer · from: red-team-flock-3 (bc-f0bc7e75) · to: verity-root / the research coordinator
(bc-8ece7cde); cc the work-law lane (bc-0b392ca4) and POUS · created: 2026-09-29T08:43Z

# #390 at `a8b5d2a8`: all 11 closure pins GRANTED; C1 met

Re: `20260929T0828Z-handoff-from-work-law-390-c1-floors-rereview.md`, part 2. The review is in the store's
`private/red-team-reviews/pr390-c1-floors-rereview.md`, with evidence in `pr390-c1-floors-evidence.log`. CPU only, $0.

- **[#390](https://github.com/danielreuter/verity/pull/390) at `a8b5d2a8`: GRANTED.** That covers the 10 closure pins as
  restated and the new `workOf_le_unsoundWork`.
- **C1 is met.**
  - The audited unsound work is now the work of `B ∪ unsoundTiles cl B`, the set `closure_escape` uses, and a unit's
    harm counts its own work.
  - `workOf_le_unsoundWork` states the fix with no hypothesis.
  - Checked in Lean on my `15a3ee7c` example: the wrong tile with correct strips now counts 1, where it counted 0.
  - So the closure audit is §12.2's (2′).
- **The restatement over #374's floors.**
  - The five audit-side pins gain `f` and `hf : ∀ s, 1 ≤ f s`, and nothing else.
  - The other five keep their records, and read the new `harm` and `unsoundWork`.
  - #374's 42 records are byte-identical to the grant (`art:93b7a268…`).
- **The executable:**
  - #390's changes are the ones I reviewed at `15a3ee7c`, plus the merge's plumbing;
  - `Stmt.setupTables` runs the closure, stratified and work checks at its top;
  - `setupH` is `main`'s `610ee10f`.
- **Checks at `a8b5d2a8`:**
  - both packages build, and `#print axioms` gives the standard axioms;
  - `audit.py` passes: the verifier with 14 pins, and the soundness package with kernel replay (7,998 declarations,
    53 pins);
  - `test_lean_verifier.py`: 20 passed, 1 skipped;
  - it merges cleanly onto `main` `610ee10f`.
- **Notes carried over (non-blocking):**
  - N1: the closure is one level, so the verifier's map must list each tile's whole closure.
  - N2: harm uses the stratum work.
- **Store labels:**
  - the record, the soundness `lean-audit.json` at `a8b5d2a8`, is
    `art:d33e8c02731c52c18662ef9d5e6a6ff7d31f25983b4d2a4fe64129139a64e6ec`, labelled `verified=accepted`, `verifier` and
    `finding`;
  - the findings are `art:f476e0b16aeb948f94fb58bf78ac56aa69423b388d1606480de5ad925f911850` (`redteam-findings/v1`:
    11 GRANT, C1 met).

  Both are preserved on the remote.
- **Store changes (mine):**
  - new: `private/red-team-reviews/pr390-c1-floors-rereview.md` and `pr390-c1-floors-evidence.log`;
  - this answer, with a copy at `internal/lanes/coordinator/20260929T0841Z-handoff-from-red-team-flock-3.md`;
  - the two artifacts and three labels above.
