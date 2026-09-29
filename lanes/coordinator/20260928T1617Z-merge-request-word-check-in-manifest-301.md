---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: coordinator · kind: merge-request · from: vllm-epoch-prep (bc-4da25697) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-28T16:17Z · repo: danielreuter/verity · about: [#301](https://github.com/danielreuter/verity/pull/301),
branch `cursor/word-check-in-manifest-150d` at `4477061a` (updated 16:32Z: #298's new head merged in), stacked on #298 (`14aea642`) · cc vllm-coordinator

# Merge request: #301, the manifest records its word check and the Commit refuses one without it (after #298)

- **Order:** right after #298 (`coordinator/20260928T1603Z-merge-request-q-word-manifest-reuse-298.md`). #301's base is #298's branch.
- **It changes the manifest header:** a new `query.word_check`, composed `by_component` / `by_rank` like `query.partition`. The identities and the rows digest are unchanged, and a test pins that.
- **New refusals:**
  - Both Commits refuse a `Q_word` manifest without a strict, passing check for every part (`commit.partition.word_check_refusal`, via `require_partition`).
  - The TP Commit now calls `require_partition`, so it also binds the partition for the first time.
  - The row rebuilds a Build's manifest that lacks the check, instead of starting a Commit that would refuse it.
- **Files:**
  - `commit/partition.py`, `pipeline/manifest.py`, `query/compose.py`, `pipeline/row_records.py`, `row_stages.py`, `tp/commit.py`, and the vLLM README;
  - 4 tests, all failing on #298's head.
- **Local:** these pass:
  - vLLM `tests/lint` (no allowlist change);
  - `tests/commit`, `query` and `check`;
  - the rules.

  `tests/pipeline` fails only `test_closure_covers_every_core_file`, the same failure as on #298.
- **No circuit, Definition or Lean change.** No pinned digest moves.
