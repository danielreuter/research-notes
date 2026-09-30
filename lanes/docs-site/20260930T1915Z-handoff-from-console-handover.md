---
id: 20260930T1915Z-handoff-from-console-handover
campaign: verity
lane: docs-site
kind: handoff
status: open
repo: danielreuter/website
origin: console
supersedes: 20260930T1910Z-handoff-from-console-division-of-work
---

# Console -> docs-site: Daniel is moving your remit to the console agent; please hand over your state by 20:15Z, then stop taking work and go idle

**Daniel's ruling (19:10Z, through the top-level):** the console agent bc-ddee017b (lane `console`) becomes the single owner of
the website remit: the Verity docs app, the live console, fixtures served through the site, and the site-store API. Agents can't
be reparented, so you hand over through notes. This note replaces the 19:10Z division-of-work proposal.

## 1. Write the handover (one file, due 20:15Z)

Write it as `lanes/console/<stamp>-handoff-from-docs-site-handover.md`, with these sections:

1. **Branches:** every website branch you or your workers own, plus any verity branches or PRs. For each: the tip sha, what's on
   it, whether it's merged into `cursor/live-console-de55` or deployed, and what's unfinished. The ones I know about:
   `cursor/live-console-de55`, `cursor/job-queue-de55`, `cursor/pr-routes-de55`, `cursor/store-broker-de55`,
   `cursor/token-requests-de55`, `cursor/verity-docs` and `cursor/infra-diagram-8b4a`. Commit and push any uncommitted work first,
   and name each worktree you used (`~/projects/website-verity-docs`, `~/projects/website-infra-diagram`, `/private/tmp/infra-view`)
   and whether it can go.
2. **The five verity-root store docs as notes copies,** one file each, named
   `lanes/console/<stamp>-copy-from-docs-site-<doc>.md`: `website-morning-review`, `site-store-api`, `fixtures-access-via-site`,
   `docs-site-and-fixtures-walkthrough`, `spend-broker-via-site`. The notes repo is public: leave out tokens, keys, private URLs
   and bypass values. Put anything sensitive that I'll need in the Project store's `private/console/` folder at
   `/Users/danielreuter/Library/Application Support/Cursor/AgentStores/cursor_agent_stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/files/private/console/`,
   and name it in the copy only by path.
3. **Production checklist** behind Daniel's go-ahead for the live console: what's done and what's left, one line each.
4. **Deploys and ops:** how production is deployed today (the Vercel project `website-docs` is deployed as danielreuter; from which
   branch and checkout?), crons, and anything else running, such as `verity-console.timer` on vy-nebius-1.
   Also: who created the GitHub sign-in OAuth App whose variables were set about 17:00Z, and which callback URL it registered.
5. **Promises owed:** to whom, what, and by when; open requests from other lanes.
6. **Your three workers:** for bc-94d0b126 (live panels), bc-52e0a086 (infra diagram) and bc-9916bbb1 (circuit export), give
   the current task, branch, what "done" is, and when it should end. Say if you'd stop any of them now.
7. **Gotchas** the next owner would lose: anything you know that isn't written down.

## 2. Then

- **Stop taking new work.** Point anyone who asks at `lanes/console/`, or at `@console-agent` once Slack is live.
- **Tell your three workers,** in one follow-up each: send results and questions to `lanes/console/`, finish the current task,
  write a closing note there, and take new work only from console.
- **Go idle:** end with a last checkpoint that points at your handover file. Don't delete branches or worktrees; console decides.
