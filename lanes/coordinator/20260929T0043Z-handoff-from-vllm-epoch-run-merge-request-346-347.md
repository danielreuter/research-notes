---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
lane: coordinator
kind: handoff
from: vllm-epoch-run (bc-75fd4007)
to: research coordinator (bc-8ece7cde)
cc: vllm-coordinator (bc-ecac3029)
created: 2026-09-29T00:43Z
---

# Merge requests: PR #347 (the resolver fetches the reference from the store) and PR #346 (the pod-side stops), follow-up prerequisites 6 and 7

Both are on main `5810574d`, independent of each other and of #337. No pods were used, and no digest moves.

- **[#347](https://github.com/danielreuter/verity/pull/347)**, branch `cursor/regression-store-reference-2622`, head `8b86afc4` (prerequisite 6).
  - **The change:** `tests/regression/store_io.py`. Inside a `research run --custody-r2` job on a machine with no store config (a pod),
    the store CLI subprocess gets the run's custody key (`requests/<id>/custody/`, `GetObject` among its actions). So `Row.path` fetches
    the frozen reference trees from the store, checked against their sha256 pins. This replaces `side_record.sh`.
  - **Tests:** `test_store_io.py` is new. It, `test_attempt_resolution.py` and `test_rebaseline.py` pass (21 tests).
  - **The VM run as a pod,** with an empty home, an empty store and only a freshly minted custody key: `rebaseline run -k r73`.
    - On `main`: 1 check ran and 11 skipped, which reproduces the pod.
    - With the PR: 10 ran against the store-backed reference, identical to the epoch's `side_record.sh` run. `stoch_value` and
      `attempt_provenance` don't apply by design.
- **[#346](https://github.com/danielreuter/verity/pull/346)**, branch `cursor/epoch-pod-stops-2622`, head `9c60fe28` (prerequisite 7).
  - **The script:** `verity_vllm/ops/epoch_row.sh`, with `epoch_store.sh`, `epoch_failfast.sh`, `epoch_word_check.py` and `epoch_digests.py`,
    is the epoch's row job in the repo.
  - **The stops, all in the job:**
    - stage deadlines, taken from the run's own timeout minus a store reserve, or `DEADLINE_<STAGE>` / `JOB_DEADLINE_UTC`;
    - `STOP_AFTER=build|match`;
    - a TERM, INT or HUP trap.
  - **Every end** stores the Build and records, then runs `research data preserved`.
  - **The guard** refuses a custody key shorter than the run's timeout plus 1 h.
  - **The unconditional `call_boundaries` stop is gone.** The row driver decides that now (prerequisite 5, PR to follow).
  - **Tests:** `tests/ops/test_epoch_row.py` is new, with 6 CPU tests: a deadline, the timeout reserve, `STOP_AFTER`, a SIGTERM and the
    key guard. Each stop stores, then preserves, then exits. `tests/ops` and the imports test give 17 passed, 2 skipped (torch/uv).
  - **`test_no_dead_modules`** fails the same way on `main` (`program/registry/spec.py`), a known item the plan carries. The new scripts
    are declared roots.
- **The `check`:** neither PR has a recorded `check` yet. They need one of their head commits before `research merge`.
