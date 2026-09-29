---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Docs site report: the Scheduler's batch jobs, stage 1, is in production

**To:** coordinator, cc the merge-queue lane (bc-605d7c89). **From:** the docs-site worker. **Written:** Tue Sep 29, 3:45 PM PT.

**Status:** stage 1 of [the site spec](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/job-service-site-spec.md) is live, including changes 1–4 and 6–8. The 17 shared job cases (`84eb3d11…`, from verity#442 at `d7272158`) pass on PGlite and on Neon. Migration 004 ran in production after preview passed. The GitHub App check in production is **ok**. What's left is two tokens that Daniel mints himself (below).

## Deployed

| What | Deployment | URL |
|---|---|---|
| Production | `dpl_GBtqXXgnn7LSiuCM16UHnG6GBe3M` (commit `90591a4`) | https://website-docs-sage.vercel.app |
| Production, own URL (admin, Vercel login) | same | https://website-docs-ocg8bq38j-compute-6da2eae4.vercel.app/admin/jobs |
| Preview it was verified on | `dpl_7UehJmVgP13YgbhPC97WJUa27ssE` (same commit) | https://website-docs-dudm9yjad-compute-6da2eae4.vercel.app |
| Rollback target | `dpl_2C3m4qQHLxuPR2SxdWhfN24AjpeX` | the store-crons production from earlier today |

- The API base URL for `research jobs` and the dispatcher is `https://website-docs-sage.vercel.app` (the tools' default; `$JOBS_URL` overrides it).
- `/admin` on the public domain redirects to the deployment's own URL, which Vercel's login protects.
- Branch `cursor/job-queue-de55` in the website repo, pushed at `90591a4`.

## Verified

- **The shared cases:** `npm test` passes 107 of 107 on PGlite, and `npm run test:neon` passes 54 of 54 against a Neon test database. Both runs include the 17 job cases and the concurrent claim and add tests.
- **Preview over HTTP:** 24 of 24 checks passed. They cover:
  - auth: 401 with no token, 403 for a wrong scope;
  - add, dedupe, claim, renew, complete and cancel, with a wrong or finished lease answering 409;
  - `line: "vy-coord-"` round-trips in the job's view, while a malformed line and `lease_s` 3601 answer 400;
  - a 60 s lease that the expire-leases cron puts back in the queue;
  - the admin pages.
- **Production:**
  - The migration applied cleanly after a snapshot, and was purely additive. It creates four new tables and one function, and adds a defaulted column to `cron_runs`.
  - `vercel crons ls` shows four crons: `jobs-expire-leases` (every minute), `jobs-audit-main` (`0 9 * * *`), and the two store crons.
  - `jobs-expire-leases` runs ok every minute on the new deployment.
  - Without a token, `/api/jobs`, `/api/events` and `POST /api/jobs/claim` answer 401.
  - `/admin/jobs`, `/admin/tokens`, `/admin` and `/admin/store` render.
  - No scratch jobs were added.
- **GitHub App:** `GITHUB_APP_ID`, `GITHUB_APP_INSTALLATION_ID` and `GITHUB_APP_PRIVATE_KEY` are present in Production (checked by name only), and this deployment picked them up. The admin page's "Check the App" button mints an installation token server-side, reads the repository and `main`, and revokes the token. It came back **ok**. The token is never logged or shown.
- **`jobs-audit-main`** wasn't triggered by hand in production. Its first run is the scheduled one at 09:00 UTC tomorrow, and it will add one `audit-main` job for `main`'s tip.

## The tokens: Daniel mints both on `/admin/tokens`

The worker row `dispatch:rc` is already in production:
- kind `dispatcher`;
- token `dispatch-rc`;
- kinds `merge-check`, `lean-regen` and `audit-main`.

It can't claim until its token exists. Neither token name is taken in production.

| Name | Tick on the form | Where the value goes |
|---|---|---|
| `coordinator` | `jobs:enqueue` and `events:read` (no store kinds) | the RC's `JOBS_TOKEN` |
| `dispatch-rc` | `jobs:work` only | `~/.research/jobs/token`, mode 600, on the RC's VM |

- Daniel opens https://website-docs-sage.vercel.app/admin/tokens, which forwards to the deployment's admin.
- The form shows each value once.
- Neither value goes into chat, notes, an argv or a pod (spec §8).

## Where the site differs from the spec

None of these changes the API's answers. The cases pass as written.

1. **Cron paths.** The expire-leases cron is `/api/cron/jobs-expire-leases`, not `/api/jobs/cron/expire`; the site's crons all live under `/api/cron/{job}`. The nightly audit is `/api/cron/jobs-audit-main`.
2. **`workers.token_name` isn't a foreign key.** `tokens.name` is unique only among live tokens, since a revoked name can be minted again. The column has a shape check instead, and the claim compares it with the calling token's name.
3. **Scopes live in `tokens.actions`**, a `text[]` that also holds the store's `write`.
4. **Stricter bodies.** `slot`, `run_id` and `summary` must be strings, and a body that isn't a JSON object answers 400.
5. **No INSERT- and SELECT-only grants on `events`.** The app connects as the database owner, so the `events_append_only` trigger is what enforces append-only.
6. **Test database, not branch.** The Neon tests run against a separate database on the preview host, because there's no Neon API key to cut branches. §2's "Neon preview branching is already on" isn't accurate: all previews share one database.
7. **Run ids aren't links.** The site has no store run page yet.
8. **The table is `events`,** which was free.
9. **Two stale lines in the spec:**
   - §1's "left for later" table still puts the nightly `audit-main` at stage 4;
   - §8 step 3 still says 15 cases.

## Next

- **Stage 1.5 (§9):** the trains table, the `trains:write` scope, the three routes, the reconcile cron with the ported gate (its main guard report-only), `/admin/trains`, and the 9 train cases (`a71238b4…`, `d7272158`). Preview first; I'll report before its production migration.
- **The first job:** once both tokens are in place, the merge-queue lane runs it with the RC's agreement (spec §8 step 8).
