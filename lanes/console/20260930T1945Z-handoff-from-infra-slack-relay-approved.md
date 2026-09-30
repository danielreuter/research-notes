---
id: 20260930T1945Z-handoff-from-infra-slack-relay-approved
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra)
---

# Console (bc-ddee017b): Daniel said yes to the Slack relay (19:44Z). Build `/api/agent-slack/call` right after the approvals route

**Why:** it lets coordinators that were already running when `SLACK_BOT_TOKEN` was saved post, react, read threads and run
`verify-author` without a relaunch. The bot token never leaves Vercel.

**The spec:** it comes from the slack-via-broker worker (bc-1b17c323) as a `...-handoff-from-infra-slack-call-route-spec.md`
note in this lane. It may say bc-41cff24f; that was written before the website moved to you.

**The route, briefly:**
- **Auth:** Cursor OIDC, verified as in `/api/agent-github/token` (audience = this route's URL, repository
  danielreuter/verity).
- **Request:** `{method, args}`.
- **Methods:** only those in the spec's allowlist, which mirrors `slack.py`'s constant.
- **Response:** Slack's JSON, unchanged.
- **Limits:** a size limit and a rate limit per agent.
- **Logging:** the agent id, method and channel; never tokens.
- **Emergency stop:** unset `SLACK_BOT_TOKEN` in Vercel.

Reply in `lanes/infra/` with the deployed commit. Infra then checks it from a running coordinator (me): `research slack` falls
back to the broker when the token is absent.
