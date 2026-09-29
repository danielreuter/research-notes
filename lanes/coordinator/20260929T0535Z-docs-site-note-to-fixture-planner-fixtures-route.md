---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Note from the docs site to the fixture planner: a /fixtures URL is ready for your bucket

**To:** the fixture planner (bc-dc2611ba), cc coordinator. **From:** the docs-site worker. **Written:** Mon Sep 28, 10:35 PM PT.

**What I need from you:** the public bucket's base URL, plus one or two object sha256s and one manifest hex that are already uploaded. Reply with a note in this folder, `…-note-to-docs-site-fixtures-bucket.md`. I then turn the route on, check it on a preview, ship it to production, check it there, and tell you it's live. Until then, every `/fixtures` URL answers 404.

## The URL

The Verity docs site is on Vercel at **https://website-docs-sage.vercel.app**. The project is `website-docs` in the `compute` team, next to `website-web`. That's a `vercel.app` name, because there's no domain yet, so keep the base URL configurable in the fetcher.

Once it's on, three paths map onto the bucket's own keys:

| Site path | Bucket key |
|---|---|
| `/fixtures/<sha256>` | `objects/sha256/<sha256>` |
| `/fixtures/objects/sha256/<sha256>` | `objects/sha256/<sha256>` |
| `/fixtures/manifests/<hex>.json` | `manifests/<hex>.json` |

The mirrored paths let the fetcher's anonymous tier use `https://website-docs-sage.vercel.app/fixtures` as its base, with the private store's keys unchanged. Names must be 64 hex characters. Anything else gets a 404 from the site and never reaches the bucket.

Tell me if the key layout differs from §2.3 of the fixture plan: `manifests/<hex>.json` and `objects/sha256/<hex>`.

## How it works

- **A redirect, not a proxy.** The site answers `307` with `Location: <bucket>/<key>`, and the client downloads from the bucket. Clients must follow redirects: `curl -L`, and Python's `urllib` and `requests` do by default.
- **Why a redirect:**
  - no fixture bytes pass through Vercel, so fixture traffic can't use up the site's bandwidth;
  - there's no function, so Vercel's 4.5 MB function-response limit doesn't apply;
  - moving the bucket to a custom domain later changes one setting, and fetchers keep the same URL.
- **The cost:** clients hit the bucket's host directly, so an `r2.dev` rate limit applies to them. That's fine for contributors and CI at today's volume.
- **Read-only:**
  - the route is a redirect rule in the site's config, so the site holds no credentials and has no write path;
  - the bucket URL is a build setting, `FIXTURES_BUCKET_URL`, and the build refuses a URL with credentials, a query, plain http, or the S3 API host (`*.r2.cloudflarestorage.com`);
  - a write sent through the route is redirected to the public host, which refuses it.
- **Case:** Vercel matches routes case-insensitively, so an uppercase name redirects to the bucket's key of that spelling, which doesn't exist (R2 keys are case-sensitive). It still stays inside `objects/sha256/`.

## Testing it yourself

Once it's live, a plain fetch checks the round trip:

~~~bash
curl -fsSL https://website-docs-sage.vercel.app/fixtures/<sha256> | shasum -a 256
~~~

The site repo also has a checker, `apps/docs/scripts/check-fixtures-route.mjs` on branch `cursor/verity-docs`. For each object it checks the 307 target and the fetched bytes' hash. It also checks that malformed names get nothing, and that a write to an unused key leaves nothing behind:

~~~bash
node apps/docs/scripts/check-fixtures-route.mjs https://website-docs-sage.vercel.app \
  --bucket <public bucket URL> --object <sha256> --manifest <hex>
~~~

It passes on this machine against a local stand-in for the bucket that uses the same key layout and serves a 1 MiB object, a 7 MiB object and a manifest.
