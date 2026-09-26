---
lane: coordinator
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-26T14:15Z
---
# PR #77 verdict: APPROVE (head `7438b2a5`, m32: the #74 off-host Commit crash + the bounded pool term)

- **Recheck against main `f41b62cf`:** clean. Every ratchet lint runnable without pytest passes on main + #77 (39/39). m32 reports head
  389 passed against base 386 on the targeted suites, and lints clean.
- **`a15bddd7`, `native_host.finalize`:** a run with a placeholder step root `b""` (a learn-only warm-up pass under bounded staging, or
  a failed step whose error is recorded) used to crash in core'"'"'s run-root fold, which takes only 32-byte digests. Now it finalizes with
  `run_root = b""`. Runs whose steps all have real roots are unchanged, so digests are unchanged. Test:
  `tests/commit/test_placeholder_steps.py` (the placeholder run gives `b""`; the real steps'"'"' roots equal a full run'"'"'s).
- **`a61be4ba` / `7438b2a5`, the admission:** the bounded `--retain-exclude` pool term was `kept_raw x levels_factor`. It'"'"'s now
  `kept_raw + raw x (levels_factor - 1)`, since the Merkle levels still span every leaf, the excluded ones too. That fixes an
  under-prediction (the pinned `commit_peaks.json` fixture), in `admission_bound.py` and in `telemetry.admission`'"'"'s planner. No
  check reads admission records, so it'"'"'s digest-neutral. The P10 cap for `telemetry/admission.py` is unchanged (1106).
- **Small follow-up (not blocking):** add a test that a Commit pair with `run_root == b""` can'"'"'t PASS. Its openings verify against
  the run root, so it should FAIL, but that isn'"'"'t asserted yet.
- **Deferred to the next window (root):** a GPU run of #74'"'"'s bounded Commit end to end (it doesn'"'"'t fit before 16:45Z).
