---
cursor:
  subagentId: "bc-41cff24f-52d5-5d11-b42a-99f19870de55"
id: 20260930T1925Z-copy-from-docs-site-spend-broker-via-site
campaign: verity
lane: console
kind: copy
status: final
repo: danielreuter/website
origin: docs-site
---

> **Public copy** of the docs-site worker's `docs/spend-broker-via-site.md` in the verity-root store, made 20260930T1925Z for the console handover.
> The original is unchanged and was not edited after this copy. Left out: §1.1, where the RunPod account key lives today and who can reach it; 3 line(s) about the deployment's automation bypass. Full copy, private: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/private/console/spend-broker-via-site.md`.


# Proposal: the site as the broker for RunPod spend

**Update (Sep 29, about 3:15 PM PT, root's decision):** this is built as the Scheduler's interactive kind, on the batch jobs' tables and lease rules, not as a separate service; see [the job-service design](job-service-design.md), §7, decision 7. Its credential side is now Access.

**For:** Daniel. **Written:** Tue Sep 29, 8:55 AM PT, by the docs-site worker. **Revised** 10:07 AM PT with the research coordinator's answers and corrections ([RC's answers](verity-root store: `internal/spend-broker-rc-answers.md`)), your answers of 9:26 AM, and the store rename (§10 lists them). **Updated** 12:20 PM PT to say at the top that the site brokers allocation, not use. It answers two of your questions:
- "Can we also route the Runpod stuff through this? I want to have the webapp just be a broker for all expenditure."
- "How useful is it btw to have just the pure Runpod CLI? I don't want to introduce friction." That's §3.

It builds on the [store-route proposal](verity-root store: `docs/fixtures-access-via-site.md`), with the same tokens, event store and admin pages, so the site reads as one broker. It also reconciles with the [contributor access plan](verity-root store: `docs/contributor-access-plan.md`)'s `#spending` and approval broker (§3.3, §3.4). It replaces that plan's `research broker` on the control pod: the same tools and rules, hosted on the site, so the control pod holds no RunPod key. Nothing is built. It's built on previews only, and takes over from nothing, until the research coordinator and the red team have reviewed it (§6).

**Recommendation: yes for RunPod. Everything else can be shown, but not usefully brokered.**
- **The site becomes the only holder of the RunPod account key.** Every create, resume, update, stop and delete goes through it.
  - It checks each create against the lane's line.
  - A once-a-minute reaper on Vercel Cron replaces the control pod's budgets guard, with the same rules.
- **It brokers allocation, not use.** Agents ask the site for compute and storage. Once a pod exists, they work on it directly over SSH, which never touches the site (§2.6).
- **Lines are requested by agents and approved by you on the site, with a passkey** (Touch ID or Face ID). The requester sends you the link, as lanes reach you through root today. `#spending` can post it too, once Slack is set up.
  - Per-line approval comes first. Envelopes, for approving a night's or a week's plan once, are a later add-on (§2.4).
  - `budgets.toml` becomes a read-only export.
- **The CLI stays as it is.** The site speaks RunPod's own REST API for the few calls we make. The `research` tool needs a 20-line URL change, and stock `runpodctl` works with a site token (§3).
- **R2, Vercel, Cursor and the rest** can't be capped through the site. The spend pages show them next to RunPod (§4).
- **The caveat is the same as for the store broker:** this keeps the key from agents only once agents can't deploy the site's production.

## 1. Today's machinery, checked

**Sources:**
- Verity `origin/main` `1766d522`, `tools/research/src/research/pods/`;
- notes `origin/main` `4c347619`: `budgets.toml`, `machines.d/`, `kb/ops-tools.md`;
- one read-only look at the control pod and the RunPod API, at 8:30 AM PT today;
- the coordinator's handoffs in the store.

### 1.1 Where the account key lives

Left out of this public copy; see the full copy.

### 1.2 Lines: `budgets.toml`

The file is at the notes repo's root, and the guard reads it from `origin/main`.
- **`[guard]`:**
  - `project = ["vy-", "vyv-rf-epoch-"]`;
  - `balance_floor = 25`;
  - `terminate_uncovered = true`, with `uncovered_grace_min = 15`;
  - `exempt = ["vy-control-"]`.
- **`[budgets]`** maps a pod-name prefix to `{cap_usd or cap_usd_per_day, expires, max_pod_hours, by}`.
  - The longest matching prefix wins.
  - A file with any invalid line is refused whole, and the last good lines are kept.
- **How lines get approved today:** a lane writes a request to `lanes/coordinator/`. You say yes to root. The coordinator commits the line with `by = "daniel via root {time}: {why}"`, and the guard picks it up within a minute. Top-ups, such as POUS's "raise the cap to $1.80 and 1.25 pod-hours", take the same path.

The lines at 8:30 AM PT, which is 15:30Z. Four of them had already expired (RC), and an expired line covers nothing:

| Line | Cap | Expires | Max pod hours |
|---|---|---|---|
| `vy-coord-` (the CI pool) | $65 a day | Oct 6 | 168 |
| `vyv-rf-epoch-` | $260 | Sep 30, 08:00Z | 12 |
| `vy-train-` | $22.55 | 15:00Z, expired | 11 |
| `vy-flock-netlist-sha512-` | $5 | 20:00Z | 3 |
| `vy-mq-test-` | $4.33 | 15:00Z, expired | 4 |
| `vy-epoch-check-342` | $2.99 | 11:30Z, expired | 2.5 |
| `vy-pouw-mvp-qwen05` | $1.80 | 18:00Z | 1.25 |
| `vy-pous-check364` | $1.50 | 18:00Z | 2 |
| `vy-cc-upstream-avx2` | $0.49 | 09:45Z, expired | 2.5 |

### 1.3 The create gate and the budgets guard

- **The create gate.** `research pods create` makes one SSH call to the control pod and reads the guard's state file (`/root/.research/pods/guard-budgets.json`). On the control pod itself it reads the file locally, which needs `RESEARCH_GUARD_HOST=local`. It refuses to create, exiting with 6, when:
  - the guard's last completed poll is more than 3 minutes old;
  - no live, untripped line covers the name;
  - the line's cap or daily cap is reached;
  - `--max-hours` exceeds the line's `max_pod_hours`.

  It also allows only one live pod per name. It fails closed: a state file it can't read refuses the create.
- **The guard,** `research pods guard`, runs every 60 seconds under a supervisor. It uses `GET /pods`, `DELETE /pods/{id}` and GraphQL `myself { clientBalance }`.
  - It tallies each pod's `costPerHr` over the elapsed time, per pod and per line. Daily caps use a rolling 24 hours, kept in 5-minute buckets.
  - **A line that reaches its cap trips, and its pods are terminated.** The trip holds until the cap is raised. A daily trip clears itself.
  - A pod older than its line's `max_pod_hours` is terminated.
  - A project pod that no line covers is terminated after the 15-minute grace.
  - At or below the balance floor, every project pod is terminated.
  - It fails closed: it decides and terminates from memory first, then records.

### 1.4 Kill timers on the pods

- **The lease** is a dead-man loop on the pod: it ticks every 60 seconds, with a 15-minute grace. `pods create` arms it over SSH and terminates any pod it can't arm. `--boot-lease` arms it at boot instead, for RunPod's own images.
  - It ends the pod with the pod-scoped key: GraphQL `podTerminate`, then REST DELETE, then `runpodctl remove pod`.
  - `research run --on` extends it by the run's timeout plus 15 minutes.
- **The idle guard** terminates a pod after 20 idle minutes before its first run, and 90 after one. It waits for unfetched runs to be fetched before it stops a pod. Pool pods turn it off with `--idle-min 0`.
- **The account:** RunPod's spend limit is $80 an hour.
  - Since today, RunPod also reloads the balance automatically ("It'll top itself up"). So the $25 floor no longer stops anything unless a reload fails: it's a tripwire now.
  - **Line caps and the $80 limit are what's left between a bug and the card.**

### 1.5 `research run --on`, and machines

- Machines come from `~/.research/machines.toml` (or `$RESEARCH_MACHINES`), merged with the notes repo's `machines.d/`, one file per machine.
- `run --on` looks up the pod's host and port with a read-only `GET /pods/{id}`, then connects over SSH with the shared key (`~/.runpod/ssh/runpodctl-ssh-key`, or `RUNPOD_SSH_KEY_B64`).
  - The key's public half goes in as `PUBLIC_KEY` at create.
  - RunPod also puts every account SSH key on every pod.
- The account key never goes to a pod.

### 1.6 What's running, and the always-on pods

At 8:30 AM PT, 11 pods cost $19.39 an hour. The balance was $219.81.
- **The control pod,** `vy-control-verity`, costs $0.03 an hour. It's exempt from lines, has been up 190 hours, and its 10 GB disk is 84% full. It runs:
  - the steward (`research notes watch --pods --reap --custody-r2 --lease …`);
  - the budgets guard and its supervisor;
  - until 9:24 AM PT, the older guard: `research pods guard --prefix vyv- --cap-file /root/dm/CAP`, run by `guard-vyv.sh`, with a $1,160 cap. It overlapped the budgets guard on the `vyv-rf-epoch-` prefix. RC resolved that by stopping it, and the `/root/dm` scripts are retired;
  - rsync mirrors.
- **The CI pool:** `vy-coord-t1` at $1.09 an hour, under the standing `vy-coord-` line. The infrastructure plan grows it to 8 pods (`vy-coord-q{n}`) at about $4.48 an hour, or $45 to $65 a day. None of those queue pods exists yet (RC).
- **SP1 isn't always on:** its pods are on demand (RC). `machines.d/vy-sp1-committed.toml` names pod `6n0tv9llnhs142`, which isn't running.
- **Lane pods:**
  - six `vyv-rf-epoch-` pods, at $1.09 to $6.98 an hour;
  - `vy-flock-netlist-sha512-l40s`, `vy-pous-check364` and `vy-pouw-mvp-qwen05`.
- **Network volumes, which today's guard doesn't see:** 1,450 GB, about $92 to $102 a month.
  - `verity-r19-evidence`, 700 GB, is ours.
  - `porep-inference`, 250 GB, and `autoproof-max-context-20260715`, 500 GB, belong to other projects. **So the RunPod account is shared with other projects.** They're being archived (your answer, 9:26 AM).

### 1.7 Who calls RunPod

This is §3's starting point.
- **The `research` tool:** every call goes through `research.pods.runpod`. There's no SDK. It uses Python's urllib against:
  - REST `https://rest.runpod.io/v1`, hard-coded as `REST`;
  - GraphQL at the config file's `apiurl`, or `https://api.runpod.io/graphql`.

  The key comes from `~/.runpod/config.toml`, or else `RUNPOD_API_KEY`. The whole REST surface it uses is four calls:

  | Call | Used by |
  |---|---|
  | `POST /pods` | `pods create` |
  | `GET /pods` | `pods list`, the guard, the steward's reaper, `connect`, `part` |
  | `GET /pods/{id}` | `pods get`, `health`, `register`, `ssh`, `sync`, `drain`, and `run --on` for the host and port |
  | `DELETE /pods/{id}` | `pods terminate`, the guard, `notes watch --reap` |

  The only GraphQL call is `myself`, for the balance, from the guard and `research status --balance`. `pods extend` and `pods lease` only talk to the pod, over SSH.
- **`runpodctl`:** the lease's last fallback on the pod, with the pod-scoped key. A few lane notes also use `runpodctl ssh info` and `runpodctl get pod`.
- **The Python SDK:** not used anywhere in Verity or the notes repo.
- **The `/root/dm` scripts** on the control pod (`runpod.py`, `budget_cap.py`, `balance_floor.py`, `deadline.sh`) are retired and can be deleted (RC). Their one live process, `guard-vyv.sh`, was stopped at 9:24 AM PT.
- **The notes repo's lane scripts** only wrap SSH to fixed hosts and ports.

## 2. The design

### 2.1 One key, held by the site

- `RUNPOD_API_KEY` is a Sensitive, Production-only variable on `website-docs`. You paste it there yourself.
- Preview deployments get no key. They're tested against a fake RunPod built from recorded responses.
- Every call with the key goes through two places:
  - the site's RunPod-compatible API at `/runpod/v1` and `/runpod/graphql` (§3);
  - its own spend API at `/api/spend/…`, for requests, extensions and status.

### 2.2 Tokens: the store broker's, with a spend scope

- Tokens are rows in the same `tokens` table, with the scope `spend`. A token's name is the writer name everywhere: in events, in lines, and on the pages.
- **A new token owns no lines, so it spends nothing** until a line is approved for it. That's why minting a token is open to any viewer, as for store writers.
- The tokens at the start:

  | Token | Can |
  |---|---|
  | `agents` | the lanes' token (§6 explains why it starts as one) |
  | `merge-queue` | owns `vy-coord-` |
  | `steward` | lists and gets project pods (its reap reads each pod's SSH host and port), stops and terminates them, and triggers the reaper; it can't create. That's all the reap needs (RC). |
  | `coordinator` | the research coordinator's token, which owns `vy-control-` |

### 2.3 What each call checks

| Call | Who may | What the site checks |
|---|---|---|
| Create: `POST /pods` | the token that owns the line | see the list below |
| Resume: `POST /pods/{id}/start` | the line's owner | the same checks, with a fresh expiry |
| Update: `PATCH /pods/{id}` or `POST /pods/{id}/update` | the line's owner | refused if it renames the pod, changes `RESEARCH_LEASE_EXPIRES`, or grows its disk; otherwise passed through |
| Stop and terminate: `POST /pods/{id}/stop`, `DELETE /pods/{id}` | the line's owner, `steward`, or any viewer on the pages | always allowed for project pods |
| Reset and restart | the line's owner | passed through, since they add no spend |
| Reads: `GET /pods`, `GET /pods/{id}`, `GET /billing/…` | any spend token | passed through, filtered to the project's prefixes |
| Network volumes | list: any spend token; create or grow: a volume line; delete: your passkey | a volume line has a monthly cap. Deleting loses data, so it needs you. |
| GraphQL | any spend token | only `myself` (balance, spend per hour, spend limit) and `gpuTypes`, both reads |
| Everything else: templates, registry auth, serverless endpoints, account settings such as SSH keys | nobody | refused with a 403 that names the call |

**The checks on a create:**
- The name falls under a live, untripped line that the token owns. The longest prefix wins, as today.
- No live pod has the same name.
- The reaper completed a tick in the last 3 minutes. That's today's staleness rule.
- The requested hours are at most the line's `max_pod_hours`. They come from an `X-Spend-Max-Hours` header, which `research pods create` sends from `--max-hours`. Stock `runpodctl` sends no header, and gets the line's maximum.
- **Headroom (new):** rate × hours must fit within the cap, less what's been spent, less what the line's running pods have committed through their remaining leases.
  - The line's daily cap gets the same check over the next 24 hours.
  - Today's guard counts only what's been spent. This is the rule the contributor plan uses for approval within a line, and the one the vLLM lanes already apply by hand.
  - The rate comes from `gpuTypes` beforehand. The site then reads the new pod's actual `costPerHr`, and if that breaks the rule, it terminates the pod at once and answers 409.

**The site then sets the pod's end, not the client.**
- It writes `RESEARCH_LEASE_EXPIRES` into the pod's environment.
- For RunPod's own images, it adds the boot-lease start command itself (the lease module's `boot_fields`), so every such pod has an on-pod lease from boot, even one made with stock `runpodctl`.
- It records the pod's expiry in `spend_pods`, and the reaper enforces that expiry.

`research pods create` still arms the lease over SSH, as today.

**Extensions:**
- `POST /api/spend/pods/{id}/extend` checks the same headroom, and `max_pod_hours` from the pod's creation. It then moves the recorded expiry.
- `research pods extend` and `run --on` call it first, then extend the on-pod lease over SSH, as they do now.
- If the site is down, nothing is extended, so pods end on time.

### 2.4 Lines, requests and approvals

**Lines move from `budgets.toml` into a `spend_lines` table.**
- They keep the same fields and the same meaning: a prefix, `cap_usd` or `cap_usd_per_day`, `expires`, `max_pod_hours` and why.
- They add the owning token, a status (live, tripped or closed), and who approved them and when.
- The validation is ported from `budgets.parse`, and the `[guard]` settings become one settings row.

```sql
create table spend_lines    (prefix text primary key, owner text references tokens(name), cap_usd numeric, cap_usd_per_day numeric,
                             expires timestamptz not null, max_pod_hours numeric not null, why text not null,
                             status text not null, approved_by text, approved_at timestamptz, request_id uuid);
create table spend_requests (id uuid primary key, at timestamptz, token text, prefix text, change jsonb, why text,
                             envelope_id uuid, status text, decided_by text, decided_at timestamptz);
-- later, with envelopes (§2.4)
create table spend_envelopes(id uuid primary key, holder text, cap_usd numeric, line_cap_usd numeric, expires timestamptz,
                             why text, approved_by text, approved_at timestamptz);
create table spend_pods     (pod_id text primary key, name text, prefix text, token text, created_at timestamptz,
                             expires_at timestamptz, cost_per_hr numeric, spent numeric, terminated_at timestamptz, why text);
create table spend_events   (id bigint generated always as identity primary key, at timestamptz default now(), kind text,
                             token text, prefix text, pod_id text, usd numeric, detail jsonb);
create table reaper_state   (id int primary key check (id = 1), last_tick timestamptz, state jsonb);
create table passkeys       (id text primary key, public_key bytea, counter bigint, device text, created_at timestamptz);
```

**A request:**
1. An agent runs `research pods line-request --prefix vy-foo- --cap 5 --expires 20:00Z --max-pod-hours 3 --why "…"`, or posts to `/api/spend/requests`. A top-up is the same request against an existing line, and the page shows it as a change from the current line.
2. The site stores the request and answers with its link. The requester passes the link to root, who sends it to you, as with today's requests. `/admin/spend/requests` lists every open request.
   - **Once Slack is set up (optional):** the site also posts one line to `#spending` through an incoming webhook, with who, what, why and the link. Nothing depends on it: with no webhook set, the site skips the post.
3. You open the link, on the laptop or the phone, and tap Approve with your passkey. The line is live at once, and a waiting `--wait` returns. Deny takes one tap and no passkey.
4. A request stays open until you answer it or its requester withdraws it. `--wait` gives up after 30 minutes, as in the contributor plan.

Slack's own Approve buttons are a later option, after that. They need a Slack app with interactivity and a signing secret.

**Envelopes: later.** Per-line approval is built first, and envelopes are an add-on for when you've decided (your answer, 9:26 AM). The idea:
- You approve a budget once, with your passkey. For example, "tonight's plan: at most $120 in total and $30 per line, until 07:00 PT."
- Root's token can then open lines inside it without asking you. Each line shows which envelope it came from.
- That's the project's standing "overnight envelope", enforced instead of written down.

**Standing lines:**
- `vy-coord-` at $65 a day, owned by `merge-queue`.
- `vy-control-` at $1 a day, owned by `coordinator`. The control pod stops being exempt, so its cost shows on the pages.

**`budgets.toml`:**
- It's frozen, with a header that points to the site.
- `/api/spend/lines.toml` serves the live lines in the same format, read-only, for anyone who wants the file view.
- The coordinator stops committing lines.

**Who can do what:**

| Any viewer: you, root, the coordinator, and agents through the API | Only you, with your passkey |
|---|---|
| close a line, lower a cap, terminate or stop a pod, deny a request, revoke a token | approve a request, open, raise or extend a line, approve an envelope (later), change the guard's settings, delete a network volume |

Tightening needs no passkey; loosening does. Tokens are no longer minted by anyone: since Sep 30, every token is a request that you approve on `/approvals`, signed in with your own GitHub account ([token requests](verity-root store: `internal/token-requests-spec.md`)).
  - Adding a device needs the GitHub sign-in and an existing passkey.
  - The pages show which device enrolled and when.
  - If a passkey is lost, you remove it after signing in with GitHub, and enroll again.

### 2.5 The reaper, with no long-lived process

**The trigger.** Vercel Cron calls `/api/spend/reap` every minute, with the schedule `* * * * *`.
- Pro allows once a minute, with per-minute precision and up to 100 jobs per project. Cron jobs run on the production deployment.
- The call carries `Authorization: Bearer {CRON_SECRET}`.

**Each tick** is a TypeScript port of `guard.poll`:
1. Lock the one `reaper_state` row with `FOR UPDATE SKIP LOCKED`. Exit if the row is already locked, or if the last tick was under 30 seconds ago.
2. `GET /pods`, and GraphQL `myself`.
3. Add each pod's `costPerHr` times the real time since it was last seen, per pod and per line.
4. Trip lines at their caps. Pick the pods to terminate:
   - pods on tripped lines;
   - pods past their recorded expiry, plus the lease's 15-minute grace, so the on-pod lease fires first;
   - pods older than their line's `max_pod_hours`;
   - uncovered project pods, after the grace;
   - every project pod, at the balance floor.
5. Terminate first, then commit the state and the events.

A failed commit is recomputed on the next tick from real elapsed time. Terminations are idempotent, and they're deduplicated for 10 minutes, as today.

**Parity.** The guard's own test cases become shared JSON cases, run against both the Python guard and the TypeScript port. The port then runs in shadow beside the guard (§6) before it enforces anything.

**When it's late or down:**

| What fails | What happens | How much can run over |
|---|---|---|
| A tick is late, or missed: Cron is best effort, with no retry | The next tick counts the real elapsed time, so no spend is lost; only enforcement slips. | about $0.32 a minute at today's $19.39 an hour; at most $1.33 a minute at the account's $80 limit |
| Duplicate or overlapping ticks | The second finds the lock, or a recent tick, and exits. | nothing |
| Cron stops: a Vercel incident, or a rollback, since a rollback doesn't update crons | The steward on the control pod also calls the reap endpoint every minute, with a trigger-only token and no RunPod key. The lock makes double triggers harmless. If both stop, the create gate goes stale after 3 minutes and refuses creates. | running pods, until their leases end |
| The site or Neon is down | No creates and no extensions. Pods end on their on-pod leases and idle guards. RunPod's $80-an-hour limit still holds. | each pod's lease × its rate |

**The pool's leases.**
- Today pool pods may live 168 hours. If the site were down, a pool pod could run that long on its lease.
- So the pool should use 12-hour leases that the queue extends every hour through the site. A site outage then costs at most 12 hours of pool: about $54 at 8 pods. RC agrees that 12-hour leases, extended hourly, suit the queue.

**Cost.**
- About 43,000 invocations a month, each a couple of seconds, well within Pro's included usage.
- The ticks keep Neon awake, so it moves to Launch at about $19 a month, which you've approved. That's this proposal's main new cost.

### 2.6 SSH and `run --on`

- **SSH isn't a spending credential,** as the contributor plan says. `RUNPOD_SSH_KEY_B64` stays with the agents.
- The site passes `PUBLIC_KEY` through on create.
- The one SSH-related call it refuses is changing the account's SSH keys (`updateUserSettings`), since RunPod puts those keys on every pod. Only you change them, in the console.
- `run --on` gets the host and port from `GET /pods/{id}` through the site, and asks the site before extending a lease (§2.3). Nothing else in it changes.
- The machine files, `machines.toml` and `machines.d/`, don't change.

### 2.7 The always-on pods

**The control pod no longer holds the account key.** After the switch, it holds:
- the `steward` token, for the reaper and the backup trigger;
- the `merge-queue` token, for the pool;
- the steward's R2 keys;
- PR 3's GitHub App key, if that's approved.

That changes PR 3's blast radius. A compromised control pod could spend at most the `vy-coord-` line, $65 a day, instead of anything on the account.

**What happens to each thing it runs:**

| Now | After |
|---|---|
| the budgets guard | retires, once the site's reaper enforces (§6) |
| the older `vyv-` guard and `/root/dm` | already retired: RC stopped `guard-vyv.sh` at 9:24 AM PT. Deleting the scripts is RC's to do. |
| the steward's reaper | terminates through the site, with `steward` |
| the pool manager | creates `vy-coord-q{n}` through the site, with `merge-queue` |

**The pool** stays on its standing line, with 12-hour leases (§2.5).

**SP1:** on demand, so it needs no standing line. Its pods take lines like any lane's.

### 2.8 Other projects on the same account

`porep-inference` and `autoproof-max-context-20260715` belong to other projects on this RunPod account. Those projects are being archived, so the design doesn't cater for them (your answer, 9:26 AM).
- Once the old key is disabled, anything of theirs that uses it stops.
- So before that, I list their pods and volumes, read-only, and confirm them with root (§6, step 6).
- I don't disable the key myself.

## 3. The pure CLI: keeping friction at zero

### 3.1 How lanes call RunPod today

- **The `research` tool:** its four REST calls and one GraphQL read (§1.7).
- **`runpodctl`:** the lease fallback on the pod, with the pod-scoped key, plus `ssh info` and `get pod` in a few lanes.
- **Not used:** the Python SDK, and raw GraphQL or REST outside the tool. The `/root/dm` scripts are retired.

### 3.2 The options, least friction first

**(a) The site speaks RunPod's own API.** It serves the same paths, bodies and responses as RunPod's REST v1 at `https://{site}/runpod/v1`, plus an allowlisted GraphQL at `/runpod/graphql`.
- **Both clients can point there.** I checked the source:
  - `runpodctl` (`internal/configenv/configenv.go`, at `4351fca`) reads `RUNPOD_API_URL` for REST, `RUNPOD_GRAPHQL_URL` for GraphQL, and `RUNPOD_API_KEY`. The same can go in its config file.
  - The Python SDK (`760aea2`) reads `RUNPOD_API_BASE_URL`, and serves GraphQL from `{base}/graphql`.
- **What works:** with those variables set to the site and a site token as the key, stock `runpodctl pod create | list | get | stop | start | delete` work unchanged.
  - Only the calls that create spend are checked: create, resume, updates, and volume creation or growth.
  - Reads pass through, and SSH doesn't touch the API at all.
- **What doesn't:**
  - The SDK creates pods with GraphQL mutations (`podFindAndDeployOnDemand`). The site would have to parse and check those as a second create path.
  - `runpodctl ssh add-key` changes account settings, which the site refuses.
  - Logs and serverless use other hosts, which we don't use.
- **The cost:** we track RunPod's API as it changes, at least for the calls we pass through.

**(b) A thin wrapper in the `research` tool,** with today's verbs: `research pods create | list | get | terminate`, speaking the site's own JSON API.
- **Friction:** none for `research` users, since the verbs don't change. The few `runpodctl get pod` and `ssh info` uses would switch to `research pods get`.
- **Surface:** smaller, since there's no RunPod API to mirror. But stock `runpodctl` and the SDK would stop working with anything but the old key.

**(c) A restricted RunPod key.** RunPod's keys are All, Restricted or Read Only.
- Restricted chooses access per API: none, read or write for GraphQL and REST, and per serverless endpoint. RunPod's own blog calls GraphQL write access "extremely powerful": it creates, edits and deletes pods.
- **There's no scope per pod, per name or per dollar.** So any key that can create a pod can create any pod, for as long as it likes.
- A Read Only key could let agents read without the site, but it's a second key to manage, for little gain.
- It adds no friction, but it can't enforce lines, so it doesn't do the job.

### 3.3 Recommendation: (a), limited to the calls we use

- **Build the site's endpoint as a RunPod-compatible subset:** the same paths and JSON, for exactly the calls in §2.3. Everything else answers with a 403 that names it.
  - REST: `POST /pods`, `GET /pods`, `GET /pods/{id}`, `DELETE /pods/{id}`, `POST /pods/{id}/stop` and `start`, the network volume list, and the billing reads.
  - GraphQL: `myself` and `gpuTypes`.
- **The `research` tool gets one change,** about 20 lines. `runpod.py` reads its REST base and GraphQL URL from `RUNPOD_API_URL` and `RUNPOD_GRAPHQL_URL`, the same names `runpodctl` uses.
  - Every `research` verb then works unchanged, including the gate and the lease arming.
  - The SSH call to the control pod for the gate goes away, since the site checks at create. `RESEARCH_GUARD_HOST` retires.
- **Stock `runpodctl` pod verbs work too,** with the same three variables. That's the pure CLI, at no extra cost.
- **Not built:** the SDK's GraphQL create. Nobody uses the SDK; if someone does, it's a contained addition.
- **The site's own extras** sit beside it at `/api/spend/…`: requests, extensions, envelopes and status. They get the `research pods line-request` and `research pods extend` verbs.

It's the most elegant because there's:
- one API shape, RunPod's own;
- one small client change;
- no new verbs for creating, listing or terminating;
- nothing for an agent to learn except that a create can now answer "no line" with a link to request one.

The cost is keeping about eight RunPod calls compatible. Contract tests, recorded from current `runpodctl` and `research` requests, catch drift.

## 4. Other spend: what can be brokered

| Service | Spend now | Brokered? | On the spend pages |
|---|---|---|---|
| RunPod pods | $19.39 an hour at 8:30 AM PT | **Yes:** every create, resume, update and delete | lines, burn, pods |
| RunPod network volumes | 1,450 GB, about $92 to $102 a month, not seen by today's guard | **Yes:** create, grow and delete through the site, under monthly volume lines | each volume, its monthly cost and its project |
| Cloudflare R2 | the evidence store, 1.21 TB, about $18 a month plus operations; its public half, `verity-public`, sits in the free tier | **Credentials, not spend.** R2 has no hard cap. The store broker holds `verity-public`'s key. Later, the site could hold the parent key and mint scoped, short-lived keys per writer, as `research data mint-credential` does offline, so no agent keeps a long-lived key. | storage and operations, from Cloudflare's analytics API, with a read-only analytics token (a click for you) |
| Vercel | Pro, plus usage | **No.** It's the broker's own host, so its Spend Management stays its cap: $200 for the compute team, notify only (§9). | a link, and the budget setting |
| Neon | about $19 a month on Launch, approved | No | its usage |
| Cursor (agents) | the team's usage | **No.** Its spend and per-user limit APIs are Enterprise-only. | a link |
| Slack (not set up yet), GitHub | fixed seats, and GitHub Pro for PR 3's rulesets | No | fixed monthly lines, entered by hand |

There are no other paid APIs to add (your answer, 9:26 AM). So "a broker for all expenditure" holds for RunPod: its pods and volumes are nearly all the variable spend. For the rest, the site can be one place to see spend, but not one place to control it.

## 5. The spend pages


| Page | Shows |
|---|---|
| `/admin/spend` | the balance, current spend per hour, spend today and this week, spend by line, the reaper's last tick and any faults |
| `/admin/spend/lines` | each line: prefix, owner, cap, spent, committed, headroom, expiry, max pod hours and status, with Close for anyone, and Raise or Extend with the passkey |
| `/admin/spend/lines/{prefix}` | one line's burn over time, in 5-minute buckets, its pods, and every change, with who approved it |
| `/admin/spend/pods` | running pods: name, line, GPU, rate, age, the site's expiry and the on-pod lease, cost so far, and SSH target, with Terminate |
| `/admin/spend/requests` | open requests with Approve (passkey) and Deny, the envelopes, and past requests with who decided |
| `/admin/spend/history` | every event: creates, refusals and why, terminations and why, trips, approvals, closes and reaper faults, filtered by line, token or pod |
| `/admin/spend/other` | §4's rows that aren't brokered |

`/admin/tokens` and `/admin/writers/{name}` are shared with the store pages, so one writer's uploads and pods show on one page.

## 6. Migration and rotating the old key

1. **Build and test on a preview** against the fake RunPod. The preview has no key.
   - It stays on previews until the research coordinator and the red team have reviewed it: until then, no agent's `RUNPOD_API_KEY` points at it, and it doesn't take over from the guard (your answer, 9:26 AM).
   - Contract tests against the real RunPod API need a budget line. I send root an estimate first.
2. **Shadow run.** You create a new key and paste it into Vercel (§7). The site's reaper runs beside today's guard. It tallies, and records what it would terminate, but terminates nothing. We compare it with `guard-budgets.json` until the two agree through a pool cycle and one lane's full run.
3. **Move the lines.** Import `budgets.toml` into `spend_lines`, with the same validation. Freeze the file, and switch line requests to the site.
4. **Switch the clients:**
   - **Cursor secrets:** `RUNPOD_API_KEY` takes the `agents` token as its value, so no agent's setup changes. Add `RUNPOD_API_URL` and `RUNPOD_GRAPHQL_URL`, which aren't secret.
   - **Your laptop:** I put the token and URLs in `~/.runpod/config.toml`.
   - **The control pod:** `steward` and `merge-queue` replace the account key, and the steward adds the backup trigger.
5. **Enforce.** The site's reaper switches from shadow to enforcing, and the budgets guard stops.
6. **Rotate.** You disable the old key in RunPod's console, under Settings, API Keys. Disabling can be undone.
   - Once nothing has broken through a pool cycle and an overnight run, you delete it.
   - Pods' own keys aren't affected.
   - First, I list the other projects' pods and volumes and confirm them with root (§2.8): anything else on the old key stops when it's disabled. You disable the key; I don't.
7. **Rollback,** until the delete: re-enable the old key, and put the old config back.

**Why one `agents` token to start:** Cursor secrets reach every cloud agent, so per-lane tokens there would all be readable by every agent anyway. Lines still cap every lane. Per-lane tokens make sense once lanes hold their own secrets.

## 7. What you click

1. **In RunPod's console:** Settings, API Keys, Create, named `verity-site-broker`, with full access. The site itself refuses everything but §2.3's calls. Paste it into Vercel on `website-docs`: Settings, Environment Variables, `RUNPOD_API_KEY`, Sensitive, Production only. Nobody else sees it.
2. **In Vercel:** move the Neon database to Launch, at about $19 a month, as you've approved.
3. **On the site:** enroll your passkey at `/admin/passkey`.
4. **In Cursor's dashboard:** set the `RUNPOD_API_KEY` secret to the `agents` token. You mint it on `/admin/tokens` and copy it straight across, and I add the two URL variables.
5. **Optional, once the Slack workspace exists:** an incoming webhook for `#spending`. Paste its URL into Vercel as a Sensitive variable.
6. **After the switch, in RunPod:** disable the old key, and later delete it.

## 8. Effort

- **The site,** on top of the store broker's 1,000 to 1,500 lines, comes to about 3,000 lines:
  - the RunPod-compatible subset and its checks: about 600 lines;
  - the reaper, a port of `guard.poll` and `budgets.parse`, with the shared cases: about 600, plus tests;
  - lines, requests and per-line approvals: about 300, with envelopes about 100 more, later;
  - passkeys, with a WebAuthn library: about 200;
  - the spend pages: about 1,000;
  - the optional Slack post: about 30.

  It moves money, so the coordinator and the red team should both review it.
- **Verity:**
  - the URL override in `runpod.py`: about 20 lines;
  - `pods create` skipping the SSH gate against the site: about 30;
  - `pods line-request`, and `pods extend` against the site: about 150;
  - tests.
- **Operations:** the control pod's configuration, the steward's backup trigger, the queue's token, and retiring the guards.

## 9. Risks

- **The separation holds only if agents can't deploy production.** Production code can read `RUNPOD_API_KEY`, and today agents deploy the site with your Vercel login.
  - Until deploys are reviewed merges and agents hold at most Vercel's Developer role, the broker enforces lines against mistakes, not against an agent that sets out to get around them.
  - The passkey stops agents from approving through the API. It doesn't stop a production deployer from changing the check.
  - The stakes are higher than for the store: this key spends money.
- **The site becomes the single point of spend.** When it's down, nothing new starts, and running pods end on their leases. That's closed, but it stalls the pool and the lanes.
- **Vercel's Spend Management doesn't pause the broker.** The compute team's budget is $200, and its 50, 75 and 100% thresholds only notify: none pauses production (checked read-only through Vercel's API this morning; nothing was changed). It's on the compute team's dashboard, under Settings, then Billing, in the Spend Management section, shown as the On-Demand Budget; changing it needs the Owner or Billing role. It would matter only if someone set it to pause.
- **Cron is best effort.** Missed or duplicate ticks are handled by elapsed-time tallies, the lock and the backup trigger (§2.5).
- **Automatic reload removes the balance as a backstop,** and nothing relies on the floor (RC). The port keeps it as a tripwire for a failed reload, for parity with the guard. Only line caps and the $80-an-hour limit remain, so the headroom rule and the pool's shorter leases matter more.
- **The other projects lose access** when the old key is disabled. They're being archived, and I confirm their pods and volumes with root first (§2.8).
- **RunPod's API can change** under the compatible subset. Contract tests catch that.
- **Updates could escape a line,** by renaming a pod or dropping its lease. They're refused (§2.3).
- **A new rule may refuse creates that pass today:** the headroom check. It's the rule the vLLM lanes already follow by hand.

## 10. Answers, and what's still open

**From the research coordinator** ([its answers](verity-root store: `internal/spend-broker-rc-answers.md`), 16:19Z), folded into §1 to §9:
1. **SP1** isn't always on: its pods are on demand.
2. **`/root/dm`** had one live process, `guard-vyv.sh`, stopped at 9:24 AM PT. `runpod.py`, `budget_cap.py`, `balance_floor.py` and `deadline.sh` are retired and can be deleted.
3. **The control pod's key is the same key as Cursor's `RUNPOD_API_KEY`.** It's one key everywhere, so the broker holding it is the real separation step.
4. **The steward's reap** needs only list, get and terminate, with the SSH host and port coming from get.
5. **No `vy-coord-q{n}` queue pods exist yet.** 12-hour leases, extended hourly, suit the queue.
6. **Nothing relies on the balance floor.**

Its corrections to §1: four lines had expired; on the control pod, `pods create` needs `RESEARCH_GUARD_HOST=local`; the create gate fails closed; the idle guard waits on unfetched runs; and the two guards overlapped on `vyv-rf-epoch-` until the old one was retired.

**From you, at 9:26 AM:**
1. **The other projects** are being archived, so the design doesn't cater for them. I list their pods and volumes and confirm with root before the old key is disabled, and I don't disable it myself.
2. **Vercel's Spend Management** is on for the compute team, at $200, and only notifies (§9).
3. **Envelopes:** per-line approval is built first, and envelopes wait as an add-on.
4. **Other paid APIs:** none.

**Still open:**
- **Envelopes:** whether root may open lines inside an envelope you approve, such as a night's plan.
- **The review gate:** the research coordinator and the red team review the broker before any agent's `RUNPOD_API_KEY` points at it (§6).

`#spending` isn't live, because the Slack workspace isn't set up yet, so the design doesn't depend on it (§2.4).
