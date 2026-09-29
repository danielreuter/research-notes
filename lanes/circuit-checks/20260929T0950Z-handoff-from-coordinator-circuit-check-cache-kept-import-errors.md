---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: circuit-checks
kind: handoff
from: coordinator
created: 2026-09-29T09:50Z
---

# coordinator -> circuit-checks: the circuit-check cache reused an ImportError result on a different tree

**What happened:**

1. On `vy-train-3`, a check of `29787e50` ran with a broken source directory. A stale run sharing the pod had changed files
   under it.
2. Its `circuit-check` targets failed with `ImportError`, for example:

   ~~~text
   cannot import name 'lowerings' from 'verity_numerical.bench' (/workspace/research/src/29787e50.../backends/numerical/python/verity_numerical/bench/__init__.py)
   ~~~

3. The next check on that pod, `r20260929-093924-b0b3`, was of a different commit, `26d506d6`, whose files are all correct.
   It finished `circuit-check` in 26.7 s with the same errors, still naming the old `29787e50` paths. The cached results were
   reused.

**What I did:** I moved the pod's cache aside to `~/.cache/verity-check/circuit-check.poisoned-0947Z`, 37 MB, kept for you to
inspect, and re-ran as `r20260929-094710-3c7d`.

**Please look at two things:**

- a target that errors, as opposed to one that fails its check, probably shouldn't be cached;
- the reads a cached result depends on may need to include the source root it ran from.
