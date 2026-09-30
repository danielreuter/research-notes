---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
---

# Token approvals now need Daniel, and the website repo's secret scan

**For:** root and the coordinator. **From:** the docs-site agent (bc-41cff24f), Sep 29 about 6:45 PM PT. **Answers:** the two items for me in the [security review](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/open-source-readiness.md) (its line 41 and "scan the website's history").

## The short version

1. **Approve needs Daniel personally now, in production. Before today it didn't.** Until this evening, the automation bypass alone opened production's `/admin/tokens` and its mint form. Now:
   - granting lives on `/approvals`, which checks Daniel's own GitHub session in its server actions;
   - the legacy `tokens` table refuses new rows, so the five older production deployments, which still show the old form, can't mint either.

   Nobody can approve anything in production until root creates the GitHub sign-in OAuth App (§1.5).
2. **The website repo's history is clean.** Both passes covered all 753 commits on every ref, plus the local branches:
   - **gitleaks 8.30.1:** 88 hits, all `generic-api-key` and all false positives. They're benchmark run keys, sampling-stream ids, one camelCase field name and one model-config label.
   - **My own pass,** for our token shapes and five live values: no hits.

   Nothing needs rotating.

## 1. Approval needs Daniel's own sign-in

### 1.1 What was true before

The admin gate (`adminVerdict`) allows a request only on the deployment's own `VERCEL_URL`, which Vercel's Standard Protection covers. Both Daniel's Vercel login and the automation bypass header satisfy that protection. So the answer to "does Approve on `/admin/tokens` already require Daniel?" was **no**. I checked production today:
- `GET /admin/tokens` on the production deployment URL with only the bypass header answered `200` and rendered the mint form;
- without the header it answered `302` to Vercel's login.

Any agent holding the bypass could have minted a token of any scope in production.

### 1.2 What's built

This is on branch `cursor/token-requests-de55` at `086e77a`, with the design in the [token-requests spec](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/token-requests-spec.md).
- **`/approvals` lives on the site's public domain** (`website-docs-sage.vercel.app`). A Vercel bypass means nothing there, and the page's server actions don't trust anything the gate lets through.
- **Every grant checks Daniel's GitHub session:** Approve, Change (narrowing), Deny, adding and removing rules, and Revoke.
  - The session must belong to login `danielreuter` *and* GitHub account id `62895916`, so a renamed or recreated account can't pass.
  - The grant functions take an `Approver` value that only this check produces, so no code path can call them without it.
  - A sign-in lasts 12 hours and is never extended.
  - Anyone else who signs in sees "@{login} can't grant tokens; only Daniel can."
- **Nothing mints by hand any more.** The admin mint form, its action and the `store-admin.mjs mint` command are removed. `/admin/tokens` redirects to `/approvals`.
- **The old deployments are closed off in the database.** Vercel keeps every earlier deployment reachable at its own URL. Those run against production's database, and the bypass opens their mint form. Migration 007 adds a trigger that refuses every insert into `tokens`. Tokens minted earlier keep working until revoked or expired.
- **Better Auth's HTTP surface is closed** except the GitHub callback and error routes. Sign-in starts in a server action, and the site stores no GitHub token.

### 1.3 What I verified

- **Tests:** 135 of 135 pass, plus the 36 jobs cases against Neon. They include the approver cases:
  - Daniel's login and id pass;
  - another login is refused;
  - the right login under another id is refused;
  - a forged or expired session is refused;
  - the legacy table refuses a row.
- **Preview** (`website-docs-mxnl7otgg`), 22 of 22 checks:
  - Better Auth's routes answer `404`, except the callback, which answers `302`;
  - `/admin/tokens` with the bypass answers `307` to `/approvals`, with no mint form;
  - `/approvals` shows no grant controls;
  - a request went through create, `/device`, approve (through the preview database, since previews have no sign-in), collect, use on `/api/events` and `/api/jobs`, and revoke. The key only ever went to a 0600 scratch file, emptied afterwards.
- **Production** (`dpl_CE6AK3LQMXD7hRSXVjjVUajhXu3E`, commit `2843824`, aliased to the public domain):
  - before migrating, I took a snapshot (01:32:39Z, LSN `0/2118288`) and confirmed it restores exactly;
  - I applied 006 and 007;
  - the new deployment's `/admin/tokens` with the bypass answers `307` to the public `/approvals`, which says sign-in isn't set up;
  - Better Auth's routes answer `404` except the callback;
  - the token-request routes refuse bad input without writing anything;
  - an insert into `tokens` is refused by the trigger, and the row count stayed at 10. I tested this with a statement that couldn't commit even if the trigger failed.
  - The previous deployment `website-docs-ocg8bq38j` still renders its mint form with the bypass, but can't write what it would mint.
- I created no requests, jobs or events in production.

### 1.4 What's still true

- **Deploy rights and `DATABASE_URL` beat any check in the app.** Whoever can deploy production or holds the database URL can grant themselves anything, or drop the trigger. Only Daniel's Vercel account deploys today, and I do it with his login on this Mac. The review's line 41 still stands.
- **This Mac's browser.** If a browser profile here is logged in to GitHub as Daniel, an agent driving that browser could complete his sign-in. Agents here must not drive a browser to `/approvals`. A passkey step-up (Better Auth's passkey plugin) would close this; I can add it next if Daniel wants.
- **Five superseded production deployments are still live:** `ocg8bq38j` (`90591a4`), `h6z2zt7wy` (`092f0d9`), `3fx4nhyrh` (`c3cf94b`), `enx0115ed` (`0ce2754`) and `pmh91m8hw` (`0e35e00`).
  - They can't mint any more.
  - Their other admin actions are no more than today's admin pages allow. Those are revoking legacy tokens, event exclusions, and on the newer ones, job admin.
  - Removing them would also stop anyone rolling back to a pre-006 build. **I recommend root removes them; I haven't, since it can't be undone.**
- **The spend broker's passkey** (not built yet) was specced as "the first enrollment wins", which the review flagged. I've changed the proposal so that enrolling also needs Daniel's GitHub sign-in.

### 1.5 What root needs to do

Create a GitHub **OAuth App**, "Verification Institute sign-in":
- callback `https://website-docs-sage.vercel.app/api/auth/callback/github`;
- no other settings;
- set `GITHUB_SIGNIN_CLIENT_ID` and `GITHUB_SIGNIN_CLIENT_SECRET` (sensitive) in `website-docs` Production.

`BETTER_AUTH_SECRET` is already set in Production and Preview; I generated it without printing it. Until the App exists, Daniel's two pending admin keys and `dispatch-rc` can be requested but not approved. After that, the variables take effect on the next production deploy, which I'll do on root's word.

### 1.6 For Daniel to confirm

- **The admin scopes, which no rule can pre-approve,** are everything except `events:read` and `jobs:enqueue`: `jobs:work` now, and `trains:write` and `prs:write` when they ship. That makes `prs:write`, which the PR-ownership plan gives coordinators, a Daniel-approves-each-one scope. Say if it should be rule-eligible instead.
- **Unsigned requests.** Daniel can approve a request nobody has signed for; it's marked **not signed in**, and the key's owner is a placeholder. Say if these should be refused.
- **Store writer scopes** (`write:{kind}`) aren't requestable, so no new writer tokens can be issued now. That's a follow-up when a writer is next needed.

## 2. The website repo's secret scan

### 2.1 Method

- **The repo:** a mirror clone of `danielreuter/website` with every remote ref, plus the local branches of `~/projects/website` and `~/projects/website-verity-docs` fetched in read-only. That's 753 commits.
- **gitleaks 8.30.1** (`gitleaks git --log-opts=--all --redact`) scanned 749 commits and 691 MB. I ran it this afternoon, and again tonight after the new branches landed; the hits were the same.
- **My own pass** covered every added line in `git log --all -p`, 15.3 million lines. It checked two things.
  - **Our shapes:** `vsb_` tokens, `vsk_` keys, Postgres URLs with a password, Neon `npg_` passwords, the Vercel bypass header with a value, RunPod `rpa_` keys, GitHub tokens, PEM private keys and `CRON_SECRET` assignments.
  - **Five live values held on this machine:** the bypass secret and four database passwords. They were read from their 0600 files into memory and never passed on a command line.

  **No hits.**
- **Also:** `.npmrc` is empty. The gitleaks JSON reports are redacted, mode 0600 and local.

### 2.2 Every gitleaks hit

All 88 are the `generic-api-key` rule, which fires on a long string near a word like "key". None is a credential.

| Path | Commits | Kind |
|---|---|---|
| `analysis/inference-economics/01_generate_fixtures.py` | `dc933d851d` | ×2, a model-config label |
| `apps/docs/data/boolean/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager.json` | `47936872bf`, `5d164dc790`, `90759c4d53`, `a2a2fac01a`, `aa78a7a761`, `c267d230f1`, `d9eb4a7795`, `ee5a81e5dd` | ×8, a GumbelStreamKey_v1 sampling-stream id |
| `apps/docs/data/programs/gemma2-2b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/index.json` | `65eccaa6c9` | ×13, benchmark run keys |
| `apps/docs/data/programs/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/llama32-1b__bf16__l40s__tp1__b1__i4096__o512__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/llama32-1b__bf16__l40s__tp1__b64__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/mistral-7b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed-arrivals__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/olmoe-1b-7b__bf16__l40s__tp1__b32__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/qwen25-15b__bf16__l40s__tp1__b1__i4096__o512__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/qwen3-30b-a3b__bf16__l40s__tp2__b2__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/qwen3-4b-fp8__fp8__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/programs/smollm2-135m__bf16__l40s__tp1__b16__i1024__o128__mixed__greedy__bi-eager.json` | `65eccaa6c9`, `8b67e886d7`, `fc4931eeb0` | ×3, a benchmark run key |
| `apps/docs/data/serving/index.json` | `4b6bb970c8`, `d4d40a3baf` | ×2, benchmark run keys |
| `apps/docs/data/serving/llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager.json` | `4b6bb970c8`, `d4d40a3baf` | ×2, a benchmark run key |
| `apps/docs/data/serving/olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager.json` | `4b6bb970c8` | ×1, a benchmark run key |
| `apps/docs/data/vllm-101.json` | `e0d18cb938` | ×13, benchmark run keys |
| `apps/web/components/design/isolated-replay-usefulness.tsx` | `08b52f8c63`, `47b40335aa`, `873df310ef`, `ec03ef3b1f` | ×8, a camelCase field name (`improvementKey`) |

A "benchmark run key" is a run's name built from its settings, such as model, dtype, GPU and batch, in the `model__dtype__gpu__…` form of the file names above.

## 3. Docs I changed

- **Rewritten:** [token-requests spec](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/token-requests-spec.md), for Better Auth, `/device` confirmation, `/approvals` and the `vsk_` key shape.
- **Edited in place:** [spend broker proposal](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/spend-broker-via-site.md), where passkey enrollment now needs Daniel's GitHub sign-in and nobody mints, and [fixtures access](/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/docs/fixtures-access-via-site.md), where "who can do what" no longer lists minting.
- **New:** this report.
