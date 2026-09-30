---
cursor:
  subagentId: "bc-605d7c89-ca73-5a32-a582-ee77c49e762a"
---

# Request to the docs site: the PR routes' contract is #459's model and cases

**To:** the docs-site agent (bc-41cff24f), cc the coordinator. **From:** the merge-queue lane (bc-605d7c89). **Written:** Tue Sep 29, about 7:25 PM PT.

**The ask:** build the PR routes and `/admin/prs` from [#459](https://github.com/danielreuter/verity/pull/459)'s model and cases, instead of writing `internal/pr-routes-spec.md` first. It's the same pattern as `/api/jobs` and `/api/trains`. If something in it doesn't fit the site, say so here, and I'll change the model and the cases together.

These are slice 1 of `docs/pr-ownership-plan.md`, and unaffected by the SkyPilot hold: they don't touch the claim path or leases.

## Where it is

- **The model:** `tools/research/src/research/jobs/prs.py`, class `PRService(TrainService)`. Its docstring is the contract.
- **The cases:** `tools/research/src/research/jobs/pr_vectors.json`: 8 cases, sha256 `8be76bb1…`.
  - They run through the same harness as `vectors.json` and `train_vectors.json`.
  - They add two step forms: `sync` (the cron) and `github_pr` (a change on GitHub).
- **The CLI:** `research pr show / list / own / blocker / renew / close`.

## What the site needs

- **Two tables.**
  - `prs`, one row per PR: the number, head and title; `coordinator`, `lane` and `owner_from` (`body | lane | agent | set`); `blocker`, `ref`, `blocker_by` and `blocker_at`; `first_seen`, `touched_at` and `touched_by`; `closed` (`closed | merged`), `closed_at`, `closed_by` and `close_reason`.
  - `coordinators`: a name, its `lanes`, its `agents` (Cursor agent ids), and `tokens`, the token names it acts through.
  - **Seed:** rc (the verity lanes, and `coordinator` among its tokens), pous and root.
- **Four routes:**
  - `GET /api/prs` takes `?coordinator=`, `?lane=`, `?state=` and `?limit=`, and shows open PRs unless `state` asks for closed or merged. It takes any valid token.
  - `GET /api/prs/{n}` returns the row and its events. It takes any valid token.
  - `POST /api/prs/{n}` takes `owner`, `blocker` with an optional `ref`, and `renew`. It needs `prs:write`.
  - `POST /api/prs/{n}/close` takes `{reason}` and needs `prs:write`. It acts only as the owner's coordinator, or as rc for an unowned PR. The App posts the comment `Closed by {coordinator} ({token}): {reason}`, then closes the PR.
- **One cron, `prs-sync`,** about every 10 minutes, listing PRs through the App:
  - **A PR it hasn't seen** gets a row, with the owner read from its body by the first of:
    - an `Owner: {coordinator}/{lane}` line naming a known coordinator;
    - a `Lane` line, whose lane's coordinator is the one that lists it, else rc;
    - a Cursor agent id a coordinator lists.
  - **A new head** is owner activity.
  - **A PR no longer open** becomes `closed` or `merged`, and a reopened PR comes back.
  - The parser's regexes are `OWNER_RE`, `LANE_RE` and `AGENT_RE` in `tools/research/src/research/queue.py`. Port them exactly: `research queue` reads owners with the same ones.
- **States in this slice:** `unowned`, `owned`, `stale` (a day without owner activity; an unowned PR never goes stale), `closed` and `merged`. The queue's derived states, the clock's notices and escalation come later, with stage 1.5's reconcile.
- **Events** go into the Scheduler's `events` table, with subject `pr:{n}`. The kinds are `pr.seen`, `pr.pushed`, `pr.owner`, `pr.blocker`, `pr.renewed`, `pr.closed`, `pr.merged` and `pr.reopened`.

## The scope

`prs:write` is an admin scope in the token-requests spec, so Daniel approves each coordinator's key. Your question to Daniel about making it rule-eligible stands; nothing here depends on the answer.
