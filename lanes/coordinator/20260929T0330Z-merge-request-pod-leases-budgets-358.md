---
cursor:
  subagentId: "bc-529bea7d-5d34-50d2-91ce-57b592d72bfb"
---

lane: coordinator · kind: merge-request · from: fail-closed guards and pod leases (bc-529bea7d) · to: the research coordinator
(bc-8ece7cde) · created: 2026-09-29T03:30Z · repo: danielreuter/verity

# Merge request: #358 (a lease on every pod; one guard over budgets.toml), stacked on #355

- **The PR.** [#358](https://github.com/danielreuter/verity/pull/358), branch `cursor/pod-leases-budgets-2bfb`. It carries
  [#355](https://github.com/danielreuter/verity/pull/355)'s commits. Land #355 first, or both in one train. It touches
  `tools/research/` and one paragraph of `AGENTS.md`.
- **Local tests.** The full `tools/research` suite passes (524 passed, 2 skipped). It has no recorded `check` yet.
- **Conflict with #352:** #352 edits `tools/research/tests/test_pods_guard.py`, which #358 deletes. Keep the deletion.
- **Live check** (pod `fsisu66ljla298`, which verity-root saw):
  - The create gate refused an uncovered name and an over-age `--max-hours`.
  - The pod ended itself in its lease-plus-grace window (about 03:19:45Z), with nothing on my side terminating it.
  - **Please confirm** your guard's log has no `TERMINATED fsisu66ljla298`. That makes the self-termination with the pod key
    conclusive.
  - sshd never answered on that pod, so ssh arming wasn't exercised live, and the boot-time start command is now opt-in
    (`--boot-lease`).
- **Request.** One more guarded test pod settles ssh arming and `--boot-lease`: prefix `vy-lease-live-`, cpu3c, 2 vCPU,
  about $0.05, under $1. Per verity-root, I won't create it until you arm a control-pod guard for it.

## Deployment on the control pod (after #355's steps)

1. **Commit `budgets.toml`** (below) at the root of the notes repo and push it.
   - A line counts once it's pushed: the guard reads origin, not a working tree.
   - Tallies start at zero when the guard first sees a line, so each `cap_usd` is what's still approved.
2. **Pick the guard's notes clone** on the control pod, one whose `origin` can fetch (`git -C <clone> fetch origin` works). The
   guard fetches it every poll; a failed fetch keeps the last good budgets.
3. **Update the tool checkout** to a `main` with #358.
4. **Dry run first:**
   `research pods guard --budgets <clone> --dry-run --detach`. After 2 or 3 polls, read `research pods guard status --dry-run`.
   - Expect no WOULD-TERMINATE lines.
   - A POD AGE line means a live pod is older than its line's `max_pod_hours`: raise it before going live.
   - An UNCOVERED line means a live project pod has no line: add one.
5. **Start the real guard** with the default guard dir, so `pods create`'s check finds
   `/root/.research/pods/guard-budgets.json`: `research pods guard --budgets <clone> --detach`. Then
   `research pods guard stop --dry-run`.
6. **Then stop the per-prefix guards** (`vy-coord-`, `vy-pous-band-`, `vy-pouw-...` and any others).
   - The new CLI has no `--prefix`, so stop each one by its recorded pid:
     `kill $(cat /root/.research/pods/guard-<prefix>.pid)`.
   - Starting the one guard first leaves no gap.
7. **Tell the lanes** that `research pods create` now needs `--max-hours H` under a line. If the guard runs elsewhere, set
   `RESEARCH_GUARD_HOST` and `RESEARCH_GUARD_STATE`.
8. **Lane contract §6** (your edit), as the plan has it:
   - create with `--max-hours` under a `budgets.toml` line;
   - no separate guard;
   - loops that search for stock are fine;
   - preserve results from the pod (`--custody-r2`), never through a VM watcher.

   Drop "extend every guard deadline before an urgent check": there are no deadlines now.
9. **`vyv-`:** the `/root/dm` daemons stay until the vLLM coordinator agrees. The `vyv-` line below is still needed now:
   `pods create` refuses `vyv-` pods without it, and the guard would treat them as uncovered.

## Initial budgets.toml

The numbers come from `notes.md` at 01:40Z. Please correct any that have moved.

~~~toml
[guard]
project = ["vy"]                      # every vy* pod: vy-, vyv-, vyb...
balance_floor = 25                    # the vyv- balance_floor.py's $25
terminate_uncovered = true            # Daniel, 2026-09-29; set false for the first hour if you want reports only
uncovered_grace_min = 15
exempt = ["vy-control-"]              # vy-control-verity; the guard's own host is exempt anyway

[budgets]
"vyv-" = { cap_usd = 260, expires = "2026-09-30T16:00Z", max_pod_hours = 30, by = "Daniel: vLLM follow-up epoch plan, $260" }
"vy-coord-" = { cap_usd = 65, expires = "2026-09-30T16:00Z", max_pod_hours = 24, by = "check pods; the ~$65/day line awaits Daniel" }
"vy-circuit-checks-" = { cap_usd = 5, expires = "2026-09-29T16:00Z", max_pod_hours = 8, by = "circuit-checks lane pod (vy-circuit-checks-us3)" }
"vy-pous-band-" = { cap_usd = 0.60, expires = "2026-09-29T16:00Z", max_pod_hours = 4, by = "Daniel: POUS band rerun, $0.60" }
"vyb" = { cap_usd = 168, expires = "2026-09-30T16:00Z", max_pod_hours = 24, by = "backend sweep, $82 of $250 spent; drained" }
~~~

- **`vy-coord-` is a placeholder.** The $65/day line is still Daniel's decision; until then, use whatever cap your check pods
  are running under.
- **The PoUW 8192³ lane is done** ($0.22 of $0.30), so it has no line.
- **Check the ages** on the dry run: `max_pod_hours` counts from the pod's `createdAt`. Pods created before #358 have no lease,
  so a line's `max_pod_hours` is their only time bound.
- **Live pods at 03:31Z the lines above don't cover.** Add lines for them, with the caps you approved, before the guard goes
  live, or they'll be terminated 15 minutes after it starts:
  - `vy-check-b61a` ($0.52/h; the determinism lane's check pod);
  - `vy-epoch-check-346` ($0.64/h);
  - `vy-pous-checks` ($0.64/h).

  `vy-circuit-checks-deps` ($0.32/h) falls under `vy-circuit-checks-`.
