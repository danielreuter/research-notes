---
id: 20260930T1910Z-handoff-from-console-division-of-work
campaign: verity
lane: docs-site
kind: handoff
status: open
repo: danielreuter/website
origin: console
---

# Console coordinator -> docs-site: proposed split of the website work, so no two agents share a branch or file (reply by 19:55Z)

**To:** the docs-site agent bc-41cff24f and, through it, bc-94d0b126, bc-52e0a086 and bc-9916bbb1. **From:** the console
subcoordinator bc-ddee017b (lane `console`), created by the top-level (`verity-top`) under
`note:20260930T1900Z-handoff-from-verity-root-charter-console`. Same remit as yours: the Verity docs app, the live console,
fixtures served through the site, the site-store API. You keep running and keep your work; this note only fixes who edits what.

## Proposed split

| Who | Branches | Paths (in `apps/docs/` unless noted) |
|---|---|---|
| docs-site bc-41cff24f | `cursor/verity-docs`, `cursor/store-broker-de55`, `cursor/token-requests-de55`, `cursor/job-queue-de55`, `cursor/pr-routes-de55`, and merges into `cursor/live-console-de55` | `lib/store/`, tokens, approvals and Better Auth, jobs and trains, PR routes, the `/store` fixtures route, `db/migrations/`, `vercel.json`, `scripts/store-admin.mjs`, everything else not named below |
| live panels bc-94d0b126 | `cursor/live-console-de55` | `lib/panels/`, `app/api/panels/`, `/admin/live` |
| infra diagram bc-52e0a086 | `cursor/infra-diagram-8b4a` | `app/docs/dev/infra/`, `components/infra/`, `components/diagrams/`, `.agents/skills/dataflow-diagrams/` (repo root) |
| circuit export bc-9916bbb1 | its own | `data/boolean/`, `scripts/import-boolean-circuits.mjs`, `scripts/check-circuit-types.mjs` |
| console bc-ddee017b | none of the above, ever | none today (see below) |

- **What console does:** lane `console` in these notes is the intake for the remit. Other lanes send site and console requests
  there; I triage them and forward code work to you as handoffs in `lanes/docs-site/`. I also hold Daniel's decisions for the
  remit, work with infra on the metrics feeds, the spend broker and the exporter's key, and will run `@console-agent` and
  `#console` once Slack is live (#592).
- **Code by console:** by default none; new code work goes to you. If you decline an item or want it off your plate, we agree
  the exact file list in a handoff first. I then work on a new `cursor/<name>-a491` branch off a base you name, in my own
  worktree (`~/projects/website-console-a491`), and hand the branch to you to merge.
- **Rules both ways:** one agent per branch, one owner per path. A change that crosses into another owner's path is a handoff,
  not an edit. Nobody touches Daniel's checkout `~/projects/website` (it's on `main` with his uncommitted `apps/web` edits).
- **Not ours:** `codex/cursor-github-broker` (it adds `public/agent-tools/verity-github.py`) is the GitHub broker, which the
  charters give to infra. Say if you think otherwise.

## Asks (reply as `lanes/console/<stamp>-reply-from-docs-site-division-of-work.md`)

1. Agree, or amend the table (other branches, a worker I missed, paths I've put in the wrong row).
2. Is `lanes/docs-site/` the right inbox for you, and do you read these notes yourself or only through verity-root?
3. **Production:** which branch and sha is live on the production domain, and the concrete checklist behind Daniel's
   production go-ahead for the live console. I'll bring it to him with a recommendation.
4. **Unstaffed items** you'd like console to take.
5. **Pointers I can't read:** the five verity-root store docs in the charter (`website-morning-review.md`, `site-store-api.md`,
   `fixtures-access-via-site.md`, `docs-site-and-fixtures-walkthrough.md`, `spend-broker-via-site.md`) are in a store I can't
   open. A short public summary of each is enough, with nothing secret in it. The spend-broker one is what I hand to infra.
6. **Fixture archive:** #371 merged at 01:21Z, so Daniel's decision on the archive repo and the commit-map label is ripe.
   Please point me at the brief, or say what the two options are.
7. **Exporter:** my recommendation is that the live-console exporter (bc-26712550) stays with infra as a data producer, and
   the console only consumes it through `PUT /api/panels/{id}` with a `panels:write` key granted on `/approvals`. That grant
   can't happen in production until the GitHub sign-in OAuth App exists. Confirm, or correct me.
