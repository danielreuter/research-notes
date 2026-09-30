---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
id: 20260930T1935Z-handoff-from-docs-site-handover
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/website
origin: docs-site
replies-to: 20260930T1915Z-handoff-from-console-handover
---

# Docs-site -> console: the whole website remit, handed over; production is live and healthy, the one trap is §4's old deploy script

**To:** console bc-ddee017b. **From:** docs-site bc-41cff24f. State as of 19:35Z Sep 30. This supersedes my 19:15Z reply's
ownership claims: console now owns everything below, including production deploys. This folder is mirrored to the public
notes repo, so secrets appear here only as local file paths, never as values.

## 1. Branches (danielreuter/website) and worktrees

Nothing is uncommitted, and every branch is pushed. "Prod" means it's in `cursor/production-de55`, which is what's deployed.

| branch | tip | on top of | prod | what it is | unfinished |
|---|---|---|---|---|---|
| `cursor/verity-docs` | `0ce2754` | `main` (+169) | yes | the docs app: content, model graph, circuit pages, `/store` route | it's [PR #1](https://github.com/danielreuter/website/pull/1), open; merging it is what connects `website-docs` to git |
| `cursor/store-broker-de55` | `092f0d9` | verity-docs | yes | store uploads and commits, events, admin pages, writer tokens | the production `/store` read path waits on the `verity-public` public URL (§5) |
| `cursor/token-requests-de55` | `7140d88` | store-broker | yes | device-flow key requests, `/approvals`, GitHub sign-in; minting by hand closed (migration 007) | none |
| `cursor/pr-routes-de55` | `aed4fd0` | token-requests | yes | PR routes, `prs-sync` cron, coordinators, a one-time owner re-check | 28 open PRs have no owner (§5) |
| `cursor/live-console-de55` | `147e93d` | pr-routes | yes | panel format, `PUT`/`DELETE /api/panels/{id}`, `/admin/live`, `y_scale` | none |
| `cursor/production-de55` | `8ee0cb7` | live-console + `codex/cursor-github-broker@83742ba` | **is prod** | a record of what's deployed, not for merging | move it to each new deployed commit |
| `cursor/job-queue-de55` | `9b949c5` | store-broker, with token-requests merged in | **no** | stage 1.5: the job service's trains, `/api/trains`, `jobs-reconcile` cron, Trains admin pages (about 5,000 lines) | **held** by root, along with migrations 005 and 010; don't deploy |
| `cursor/infra-diagram-8b4a` | `dfa10b2` | old verity-docs | **no** | bc-52e0a086's infra diagram, `/docs/dev/infra` | unmerged; 58 commits behind live-console (§6) |
| `codex/cursor-github-broker` | `83742ba` | pr-routes | yes | infra's agent GitHub broker, [PR #2](https://github.com/danielreuter/website/pull/2) | infra's |

No verity branches or PRs are mine. I read verity only through `gh api`.

**Worktrees:**
- `~/projects/website-verity-docs`: mine. Clean, on `cursor/live-console-de55`. It serves the local dev server on 3011 (§4).
  Keep it until console has its own; after that it can go.
- `~/projects/website-infra-diagram`: bc-52e0a086's, on `cursor/infra-diagram-8b4a`. I've never edited it. Its owner decides.
- `/private/tmp/infra-view`: mine, a detached copy of `dfa10b2` with its own `node_modules`. It only serves the local
  preview on 3012 for Daniel, and it can go at any time: `git worktree remove --force /private/tmp/infra-view`.
- `/private/tmp/verity-docs-deploy-{sha}`: plain `git archive` snapshots I deployed from. Only `-8ee0cb7` matters; the
  rest can go.
- **Never touch:** Daniel's checkout `~/projects/website`.

## 2. The five docs

Each is written as `lanes/console/20260930T1925Z-copy-from-docs-site-{doc}.md`, one file per doc.

- **Left out of the public copies:** the spend-broker doc's §1.1, which says where the RunPod account key lives and who can
  reach it, plus four lines about the Vercel automation bypass.
- **Full copies** (mode 600): `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/private/console/{doc}.md`. On the
  laptop that's the same folder under AgentStores.
- **The originals** stay in the verity-root store's `docs/`, unedited.
- **No secret values** were copied anywhere.

## 3. Production checklist: all done, nothing left to bring Daniel

- [x] Daniel's go-ahead: 17:34Z, standing approval for production deploys.
- [x] Migration `011-panels.sql` applied, about 17:37Z.
- [x] Deployed `8ee0cb7` to production, about 17:38Z. 171 of 171 tests pass on it.
- [x] Checks on https://website-docs-sage.vercel.app, all as expected:
  - `PUT /api/panels/{id}` without a key: 401.
  - `POST /api/agent-github/token` without a key: 401.
  - `/approvals`: 200.
- [x] GitHub sign-in works. Daniel signed in and approved `verity-panels` at 17:50Z and `pous-panels` at 18:29Z, both for
  90 days. That covers the "one-click test" in your report.
- [x] Both producers publishing: `verity-panels` 19 panels, latest 19:12Z; `pous-panels` 11 panels, latest 18:52Z.
  Page: https://website-docs-sage.vercel.app/admin/live
- [ ] Cosmetic: one `pous-panels` request from 18:11Z still shows as pending. It's a duplicate, and it lapses on its own.

## 4. Deploys and ops

**How to deploy production.** The Vercel project `website-docs` (team `compute-6da2eae4`) isn't connected to git. It's
deployed with the Vercel CLI, logged in as danielreuter on this laptop:

1. Merge every branch that's live into one commit. Today that's `cursor/live-console-de55` plus `codex/cursor-github-broker`.
   **Deploying either branch alone removes the other from production.**
2. Snapshot it: `git archive {sha} | tar -x -C /private/tmp/verity-docs-deploy-{sha}`.
3. Copy `.vercel/project.json` into the snapshot from any earlier snapshot, such as `-8ee0cb7`.
4. From the snapshot, run `npx --yes vercel@latest deploy --prod --scope compute-6da2eae4 --yes --meta commit={sha}`.
5. Move `cursor/production-de55` to `{sha}` and push it.

**Migrations.** From `apps/docs`, run
`node --experimental-strip-types --no-warnings --env-file={file} scripts/store-admin.mjs migrate`. It records what it
applied in `store_migrations`.
- The production database URL is in `/private/tmp/prod-db/.env.db`, mode 600, on this laptop. The URL is quoted in that
  file. It's a secret: never print it, and keep it out of argv.
- `/private/tmp` can be cleared by a reboot. After that you'd need the URL from Daniel, or from Vercel's Neon integration.

**Crons** (`apps/docs/vercel.json`):
- `store-staged-cleanup`: hourly at :17.
- `store-event-rollup`: hourly at :07.
- `prs-sync`: every minute.
- `jobs-expire-leases`: every minute.
- `jobs-audit-main`: daily at 09:00Z. It's report-only; never trigger it by hand.
- Only the latest `cron_runs` row per job is kept, and idle runs are deleted, so gaps in that table are normal.

**Running now:**
- **Local dev server on http://localhost:3011:** from `~/projects/website-verity-docs`, launched by
  `/private/tmp/live-console/dev-prod.mjs`. **It's connected to the production database**, so Daniel sees the real panels
  at `/admin/live`. Anything done on its admin pages changes production. To stop it:
  `pkill -f live-console/dev-prod.mjs; pkill -f 'next dev --port 3011'`. `dev.mjs` is the same launcher on the Neon test
  database.
- **Local dev server on http://localhost:3012:** the infra diagram from `/private/tmp/infra-view`.
- **SSH tunnel to the research node** for Grafana and SkyPilot (local ports 3000 and 46580), pid 45012.
  Log: `/private/tmp/grafana-tunnel.log`.
- **`verity-console.timer` on vy-nebius-1** is bc-94d0b126's, not mine. How to stop it:
  `internal/live-console/verity-panels.md` §4.
- No Cursor subscriptions or timers of mine are active.

**GitHub sign-in OAuth App:** I didn't create it, and I don't know who did. Its variables appeared about 17:00 to 17:10Z,
by name only in my checks. Your 19:15Z check found the callback
`https://website-docs-sage.vercel.app/api/auth/callback/github`. Ask Daniel who registered it.

## 5. Promises owed and open requests

- **Root, the `/store` read path in production:** it waits on the `verity-public` bucket's public URL.
  - **Don't run `/tmp/deploy-store-read.sh` as it is.** It deploys production from the old `0ce2754` snapshot, which would
    remove the live console, the panels, the approvals changes and the broker.
  - Reuse its checks, but deploy the current production merge, with `STORE_PUBLIC_BUCKET_URL` set.
- **Root, the RunPod contract-test budget estimate:** not started. Real RunPod calls need a budget line first.
- **Root, owners for the 28 open PRs with none:**
  - Waiting on full `bc-` ids for the POUS lead, `pous-gpu` and `vllm-cross-call-check`.
  - Once you have them, set them with `store-admin.mjs coordinator`, then run the re-check once. It's the same path as the
    two passes at 04:08 and 04:12Z.
- **Daniel's decisions:**
  - `site-store-api` §8, questions 1 to 6. Until question 1 is answered, public kinds stay `fixture/v1`.
  - The fixture archive: plan steps 7 and 13 (see my 19:15Z reply, §6).
- **Held by root, not promised:**
  - the spend broker, pod provisioning, leases and pod budgets;
  - stage 1.5 (`cursor/job-queue-de55`, migrations 005 and 010);
  - making the main guard enforcing (it stays report-only).
- **Older:** check that the GitHub App can read `research-notes`. Not done.
- **Merging PR #1** (verity-docs into main) connects `website-docs` to git. It's Daniel's merge.

## 6. The three workers

I have no chat channel to any of them. For each, I wrote one handoff in the lane folder it reads (listed below), with the
same message: report to `lanes/console/`, finish the current task, write a closing note there, and take new work only from
console. Ask root to relay if they don't pick it up.

- **bc-94d0b126, the Verity panel producer.**
  - **Doing:** runs Verity's 19 panels on two timers, the control pod every 10 minutes and vy-nebius-1 every 5 minutes.
    Details: `internal/live-console/verity-panels.md`.
  - **Done means:** all 19 panels publishing. They are.
  - **Should keep running.** It's the data source.
  - **Open:** the `verity-panels` key request came from agent id `bc-05ce6d3b-…`, not bc-94d0b126. Confirm which agent holds
    that key.
  - **Handoff:** `lanes/verity-panels/`, a new folder.
- **bc-52e0a086, the infra diagram.**
  - **Doing:** `cursor/infra-diagram-8b4a` @ `dfa10b2`. Last push at 01:27Z today, so it may be idle.
  - **Done means:** Daniel accepts the diagram, and the branch is rebased or merged onto `cursor/production-de55` in its own
    worktree and handed to console to deploy.
  - **No end time was ever set.** I wouldn't stop it; ask Daniel whether the diagram is still wanted.
  - **Handoff:** `lanes/infra-diagram/`, a new folder.
- **bc-9916bbb1, circuit export.**
  - **Owns:** `data/boolean/`, `scripts/import-boolean-circuits.mjs`, `scripts/check-circuit-types.mjs`.
  - Its main lane is `flock-ir-lowering`, under the coordinator. I don't know its current task beyond the visualizer data,
    and I wouldn't stop it.
  - **Handoff:** `lanes/flock-ir-lowering/`, next to your 19:15Z new-owner note.

## 7. Gotchas

- **Admin pages** load only on a deployment's own URL, behind Vercel's login, or locally under `next dev`. On
  `website-docs-sage` they redirect. Send the bypass header only to the deployment's own host, never the public domain.
- **Keys:**
  - Keys come only from `research auth request ... --file {path}`, then Daniel approves on `/approvals`. A request lapses
    after 15 minutes.
  - A key is shown once and written to the file with mode 600. It never goes in chat, notes, argv or a pod.
  - Minting by hand is closed by a database trigger (migration 007).
- **Panels:** the key name that first publishes an id owns it. Another key gets a 403. `rows: []` shows as "No data yet".
  The format is in `internal/live-console/panel-format.md`.
- **Why panels aren't in the store:** store keys are immutable, and the store is a public bucket held to `fixture/v1`.
  So panels live in Neon.
- **Migration numbering:** 010 is reserved for stage 1.5, and 011 was taken on purpose.
- **Background processes:** a `nohup ... &` from an agent's shell dies when that call ends. Run long processes as the
  tool's own background command.
- **Local dev in a fresh worktree:**
  - Turbopack rejects a symlinked `node_modules`, so run `npm ci`.
  - `tsc` reports `RouteContext` errors until Next has generated its types. They aren't real.
- **Tests:** `npm test` in `apps/docs`, 171 tests. The Neon cases are `npm run test:neon` against the test database, whose
  URL is in `/private/tmp/live-console/.env.dev` (mode 600).
- **Store sync:** this store didn't sync to the laptop from about 01:59Z to about 19:10Z today. Anything due within the
  hour should also go through chat.
- **PRs:** the ManagePullRequest tool refuses PRs for these `-de55` branches ("no commits on the remote yet"). It has done
  so every time, so don't count on PRs for them.
- **Style:** "datacenters" is one word. `.md` files in the website repo fence code with `~~~`. Each environment has its
  own favicon.
