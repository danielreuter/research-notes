---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T14:10Z
---
# PR #81 verdict: APPROVE (head `bf92fe34`; merge after #80, which it contains)

- **Recheck against main `f41b62cf`:** clean. Every ratchet lint runnable without pytest passes on main + #81 (39/39). The lane'"'"'s gate
  `r20260926-135130-0176`: 129 tests, 0 failures, including the by-name and dead-module lints.
- **Change:** the VU export reuses the sampled replay'"'"'s own population (`driver.keep_population` / `take_population`) instead of
  rebuilding it. On #67 that removes the more-than-18-minute rebuild from inside the Commit, before the verdict. The rebuild
  fallback's `max_population_seconds` drops to 900 s.
  - The replay'"'"'s behaviour is unchanged: `_kept` returns the same split and only stores references.
  - Records and digests are unchanged. A re-export draws a different sample, because it now uses the replay'"'"'s exact strata; that
    doesn'"'"'t matter for any record.
- **On my 13:50Z follow-up:** I accept the lane'"'"'s reason for not moving the export after `verdict.json`. The operands are pair 0'"'"'s
  committed words, held only in committer memory. Keeping them past the replay would raise the admitted peak, which is worse. #81
  shrinks the pre-verdict window to the draw (≤ 600 s) plus the extraction.
  - **Queued follow-up (the proper fix):** read the drawn units'"'"' committed words in the window (O(MB)), then evaluate, decompose and
    write them after `verdict.json`.
- **Non-blocking note:** `vu_store` calls `SR.keep_population(True)` at import, and `pipeline/commit.py:2318` imports `vu_store` in
  every Commit. So population-keeping is armed even with `VU_EXPORT=0`, and a module-level side effect sets it. It'"'"'s harmless in
  practice: `after_replay` drops the population either way, and it'"'"'s only references. It'"'"'s cleaner to arm it from `after_replay`'"'"'s
  caller only when `--vu-export-dir` is set. Worth a one-line follow-up.
