---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T04:29Z
---

# Merge request: PR #211, `README.md` and `AGENTS.md` accurate, with the Glossary (consolidation fix 10)

Outside collaborators start reading the repo tomorrow (Daniel, 03:59Z), and these two files are what they read first. Please take this in the next train you can.

- **PR:** [#211](https://github.com/danielreuter/verity/pull/211), branch `cursor/repo-docs-glossary-ac68`, head **`ce58cf83fa9402f776c68f04f3ce294a91df2bc3`**, into `main`. Marked ready. CPU only, $0.
- **Contents:**
  - `README.md` and `AGENTS.md` corrected to `main` `6746f408`: dependency direction, backends active vs frozen, repository map, and M0 not yet on `main`;
  - the Glossary rollout: proof unit, circuit vocabulary, partition, the integrity profile as the audit's own object, verifier, and old-names rows;
  - the four stale "PR #85 … not on this tree" strings in `tools/check/check.py`, plus the matching assertion in `tests/test_check.py`.
- **Code:** only those strings; the skip branch stays.
- **Pins and circuits:** none touched. No Lean file and no `lean-audit.json`.
- **Tests run here:** `tests/test_repository.py`, `tests/test_check.py`, `packages/verity/tests/test_boundaries.py`, `tests/test_lean_packages.py`, `protocols/tests/test_protocol_boundaries.py`, all passing on the tree merged with `6746f408`. No full `check` here: this VM is shared by the pass's workers, so your pipeline's recorded `check` is the run of record.
- **Conflicts it creates:** small textual ones in `AGENTS.md` for #134, #162 and #132, and in `check.py`'s four strings for #134. The resolution for #134 is in `20260928T0420Z-note-to-fast-check-from-consolidation-pr85-text.md`.
- **Epoch:** moves no digest of record.

The pass's other PRs follow as separate requests. [#210](https://github.com/danielreuter/verity/pull/210) (core boundaries) stays a draft until #192 and the epoch's gate G0 have landed, because its backend→integration allowlist must list their import sites exactly.
