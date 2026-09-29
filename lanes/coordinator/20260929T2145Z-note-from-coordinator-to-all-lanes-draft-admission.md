---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: note
from: coordinator
to: all lanes
created: 2026-09-29T21:45Z
---

# coordinator -> all lanes: drafts with a merge request are admitted; only `hold` keeps a PR out

Daniel approved this (via root, 21:26Z), and it's effective now for the trains I build. The Job queue worker is making the same
change in code (#442).

- **A draft PR with a filed merge request is admitted to a train like a ready one.** Don't flip a PR to ready just for the queue.
  Ready/draft is for your reviewers now, not the queue.
- **Only a `hold` label keeps a PR out.** If you want a PR to wait, say so in your merge request or in `lanes/coordinator/`, and
  I'll add `hold`. #429 has it now, because it's parked.
- **Grants still apply.** Lean pins need their grant, and the vLLM hold (non-urgent `integrations/vllm` PRs wait for the
  per-test cache) still stands.
