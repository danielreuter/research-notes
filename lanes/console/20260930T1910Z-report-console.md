---
lane: console
kind: report
created: 2026-09-30T19:10Z
status: open
---

CHECKPOINT none (19:10Z) [open] lane created; split proposed to docs-site (lanes/docs-site/1910Z), relay asked of verity-root, metrics feeds and spend broker handed to infra; next: docs-site's reply by 19:55Z, then Daniel's decisions

# console: the console subcoordinator's lane

- **Who:** the console subcoordinator (Cursor agent bc-ddee017b), created by the top-level (`verity-top`, bc-7f347b4b), running on
  Daniel's laptop. Slack handle `@console-agent` once #592 lands.
- **Charter:** `lanes/verity-top/20260930T1900Z-handoff-from-verity-root-charter-console.md`. Remit: the Verity docs app in the
  website repo (`apps/docs/`), the live console (panels, infra diagram, circuit visualizer), fixtures served through the site, and
  the site-store API.
- **Inbox:** `lanes/console/<UTC stamp>-handoff-from-<your lane>.md`, first heading a one-line summary. Send site and console
  requests here; code work is forwarded to docs-site (bc-41cff24f) unless agreed otherwise.
- **Code:** none of the existing website branches. Any console code goes on new `cursor/<name>-a491` branches, in the worktree
  `~/projects/website-console-a491`, only after the file list is agreed with docs-site.

## Sent

- `lanes/docs-site/20260930T1910Z-handoff-from-console-division-of-work.md`: the split, and seven asks (production state and
  checklist, unstaffed items, public summaries of verity-root's five site docs, the fixture-archive brief, the exporter).
- `lanes/verity-root/20260930T1910Z-handoff-from-console-relay-to-docs-site.md`: forward that to bc-41cff24f.
- `lanes/infra/20260930T1910Z-handoff-from-console-metrics-feeds-and-spend-broker.md`: metrics feeds, exporter, spend broker.

## Daniel's decisions for this remit

- Production go-ahead for the live console: waiting on docs-site's checklist.
- GitHub sign-in OAuth App for producer keys: no production grant (the exporter's `panels:write` key included) is possible without it.
- Fixture archive repo and commit-map label: ripe, #371 merged 01:21Z; waiting on the brief.
