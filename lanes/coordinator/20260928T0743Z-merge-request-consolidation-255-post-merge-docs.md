---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T07:43Z
---

# Merge request: PR #255, docs after the M0 and fp32 merges; and #210 waits for the epoch

**[#255](https://github.com/danielreuter/verity/pull/255)**, branch `cursor/post-merge-docs-ac68`, head **`9e83376c`**, on `main` `3ba4d8b3`. Docs only, ready, $0.
- **What changes:**
  - M0 is on `main`: the Glossary, AGENTS, the C-Flock README and the one-stage README no longer say "lands with #192" or "draft #83";
  - they say `benchmarks/one_stage` runs M0 from the pinned `m0.tar` via `--m0-pythonpath`;
  - `AGENTS.md` and `packages/verity/README.md` name `verity.ml.fp32`, `scalar` and `library`;
  - the C-Flock and core test counts, which drift daily, are replaced by their skip conditions and the command that counts.
- **Conflicts:** #218, #166 and #162 rewrite `AGENTS.md`'s one-stage sentence. This PR changes only its two middle lines.
- **Tests:** `tests/test_repository.py` passes.

**#210 (core boundaries, fix 4) stays a draft until after the epoch's switch PRs.**
- Its backend→integration allowlist is exact. It now lists `main`'s 33 sites, with #192's and #182's added, at head `34b873c1`.
- #231, on the epoch's path to GO, changes three sites. Merging #210 first would fail #231's train check.
- I'll refresh `KNOWN` and mark it ready once S1–S4 are on `main`. The other open PRs that add sites are listed in its description.
