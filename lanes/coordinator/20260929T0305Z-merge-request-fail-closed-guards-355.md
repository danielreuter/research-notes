---
cursor:
  subagentId: "bc-529bea7d-5d34-50d2-91ce-57b592d72bfb"
---

lane: coordinator · kind: merge-request · from: fail-closed guards and pod leases (bc-529bea7d) · to: the research coordinator
(bc-8ece7cde) · created: 2026-09-29T03:05Z · repo: danielreuter/verity

# Merge request: #355 (guards never fail open; the disk floor; custody --publish evicts)

- **The PR.** [#355](https://github.com/danielreuter/verity/pull/355), branch `cursor/fail-closed-guards-2bfb`, on `main` `b4fd93e9`.
  This is changes 1 and 2 of the infra refactor plan. It touches only `tools/research/`.
- **Local tests.** The full `tools/research` suite passes (`-n 8`: 493 passed, 2 skipped). It has no recorded `check` yet.
- **Overlap with #352** (deterministic tests): both PRs change `tools/research/tests/test_pods_guard.py`, in different hunks.
  This PR changes one assertion (line 167).
- **Order.** Land it before [#358](https://github.com/danielreuter/verity/pull/358) (leases and `budgets.toml`), which is stacked
  on it (`20260929T0330Z-merge-request-pod-leases-budgets-358.md`). It needs no deploy step to be safe, but its value comes with
  the restarts below.

## Deployment on the control pod

1. Update the checkout the guards run `research` from to a `main` that has #355.
2. Restart each running `research pods guard --prefix P` under the supervisor, with the same flags plus `--detach`:
   `research pods guard stop --prefix P`, then `research pods guard --prefix P <same flags> --detach`.
   - The state file carries the tally over the restart.
   - `research pods guard status --prefix P` now shows write faults. The log shows a `supervisor pid ...` line.
3. The `vyv-` daemons run their own copies under `/root/dm/`, so this PR changes nothing for them. Picking up the fix is the
   vLLM coordinator's call:
   - copy the new `tools/research/src/research/pods/budget_cap.py` to `/root/dm/`;
   - restart it with `budget_cap.py start ...`, which now runs it under a respawn loop.
4. The disk floor is on by default: `research run` and `research fetch --all` refuse under 1.5 GB free.
   - Set `RESEARCH_DISK_FLOOR_GB=0` in a shell only to override it deliberately.
   - The refusal names the eviction command: `research data evict --target-free-gb 3 --runs`.
5. `research data custody RUN --publish` now removes the run's files of 1 MiB and more once custody holds (`--keep-local` keeps
   them). Running it over the control pod's published runs frees their space, and `research data custody --triage` lists what
   needs publishing first.
