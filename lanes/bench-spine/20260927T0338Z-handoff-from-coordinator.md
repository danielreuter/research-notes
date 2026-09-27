---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: bench-spine · kind: handoff · from: coordinator · created: 2026-09-27T03:38Z

# Take flock-backend's placement-probe fix onto main as a PR for the next train after #100

- **The fix:** flock-backend's `placement.probe` fix is at cursor/flock-backend-4983 @ 852816d6. It reads `RUNPOD_*` from
  `/proc/1/environ` when the job's environment lacks them (an ssh-started job), with a test.
- **Why it matters:** without it, `register` refuses every cell because pod_id is null.
- **Please:** open a PR for it on main, with `bench.cell` / `placement` tests. It joins the next train after #100, through
  `check` and `research merge`.
- **Doesn't wait on it:** flock-backend's re-run goes ahead from its branch, and the registered cells record the commit.
