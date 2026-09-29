---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T04:35Z
---

# Merge request: PR #217, every package README current on `main` (for tomorrow's collaborators)

- **PR:** [#217](https://github.com/danielreuter/verity/pull/217), branch `cursor/package-readmes-ac68`, head **`a0543fa441cae0aa96081e171f300b501e02c43b`**, into `main`. Docs only, ready, $0.
- **Contents:**
  - 6 new READMEs: `backends/flock`, `backends/vole`, `packages/verity`, `protocols/one_stage`, `protocols/sampled_proofs`, `benchmarks/one_stage`;
  - 12 corrected: `backends/README.md` with the per-family coverage table (what `check` collects, what it doesn't, and the Rust tests it never runs), the frozen backends, `backends/flock/verifier`, `integrations/vllm`, `census`, and `fixtures/bench-instances/v1`.
- **Tests:** `tests/test_repository.py` passes. The coverage counts come from `python -m pytest --collect-only` on `6746f408`.
- **Conflicts:** none expected. No open PR touches these files, and #211 edits only the root `README.md`, `AGENTS.md` and `check.py`.
- **Order with #192:** `backends/flock/README.md` says the circuit prover "comes with PR #192", which is true before and after #192 merges. Once #192 lands, I'll drop the "until #192 merges" clause here and in #211's Glossary in one small follow-up.
- **Epoch:** moves no digest.

This, #211 and #213 are the three docs PRs that collaborators read first. If one train can take all three, that's ideal.
