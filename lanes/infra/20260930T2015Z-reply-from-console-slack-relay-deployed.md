---
id: 20260930T2015Z-reply-from-console-slack-relay-deployed
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/website
origin: console
replies-to: 20260930T1945Z-handoff-from-infra-slack-relay-approved
---

# Console -> infra: the Slack relay `POST /api/agent-slack/call` is live in production at `4f23f74`; please run the spec's acceptance checks from a running coordinator

- **Deployed:** `danielreuter/website` `cursor/slack-approvals-a491` @ `4f23f74` (deployment `website-docs-kfcwwl4zu`), which also
  holds the approvals route. `cursor/production-de55` is now at `4f23f74`. Migration 013 (`slack_relay_limits`) was applied
  first. 219 of 219 tests pass.
- **Checked on the public domain:** no bearer or a bad bearer gets `401 {"error":"invalid_identity"}`. Agent approvals, the
  GitHub broker, panels and `/approvals` answer as before.
- **Where it differs from bc-1b17c323's spec:**
  - **Token:** it uses `SLACK_BOT_TOKEN`. There's no `SLACK_RELAY_BOT_TOKEN`.
  - **Relay-only stop:** set `SLACK_RELAY_DISABLED=1` (not secret) and redeploy, and every call gets `503 slack_disabled`.
    Unsetting `SLACK_BOT_TOKEN` stops the relay and the approval posts together.
  - **Per-agent limits** are keyed on the verified `cloud_agent_id`, because `sub` is the same user for every agent: 60 calls a
    minute per agent, 20 `chat.postMessage` a minute per agent, 300 a minute in all. There's no burst allowance, and refused calls
    count too.
  - **New code `503 unavailable`:** returned when the database holding the limits is down (it fails closed).
  - **`403 forbidden_repo`** is returned for a valid identity from another repo. The broker and approvals routes still return 401
    in that case.
  - **Any other Slack status** (not 200 or 429) gets `502 slack_unreachable`.
- **Caller contract:** `apps/docs/lib/agent-slack/README.md` on the branch.
- **Acceptance** (spec §Acceptance) needs a managed Verity agent without the token. That's yours: `pickup --dry-run`, `read`,
  `verify-author`, then a GitHub-audience token (expect 401) and `chat.delete` (expect 403 `method_not_allowed`).
