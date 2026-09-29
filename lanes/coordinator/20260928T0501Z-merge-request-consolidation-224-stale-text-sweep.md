---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T05:01Z
---

# Merge request: PR #224, a sweep of stale status text, retired names and dead doc citations (with or after #211)

- **PR:** [#224](https://github.com/danielreuter/verity/pull/224), branch `cursor/stale-text-sweep-ac68`, head **`3941a843b660ddbccb27fdf00d3d97739fbaa671`**, on `main` `6746f408`. Ready, $0.
- **Contents:** text only, across 68 files, with no behaviour change:
  - the frozen backends' specs no longer read as proposals;
  - veritor paths and dead file citations are fixed;
  - the package descriptions are fixed;
  - "proof unit", "serving" and "input set" appear in prose; identifiers stay;
  - citations of Project docs outside the repo now point at the README Glossary.
- **Identity:** the two Rust edits are one-line doc-comment swaps that keep every line number, so SP1's approved `elf_sha256` is unaffected.
- **Conflicts:** it touches no file any open PR touches, checked against all of them at 05:00Z.
- **Order:** with or after #211, whose Glossary defines "proof unit". It is one of tonight's docs PRs for outside readers, with #211, #213 and #217.
- **Tests:** repository, `instances_hw`, `store_prov`, and every touched test file: 226 + 167 + 818 passed, and 3 skipped (torch and GPU).
- **Epoch:** moves no digest.
