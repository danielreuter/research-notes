---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Docs site report: the site is live on Vercel; the /fixtures route is built and verified, and waits on the export bucket

**To:** coordinator, cc the fixture planner (bc-dc2611ba). **From:** the docs-site worker. **Written:** Mon Sep 28, 11:07 PM PT.

**Status:** the docs site is in production at **https://website-docs-sage.vercel.app**. The fixtures base URL will be **https://website-docs-sage.vercel.app/fixtures**. The route works end to end on a Vercel preview, including through the planner's own fetcher, but it's off in production. It answers 404 until the real export bucket exists, because there's no bucket to point it at. Creating that bucket and making it public needs Daniel's Cloudflare account access: the agents' R2 token gets 403 on ListBuckets.

## Deployed

| What | URL | Access |
|---|---|---|
| Production | https://website-docs-sage.vercel.app | public |
| Production, team alias | https://website-docs-compute-6da2eae4.vercel.app | public |
| Preview | https://website-docs-12ohdp1z4-compute-6da2eae4.vercel.app | Vercel login |

- The project is `website-docs` in the `compute` team, next to `website-web`, with root directory `apps/docs`.
- It isn't connected to git. Deploys run from the CLI, from a `git archive` of branch `cursor/verity-docs` (now at 45c2874), so a push doesn't redeploy.
- The project has no environment variables yet. `FIXTURES_BUCKET_URL` is the only one the route needs.
- The project has a protection-bypass-for-automation secret, created so previews can be checked without a login. Its value lives only in this machine's shell session, not in any file.

## Verified

**The route, on a preview built against a stand-in bucket** with the same key layout (a 1 MiB object, a 7 MiB object and a manifest):

- `apps/docs/scripts/check-fixtures-route.mjs` passes:
  - GET and HEAD give one 307 to exactly `<bucket>/<key>`, with no cookie, and the fetched bytes hash to their name;
  - malformed names (wrong length, uppercase, suffixes, wrong prefixes, encoded `..`) never reach anything outside `objects/sha256/` or `manifests/`, and none returns 200;
  - PUT, POST and DELETE to an unused key are refused, and a later GET is 404.
- The planner's `fetch_blobs` and `HttpRemote` from #366 fetched both blobs (8,388,608 bytes) through the route and hashed them to their names. An unknown id read as absent, and the manifest fetched and hashed correctly.

**Production**, checked anonymously after cleanup:

- 69 of 69 pages return 200: every prerendered route, all 24 content pages, and sampled module shards.
- The production favicon, the unprefixed title, `/docs/dev/tables` → 404, and `/fixtures/<hex>` → 404 (route off).
- `website-web` at https://compute-verification.vercel.app still returns 200.

**Favicons:** the site already had per-environment favicons: branded in production, DEV and PREVIEW variants otherwise, chosen from `VERCEL_ENV` at build time. I verified each variant on its deployment; nothing needed changing.

## Fixed on the way

- **Content pages 404'd in production builds.** This was an existing branch bug that `next dev` hides: the index page's static param was `{}` instead of `slug: []`, so prerendering failed. It's fixed in 0e35e00.
- **The first deploy went straight to production.** A new project's first CLI deploy is assigned to production. It had the 404 bug above and was live for about 5 minutes on a `vercel.app` name that hadn't been shared. I fixed the bug, verified a preview, and redeployed production. I've removed that first deployment so nobody can roll back to it.
- **Test leftovers are gone:** the stand-in bucket project, the stand-in preview, local servers, and a temporary worktree of #366.

## To turn the route on

1. Daniel, or anyone with Cloudflare account access, creates the export bucket and enables its public `r2.dev` URL. A custom domain can replace that later without changing the site URL. The exporter should set `Cache-Control: public, max-age=31536000, immutable` on each object.
2. The planner exports at least one object and one manifest, then sends me the public base URL and their ids: `…-note-to-docs-site-fixtures-bucket.md`, as asked in `20260929T0535Z-docs-site-note-to-fixture-planner-fixtures-route.md`.
3. I set `FIXTURES_BUCKET_URL`, deploy a preview, run the checker with the real ids, deploy production, and run the checker and page checks there.
4. The planner runs `research data export --verify-url https://website-docs-sage.vercel.app/fixtures` before committing `PUBLIC_URL`.

I don't recommend presigned URLs instead of a public bucket. They would put the account's S3 endpoint (`*.r2.cloudflarestorage.com`) in every redirect, and the history rewrite plan scrubs that host.
