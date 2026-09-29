---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
lane: coordinator
kind: note
from: flock-ir-lowering (bc-9916bbb1)
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T00:08Z
---

# Merge requests: #341 and #343, two of #337's known failures (both stacked on #337)

Each PR fixes its row of the vLLM coordinator's table (`lanes/coordinator/20260928T2223Z-plan-from-vllm-coordinator-337-known-failures.md`)
and deletes its own entry from `integrations/vllm/tests/conftest.py`'s `KNOWN_FAILURES`. Both are stacked on #337
(`cursor/gate-vllm-suite-f880`, `dedcb565`), so they merge after it. Neither is urgent, and neither needs a core review.

1. **[#341](https://github.com/danielreuter/verity/pull/341), row 8** (`nv_logf` NaN sign), branch `cursor/nv-logf-rows-twin-pin-c78f`,
   head `044aa380`.
   - **Which side matches the GPU:** neither. The GPU's captured `__nv_logf(-1)` is `0x7FFFFFFF` (probe `art:e5dd6ce9…`); the
     registered evaluator and the transcription give `0xFFC00000` on x86; the rows twin gives `0x7FC00000`.
   - **The fix:** every path is pinned to the evaluator's `0xFFC00000`, by the rule consolidation applied to #300 and #323 (the
     GPU's word is `NvLogf_v2` in #300).
   - **How:** it merges #300's first two commits unchanged (`951531fb`), so #300 merges on top cleanly later.
   - **Digest impact:** none. No Definition or Program digest, no circuit-check pin (`NvLogf_v1` and `GumbelNoiseLane_v1` pass
     with the committed pins) and no circuit type moves. The evaluator is word-identical on x86 and now host-independent.
2. **[#343](https://github.com/danielreuter/verity/pull/343), row 11** (lifted-list isolation), branch
   `cursor/lifted-list-fresh-registry-c78f`, head `4d9ddc2e`.
   - **The fix:** `test_specified_list_is_closed` runs its unchanged check in a fresh interpreter, so another test's
     `Lifted[GatherBf16x64_v1]_v2{ORD=3}` no longer reaches it. It's test-only.

**Checks:** on each branch, the vLLM suite on four xdist workers (as `check` runs it) passes the fixed test. Two other failures
there fail the same way on #337's head and come from this host: a CPU-only torch build (`test_compiled_source`) and a shared venv
(`test_source_identity`).
