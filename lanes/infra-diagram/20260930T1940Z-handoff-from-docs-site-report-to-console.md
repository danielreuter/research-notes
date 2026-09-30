---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
id: 20260930T1940Z-handoff-from-docs-site-report-to-console
campaign: verity
lane: infra-diagram
kind: handoff
status: open
repo: danielreuter/website
origin: docs-site
---

# Docs-site -> infra-diagram: the website remit is now console's (bc-ddee017b); report to lanes/console/ from now on

**To:** bc-52e0a086-df9d-55c2-8dce-f6c32ba68b4a (the infra diagram agent). **From:** the docs-site worker bc-41cff24f, which has handed its website remit to console and is
going idle (Daniel, 19:10Z). The handover: `lanes/console/20260930T1935Z-handoff-from-docs-site-handover.md`.

- Send results and questions to `lanes/console/`, not to docs-site.
- Finish your current task, then write a closing note in `lanes/console/`.
- Take new work only from console.
- `cursor/infra-diagram-8b4a` @ `dfa10b2` isn't merged or deployed yet. To go live, rebase or merge it onto `cursor/production-de55` in your own worktree, and hand console the branch and sha. Console deploys production.
