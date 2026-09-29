---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T07:01Z
---

# Merge request: PR #251, `ligero-verify/DISCREPANCIES.md` split under the size cap (fix 3), right after #224

- **PR:** [#251](https://github.com/danielreuter/verity/pull/251), branch `cursor/ligero-discrepancies-index-ac68`, head **`2ae722bc7a0550023b2c1349b911cf1364df6aa3`**. Stacked on #224's branch. Take it after #224, or take its head alone, which lands both. Ready, $0.
- **Why:** the file was 49,036 bytes against the 49,152-byte cap, so any edit to it would fail `tests/test_repository.py`.
- **Contents:**
  - a 4.0 KB index, with entries D1–D15 in `discrepancies/d<n>.md`;
  - moved verbatim: a script rebuilt the old file byte for byte;
  - `tests/test_repository.py` allows the new directory (`SPLIT_DOCUMENT_DIRS`).
- **Identity:** the `ligero_verify_batch` tool's source closure hashes differently. No code, fixture or vector changes.
- **Tests:** `tests/test_repository.py` passes, and `cargo test --no-run` for ligero-verify compiles. Trial merges are clean with #210, #228 and #241.
