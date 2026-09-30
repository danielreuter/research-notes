---
id: 20260930T2006Z-handoff-from-infra-relay-spec-decisions
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra)
---

# Console (bc-ddee017b): the relay spec is yours; build it now (Daniel said yes at 19:44Z); two decisions settled

The spec is `note:20260930T1944Z-handoff-from-infra-slack-call-route-spec`, in this lane. It names bc-41cff24f and says "only
after Daniel's yes". It's addressed to you now, and the yes has been given.

The spec left two questions open. Infra's decisions:
1. **No `usergroups.*` write methods through the relay.** Drop `usergroups.create`, `usergroups.enable` and `usergroups.update`
   from the allowlist; keep `usergroups.list`. `groups sync` runs only on VMs that have the token.
2. **One token, one kill switch.** The route uses the existing `SLACK_BOT_TOKEN` (Production, set by Daniel). There's no second
   token. `SLACK_RELAY_DISABLED=1` stops relaying and leaves the approval messages working.

**The allowlist, then:** `auth.test`, `chat.getPermalink`, `chat.postMessage`, `conversations.history`, `conversations.replies`,
`reactions.add`, `usergroups.list`.

**Order of work:** the approvals route first (Daniel is waiting for the button test), then this one. Reply in `lanes/infra/` with
the deployed commit.
