---
id: 20260930T1925Z-handoff-from-console-deploys-until-handover
campaign: verity
lane: docs-site
kind: handoff
status: open
repo: danielreuter/website
origin: console
---

# Console -> docs-site: keep deploying `website-docs` production until your handover file lands; then deploys and `cursor/production-de55` move to console

The top-level ruled this at 19:22Z, consistent with Daniel's 19:10Z and 19:15Z statements (he can override).

- **Until** `lanes/console/*-handoff-from-docs-site-handover.md` is pushed, you're the only one who deploys `website-docs`
  production, as you wrote.
- **After it:** console deploys, and moves `cursor/production-de55` to each deployed commit. Put the exact deploy procedure in the
  handover's §4 (checkout, merge recipe for the live branches, checks, how the branch is moved).
- Thanks for the five copies in the Project store's `private/console/` and the 19:15Z reply. The handover order
  (`20260930T1915Z-handoff-from-console-handover.md`) still stands for the parts the reply didn't cover: branches and worktrees,
  promises owed, the three workers' status, and gotchas.
