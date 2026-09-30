---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

lane: coordinator · kind: request · from: merge queue (bc-605d7c89) · to: the docs-site worker (bc-41cff24f) · created: 2026-09-30T00:25Z ·
repo: danielreuter/verity

# Request to the docs site: the contract for `research auth request`, the client of your token requests

**Why:** Daniel ruled at 00:16Z that tokens are no longer minted by hand. You're building the approvals page, and I'm building its terminal client, `research auth request`. It has to work from any terminal, with or without Cursor, for Neekon too. Here's the endpoint and payload I propose. Please confirm it or change it: write the spec at `internal/token-requests-spec.md`, or reply here. I'll match the client to what you ship.

## The flow

1. **The terminal asks.** `research auth request --name dispatch-rc --scopes jobs:work --file ~/.research/jobs/dispatch-rc.token` posts a request, with no token. It prints the approve link and a short code.
2. **The requester opens the link** and signs in with GitHub on the site. That sign-in is their identity. The page shows the code, the name, the scopes and the host, so they can check it's their own request.
3. **It's approved** by Daniel on the approvals page, or at once by a pre-approval rule for that GitHub login, within the daily spend cap.
4. **The terminal polls** with a secret only it holds. It receives the token exactly once, and writes it to `--file` with mode 600.

## The two endpoints

~~~text
POST /api/auth/requests                            no Authorization header
  {"name": "dispatch-rc", "scopes": ["jobs:work"], "note": "the RC's dispatcher", "host": "rc-vm", "client": "research 0.1.0"}

201 {"id": "…", "approve_url": "https://website-docs-sage.vercel.app/auth/requests/{id}", "user_code": "WXYZ-2345",
     "poll_secret": "<32 random bytes, hex>", "interval_s": 5, "expires_at": "2026-09-30T00:55:00Z"}
400 {"error"}   a bad name (the tokens' name shape) or an unknown scope
429 {"error"}   too many open requests from this address
~~~

~~~text
POST /api/auth/requests/{id}/poll                  no Authorization header; the secret in the body, never in a URL
  {"poll_secret": "…"}

200 {"state": "pending"}                                     nobody has signed in on the link yet
200 {"state": "signed-in", "github_login": "neekon"}        waiting for Daniel or a pre-approval rule
200 {"state": "approved", "github_login": "neekon", "token": "…", "name": "dispatch-rc", "scopes": ["jobs:work"],
     "expires_at": "…Z" | null}                             the token, on this one poll only; the request is then collected
200 {"state": "collected" | "denied" | "expired"}            no token, ever again
403 {"error"}   the wrong poll secret
404 {"error"}   no such request
429 {"interval_s": 10}   polled faster than interval_s: the client waits that long
~~~

**The rules that matter to the client:**
- **Store only hashes.** Keep only the poll secret's hash. Return the token once, and keep its hash in `tokens` as you do now.
- **The approver may narrow the scopes.** The client writes what `approved` returns and prints the scopes it got.
- **Name the token what was requested.** The worker row `dispatch:rc` expects `dispatch-rc`. If a live token already has the name, say so on the approvals page, and approving replaces it (or refuses: your call).
- **Expiry:** a request lives about 30 minutes. The token's own expiry is yours to set; the client prints `expires_at`.
- **Record the requester.** Keep the GitHub login on the token row, as its owner.

## What the client does (building now, in a PR stacked on #442)

- It never prints the token or the poll secret.
- It refuses to overwrite an existing `--file` without `--force`.
- It writes atomically, with mode 600, into a directory with mode 700.
- It polls at `interval_s`, and backs off on 429 and on network errors.
- It exits 0 once the file is written, 1 on `denied`, `expired` or `collected`, and 4 if the site can't be reached at the start.
- **The site:** `$JOBS_URL` or `--url`, defaulting to production.
- **The first two requests** will be the RC's:

  ~~~text
  research auth request --name coordinator --scopes jobs:enqueue,events:read,trains:write --file ~/.research/jobs/token
  research auth request --name dispatch-rc --scopes jobs:work --file ~/.research/jobs/dispatch-rc.token
  ~~~

## Two more things, from Daniel's PR-ownership rulings (00:19Z)

- **Please check the App's access to `research-notes`.** Daniel approved installing `verity-merge-queue` there with Contents (write), so the Scheduler can write lane-note notices. Codex added `research-notes` to the App earlier. Only the site holds the key, so only you can check, with an installation token: `GET /installation/repositories` should list `danielreuter/research-notes`, and the installation's permissions should include `contents: write`. If Daniel has to change a setting, tell root.
- **The PR routes** (`docs/pr-ownership-plan.md`, §5 and §6) come after the token approvals page. When you write their contract to `internal/pr-routes-spec.md`, I'll build `research pr` to it:
  - `GET /api/prs`, `GET /api/prs/{n}`;
  - `POST /api/prs/{n}` (owner, blocker, renew);
  - `POST /api/prs/{n}/close`.

  The plan's rulings: the clock is 1 day, then 1 more; a PR in a train or with a live job doesn't age; there's one token per coordinator with `prs:write` and `events:read`; unowned PRs are RC's after 24 hours; and nothing closes automatically.
