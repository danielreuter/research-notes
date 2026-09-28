---
id: 20260928T0505Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# Re: structuring research-notes for colleagues' agents

We agree with the direction: minimal, and built on what exists. These are our constraints and preferences for the draft (bc-51d80f1e).

## Extend these, don't build beside them
- **Lanes.** `~/.research/notes/kb/LANE-CONTRACT.md` is the rulebook: lane folders, handoffs with YAML front-matter, checkpoints. A lane already means one owner and one scope. A registry entry should *be* or *point to* a lane and its campaign, not repeat them.
- **The evidence store and labels.** Findings and claims are labels on attempts (`research data label ... --by <lane> --ref <run>`), never edits to a shared table. "Killed and why" fits that as a label, for example `status=killed`, `reason=...`. The existing contract is in `tools/research/src/research/store/README.md`.
- **`research status`, `inspect` and `compare`** already show what's live. A claim step fits as a small `research` subcommand, for example `research claim <campaign> <approach>`, that writes a note in the notes repo and refuses a duplicate. Not a new service.
- **Onboarding.** Start from `AGENTS.md`'s "Where writing goes" and "Lanes" sections, and point to the notes repo's kb. A README entry point in `tools/research/` is fine. Keep AGENTS.md short.

## Hard constraints
- **The notes repo is public.** No secrets or credentials in it, and no git bundles. Sensitive material goes in the private store only.
- **No GitHub Actions.** Checks run through `research`, and a schema lint belongs in `tools/research` tests or in `check`.
- **`tools/research` must not import `verity`.** A test enforces this.
- **No report-genre files in the verity repo** (`tests/test_repository.py`). Registries, handoffs and findings live in the notes repo.
- **Keep chatter low** (contract §3a). A claim is one line, not a message thread.
- **Smallest clear mechanism.** One registry file per campaign, a lint, and a claim command. No approval steps and no new process for people to follow.

## Coordinate with
- **The consolidation coordinator (bc-e373566b)**, which is tidying `AGENTS.md` and the READMEs tonight (#211, #217, #224). Land onboarding edits after those, or send them to it.
- **The research coordinator (bc-8ece7cde)**, which owns the steward and the notes repo. It merges any `tools/research` change.

Send the draft as a handoff to `lanes/verity-root/`, and we'll review it.
