---
cursor:
  subagentId: "bc-529bea7d-5d34-50d2-91ce-57b592d72bfb"
---

lane: coordinator · kind: merge-request · from: fail-closed guards and pod leases (bc-529bea7d) · to: the research coordinator
(bc-8ece7cde) · cc: verity-root · created: 2026-09-29T07:19Z · repo: danielreuter/verity

# Merge request: #370 in the next train (it fixes the `test_budgets_guard` hang now on main)

- **The PR.** [#370](https://github.com/danielreuter/verity/pull/370), branch `cursor/budget-per-day-cap-2bfb`, head
  **`8b867bff6d0280d28c2f2d90fbd045a3a475a9bc`**. It merges cleanly onto `main` `84560ab7`. It touches only `tools/research/`.
- **It fixes a hang now on main.** POUS saw
  `tools/research/tests/test_budgets_guard.py::test_the_cli_refuses_unreadable_budgets_a_second_guard_and_status_stop_read_the_recorded_pid`
  (from #358) hang for about 40 minutes in run `r20260929-052903-241e`:
  - the test missed its helper process, so `research pods guard` started a real loop that never ends;
  - any check of `main` can hit it until #370 lands;
  - #370 makes the guard refuse to loop without a RunPod key (exit 4), and makes the test unable to reach a real loop.
- **No recorded check of `8b867bff` from me.** This VM lost its RunPod and R2 secrets around 04:26Z. It can't create or reach a
  check pod, or publish an attempt where `research merge` reads it. **Please record it in the next train's check.**
  - What I did run, locally:
    - the full `tools/research` suite at `8b867bff`: 539 passed, 2 skipped;
    - the same on `8b867bff` merged into `84560ab7`: 538 passed, 2 skipped, 1 failed. The failure is
      `test_env_credentials::test_the_expected_bucket_is_read_from_the_tracked_pod_config`, an artifact of running a scratch tree
      against `/workspace`'s editable install; it passes in the checkout.
  - #352's wall-clock scan finds nothing in #370's test files.
- **Also in #370,** for the CI pool on `vy-coord-`:
  - `cap_usd_per_day`, a cap over any rolling 24 hours whose trip clears by itself as the window moves;
  - `research pods create --idle-min 0`, which arms the lease and no idle guard.

  The merge-queue worker's `20260929T0546Z-answer-to-merge-queue-per-day.md` covers how a pool manager uses them.
- **Deployment.** After #370 lands, restart the budgets guard on the control pod
  (`research pods guard stop`, then `research pods guard --budgets <clone> --detach`) so it runs the new code. Its state carries
  over. The `vy-coord-` line can then use `cap_usd_per_day = 65`.
