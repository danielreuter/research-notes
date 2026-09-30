---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
id: 20260930T1925Z-copy-from-docs-site-docs-site-and-fixtures-walkthrough
campaign: verity
lane: console
kind: copy
status: final
repo: danielreuter/website
origin: docs-site
---

> **Public copy** of the docs-site worker's `docs/docs-site-and-fixtures-walkthrough.md` in the verity-root store, made 20260930T1925Z for the console handover.
> The original is unchanged and was not edited after this copy. Nothing was left out. Full copy, private: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/private/console/docs-site-and-fixtures-walkthrough.md`.


# The docs site and the store's public route: a walkthrough

**For:** Daniel. **Written:** Tue Sep 29, 7:40 AM PT, by the docs-site worker. **Updated** 8:05 AM PT with a link to the site-broker proposal, and 9:55 AM PT for the rename: the route is now `/store`, for the evidence store's public half, and the bucket is `verity-public`. Fixtures are the first thing it serves. The test results in §3 are for the same code under its old name, `/fixtures`, and the renamed code passed the same checks locally.

**In short:** Verity's documentation site is live at **https://website-docs-sage.vercel.app**. It also has a `/store` route, the evidence store's public half, so that anyone can download Verity's public artifacts without keys, starting with its test fixtures. The route passed every test on a preview, against a stand-in bucket. It stays off in production until there's a real bucket behind it, and only you can create that bucket in Cloudflare (§4).

## 1. The site

**What it is.** The public documentation for Verity. It covers:
- **the overview:** how the layers compose;
- **the reference sections:** core, protocols, backends, integrations and assumptions;
- **the census:** hardware, models, workloads, served configs, proof units and networks;
- **autoresearch.**

The Models page has the interactive model graph. It draws each served config's Program, and you can open any part of it down to its gates.

![The docs site's overview page, live in production](verity-root store: media/docs-site-live-home.png)

![The model graph on the Models page, live in production](verity-root store: media/docs-site-live-model-graph.png)

**Where it lives:**
- **Code:** `apps/docs` in the `danielreuter/website` repo, on branch `cursor/verity-docs`. That branch is [website PR #1](https://github.com/danielreuter/website/pull/1), not merged yet.
- **Hosting:** the Vercel project `website-docs`, in the compute team, next to the existing `website-web`.
- **URL:** https://website-docs-sage.vercel.app. It's a `vercel.app` name because there's no domain yet.

**How it's deployed.** From the command line, using a snapshot of the branch. The project isn't connected to git, so a push doesn't redeploy. Each change goes to a preview first. It's checked there, then deployed to production and checked again. The checks load 69 pages: every prerendered page, all 24 content pages, and a sample of the model graph's data files.

**Per-environment favicons.** A browser tab always shows which environment it is. The site picks the environment from Vercel's own `VERCEL_ENV` when it builds:

| Environment | Favicon | Tab title |
|---|---|---|
| Production | the plain Verity mark | `Verity · Verity documentation` |
| Preview | the mark on an amber tile | `[PREVIEW] Verity · …` |
| Local development | the mark on a red tile | `[DEV] Verity · …` |

All three were checked. Only production may be indexed by search engines.

## 2. How fixtures flow

Fixtures are the large test inputs, such as proofs, compiled systems and hardware captures. The [fixture plan](verity-root store: `docs/fixture-process-plan.md`) takes every fixture over 256 KiB out of git. Git keeps only each fixture's id, which is a hash of its contents, and the bytes are fetched on demand.

```text
 git: fixtures/artifacts.json               private evidence store (R2)
 (fixture id → repo path)                   (the bytes, readback-preserved)
           │                                          │
           └────────── research data export ──────────┘
                                │  writes, with a token for this bucket only
                                ▼
        verity-public, the store's public half (pub-….r2.dev)
                                ▲
                                │  307 redirect to the same key
    https://website-docs-sage.vercel.app/store/objects/sha256/{hex}
                                ▲
                                │  GET; every byte checked against the id in git
    research data fetch-fixtures (contributors, CI, check)
```

1. **In git,** `fixtures/artifacts.json` maps each fixture's id to its path in the repo.
   - [#366](https://github.com/danielreuter/verity/pull/366) merged at 12:24 AM PT today. It added the 256 KiB rule and the two commands, `fetch-fixtures` and `export`.
   - [#371](https://github.com/danielreuter/verity/pull/371) is a draft. It moves the 98 fixtures over 256 KiB out of git, which shrinks the tracked tree from 263.5 MB to 73.4 MB. All 98 are already safely stored in the evidence store.
2. **`research data export`** copies exactly what the registry names to `verity-public`. That includes older versions, and the blobs that old commits will point to after the history rewrite: about 0.3 GB in all. Nothing else from the private store is copied, and only the export writes to the bucket.
3. **The site's `/store` route** answers each request with a redirect to the same key in the bucket. Its paths are the store's own keys:
   - `/store/objects/sha256/{hex}` goes to an object;
   - `/store/manifests/{hex}.json` goes to a manifest, such as a fixture set's.

   Names must be 64 hex characters, and anything else gets a 404. No bytes pass through Vercel, and the site holds no credentials and can't write anywhere.
4. **`research data fetch-fixtures`** is what `check`, CI and contributors run. It looks in the local store first, then the private store if it has keys, then this public URL. It checks every byte against the id in git. So the bucket and the site only carry the bytes; a tampered or wrong byte can only make a fetch fail, never let a test pass.

## 3. What's proven so far

**On a preview, against a stand-in bucket.** The stand-in was a throwaway Vercel project with the real key layout, holding a 1 MiB object, a 7 MiB object and a manifest. On that preview:
- **The site's route checker passed:**
  - each request gets one redirect to exactly the right key, and the downloaded bytes hash to their name;
  - malformed names, including uppercase, wrong lengths, wrong prefixes and encoded `..`, never reach anything outside the two key prefixes;
  - uploads and deletes sent through the route are refused, and nothing is left behind.
- **The planner's own fetcher from #366** downloaded both objects (8,388,608 bytes) through the route and checked them. An unknown id correctly read as missing.

**In production:** all 69 pages load, the favicon and title are the production ones, and the route (then `/fixtures`) answers 404 because it's off. The existing `website-web` site is unaffected.

**Not proven yet:** the real bucket, Cloudflare's `r2.dev` host, and the full export read back through the site. The stand-in and its preview were deleted after the test, so there's no live route to show.

## 4. Your click-path in Cloudflare

This takes about ten clicks, all at https://dash.cloudflare.com:

1. **Create the bucket.** Open **R2 Object Storage**, then **Overview**, then **Create bucket**.
   - Name: `verity-public`. It only ever goes into secrets and store docs, never into git.
   - Location: **Automatic**. Storage class: **Standard**.
   - Select **Create bucket**.
2. **Make it public.** In the bucket, open **Settings**. Under **Public Development URL**, select **Enable**, type `allow`, and select **Allow**. Copy the **Public Bucket URL** it shows (`https://pub-….r2.dev`).
3. **Create the export's write token.** Back on **R2 Object Storage**, **Overview**: under **Account Details**, select **Manage** next to **API Tokens**. Then select **Create Account API token**.
   - Name: `verity-public-export`.
   - Permissions: **Object Read & Write**, applied to **specific buckets only**: just the new bucket.
   - Select **Create Account API token**, then copy the **Access Key ID** and the **Secret Access Key**. The secret is shown only once.
4. **Hand the token over.** In the Cursor dashboard, where the `R2_*` secrets are set, add three secrets:
   - `RESEARCH_EXPORT_BUCKET`: the bucket name;
   - `RESEARCH_EXPORT_ACCESS_KEY_ID`;
   - `RESEARCH_EXPORT_SECRET_ACCESS_KEY`.
5. **Send the Public Bucket URL** to the coordinator in chat. It isn't secret.

No read token is needed: the site redirects to the public URL.

**Proposed change to step 4:** the token would go into two Sensitive Vercel variables on `website-docs` instead of into Cursor secrets. The site would then broker every write, so agents never hold a bucket key. See [the proposal to send the store's public reads and writes through the site](verity-root store: `docs/fixtures-access-via-site.md`).

**What happens after, without you:**
1. The fixture operator runs `research data export`, which uploads the fixtures to the bucket.
2. I set the site's `STORE_PUBLIC_BUCKET_URL` to the bucket URL. I deploy a preview and run the route checker there with real fixture ids, then deploy production and check it again.
3. The operator runs `research data export --verify-url https://website-docs-sage.vercel.app/store`. This downloads every registered fixture back through the site and checks every byte.
4. Once that passes, one ordinary PR sets that URL as the fetcher's default (`fetchset.PUBLIC_URL`). #371 then comes out of draft, and the 98 fixtures leave git.
5. The history rewrite stays separate. It still waits on #385 and #387, and then on your go.

## 5. Open questions

1. **Who holds the export's write token?** Cursor secrets reach every Project agent on a cloud VM, so any of them could write to the public bucket. That can't break a test, because every byte is checked against git. But a mistaken upload would be public. **Default:** Cursor secrets, because the operator runs there. You can revoke the token from the page in step 3 at any time. The [site-broker proposal](verity-root store: `docs/fixtures-access-via-site.md`) would replace this default: the key would live only in the site, and each writer would get a site token that can be revoked on its own.
2. **Which URL goes into the code?** Once `fetchset.PUBLIC_URL` is committed, every checkout from then on uses it, so that name has to keep working. **Default:** keep `website-docs-sage.vercel.app`. If you'd like a cleaner name, say so before the URL is committed and I'll add it; `docs-verity.vercel.app` looked free when I checked.
3. **When should there be a domain?** Cloudflare rate-limits `r2.dev` and says it's for non-production use. That's fine at today's volume. **Default:** use `r2.dev` now, and get a domain when contributors arrive. Switching is one site setting, and the fetcher's URL doesn't change.
4. **Should the site be public already?** It's public now, before the repo is. It holds only material written for the public docs. Putting it behind a login would also block the keyless downloads. **Default:** keep it public.
5. **Should deploys be automatic?** Today I deploy by hand from the branch. **Default:** merge website PR #1 and connect `website-docs` to git. Then `main` deploys production and each PR gets its own preview, with the right favicon for each.
