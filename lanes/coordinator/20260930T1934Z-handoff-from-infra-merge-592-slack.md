---
id: 20260930T1934Z-handoff-from-infra-merge-592-slack
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra), via its slack-sync worker (bc-0c4b24d6)
---

# Research coordinator: please merge #592 (research slack) in your next train

[#592](https://github.com/danielreuter/verity/pull/592) (branch `cursor/slack-coordination-6081`) is ready at tip
`0bc00268e7c1f82790aac90aef257922a5c1145e`. It needs a recorded `check` of that tip before `research merge`; it touches
`tools/research/` (your area) and `.agents/skills/using-slack/`, and not `backends/flock/`, so there's no lane-agreement run.

What changed since the author's last push (b165863ce):

1. `registry.json` now records the seven user-group ids and the bot's id (`B0C5VQ1KKFW`). Nothing was renamed: the groups
   already had their handles as names. `groups sync --apply` failed with `usergroups.update: permission_denied`: the bot has
   `usergroups:write`, but the workspace restricts who manages user groups. So the ids were recorded from `usergroups.list`,
   exactly as `--apply` writes them, and the groups' descriptions (the remits) are still empty in Slack. That's cosmetic, and
   it's Daniel's call: loosen the workspace's user-group permission and rerun `groups sync --apply`, or set the descriptions by hand.
2. Fix: Slack stores a posted 📣/✅/❌ as `:mega:`/`:white_check_mark:`/`:x:`, so `match`, `roster` and `done` didn't
   recognize a live announcement. They accept both forms now, and the fake Slack in `test_slack.py` stores shortcodes like
   the real one does.
3. The test fixture gives only @infra a group id, whatever the real registry records.

Evidence, on 0bc00268e:
- `suites.py research repository`: 743 passed and 2 skipped; 32 passed.
- The live smoke announcement: ts `1790796394.520569`, <https://computeverification.slack.com/archives/C0C5RCXL66N/p1790796394520569>.
  - `verify-author` exits 0 ("Verity's bot as @infra").
  - `match --as proofs` exits 0 ("an announcement to every handle").
  - `roster` lists the six other handles as missing.

The PR body's "Before it's live" and "Tests" sections are stale: the worker had no PR-editing tool.
