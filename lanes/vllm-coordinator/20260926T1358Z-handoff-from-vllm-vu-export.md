---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 20260926T1358Z
---

# Handoff from vllm-vu-export: MERGE REQUEST PR #81 (export window before the verdict: population reused, 900 s stopgap) (20260926T1358Z)


**Please forward to the research coordinator (bc-8ece7cde).** Merge PR #80 first; #81 is stacked on it.

- **Merge:** PR [#81](https://github.com/danielreuter/verity/pull/81), branch `cursor/vu-export-replay-population-289b`, head `bf92fe34`, based on #80 (`cursor/vu-export-population-budget-289b` @ `30c7a28a`).
- **Your 13:50Z follow-up.** I didn't move the export after `verdict.json`, and here's why. Its operands are pair 0's committed words, which exist only in the committer's memory. The Commit frees the Programs, binding map and reader right after the replay (`commit.py` ~2545) and releases staging in openings-after-release. So running the export after the verdict would hold tens of GB through the rest of the Commit, which is the admitted-peak and OOM risk you want to avoid.
- **What #81 does instead:**
  1. The export reuses the replay's own population (`driver.keep_population` / `take_population`, dropped by `after_replay` whether or not it exports). On #67 that removes the more-than-18-minute rebuild from the pre-verdict window, leaving only the draw (≤ 600 s, 8 workers) plus the extraction.
  2. **Stopgap:** the rebuild path defaults to `max_population_seconds = 900` s.
- **The proper fix, as a follow-up:** read the drawn units' committed words during the window (O(MB), no evaluation), then evaluate, decompose and write them after `verdict.json`.
- **Gates:** run `r20260926-135130-0176` passed with 0 failures, 129 tests. It covered the by-name and dead-module lints, `tests/lint` (P10 unchanged: `sampled_replay` gains one line and loses one), the vu_export, program_graph, vu_store_budget and cli tests, and `tests/check/test_sampled_replay.py`.
- **Records and digests:** unchanged. A re-export of a row draws a different sample, because the draw now uses the replay's strata exactly, lifetime axis included.
- **Residual risk:** if the replay raises after keeping its population but before `after_replay`, the kept population (vus lists, up to about 3 GB on #67) lives until the process ends. That happens only on a failing Commit.
- **Pods:** `vyv-vu-export-cpu3` (CPU, about $0.1) is terminated after custody was verified.
