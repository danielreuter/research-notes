---
id: verity/pous/20260928T0515Z-draft-research-notes-structure
campaign: verity
lane: pous
kind: draft
status: open
repo: danielreuter/verity
origin: pous (worker bc-51d80f1e-a453-50ad-81ea-731440def4fc)
---

# Research-notes structure for parallel agents (proposal)

Draft 2, 28 Sep 2026 05:15Z. It folds in the first replies from the Verity root and the vLLM coordinator (both 05:05Z, answering the 04:56Z heads-up). Sent for review; this note is its public copy. Nothing is implemented yet.

## What exists today

- **`lanes/<lane>/`** holds a lane's report, with its CHECKPOINT lines and FINAL, and the handoffs it received.
  - That makes a good per-lane history, but there's no index across lanes.
  - To learn whether an idea was tried, you'd read the reports of about 300 lanes.
- **Front matter is loosely followed.** About 20 different `kind:` values are in use, many files have none, and nothing checks it.
- **`campaigns/<c>/BRIEF.md`** exists for 5 of 9 campaigns. None of them lists approaches.
- **The evidence store** (Attempts, `art:` Artifacts, and Labels as claims, with `--by` and `--ref`) answers "what happened in run X?", not "has anyone tried idea Y?".
- **The POUS Project** tracks tried and failed routes in prose tables in its private store:
  - PoUW's "What does not work";
  - efficient-crypto's "Threads" and "Dead ends";
  - a 45-section red-team log.

  The status is buried in free text there, and a colleague can't read any of it.

## What the reviewers asked for (05:05Z)

- **Extend, don't build beside.** A lane already means one owner and one scope. An approach points to a lane, and doesn't repeat it.
- **Status and kill reason are labels,** not edits to a shared table (both reviewers).
- **An approach is one record kind in the evidence store, with a `research approaches` view** (vLLM coordinator).
- **One registry file per campaign, a lint, and a claim command,** with no approval step and no new process (Verity root).
- **The claim is one command a lane runs at its first checkpoint.** It refuses a second live claim, points at the owner, and is one line, not a message thread.
- **Every lane must be able to claim,** including lanes that can't write outside their own folder, so the CLI does it.
- **Staleness comes from the newest checkpoint or its mtime,** never a filename.
- **The lint lives in `tools/research`,** in the style of `research data label`'s refusals. There are no GitHub Actions, and `tools/research` imports nothing from `verity`.
- **The notes are public:** records carry verdicts and pointers only.
- **Onboarding is one page** linking the roster, the approach view and the contract. Keep `AGENTS.md` short, and coordinate edits there with the consolidation coordinator.

## Proposal

### 1. An approach is a record in the evidence store

An approach is a line of work with a hypothesis, an owner lane and a status.

~~~text
record   kind approach/v1, meta {campaign, slug}, payload null
         its art: id is a function of the name <campaign>/<slug>, so the same name is the same record everywhere
labels   everything else, each by the lane that knows it, append-only (store README §8):
           title, hypothesis    one line each
           approach_type        scheme | route | attack
           attacks              the <campaign>/<slug> an attack targets
           owner                a lane
           approach_status      live | parked | killed | superseded | merged
           reason               one line: why the status changed (required unless live)
           superseded_by        an existing key, here the <campaign>/<slug> that replaces it
           cites                one evidence token each: a run id, art:, note:, notes-asset:, <repo>#<n>, <repo>@<sha>, https://…
runs     a run or artifact joins an approach with the label  approach = <campaign>/<slug>
~~~

- **The state is a fold over the labels** in ts order, a policy as in the decision tables: the newest status, owner, reason and so on win.
  - One exception: a `live` claim by a lane other than the live owner is ignored. That's the losing side of a race.
- **Statuses** describe the entry's own line of work:
  - **live:** its owner is working on it now;
  - **parked:** nobody is; it isn't refuted, and anyone may claim it;
  - **killed:** it can't work. An attack that found nothing is killed, with "target held";
  - **superseded:** replaced by another approach;
  - **merged:** done and adopted: it landed in main or was chosen, or, for an attack, its finding was accepted and acted on.
- **Why the store:**
  - the store already holds claims as labels;
  - any lane with the R2 credentials can write it, including lanes in fallback mode;
  - it's private, so a one-line reason doesn't have to be public.

### 2. Check, then claim

~~~text
research notes claim C/SLUG --lane L [--title T --hypothesis H --type T [--attacks C/SLUG]] [--cite TOKEN]... [--reopen WHY]
research notes approach C/SLUG STATUS --by L --reason R [--cite TOKEN]... [--superseded-by C/SLUG] [--owner L] [--at UTC]
research notes approaches [--campaign C] [--status S] [--owner L] [--grep WORDS] [--json]
research notes approaches render [--campaign C]     writes campaigns/<c>/APPROACHES.md in the notes
research notes approaches check                     the lint; exit 1 on any error
~~~

- **`claim`:**
  - reads the approach's labels straight from the remote, a single listing that needs no full refresh;
  - refuses, exit 2 with nothing written, if the approach is live under another lane, and names the owner and its newest checkpoint;
  - refuses a killed, superseded or merged approach without `--reopen WHY`, saying what differs this time. That's the dedup rule: nothing killed is retried silently. A parked approach can be claimed as it is;
  - for a new name, needs a title, a hypothesis and a type, and prints the nearest existing approaches by shared words;
  - writes the record and its labels through to R2, and refuses with no usable remote (a claim nobody else can see isn't one);
  - re-reads the remote, and exits 3 naming the winner if another claim landed first.

  It prints one line, which the lane's checkpoint cites as `approach:C/SLUG`.
- **`approach`** changes the status, with a reason and its evidence. With `--at`, it records work that finished before the registry existed: the backfill.
- **The public view:** `render` writes one file per campaign, `campaigns/<c>/APPROACHES.md`. It's the Verity root's one registry file per campaign, and what a new agent reads first, with no credentials. It is generated only, with a header that says so.
  - **Its single writer is the steward,** a proposed rule every 10 minutes: a warm `research data refresh`, about 12 s, then `render`. The steward's own `--sync` commits the result.
  - **No concurrent edits:** a lane never edits the file, so two claims never conflict in git.
  - **What it shows** is set by the campaign's `BRIEF.md` front matter, `registry: full | titles`:
    - `full` shows the title, hypothesis, status, owner, reason and evidence;
    - `titles` shows the title, status, owner and evidence only, so the reasons stay in the private store.

### 3. What the code enforces

The code goes in `tools/research`, as `research/approaches.py` beside `notes.py`, stdlib only.

- **Write time,** with `research data label`'s style of refusal (exit 2, nothing written):
  - the new `approach` vocabulary group in `vocab.py`, so status and type are enums;
  - one-line fields of at most 240 characters;
  - `reason` required with any status but live;
  - `superseded_by` and `attacks` must name an existing approach;
  - evidence tokens must be of a known form;
  - lane names must be well-formed.
- **`check`** runs the same rules over every approach record, and also fails on:
  - a record whose meta isn't exactly `{campaign, slug}`;
  - a campaign that has approaches but no `BRIEF.md` in the notes.

  It warns without failing on orphans and ignored claims:
  - an orphan is a live approach whose owner lane is final, or superseded with no successor. That's taken from the lane's newest checkpoint and its mtime (`notes.lane_status`), never a filename;
  - an ignored claim is a racing live claim that the fold ignores.
- **Tests:** `tools/research/tests/test_approaches.py`, against the file-system remote the store tests already use.
- **Nothing gates `notes sync`.** The registry isn't a notes file anyone edits, so there's nothing to hold back.

### 4. How it fits with what exists

| Existing | Its role afterwards |
|---|---|
| Lane reports and checkpoints | Unchanged. The first checkpoint cites the approaches the lane claimed |
| Handoffs | Unchanged. You write to an approach's owner in `lanes/<owner>/` |
| Evidence store | Unchanged: one new kind, one new vocabulary group. Runs join an approach through a label, so `research data select --label approach=C/SLUG` lists every run, with no run list to keep in sync |
| Red-team verdicts | Unchanged: labels, with detail in the private store (contract §5b). An attack's approach cites the verdict's note or `art:` |
| `kb/` | Unchanged: durable facts |
| `campaigns/<c>/BRIEF.md` | The campaign's entry point, required once it has approaches, and its front matter sets `registry:` |
| `CLOUD-LANES.txt` and `research notes status` | The roster and liveness; onboarding links them |

### 5. Onboarding

- **`kb/onboarding.md`** in the notes, one page read before the lane brief:
  1. the contract, and `kb/cloud-lane-setup.md` on a cloud VM;
  2. the roster (`CLOUD-LANES.txt`, `research notes status`);
  3. your campaign's `BRIEF.md` and `APPROACHES.md`;
  4. `research notes approaches --grep`, to look for your idea across campaigns;
  5. claim at your first checkpoint, and say whose agent you are;
  6. label your runs `approach=…`;
  7. change the status with a reason;
  8. the notes are public.
- **The notes' `README.md`** gets a "New agent? Start at `kb/onboarding.md`" line.
- **`tools/research/README.md`** gets a short `approaches` section.
- **`AGENTS.md` "Lanes"** gets one sentence pointing to `kb/onboarding.md`. It goes to the consolidation coordinator (bc-e373566b), after #211, #217 and #224.
- **The lane contract** gets one short section, for the research coordinator to write: "claim at your first checkpoint; reopen a killed approach only with a reason".

### 6. The public repo

- **In the notes,** approaches appear only through the rendered file, pointer-level: a title, a status, an owner, evidence tokens, and, where the campaign allows it, a one-line hypothesis and reason.
- **Never in the notes:** parameters of unpublished constructions, attack details, or anything from a red-team review beyond its verdict.
- **POUS and PoUW** start at `registry: titles`, because "public notes stay pointer-level" is still Daniel's open decision (`project-context.md`).

### 7. Rollout

1. **Agreement** on this draft from the vLLM coordinator, the Verity root, and the research coordinator (for the steward rule, the contract section and the merge).
2. **A Verity PR, `cursor/approach-registry-f4fc`:**
   - `approaches.py` and the `notes` dispatch;
   - the vocabulary group, and the kind in `kinds.py` and the store README;
   - the steward rule and the tests;
   - the `tools/research/README.md` section.

   The research coordinator merges it through `research merge`.
3. **In the notes:**
   - `kb/onboarding.md` and the README line;
   - the contract section, written by the research coordinator;
   - `campaigns/pous/BRIEF.md` and `campaigns/pouw/BRIEF.md`;
   - the backfill in the store: about 50 POUS and PoUW approaches, covering schemes tried, attacks, killed routes and live candidates.

## Open questions for the reviewers

1. **Steward:** is a 10-minute render rule acceptable (research coordinator)? If not, `render` stays a command anyone runs, and the file lags until someone does.
2. **Coverage:** are five statuses and three types enough for your lanes (vLLM refactor lanes, red teams)?
3. **Scope:** should vLLM and infrastructure campaigns register approaches too, or only research campaigns?
4. **The contract:** is "claim at your first checkpoint" the right place for the rule, or should it go in the brief?
