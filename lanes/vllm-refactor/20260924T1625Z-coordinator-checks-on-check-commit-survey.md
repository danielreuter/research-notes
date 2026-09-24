---
id: vllm-refactor/coordinator-checks-1
lane: vllm-refactor
kind: note
created: 2026-09-24T16:25Z
---
# Coordinator spot-checks of survey-check-commit.md (at f0810a11)

## Confirmed
- **Production commitments don't verify under core.** The leaf is `SHA-256("verity/pos-leaf/v0" || u64 nbytes || value)` and the root `SHA-256("verity/semantic-root/v0" || program_digest || query_id || template_digest || ctx_digest || epoch || u64 N || merkle_root)` (`commit/semantic_layout.py:1-45`). Core `verity.commitments.leaves` uses a different leaf rule, so no core verifier can check these roots.
- **Core is monkeypatched at runtime.** `check/global_match_fast.py:482-520` rebinds `verity.ir.codec._spec_id`, `verity.ir.refs.runs` and several Prog, compare and dag functions at runtime.

## Corrected
- The survey says sampled replay "authenticates nothing". It is narrower than that.
  - The Commit harness **does** open sampled leaves and verify them against the run root (`harness/commit_delta.py:2022-2033` and `734-742`), and a failed opening fails Commit.
  - The **value comparison** (`OC.oracle_compare(..., OC.committed_reader(com), ...)` at `harness/commit_delta.py:2339`, also `tp/worker.py:1192`) reads the collector's in-process retained buffers (`com._layouts`, `com._gpu_blocks`, `meta.host`; `check/oracle_compare.py:914-953`), not the opened values.
  - So there are two independent checks that nothing ties together. The bytes compared against the oracle are never shown to be the bytes that were committed and opened.
  - Refactor rule: value checks consume opened (authenticated) values only.
