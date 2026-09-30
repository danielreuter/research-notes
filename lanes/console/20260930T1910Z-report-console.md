---
lane: console
kind: report
created: 2026-09-30T19:10Z
status: open
---

CHECKPOINT none (19:26Z) [open] deploys: docs-site until its handover lands, then console (top-level 19:22Z; lanes/docs-site/1925Z); five doc copies received in Project store private/console/; rewrite-window facts asked of fixture-process (lanes/coordinator/1925Z); Daniel's batch sent via top-level
CHECKPOINT none (19:22Z) [open] docs-site replied 19:15Z (to the old split note): live console, prod checklist done, keys verity-panels (bc-94d0b126) and pous-panels already granted and publishing, so no new panels:write request filed; subscribed #agent-coordination (no SLACK_BOT_TOKEN on this VM); handover still due 20:15Z
CHECKPOINT none (19:17Z) [open] Daniel 19:10Z: console owns the remit; handover ordered from docs-site (lanes/docs-site/1915Z, relay via verity-root, due 20:15Z); OAuth App already exists and prod sign-in reaches GitHub, Daniel's one-click test left
CHECKPOINT none (19:10Z) [open] lane created; split proposed to docs-site (lanes/docs-site/1910Z), relay asked of verity-root, metrics feeds and spend broker handed to infra; next: docs-site's reply by 19:55Z, then Daniel's decisions

# console: the console agent's lane

- **Who:** the console agent (Cursor agent bc-ddee017b), created by the top-level (`verity-top`, bc-7f347b4b), running on
  Daniel's laptop. Slack handle `@console-agent` once #592 lands.
- **Charter:** `lanes/verity-top/20260930T1900Z-handoff-from-verity-root-charter-console.md`. Remit: the Verity docs app in the
  website repo (`apps/docs/`), the live console (panels, infra diagram, circuit visualizer), fixtures served through the site, and
  the site-store API.
- **Owner (Daniel, 19:10Z):** console is the single owner of the remit. docs-site (bc-41cff24f) hands over and goes idle; its
  workers bc-94d0b126 (live panels), bc-52e0a086 (infra diagram) and bc-9916bbb1 (circuit export) finish their current tasks and
  report here.
- **Inbox:** `lanes/console/<UTC stamp>-handoff-from-<your lane>.md`, first heading a one-line summary. Send site and console
  requests here.
- **Code:** console's own work goes on new `cursor/<name>-a491` branches in the worktree `~/projects/website-console-a491`. The
  existing branches stay with the workers on them until their tasks finish.

## Sent

- `lanes/docs-site/20260930T1915Z-handoff-from-console-handover.md`: the handover order (branches, notes copies of the five
  verity-root site docs, production checklist, deploys and ops, promises owed, workers, gotchas), due 20:15Z. It supersedes
  `lanes/docs-site/20260930T1910Z-handoff-from-console-division-of-work.md`.
- `lanes/verity-root/20260930T1915Z-handoff-from-console-relay-handover.md`: forward it to bc-41cff24f (supersedes the 19:10Z relay).
- `lanes/flock-ir-lowering/20260930T1915Z-handoff-from-console-new-owner.md`: bc-9916bbb1 reports to console.
- `lanes/infra/20260930T1910Z-handoff-from-console-metrics-feeds-and-spend-broker.md`: metrics feeds, exporter, spend broker.

## GitHub sign-in OAuth App (Daniel approved 19:10Z)

- Already in place: `GITHUB_SIGNIN_CLIENT_ID` and `GITHUB_SIGNIN_CLIENT_SECRET` are set for Production on the Vercel project
  `website-docs` (about 17:10Z), and the production deployments are newer than them.
- Checked 19:15Z: production's "Sign in with GitHub" on `/approvals` redirects to GitHub's authorize page with
  `redirect_uri=https://website-docs-sage.vercel.app/api/auth/callback/github`, and GitHub accepts the client id.
- Left: Daniel signs in once. That's the only check of the registered callback URL and the secret.

## Daniel's decisions for this remit

- Production go-ahead for the live console: waiting on docs-site's checklist.
- Fixture archive repo and commit-map label: ripe, #371 merged 01:21Z; waiting on the brief.
