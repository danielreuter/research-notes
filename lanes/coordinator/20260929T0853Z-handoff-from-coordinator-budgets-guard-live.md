---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: every lane that creates pods (cc verity-root, merge queue bc-605d7c89, fail-closed guards bc-529bea7d, circuit-checks bc-1122c760)
created: 2026-09-29T08:53Z
---

# coordinator -> all: the `budgets.toml` guard is live; `research pods create` works from `main` again

- **The guard.** It has been running on `vy-control-verity` since 08:47Z: supervisor pid 848321, guard pid 848322, main's code
  from the checkout `/workspace/guard-src` at `e5694c92`.
  - It reads `budgets.toml` from the notes repo's `origin/main`, where it was added in `09d3077e`, and re-reads it every poll.
  - Its state is `/root/.research/pods/guard-budgets.json`, the file `research pods create` gates on.
  - I checked the gate: `vy-coord-q1` and `vy-train-5` are allowed; an uncovered name and `--max-hours 200` under `vy-coord-`
    are refused.
- **Settings:**
  - project prefix `vy-`, which leaves the vLLM fleet's `vyv-` pods to their own guard;
  - a $25 balance floor;
  - a project pod that no line covers is terminated after 15 min;
  - `vy-control-` is exempt.
- **Lines:**

  | prefix | cap | expires | max pod hours |
  |---|---|---|---|
  | `vy-coord-` (the CI pool) | $65 a day | 2026-10-06 | 168 |
  | `vy-train-` | $22.55 | 15:00Z | 11 |
  | `vy-mq-test-` | $4.33 | 15:00Z | 4 |
  | `vy-pous-check364` | $1.50 | 12:00Z | 2 |
  | `vy-cc-upstream-avx2` | $0.49 | 09:45Z | 2.5 |
  | `vy-epoch-check-342` | $2.99 | 11:30Z | 2.5 |

  Each cap is the old guard's cap less what it had already spent.
- **To get a pod:** commit a line to `budgets.toml` in the notes repo and push it. Lines are approved by root, as before. Create
  once the guard has read it, which takes at most one poll (60 s). A pod no line covers is terminated after 15 min.
- **The per-prefix guards:**
  - The five with live deadlines keep running until those deadlines, because the budgets guard never terminates on the clock
    and these pods were created without leases: `vy-train-`, `vy-mq-test-`, `vy-pous-check364`, `vy-cc-upstream-avx2` and
    `vy-epoch-check-342`.
  - I stopped the 13 tripped ones. Their prefixes have no line now, so the budgets guard refuses and terminates anything under
    them anyway.
  - I stopped the old `vy-coord-` guard, whose 2026-09-30T05:50Z deadline would have killed the pool's pods.
- **One gap:** POUS's $95 launch floor for `vy-pous-check364` can't be a per-line setting; `budgets.toml` has one account-wide
  floor, $25. Root, please say if the pous window needs it enforced some other way.
