---
id: 20260930T2100Z-handoff-from-infra-merge-592-frozen
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra)
---

# Merge request: #592 is frozen at `5ad088055`; please put it in the next train, ahead of the backlog

`cursor/slack-coordination-6081` @ `5ad088055a` (PR #592). This supersedes `note:20260930T1934Z-handoff-from-infra-merge-592-slack`.
verity-top has agreed that #592 goes ahead of the backlog.

**What's in it:**
- **`research slack`**, the coordination API: its handles, channels and threads.
- **The relay transport:** agents without `SLACK_BOT_TOKEN` go through the docs-site broker, which is live and passed acceptance
  at 1:22 PM PDT.
- **`ask-daniel` cards.**
- **`research/timefmt.py`:** times people read print as "1:41 PM PDT (20:41Z)", and Slack posts carry `<!date>` tokens.
- **The registry:** 9 handles with their group ids, and 3 channels.
- **The using-slack skill.**

**What it touches:** `tools/research` (`slack.py`, `timefmt.py`, `notes.py`, `status` output, and tests), `.agents/skills/using-slack/`,
one line of `AGENTS.md` and `tools/research/README.md`. No circuit, Lean or `backends/flock/` change.

**Tests on `5ad088055`:** the research suite 800 passed and 2 skipped; the repository suite 32 passed. It needs a recorded `check`
of this tip.

**Frozen:** infra's workers don't push to this branch until it merges. Anything later goes into a follow-up PR.
