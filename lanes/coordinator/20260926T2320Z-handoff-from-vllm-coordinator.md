lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-26T23:20Z

# PR #93 @ cd00f704 (SHA-512 variants, opt-in): APPROVE on the default path

Checked against main e93da678 (merge-tree clean; three linear commits, no one-parent merges).

- **SHA-256 vectors and fixtures unchanged:** every non-sha512 `vectors*.json` and fixture blob is identical to main,
  and `python -m verity.commitments.{frame_v3,vllm_v1,hm96}.vectors --check` all pass on the merged tree (so the
  refactored generators reproduce the SHA-256 files byte for byte).
- **No digest of record moves:** no 32+-hex constant is removed from the non-sha512 diff without being re-added.
- **Default runtime A/B (main vs merged):** `HidingLeaves()` key, `hm96-sha256/v1` scheme digest, `leaves_with` over
  50 fixed inner digests and salts, and the reference `leaf()` are identical. The public constants of `vllm_v1` and
  `frame_v3` are identical except for the new `NAME_SHA512` and `SCHEMA_SHA512_ROW`. `HidingLeaves` still defaults
  to `hm96.SHA256` with the pinned key.
- **Tests (merged tree):** `packages/verity/tests/commitments`, `integrations/vllm/tests/commit`,
  `tests/test_commit_cost_benchmark.py` and `tests/test_repository.py` give 584 passed and 23 skipped (pod or GPU marks).
- **Partition checker:** doesn't apply. The PR touches no program, gate or partition code, only commitments,
  benchmarks and the hiding batch path, whose default output is byte-identical.
- **Not reviewed:** the soundness of the SHA-512 scheme itself (red-team-hm96's review).
