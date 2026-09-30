---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
id: 20260930T1925Z-copy-from-docs-site-fixtures-access-via-site
campaign: verity
lane: console
kind: copy
status: final
repo: danielreuter/website
origin: docs-site
---

> **Public copy** of the docs-site worker's `docs/fixtures-access-via-site.md` in the verity-root store, made 20260930T1925Z for the console handover.
> The original is unchanged and was not edited after this copy. Left out: 1 line(s) about the deployment's automation bypass. Full copy, private: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/private/console/fixtures-access-via-site.md`.


# Proposal: send the store's public reads and writes through the site

**For:** Daniel. **Written:** Tue Sep 29, 8:05 AM PT, by the docs-site worker. **Revised** 8:55 AM PT, for your question "Do we need Vercel's logs or would we build our own?" **Renamed** 9:55 AM PT: the route now serves the evidence store's public half, not just fixtures. The route is `/store`, the bucket is `verity-public`, and fixtures are its first kind, `fixture/v1`. The [HTTP contract, v2](verity-root store: `internal/site-broker-contract.md`) has the exact paths and supersedes §2.1 and §2.2 where they differ. The [site-store addendum](verity-root store: `docs/site-store-api.md`) makes the design generic over kind.

It answers your question "Should we route the reads/writes through the public Vercel site?", and follows the [walkthrough](verity-root store: `docs/docs-site-and-fixtures-walkthrough.md`). The [spend broker proposal](verity-root store: `docs/spend-broker-via-site.md`) reuses this proposal's tokens, event store and admin pages for RunPod. Nothing is built yet.

**Recommendation: yes, for writes and for recording reads, but don't presign reads yet.**
- **Writes go through the site.** It holds the bucket's only key. Agents get a per-writer site token that can only add new, verified objects, and each token can be revoked on its own.
- **Reads get recorded, then redirected** to the bucket's public URL, as they are today. Presigning them would put the account id and bucket name in every public redirect (§1).
- **The site keeps its own record.** Its TypeScript route handlers write every fetch and upload to a small Postgres database (Neon, added through the Vercel Marketplace). Admin pages on the site show:
  - recent activity;
  - each fixture's and each writer's history;
  - failures and mismatches;
  - the token list, with Revoke.

  Vercel's logs stay, but only for the handlers' own errors (§2.3 to §2.6).

**What this revision changed:**
- Events go to our own database instead of Vercel's runtime logs (§2.3).
- Writer tokens live in the same database instead of a Global Config store, so the admin pages can revoke a token without holding a Vercel API token (§1, §2.2).
- There are new admin pages, reachable only through Vercel's login (§2.4, §2.5).
- There's one more click for you: add Neon's Free plan (§4). The site's side grows by about half, mostly the pages (§5).

## 1. The starting idea, checked

| Assumption | Holds? | What the docs say |
|---|---|---|
| Broker, don't proxy | **Yes** | A Vercel function's request or response body is capped at 4.5 MB (`413 FUNCTION_PAYLOAD_TOO_LARGE`), and objects are up to 7.1 MB today ([limits](https://vercel.com/docs/functions/limitations)). Proxying would also bill every byte twice, as Fast Origin Transfer in and out of the function ([CDN usage](https://vercel.com/docs/manage-cdn-usage)). R2 charges no egress, so bytes going straight from R2 to the client are free. |
| Private bucket, presigned GETs | **Works, at a price** | Presigned URLs only work on the account's S3 host, `https://{ACCOUNT_ID}.r2.cloudflarestorage.com/{bucket}/…`, not on `r2.dev` or a custom domain ([presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/)). Every public redirect would show the account id, the bucket name and the access key id. Those are the literals #385 and the history rewrite are removing from git. A presigned GET also doesn't answer a HEAD: HEAD needs its own signature, and `fetch-fixtures` reads a 403 as "absent". |
| PUT bound to its sha256 | **No** | For PutObject, R2 supports `If-None-Match` (write-once) and `Content-MD5`. It doesn't support a full-object SHA-256 checksum, only composite ones for multipart ([S3 compatibility](https://developers.cloudflare.com/r2/api/s3/api/)). So the site checks the bytes after the upload (§2.2). |
| Per-writer tokens, revoked one at a time | **Yes** | Keep each token's SHA-256 hash in the event store's `tokens` table. Revoking is one row update, made from the admin pages, and it applies to the very next request. A Global Config store (formerly Edge Config) would also work, with revocation everywhere within 10 seconds and no redeploy ([limits](https://vercel.com/docs/edge-config/edge-config-limits)). But revoking from our own pages would then need a Vercel API token with write access inside the site. |
| Agents never hold a bucket key | **Only if they can't deploy production** | Deployed code can read the key, so the key is exactly as private as the site's production deploys. Today agents deploy the site with your Vercel login. Vercel's Developer role can't edit production environment variables, and it reaches production only by merging to the production branch ([roles](https://vercel.com/docs/rbac/access-roles)). The same holds for the event store's connection string. |
| Vercel's logs as the record | **No: build our own** | Runtime logs cover functions, and config redirects too. But Vercel Pro, which the compute team is on, keeps them for 1 day; Observability Plus keeps 30 days ([runtime logs](https://vercel.com/docs/logs/runtime)). A log drain forwards them elsewhere, at $0.50 per GB ([drains](https://vercel.com/docs/drains)). None of those can be queried per fixture or per writer from our own pages. |

## 2. Design

### 2.1 Reads: `GET` and `HEAD /store/…`

The paths are the store's own keys under `/store`, such as `/store/objects/sha256/{hex}` and `/store/manifests/{hex}.json`.
- A route handler replaces today's config redirect.
- It checks the key's shape, answers `307` to the same key on the bucket's public URL, and then records one event (§2.3).
- It needs no credential. Clients can still reach the bucket directly: this is for observability, not access control.
- **The switch to presigned reads, if ever needed:** say the bucket has to go private, or needs real rate limits. The handler would sign each GET, and each HEAD separately. `fetch-fixtures` already follows a redirect to a presigned URL, so clients wouldn't change.

### 2.2 Writes: two calls, and nothing unverified sits at a real key

1. **The writer asks for an upload URL.** It sends `POST /store/uploads` with `Authorization: Bearer {writer token}` and a body of `{key, bytes}`, where key is the store key, `objects/sha256/{hex}` or `manifests/{hex}.json`.
   - The site looks up the token's hash in the `tokens` table. It refuses a revoked, expired or unknown token, a bad shape, or a size over the cap.
   - If the key already exists, it answers `exists`.
   - Otherwise it answers with a 10-minute presigned PUT to `incoming/{sha256}/{upload_id}`. The URL is bound to the declared length, and to `If-None-Match: *`.
2. **The writer uploads** straight to R2. No bytes pass through Vercel.
3. **The writer asks the site to commit it,** with `POST /store/uploads/{upload_id}/commit`.
   - The function reads the staged object and hashes it: 7.1 MB takes well under a second.
   - If it matches, R2 copies it server-side to `objects/sha256/{sha256}` or `manifests/{sha256}.json`. The site records the writer in its index and deletes the staged copy. For a manifest, it first checks the envelope, that its kind is public, and that every payload blob is already committed.
   - If it doesn't match, the site deletes the staged copy and answers `409`.

Each step records an event before it answers.

The site's key stays with the site. It's an Object Read & Write token for `verity-public` alone, stored as Vercel Sensitive environment variables, for Production only, so preview code never sees it. No endpoint lists, overwrites or deletes a committed object.

### 2.3 Events: our own store

**What's recorded:**

| Event | Fields |
|---|---|
| Each fetch | time, `GET` or `HEAD`, kind, id, status (`307` or `404`), user agent (`research-store-fetch` or a browser), country, a salted hash of the client IP |
| Each upload step | time, writer name, id, bytes, result (`created`, `exists`, `mismatch`, `refused`), and time to verify |

The index also records each committed key's writer, by a label such as `fixture-export`, never by a person's name. The bucket holds store keys only, so it has no receipts.

**The schema.** There's one table of events and one of tokens. The spend broker adds its own tables beside them.

```sql
create table store_events (
  id          bigint generated always as identity primary key,
  at          timestamptz not null default now(),
  kind        text not null,     -- fetch | upload | commit
  method      text,              -- GET | HEAD | POST
  key_kind    text,              -- object | manifest
  sha256      text,
  status      int  not null,
  result      text,              -- redirected | not_found | bad_key | created | exists | mismatch | refused | error
  writer      text,              -- token name; null for fetches
  bytes       bigint,
  ua          text,
  country     text,              -- x-vercel-ip-country
  ip_hash     text,              -- HMAC-SHA-256(IP_HASH_SALT, ip), hex
  deployment  text,              -- VERCEL_DEPLOYMENT_ID
  duration_ms int
);
create index on store_events (at);
create index on store_events (sha256, at);
create index on store_events (writer, at);
create index on store_events (at) where result not in ('redirected', 'created', 'exists');

create table tokens (
  id          uuid primary key default gen_random_uuid(),
  name        text unique not null,  -- the writer name shown in events
  scope       text not null,         -- store:write with its kinds, or spend (see the spend proposal)
  hash        text unique not null,  -- SHA-256 of the token; the token itself is shown once, at minting
  created_at  timestamptz not null default now(),
  created_by  text not null,
  expires_at  timestamptz,
  revoked_at  timestamptz,
  revoked_by  text,
  last_used   timestamptz
);
```

**Store options.** The rough latencies are typical figures, not measurements.

| | Neon Postgres (Vercel Marketplace) | Upstash Redis (Vercel Marketplace) | JSON lines in R2 |
|---|---|---|---|
| The pages' queries: per object, per writer, failures, time ranges | SQL with indexes | a hand-built sorted set per view; no ad hoc queries | scan and parse objects; no queries |
| Cost at the planning volume below | $0 on Free (0.5 GB, 100 compute-hours a month) | about $2.40 a month pay-as-you-go, for about 1.2M commands | about $1.35 a month in writes, at one PUT per event (R2 can't append) |
| Write latency, warm and in the same region | one HTTP round trip, roughly 5 to 20 ms; a few hundred ms when compute resumes from suspend | roughly 1 to 5 ms | roughly 50 to 100 ms |
| Privacy | private | private | the public bucket would publish the IP hashes, and a second, private bucket needs another key |
| Also serves the spend broker, which needs transactions and locks | yes | partly | no |

**Pick: Neon Postgres, on the Free plan.**
- **Volume.** Today's volume is close to zero: the route shipped this morning, and clients move to it with #371. For planning, I assume 10,000 fetches a day once CI and lanes fetch through the site. At about 300 bytes a row with indexes, that's about 3 MB a day. The pages show the real count.
- **Retention.** Fetch events are kept for 30 days. After that they're rolled up into daily counts per key, method and status, kept indefinitely. Upload events and token history are also kept indefinitely. At the planning volume that stays under 100 MB, well inside Free's 0.5 GB. A daily Vercel Cron job does the rollup.
- **Compute.** Neon suspends compute after 5 idle minutes. At the 0.25 compute-unit minimum, Free's 100 compute-hours cover about 13 active hours a day.
  - If CI keeps the database awake around the clock, that's about 183 compute-hours, and Free runs out. Compute then suspends until the next month: reads still redirect, but their events are lost, and uploads are refused.
  - The pages show hours used. At that level, Neon's Launch plan costs about $19 a month.
  - If the spend broker ships, its once-a-minute reaper keeps the database awake anyway, and Launch is part of that proposal.
- **Write latency on the redirect path: none added.**
  - The handler sends the `307` first, then inserts the event inside Next.js's `after()`. On Vercel, `after()` runs after the response has been sent, through `waitUntil`, including on errors and redirects. The insert costs function time, not client time.
  - What a client does feel is the move from today's config redirect, which Vercel's CDN serves, to a function: tens of ms when it's warm, a few hundred when it's cold. That was already true of the original proposal.
  - The database goes in the function's region (the default, `iad1`, is AWS us-east-1).
- **Upload latency.** The upload and commit steps look up the token first, and record their event before answering. One or two queries are negligible next to an upload.

### 2.4 The admin pages

These are server-rendered pages built with shadcn tables. The browser never talks to the database.

| Page | Shows |
|---|---|
| `/admin/store` | fetches and uploads in the last hour, day and week, by status and user agent; a live table of recent events with filters |
| `/admin/store/{sha256}` | one object or manifest: its uploads (writer, result), fetches per day, and recent fetchers (user agent, country, IP hash prefix) |
| `/admin/store/failures` | 404s, malformed keys, refused tokens, mismatched uploads and handler errors |
| `/admin/writers/{name}` | one token's history: its uploads here, and its RunPod activity if the spend broker ships |
| `/admin/tokens` | every token: name, scope, created by and when, last used, expiry, revoked; Mint and Revoke |

Every page action is also an API route behind the same gate (§2.5), so agents can use them with curl.

### 2.5 Who can see it, and how that's enforced

The pages show writer names and hashed IPs, so they aren't public.
- **Viewers** are:
  - members of the compute team on Vercel: you, and anyone you add;
- **The gate.** The admin pages and their API routes answer only when the request's host is the deployment's own URL (`VERCEL_URL`).
  - Vercel's Standard Protection puts every deployment URL behind Vercel's login, but leaves the public alias public. I checked this morning: the deployment URL answered `302` to Vercel's login, and the alias answered normally.
  - On the public alias, `/admin` answers `307` to the current deployment URL, which then asks for the login. Anything else under `/admin` answers `404` there.
  - The pages send `noindex` and `Cache-Control: private, no-store`. Their actions are Next.js Server Actions, which refuse cross-origin posts.
- **IP hashes.** Raw IPs are never stored. The hash is an HMAC-SHA-256 keyed with a salt, kept as a Sensitive variable, so nobody can reverse it by hashing every IPv4 address. The pages show only the first 8 hex characters.
- **Who can do what.** Any viewer can revoke a writer token. Nobody mints one any more: since Sep 30, tokens start as requests that you approve on `/approvals`, signed in with your own GitHub account, and the old `tokens` table refuses new rows ([token requests](verity-root store: `internal/token-requests-spec.md`)). A store writer is asked for with the scope `write:fixture/v1`. That's an admin scope, so no pre-approval rule issues it, and only you can approve it. The spend broker is on hold since the switch to SkyPilot.
- **The same caveat as §1.** Anyone who can deploy production can read and change the database. Readers still check every byte against its id, so a changed database can't change what a test reads.

### 2.6 Are Vercel's logs still needed?

Only for the handlers' own failures: uncaught errors, timeouts, and event inserts that failed. A failed insert logs the event as one JSON line, so it can be replayed the same day. There's no drain, and Pro's 1 day of retention is enough for this.

## 3. What changes in Verity

This is the fixture lane's part (bc-dc2611ba). The event store doesn't change it.
- **`research data export`:**
  - Add a `BrokerRemote` in `remote.py`. Its `put` makes the three calls in §2.2 and keeps today's results: `created`, `exists`, or `RemoteConflict` on `409`. Its `head` and `get` go through the public route, like `HttpRemote`.
  - `load_export` reads `RESEARCH_EXPORT_URL` and `RESEARCH_EXPORT_TOKEN` ahead of today's `RESEARCH_EXPORT_BUCKET` and key pair.
  - `export()` and `--verify-url` don't change: they only use `put` and `head`.
  - It needs tests against a fake local broker.
- **`fetch-fixtures`:** no change. `HttpRemote` already follows redirects for GET and HEAD. I checked that urllib keeps HEAD across a `307` on Python 3.13. Optionally, add a version to its user agent so the pages can tell tool versions apart.

## 4. Your click-path, compared

| Step | Today's plan | With the broker |
|---|---|---|
| 1. Create the bucket | same | same |
| 2. Enable the Public Development URL | yes | yes |
| 3. Create an Object Read & Write token for that bucket | yes | yes |
| 4. Where the token goes | three Cursor secrets, which reach every cloud agent | two Sensitive, Production-only variables on `website-docs` in Vercel (Settings, Environment Variables). I set the bucket name and endpoint, which aren't secret. |
| 5. Send the public URL | yes | yes |
| 6. Add the event store | none | In Vercel: Storage, Create Database, Neon, Free, connected to `website-docs`. That takes about 2 minutes, including accepting Neon's terms. Tick its preview branching, so preview deploys get their own database and never see production events or tokens. |

It's almost as simple as today's plan. Step 4 changes where the key goes, which is what keeps the key away from the agents. Step 6 is new.

A writer token is one click for you. Since Sep 30, the export's client asks for it with `research auth request --scopes write:fixture/v1`, and you approve it on `/approvals`, signed in with your own GitHub account. The key goes straight to the client's file and never reaches you. You can revoke it on `/approvals`, and any viewer can revoke a token minted before requests on `/admin/tokens`. If the site is down, one SQL update in Neon's console revokes it.

## 5. Effort and risks

**Effort:**
- **The site:**
  - three route handlers (read, upload, commit), replacing today's config redirect;
  - SigV4 presigning for PUT, plus R2's copy and delete;
  - the event store: its schema and migrations, the event writes, and the daily rollup;
  - tokens in the database, with Mint and Revoke;
  - the admin gate and the five pages;
  - the route checker extended to cover uploads and the gate.

  That's about 1,000 to 1,500 lines instead of a few hundred; the pages are most of the increase. Credentials pass through it, so it needs a careful review.
- **Verity:** `BrokerRemote` and its configuration, about a hundred lines, plus tests.
- **Setup:** connect `website-docs` to git, use the Sensitive, Production-only variables, and add Neon.

**Risks:**
- **The site becomes the only write path.** When it's down, exports wait. Reads can still fall back to the bucket's URL through the fetcher's public-URL setting (`RESEARCH_FIXTURES_URL` in #371 today).
- **The event store sits on the write path.** When Neon is down, or out of Free compute, reads still redirect, and their lost events show up as logged errors. Uploads are refused, since the token lookup fails closed.
- **Real separation needs production deploys to be reviewed merges.** Agents deploying with your login could ship code that reads the key. The broker still narrows what a writer's token can do. But until deploys go through reviewed merges and agents hold at most a Developer-role account, it doesn't remove agents' access to the key.
- **It's more to build than a bucket key,** and it puts the broker on the fixture migration's path (#371).
- **`r2.dev` rate limits** apply exactly as in today's plan.

## 6. Order

1. You create the bucket and token (§4), put the token in Vercel, not Cursor, and add Neon.
2. I build the site's side, including the event store and the pages. I verify it on a preview, with a scratch writer token and the preview database. That includes confirming that R2 enforces the signed length and `If-None-Match` on a presigned PUT, and that the admin gate holds on the public alias. Then I deploy production and verify again.
3. The fixture lane adds `BrokerRemote`, then runs the export and `--verify-url` through the site.

If #371 can't wait for that, do the first export now, with a short-lived token in Cursor secrets: Cloudflare tokens can expire. Then switch to the broker and let that token lapse.
