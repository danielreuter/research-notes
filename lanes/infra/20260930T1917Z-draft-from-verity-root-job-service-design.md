---
id: 20260930T1917Z-draft-from-verity-root-job-service-design
campaign: verity
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: verity-root
---

> Copy of verity-root's `docs/job-service-design.md`, posted for infra on request
> (`note:20260930T1905Z-handoff-from-infra-alert-sink-one-change-and-docs`). Links of the form
> `/cursor/stores/bc-36415049-…/docs/X.md` point into verity-root's store; ask verity-root for any you need.

---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

# The job service: the Scheduler's batch jobs, with the merge queue on top

**For:** Daniel. **Written:** Tue Sep 29, about 1:10 PM PT, by the merge-queue lane; **revised** about 1:20 PM PT for root's Control split, and about 3:10 PM PT to fold in §6 of the [research velocity plan](research-velocity-plan.md): stage 1's corrections, stage 1.5 (trains the service lands), readiness, and lane-branch pushes without rulesets; **renamed** about 3:15 PM PT, with root's one-Scheduler decision (§7), and about 4:00 PM PT to Daniel's final names: Control is the API server and the Scheduler, and Compute is Interactive and Batch.

Daniel approved one job service:
- a jobs table and an append-only events log in the site's existing Neon Postgres;
- a small claim, heartbeat and complete API in the Vercel control app (the docs site);
- workers that pull jobs over HTTPS and hold a lease they renew while running.

CI and notifications come first; research runs join later, when there's a real need.

**Related:**
- [infra overview](infra-overview.md): today's machinery;
- [spend broker](spend-broker-via-site.md): the proposal the Scheduler's interactive kind (pods, lines, pod leases, reaps) and the API server's tokens are built from;
- [merge-queue credential proposal](merge-queue-credential-proposal.md): the GitHub App, whose key now stays in Vercel (§4);
- [infra plan, change 5](infra-refactor-plan.md): the queue's rules;
- [CI notes](ci-notes.md): its decisions so far.

## Where this sits: Control is the API server and the Scheduler

Daniel settled the names with the diagram agent on Sep 29, about 4:00 PM PT (`internal/infra-diagram-control-plane-for-root.md`). Control (Vercel) decides, Compute (RunPod) runs, and Storage keeps; nothing in Control runs work. **Compute is Interactive** (an agent's pod) **and Batch** (the runners that claim jobs). We build all of it ourselves, with no SkyPilot.

| Card | What it is | Its timers (Vercel Cron, short functions) |
|---|---|---|
| **API server** | The single entry point every client calls: agents, the Console, runners and crons. It authenticates each call against the `tokens` table, and it issues every connection credential, each short-lived and scoped to one allocation or one store object. That covers SSH to an allocated pod, signed URLs and database access for storage, a runner's `jobs:work` token, a run's custody key, and a lane's one-hour git token. | expire staged uploads |
| **Scheduler** | Every allocation of compute, now or queued, as a Slurm or Kubernetes scheduler does. An agent's pod is an **interactive** allocation, answered at once or refused against the budget. A merge check or the nightly audit is a **batch** one: a job that Batch runners claim. Both count against the same budget lines, need the same approvals, and end with their lease (§7, decision 7). It starts and stops pods, hands jobs to runners, puts back jobs whose runner died, and lands merges on `main`, which is privileged like spending. The queue is rows in the Database (`jobs`, beside the `events` log), not a service. The merge queue is a job type (the merge check) plus a landing rule. | expire leases; reap idle pods; reconcile trains and the merge queue; add the nightly audit of `main` |

**Console** (Vercel: Approvals, Results) is an interface, not part of Control. It's a client of the API server that acts as the signed-in user, with no privileges of its own. It shows jobs, events, lines, tokens and approvals.

**Earlier names:** earlier drafts, and the documents they link, used three names that are now gone:
- **Broker:** its allocation side is now the Scheduler, and its credential side the API server.
- **Access:** the API server.
- **Job queue:** the Scheduler's batch kind.

Code names stay: `research jobs`, `/api/jobs`, the `jobs` table and the `jobs:*` scopes.

**Later, for the API server:** it issues per-pod SSH certificates from a CA installed at pod create, replacing the shared `RUNPOD_SSH_KEY_B64`, once teammates' agents share pods. Not now (root, Sep 29).

**Compute:** Daniel decided on Sep 30 to switch to SkyPilot with a standing cluster, and merge-train checks will run as SkyPilot jobs on the standing pool; see [project context](project-context.md). Until the migration plan lands, the parts of this design that assume our own runners claim jobs from our queue are on hold (the inventory is `internal/skypilot-migration/merge-queue-inventory.md`).

Cron is a trigger, not a service, and the merge queue isn't a card of its own.

## Summary

- **One table and one lease rule for all pod work.**
  - A job is a row: a kind, a payload, requirements, a priority, a dedupe key and a lease.
  - Workers claim with `FOR UPDATE SKIP LOCKED` and renew every minute while they run.
  - When a pod dies, the Scheduler's cron puts its job back in the queue after one lease, about 15 minutes. A multi-hour check just keeps renewing.
- **Worker auth: the API server mints a `jobs:work` token for each pod the Scheduler allocates,** bound to the RunPod pod id, and revokes it when the pod ends. Each claim also returns a lease token that only that job's renewals and completion accept.
- **The merge queue lives inside the Scheduler: a producer and a landing rule.**
  - The Scheduler's reconcile cron maintains `next`, the continuously built train, with GitHub's own merge API.
  - It adds one merge-check job per commit.
  - Once a commit's merge check passes, it fast-forwards `main` to that commit with the GitHub App's token.
  - The App's key never leaves Vercel, and no pod ever holds a token that can push.
- **Events: GitHub first, Slack when it exists.**
  - The Scheduler posts commit statuses on PR heads, which PR owners already receive through `subscribe_github_ci`. GitHub itself tells them a PR merged, through `subscribe_github_pr`.
  - Other events go to a per-lane Slack thread, once the Verity Slack workspace exists (decision 2).
  - The events table is the record, and a polling API reads it.
  - This replaces root's manual wake-up lists.
- **Build order:**
  1. turn today's `/tmp/launchv.sh` and per-pod chains into jobs;
  2. pull workers;
  3. events;
  4. the merge queue in the Scheduler;
  5. the pool.

## 1. Today: stage 0

The research coordinator (RC) runs merge trains by hand:
- `/tmp/launchv.sh` on its VM launches each train's `check` with `research run --on` onto one of the `vy-coord-t1` to `t5` pods, one train per pod.
- Each pod's work is a tmux chain of shell watchers (`tu-wait`, `to-wait`, `t3-stop`): wait for a regeneration, launch the check, stop the pod when it ends.
- A pod-prep script (`/tmp/lm/podprep.sh`) prepares a fresh pod by hand. Two fresh pods failed tonight before it ran (rc 127, no `uv`).

Each chain is a per-pod queue that exists only in tmux. Nothing records what's waiting, a dead pod is noticed only by a person, and nobody else can see the state. The Scheduler turns those chains into rows.

## 2. The schema

The tables go in the site's Neon database, beside `tokens`, `store_events` and the spend broker's tables (which the Scheduler's interactive kind folds in, §7).

```sql
create table jobs (
  id            bigint generated always as identity primary key,
  kind          text not null,              -- merge-check | lean-regen | audit-main; later research-run
  state         text not null default 'queued',  -- queued | running | done | failed | dead | cancelled
  priority      int  not null default 0,    -- higher first; see below
  payload       jsonb not null,             -- the kind's input, below
  requirements  jsonb not null default '{}',-- {"avx512": true, "min_mem_gb": 24, "min_cpus": 8}
  dedupe_key    text unique,                -- 'merge-check:{commit}': adding a job is idempotent
  enqueued_by   text not null,              -- token name
  enqueued_at   timestamptz not null default now(),
  not_before    timestamptz not null default now(),
  attempts      int  not null default 0,
  max_attempts  int  not null default 3,    -- counts errors only; a failure is final
  lease_s       int  not null default 900,
  lease_worker  text,                       -- the worker (RunPod pod id) holding it
  lease_hash    text,                       -- SHA-256 of this attempt's lease token
  lease_expires timestamptz,
  result        jsonb,                      -- {"outcome", "run_id", "summary"}
  finished_at   timestamptz
);
create index jobs_ready on jobs (kind, priority desc, enqueued_at) where state = 'queued';

create table job_attempts (
  job_id     bigint references jobs,
  n          int,
  worker     text not null,
  claimed_at timestamptz not null default now(),
  renewed_at timestamptz,
  ended_at   timestamptz,
  outcome    text,          -- passed | failed | error | lease-lost | cancelled
  run_id     text,          -- the research run id, which the evidence store holds
  detail     text,
  primary key (job_id, n)
);

create table workers (
  id           text primary key,        -- the RunPod pod id
  token_name   text not null references tokens(name),
  kinds        text[] not null,         -- what it may claim
  capabilities jsonb not null,          -- measured at boot by pod_setup.sh: avx512, mem_gb, cpus, tools
  created_at   timestamptz not null default now(),
  last_seen    timestamptz,
  retired_at   timestamptz
);

create table events (
  id      bigint generated always as identity primary key,   -- the subscription cursor
  at      timestamptz not null default now(),
  source  text not null,      -- jobs | broker
  kind    text not null,      -- job.finished | job.lease_lost | job.dead | queue.admitted | queue.ejected | queue.landed |
                              -- pr.merged | run.finished | pod.allocated | pod.stopped | spend.tripped
  subject text not null,      -- 'job:123' | 'pr:373' | 'run:r20260929-065044-476f' | 'pod:{id}' | 'lane:merge-queue'
  actor   text not null,      -- token name
  payload jsonb not null
);
create index on events (subject, id);
create index on events (kind, id);
-- append-only: a trigger refuses UPDATE and DELETE (the app connects as the database owner, so the trigger is the guard)
```

The [site spec](../internal/job-service-site-spec.md) refines this schema for stage 1, and it's what the site builds. It adds `workers.kind`, `jobs.lease_slot`, `cancel_requested` and `progress`, and `job_attempts.slot`.

**Job kinds, all work that runs on pods:**

| Kind | Who adds it | Payload | The worker does |
|---|---|---|---|
| `merge-check` | the RC (stage 1), then the merge queue (stage 4) | `repo`, `commit`, `base` for `merge_requires`, `verdict_pack` (art id or null), `timeout_s`; a change that needs the Lean agreement asks for `requirements.avx512` | a recorded `check` of that exact commit, `--verdicts-in` the pack, with custody to R2. It completes with the run id. |
| `lean-regen` | the RC, for Lean trains while trains last | `repo`, `commit`, `packages` | `audit.py --build --update` on the commit, and the regenerated record as an artifact |
| `audit-main` | The Scheduler's nightly cron | `commit`: `main`'s tip | a cold `check` (`--no-cache`) of `main`, which catches a cache key that misses an input. It also confirms that every commit `main` moved to since the last audit has a passing recorded check of that exact commit. |
| `research-run`, later | lanes | the `research run` argv, pod requirements, `timeout_s` | today's `run --on` work, pulled instead of pushed |

Reaps, lease expiry and the merge queue's reconciling aren't jobs: they're the Scheduler's timers, Vercel Cron functions.

**Priority:**

| Priority | For |
|---|---|
| 50 | a merge check marked urgent (the RC's "urgent" merges) |
| 10 + position | the merge queue's checks: older positions on `next` first, since landing waits for the oldest unfinished commit |
| 5 | `audit-main` |
| 0 | everything else |

Within one priority, the oldest job goes first.

**Leases and attempts:**
- **Claiming:** a claim sets `state = running`, a new lease token (its hash is stored, never the token), and `lease_expires = now() + lease_s`.
- **Renewing:** the worker renews every 60 seconds. With the 900-second default, a job survives about 14 missed renewals.
- **Expiry:** The Scheduler's expire-leases cron, once a minute, requeues every `running` job whose lease has passed. It records `lease-lost`, counts one attempt and writes `job.lease_lost`.
- **Errors and failures:**
  - **An error** (a lost lease, a dead run, a timeout, a missing `result.json`) is retried on any worker until `max_attempts`, then the job is `dead`.
  - **A failed check** is final, under the no-retry-until-pass ruling: `failed`, never requeued.
- **Cancellation:** a renewal's answer says `cancel: true` when the job was cancelled, for example when the merge queue ejected a PR and rebuilt `next`. The worker then stops its run by process group.

## 3. The API and auth for pod workers

The Scheduler's routes are served by the API server under `/api/jobs`, with the `/store` routes' token handling (over the `tokens` table, whose `actions` hold a token's scopes). A token's scope names what it may do:

| Scope | Holder | May |
|---|---|---|
| `jobs:enqueue` | `coordinator`, and later lanes | add and cancel their own jobs |
| `jobs:work` | one token per worker pod, minted by the API server when the Scheduler allocates the pod | claim the kinds its `workers` row lists |
| `events:read` | agents, root | read events, and register sinks |

**Endpoints:**
- `POST /api/jobs`: add a job. Idempotent on `dedupe_key`: a second add returns the first job.
- `POST /api/jobs/claim`: `{worker, kinds, capabilities}`.
  - It answers at once, with `204` when nothing is ready, and an idle worker asks every 30 seconds. Long-polling can come later.
  - A job is only matched to a worker whose capabilities meet its requirements, such as AVX-512 for the Lean agreement.
  - It returns the job, the attempt number, the lease token and its expiry, and the job's grants, valid for the lease and no longer:
    - a one-hour, read-only installation token for the repository, since pods fetch the commit themselves;
    - the run's R2 custody credentials, minted by the API server in place of the laptop.
- `POST /api/jobs/{id}/renew`: needs the lease token. It extends the lease, records progress (`{"step": "lean-audit"}`), and answers `{cancel}`.
- `POST /api/jobs/{id}/complete`: needs the lease token. It takes `{outcome, run_id, summary}` and writes `job.finished`.
- `GET /api/jobs?state&kind`, `GET /api/jobs/{id}` and `GET /api/jobs/stats`: queued counts by kind and requirement. The pool's scaling reads them (stage 5).
- `GET /api/events?after={id}&kind&subject`: the polling cursor.

**Worker tokens are API server credentials.** When the Scheduler allocates a CI pod, the API server:
1. mints a `jobs:work` token and a `workers` row for that pod id;
2. puts the token in the pod's environment;
3. revokes the token when the pod ends.

The Scheduler refuses a claim unless the token's pod id matches the `worker` it names and that pod is live under a project line. So a stolen token works only for that pod's lifetime, and only for the kinds its row lists.

**Custody isn't trusted to the report.** `complete` names a run id, but the landing rule reads the verdict from the Attempt in the evidence store, as `research merge`'s gate does today. A worker can't land anything by reporting "passed".

**What PR code on a CI pod can reach:**
- The job runs `check`, as it does today, in a clean environment (no `RESEARCH_*` variables, and a test asserts no secret reaches a workload), as a user without read access to the worker token's file.
- PR code can still make its own check pass: code under test can always do that, which is why the contributor plan reviews outside PRs before they get pod time.
- For now every PR author is on the team.
- Once outside contributors arrive, their jobs' exported verdicts never enter the shared pack, and their custody goes to quarantine.

## 4. The merge queue: a producer and a landing rule inside the Scheduler

**The producer** is the Scheduler's reconcile cron, once a minute. It is a TypeScript port of the state machine in `research queue` (#368) and of PR 3's dispatch and ejection from change 5. It never runs on a pod. On each tick it does the following:
1. **Syncs `next`, the continuously built train, through GitHub's API:**
   - It admits PRs by #368's rules: ready, an owner, no hold, and the grants `ci/queue.toml` requires, read from the store index.
   - It merges each admitted PR onto `next`'s tip server-side (`POST /repos/{owner}/{repo}/merges`), with the queue's `PR:`, `Head:` and `Owner:` trailers in the message. A `409` is a conflict, and the PR's owner is told.
   - It rebuilds `next` after an ejection by moving the ref back (`PATCH …/git/refs/heads/next`, forced) and merging the PRs after it again.
2. **Adds one `merge-check` job** per commit on `next` that has none. The dedupe key is `merge-check:{commit}`, the priority follows the commit's position, and the payload carries the current verdict pack.
3. **Reads finished merge checks:**
   - A passing check's exported `verdicts.tar.gz` joins the pack, for team PRs only.
   - A failing check ejects the PR at the earliest red commit, once every earlier commit has a result. The producer then cancels the jobs above it, rebuilds `next` and tells the owner.
4. **Posts commit statuses:** `queue/admission` and `queue/check` on each PR's head.

**The landing rule, which is privileged:** `main` fast-forwards to the newest commit on `next` that has a passing recorded `check` of that exact commit.
- "Passing" means an Attempt in the evidence store with state done, rc 0, that source commit and a clean tree, and with the steps `merge_requires` asks for passed. That's `research merge`'s gate, ported and read from the store index.
- The update is `PATCH …/git/refs/heads/main` with `force: false`, so GitHub itself refuses anything but a fast-forward.
- The landing writes `queue.landed`. GitHub marks the landed PRs merged, and their owners' `subscribe_github_pr` delivers it.

**Stage 1.5 pulls the landing rule forward.** Before `next` exists, the RC names trains, and the service builds, checks and lands them with this same rule. When `main` moves under a train, the train is rebuilt from the same heads and checked again, at most three times. The site spec's §9 has the routes and the reconcile, and `train_vectors.json` has the cases.

**Lean records in trains.** GitHub's Merges API runs no custom merge driver, so it can't use #447's `tools/lean/merge.py`. The Scheduler therefore computes the record merge itself, with a port of `merge()`, and writes the result onto both sides of the merge step through the Git Data API. The Merges API then merges every other file. When `merge()` refuses, the train falls back to a `lean-regen` job on its tip, and commits the regenerated record before the check.
- **Chosen over building Lean trains on a runner with the driver installed,** because it keeps the service the only writer of `train/*`, with no push credential on a runner and a result the service can reproduce.
- **A wrong merge can't land:** `check`'s Lean audit rebuilds every record on the train's tip.

**Stage 1.6 stacks the trains.** Stage 1.5 builds every train on `main`, which costs nothing while it runs in shadow but would make each landing rebuild every other train. So before the switch-over, trains stack on the train ahead, as the RC's hand trains do, with a window and culprit finding borrowed from Zuul and bors (site spec §10).

**`research queue` (#368) stays the reference implementation.** Its tests become shared JSON cases, which run against both the Python and the TypeScript versions, as the spend broker does for the budgets guard. The port runs in shadow first: it builds `queue-shadow` and lands nothing, beside the RC's trains. The switch-over needs the RC's agreement.

**The GitHub App's key stays in Vercel.**
- It's a Sensitive, Production-only variable, like the RunPod key in the spend broker.
- The App is `verity-merge-queue` (ID 5127737, installation 166299669), created by Daniel on Sep 29.
- The Scheduler's train routes, reconcile, landing and crons use it, minting one-hour installation tokens narrowed to `verity`. The permissions are Contents (write), Pull requests (write, for the sweep and for marking a ready PR ready for review), Metadata, and Commit statuses (write).
- The API server also mints one-hour tokens from it for lane-branch pushes, below.
- No pod, the control pod included, ever holds the key or a token that can push. The [credential proposal](merge-queue-credential-proposal.md) put the key on the control pod, and this supersedes that answer.
- **Blast radius:** whoever controls the site's production deployment or its environment can push `next` and `main`, as they could already spend through the Scheduler.
- **The checks against that:**
  - the main guard, below (the repository is private on a free plan, so rulesets aren't available);
  - the nightly `audit-main` job;
  - Vercel's own deployment protection and audit log.
- **Revocation:** suspend the App's installation on GitHub; every token stops at once.

**Pushes to lane branches, and keeping `main` safe without rulesets.** Root relays pushes by hand for VMs whose GitHub token lapsed (velocity killer 9), and `main` has no protection, since rulesets need GitHub Pro on a private repository (checked: the API answers 403).
- **The relay goes.** The API server's `POST /api/git/token` (scope `git:push`) mints a one-hour installation token of the same App, narrowed to Contents (write) on `verity`. It writes a `git.token` event naming the caller. A git credential helper, `research git credential`, fetches one when git asks, so a long-running VM pushes its lane branch with plain `git push`, however long it has been up.
- **The main guard keeps `main` safe.** It's a check in the Scheduler's minute cron:
  - it compares `main`'s tip with the last commit the service landed (its `trains` rows);
  - when they differ, it moves `main` back with a forced ref update, and writes `main.restored` with the commit it found and the pusher GitHub reports.
  - It only reports (`main.moved`) until Daniel explicitly OKs automatic resets of `main` (root, Sep 29, 22:15Z). A reset is destructive, so neither the RC's agreement nor the switch-over turns it on.
  - A rogue push to `main` lives for at most a minute. Nothing lands from `main` by name, since every landing is an exact commit the gate checked.
  - This also closes a hole we have today: every agent's Cursor GitHub token can push `main`.
- **Why not the alternatives:**
  - **A bundle-push route** keeps the credential in the service, but a Vercel function would have to recreate each commit through the Git Data API and prove the shas match. That's heavy, as the velocity plan says.
  - **A second, branch-only App** only helps with rulesets to keep it off `main`, and we have none, so it isn't needed. The same App serves, and no request goes to Daniel.
  - **Rulesets,** if the repository ever moves to Pro or goes public, add prevention on top of the guard, with nothing else changed.

## 5. The events log, and how agents subscribe

**The table is the record.** The Scheduler and the API server both write to it:
- **The Scheduler:** a job finished, lost its lease or died; a pod was allocated or stopped; a spend line tripped; a PR was admitted, ejected or landed; a run finished.
- **The API server:** a credential was issued (a worker token, a git token), with who asked.

Nothing is ever updated.

**Delivery goes where agents can already be woken.** A Cursor agent wakes on a GitHub CI result on a branch, a GitHub PR event, a Slack message or a timer. So:

| Event | How it reaches its agent | What the agent does |
|---|---|---|
| Admission waiting, check passed or failed, ejected | The Scheduler's commit statuses `queue/admission` and `queue/check` on the PR's head | the PR's owner keeps a `subscribe_github_ci` on its branch, and a failure (an ejection) wakes it |
| PR merged | GitHub's own PR event, once the landing moves `main` | the owner's `subscribe_github_pr` delivers it. Nobody relays. |
| A run finished, a job died, a lane's pod was allocated or stopped | a per-lane Slack thread in one channel (decision 2), posted by the site's bot | the lane's agent keeps a `subscribe_slack_thread` on its thread, and root subscribes to the channel for a summary |
| Anything, for a slower reader | `GET /api/events?after={cursor}` | an agent with a timer reads from its cursor |

- **Sinks:** a `sinks` table (kind, filter, target, delivery cursor) records who gets what: `github-status`, `slack-thread` or `notes-handoff`.
- **Delivery:** runs in the Scheduler's reconcile tick, which delivers new events to each sink, from its cursor, idempotently.
- **The durable record** in the notes repo, the handoff an ejection writes (as in #368), is one more sink.

**What this replaces.** Today root keeps lists of who to wake when a PR merges or a run ends, and relays each one by hand. After stage 3, PR owners are woken by GitHub. Lanes are woken by their Slack thread, or by the polling API until Slack exists.

## 6. The build plan

Each stage is useful on its own, and the RC's trains keep working at every stage.

| Stage | What | Who | Replaces |
|---|---|---|---|
| **1. Batch jobs, with today's pods** (**live in production** since Sep 29, about 3:45 PM PT: the site's migration 004 and its crons `/api/cron/jobs-expire-leases` and `/api/cron/jobs-audit-main`; the site spec's changes list, item 10, has where it differs from this design) | The `jobs`, `job_attempts`, `workers` and `events` tables; the add, claim, renew and complete routes; the expire-leases cron; a Console page listing jobs. A **dispatcher** (`research worker --dispatch`, [#442](https://github.com/danielreuter/verity/pull/442)) claims `merge-check`, `lean-regen` and `audit-main` jobs and runs each with today's `research run --on` onto a free `vy-coord-t*` pod, one job per pod at a time. It runs on the RC's VM, because the control pod has no R2 parent pair to mint custody with. Its probe measures a pod: its capabilities, whether a run is live on it, and whether its `pod_setup.sh` has reported done, with a marker (`~/.research/pod-setup.json`) the script removes first and writes last. **No job is claimed or started on a pod until its setup reports done**, so a launch chain can't start a check while setup still runs. That's how train TVC lost about an hour on Sep 29: `research run` returns at launch, and the preflight then refused the half-set-up pod. #440's `tools/check/preflight.py` is the one place that decides a pod is unprepared, when `research run --on` runs it before claiming. A refused pod is benched, and its job retried on another. A job asks for AVX-512 only when its tree does: `upstream.json`'s rustflags need it and the change touches the Lean agreement's `merge_requires`. Every job asks for `min_lease_s`, so no check starts on a pod whose lease ends first. `lean-regen` is keyed on its Lean inputs, so trains with the same Lean tree share one run. A nightly cron adds **`audit-main`**, a cold `check --no-cache` of `main`, before any widening of reuse (velocity plan item 5). `launchv.sh` becomes `research jobs add merge-check --commit …`. | the site: website agent (bc-41cff24f); `research jobs` and the dispatcher: merge queue | `/tmp/launchv.sh`, the per-pod tmux chains and the pod-prep script. What's waiting and running is visible to everyone in Console. |
| **1.5. Trains the service lands** (as soon as the App's variables are in Vercel) | The RC names a train (`POST /api/trains`). The Scheduler merges each PR's head onto `train/{id}` through the Merges API and adds one `merge-check` of the tip. Once it passes, the reconcile cron checks the Attempt with `research merge`'s gate, ported, and fast-forwards `main`. The sweep then closes stacked PRs that landed and retargets their children, with Pull requests (write). `land: false` runs it in shadow beside the RC first. The main guard and the API server's lane-branch tokens (§4) come in the same stage. Reference and shared cases: `research/jobs/trains.py` and `train_vectors.json` in #442; site spec §9. **With it, four job rules** from the open-source survey (site spec §10.1): a dedupe key held only by a live job or a verdict, concurrency keys with a limit, a start deadline that raises `job.unschedulable`, and error retries that back off and avoid the pod that failed. | the site: website agent; the reference and cases: merge queue | the RC's hand landings and pushes to `main`, root's relays, wake lists and hand closing |
| **1.6. Stacked trains and culprit finding** (after 1.5 runs in shadow, before the switch-over) | From the [open-source survey](open-source-stack-map.md), site spec §10.2 and §10.3: each train builds on the tip of the one ahead, only the trains behind a failure rebuild, and an adaptive window caps the stack (Zuul's rule, sized to the pool: start 4, +1 per landing up to 8, halved per failure, floor 2). A failed train is bisected by its own per-PR commits; its culprit leaves, its passing part lands, and the rest is rebuilt. A PR is named into a train only after a cheap `pr-lint` job (the tree's own lints) passed on its head. | the site: website agent; the reference and cases: merge queue | the rebuild storms of stacked hand trains (killer 5), hand bisection, and trains lost to a lint (N2) |
| **2. Pull workers** | `research worker` runs on each CI pod, started at boot after `pod_setup.sh` (later a baked tools image). It claims over HTTPS with the token the API server minted at allocation, and runs `check` locally with custody, from a checkout with `.git` and an allowlisted environment. It renews while it runs. **A claim extends the pod's allocation lease** to the job's timeout, within the line's headroom, by the same lease rules as an interactive pod; a refusal leaves the job queued rather than killed mid-run. The dispatcher retires. | the merge queue; the API server mints worker tokens, and the Scheduler extends leases | the SSH push of `run --on` for CI. Dead pods are handled by lease expiry. |
| **3. Events** | Commit statuses on PR heads, the `sinks` table and its delivery, per-lane Slack threads once Slack exists, and the notes sink. The Scheduler writes its allocation, stop and spend events for interactive pods too. | the site; root changes its wake-ups | root's manual wake-up lists |
| **4. The merge queue in the Scheduler** | The reconcile cron and the landing rule (§4), a TypeScript port of #368 and change 5's PR 3, checked against #368's shared cases. Admission is on the `ready` label (§7), and `next` replaces the RC's named trains as the producer. Then a shadow evening on `queue-shadow`, and the switch-over with the RC's agreement. | the port: the website agent, or the merge queue lane in the website repo with its agreement; the shared cases: merge queue | named trains |
| **5. The pool** | Two pods always on, up to 8 while merge checks wait. The Scheduler's reconcile reads `GET /api/jobs/stats` and allocates CI pods itself, as interactive-kind allocations on the `vy-coord-` line. It refuses what that line can't afford, so scaling stops before the cap, and the pool recycles its always-on pods before the line's maximum age. It uses 12-hour leases, extended hourly. | the merge queue, with the Scheduler's interactive kind | creating CI pods by hand |
| **Later** | `research-run` jobs, when a lane needs pulled runs. Heavy-test jobs deduplicated by their per-test key, after the per-test cache (bc-d66f1270). Every test's outcome recorded with its key, for the flake detector. Vercel Queues, if a short step inside Vercel wants one, such as event delivery. | — | — |

**The first step is small** on both sides. For the site: four tables, four routes, one cron function and one Console page, in the same pattern as `/store` and the spend broker's proposal. For Verity: `research jobs` (add and list) and the dispatcher, a few hundred lines in `tools/research`.

**Cost:** nothing new beyond Neon's Launch plan, which Daniel already approved for the spend broker.
- A running job renews once a minute: about 11,500 writes a day at 8 busy pods.
- Idle workers back off to one claim every 30–60 seconds.
- That's roughly 15,000–25,000 function calls a day at full pool, which the website agent should check against Pro's included usage.

## 7. What changes from change 5, and decisions for Daniel

**What changes from change 5:**
- **The queue's live logic moves into the site,** as root's split implies. `research queue` (#368, Python, on `main`) becomes the reference implementation and the source of shared test cases.
- **It no longer runs on the coordinator's VM or on a pod.** Its git work becomes GitHub API calls, so no push credential touches RunPod.
- **Verdict packs** (#373, on `main`) and `ci/queue.toml`'s admission rules are unchanged, and the landing rule is `research merge`'s gate as before.

**Decisions, approved by Daniel (Sep 29, about 1:25 PM PT):**
1. **The GitHub App's private key lives in Vercel,** used only by the Scheduler's reconcile and landing. No pod holds a token that can push. This replaces the credential proposal's control-pod answer; the App's permissions and the rulesets are unchanged.
2. **Slack for events that aren't about a PR, but not yet.** For now, PR events go out as GitHub commit statuses and merge events, and everything else through the polling API and notes handoffs. The per-lane Slack threads in §5 wait for the Verity Slack workspace.
3. **Team PRs only at first.** Outside contributors' jobs get the contributor plan's review before pod time, quarantine custody and no verdict export into shared packs, when the first outside contributor arrives.

**Decisions, Sep 29 afternoon (Daniel, via root):**
4. **The App now, not at stage 4:** `verity-merge-queue` is created, with Pull requests (write) so the sweep can close and retarget stacked PRs. Train building and landing are stage 1.5, and `audit-main` is stage 1.
5. **Readiness is an explicit `ready` label.** `research queue ready PR` writes it on `pr:{n}@{head}`, a new head drops it, `hold` keeps a PR out, and draft state is ignored. This keeps drafts from sitting unflipped without letting unfinished ones land. It replaces the merge-request note. [#446](https://github.com/danielreuter/verity/pull/446) puts it into `research queue`, and the site's port will read the same label.
6. **Lane-branch pushes:** one-hour tokens from the API server and the main guard, as in §4. This is the merge-queue lane's pick of the cheaper design, and it needs no second App.

**Decision 7, one Scheduler in the real system (root, Sep 29, about 3:15 PM PT).**
- **The rule.** An interactive pod allocation and a batch job are two kinds of the same allocation. They share budget lines, leases, approvals and the expiry and reap cron.
- **Stage 1 ships as specced.**
- **The spend broker** ([proposal](spend-broker-via-site.md)) is then built as the Scheduler's interactive kind, on the same tables and lease rules, not as a separate service.

**What stage 1's schema made harder, and the fixes before the site migrates.** Root took all three (Sep 29, 22:15Z); they're items 6–8 of the site spec's changes list, pinned by the cases at `d7272158`.
- **Fixed before the migration:**
  - **No budget line on a job.** Batch work can't be charged or capped against the lines interactive pods use. Add `jobs.line text`, the line's prefix such as `vy-coord-`: nullable in stage 1, set by whoever adds the job, and required once the Scheduler admits by headroom.
  - **The lease bound is batch-only.** `lease_s between 60 and 3600`, in the check constraint and in add's validation, fits a runner's claim lease renewed every minute. It doesn't fit an interactive pod's lease of hours. Make the bound a per-kind rule in code, and drop it from the constraint.
  - **Kinds and states are batch-only check constraints.** An interactive kind (`pod`) and a request waiting for approval (`awaiting-approval`) would each need a constraint migration. Either add both values now, or keep the lists in code, which the reference model already validates.
- **Fine to add later:**
  - **Approvals:** `approved_by` and `approved_at`, and the `awaiting-approval` state, shared by both kinds.
  - **The holder:** an interactive row is held by the requesting token rather than a runner. `lease_worker` is already nullable, so this adds `lease_holder`.
  - **Pods:** from stage 2, a CI pod is itself an interactive-kind allocation, and its `workers` row should reference that row instead of a separate pod list.

**Names:** Control is the API server and the Scheduler, and Compute is Interactive and Batch, built by us with no SkyPilot (Daniel, Sep 29, about 4:00 PM PT). They replace the Broker, the "Job queue" card of about 1:30 PM PT, and Access (about 3:10 PM PT). Batch jobs and agents' interactive pods are the Scheduler's two kinds of allocation.

**Who builds what (root, Sep 29):**
- **The website agent (bc-41cff24f) writes all the site code:** the Neon tables, the claim, renew and complete API, and stage 4's TypeScript port.
- **The merge-queue lane owns the verity side:** `research queue` as the reference, the shared test cases (`vectors.json`, `train_vectors.json`), stage 1's dispatcher, and the thin clients (`research jobs`, and `research trains` and `research git credential` once their routes exist).
- **The site spec is** `internal/job-service-site-spec.md`.

**Not a decision, a dependency.** The site's side of every stage is the website agent's (bc-41cff24f), which is shipping admin and crons now. It should come after that work.
