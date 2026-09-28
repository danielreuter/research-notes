# Onboarding: read this before your lane brief

> **Status (28 Sep 05:40Z):** the `research notes claim | approach | approaches` commands land with verity#240, which is merging.
> Until then, read `campaigns/<c>/APPROACHES.md` and ask `lanes/coordinator/` before starting.

You are an agent (or a person) about to do research work on Verity. Many approaches run in parallel, and the notes are how you
avoid repeating one. This page takes five minutes.

## 1. The rules

- **`kb/LANE-CONTRACT.md`** is the rulebook: your lane folder, checkpoints, handoffs, pods and data. It wins over any older brief.
- **`kb/cloud-lane-setup.md`:** on a Cursor cloud VM, its §1 block (your own clone of these notes, pushed with
  `RESEARCH_NOTES_TOKEN`) comes first.
- **The notes repo is public** (contract §5b):
  - no secrets, and no git data;
  - no attack details, exploit scripts or unfixed bugs. Those go in your Project store's `private/` or the evidence store.
- **Code** goes on a Verity branch and through a PR. Only the research coordinator merges `main`.

## 2. Who is doing what

- **Lanes:** `research notes status` shows every lane touched in the last day, with its state, freshest sign of life and pods.
  `CLOUD-LANES.txt` lists the cloud lanes. `lanes/<lane>/` holds a lane's report and the handoffs it received.
- **Coordinators** read `lanes/coordinator/` (the research coordinator: merges, pods, the evidence store), `lanes/verity-root/`
  and `lanes/vllm-coordinator/`. If you don't know who owns something, write to `lanes/coordinator/`.

## 3. What has been tried: check, then claim

An **approach** is a line of work with a hypothesis, an owner lane and a status:

| Status | Meaning |
|---|---|
| live | Its owner works on it now |
| parked | Nobody does; it isn't refuted, and anyone may claim it |
| killed | It can't work, and the reason says why (an attack that found nothing is killed: "target held") |
| superseded | Another approach replaced it |
| merged | Done and adopted: landed in main, chosen, or an attack's finding acted on |

Its type is `scheme` (a construction), `route` (a way to prove, build or measure something) or `attack` (a line of cryptanalysis
against another approach).

**When to register one:** in any campaign, vLLM and infrastructure included, whenever two agents could plausibly start the same
idea in parallel. That covers design alternatives (one approach per decision, with the PRs as its evidence), candidate
constructions, proof routes and attacks.
- **Routine PR-sized chores don't need one.**
- **Red-team verdicts stay labels** on the attempts or artifacts they judge (contract §8), not approaches.
- **If your launch brief names an approach,** claim that one.

1. **Read your campaign:** `campaigns/<c>/BRIEF.md` (the goal, the rules, who coordinates), then `campaigns/<c>/APPROACHES.md`.
   The latter is generated from the evidence store: the steward refreshes it every 10 minutes, and nobody edits it.
2. **Search across campaigns:** `research notes approaches --refresh --grep <words>`. The first `--refresh` on a new machine
   takes a few minutes; after that it takes seconds.
3. **Claim before you start, at your first checkpoint.** A claim is one command, and its output is one line:

~~~sh
research notes claim <campaign>/<slug> --lane <you> --title "…" --hypothesis "…" --type scheme|route|attack [--attacks <c>/<slug>]
research notes checkpoint <you> open "claimed approach:<campaign>/<slug> (agent bc-…, for <person>); next: …"
~~~

- **Already live under another lane?** The claim is refused and names the owner. Write to `lanes/<owner>/` instead of starting a
  copy.
- **Killed?** Read the reason first. Reopening needs `--reopen "what differs this time"`. Nothing killed is retried silently.
- **Parked?** Claim it as it is.
- **The name** `<campaign>/<slug>` is stable, lowercase with `-`, and you choose it. Pick something a search would find.

## 4. While you work

- **Tie runs to the approach:** `research run --campaign <c> …`, and label each result
  `research data label <run> approach <c>/<slug> --by <you>`. `research data select --label approach=<c>/<slug>` then finds them all.
- **Change the status when it changes,** with a reason and evidence:

~~~sh
research notes approach <c>/<slug> killed --by <you> --reason "one line: why it can't work" --cite <run id|art:…|note:…|verity#123>
research notes approach <c>/<slug> superseded --by <you> --reason "…" --superseded-by <c>/<other>
research notes approach <c>/<slug> parked --by <you> --reason "waiting for …"
research notes approach <c>/<slug> merged --by <you> --reason "landed in verity#123"
research notes approach <c>/<slug> live --by <you> --owner <new lane> --reason "handed over: …"
~~~

- **At FINAL,** no approach of yours stays live. Park it, or hand it over. `research notes approaches check` warns about orphans.
- **Durable facts** (a measured constant, a gotcha, a how-to) go into the matching `kb/` doc, with their source.

## 5. Where writing goes

| What | Where |
|---|---|
| Your report, checkpoints, small evidence | `lanes/<you>/` (the CLI writes the report) |
| A message to another lane | `lanes/<them>/<UTC stamp>-handoff-from-<you>.md` |
| What was tried, and why it was killed | The approach registry (above): labels in the evidence store |
| Runs, results, verdicts | The evidence store (`research run`, `research data put --preserve`, `research data label`) |
| Living facts | `kb/<topic>.md` |
| Code, tests, maintained docs | A Verity branch and PR (Verity's `AGENTS.md` "Where writing goes") |
