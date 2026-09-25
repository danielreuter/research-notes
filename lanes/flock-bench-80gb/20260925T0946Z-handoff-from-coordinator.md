---
lane: flock-bench-80gb
kind: handoff
from: coordinator
created: 2026-09-25T09:46Z
---

# Laptop disk at 2.6 GiB: no laptop downloads, builds or new worktrees until further notice

The laptop is below the 3 GiB stop line (Daniel's rule), and it lost 1.3 GiB in 20 minutes. Until I lift this:
- Don't `research fetch` / `data fetch` run outputs or proofs to the laptop. Verify, inspect and diff on your pod, and
  keep evidence in R2 (`data put --preserve` from the pod side, or `--custody-r2`).
- Create no new worktrees or scratch checkouts on the laptop, and no local cargo/pytest/uv builds. Reuse what you have, or
  work on the pod.
- If you already pulled something big (for example 100 MB proof files in `~/.research/store/objects` or `~/.research/runs`),
  say so in your next checkpoint, with the run or artifact id, so I can check it against R2 and evict it.
Everything else continues as planned on pods.
