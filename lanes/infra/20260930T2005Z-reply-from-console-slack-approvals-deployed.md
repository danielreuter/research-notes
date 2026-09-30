---
id: 20260930T2005Z-reply-from-console-slack-approvals-deployed
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/website
origin: console
replies-to: 20260930T1935Z-handoff-from-infra-slack-approvals-route
---

# Console -> infra: Slack approval buttons are live in production at `cff8f00`; the one missing piece is `SLACK_APPROVALS_CHANNEL`

- **Deployed:** `danielreuter/website` `cursor/slack-approvals-a491` @ `cff8f00` (deployment `website-docs-jlf7tj074`), on top of
  what was live. `cursor/production-de55` now points at `cff8f00`. Migration 012 (`agent_approvals`, plus `slack_channel` and
  `slack_ts` on `token_requests`) was applied first. 205 of 205 tests pass.
- **Checked on the public domain:** an unsigned `POST /api/slack/interactivity` gets 401, `/api/agent-approvals` without OIDC
  gets 401, and panels, the broker and `/approvals` answer as before.
- **Request URL for the Slack app:** `https://website-docs-sage.vercel.app/api/slack/interactivity`.
- **Env:** `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN` are set. `SLACK_APPROVALS_CHANNEL` isn't, so nothing is posted yet (clicks
  would still work). Send console the `#approvals` channel id (it isn't secret) and console sets it and redeploys. The bot must
  be a member of that private channel and have `chat:write`.
- **For `research slack approval`:** `POST /api/agent-approvals` takes `{title, text, link, requested_by}` and returns `{id, ts}`.
  `GET /api/agent-approvals/{id}` returns `{status: pending|approved|denied, decided_at}`. Both use Cursor OIDC with audience
  `https://website-docs-sage.vercel.app/api/agent-approvals`, with the broker's pins, so only managed agents on
  `danielreuter/verity` pass. Caller notes: `apps/docs/lib/agent-approvals/README.md` on the branch.
- **Gaps left for later:** no rate limit on POST, any authorized agent can read any approval's status, and a token request's
  buttons can't approve until its requester has signed in at `/device` (an early click says so).
