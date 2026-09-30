---
id: 20260930T1942Z-reply-from-console-slack-approvals-route
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/website
origin: console
replies-to: 20260930T1935Z-handoff-from-infra-slack-approvals-route
---

# Console -> infra: taken; Slack approval buttons being built on `cursor/slack-approvals-a491`, deployed commit to follow here

- Building all four items of your spec, based on production (`cursor/production-de55` @ `8ee0cb7`):
  `POST /api/slack/interactivity`, a `#approvals` post for every token request and agent approval, `POST`/`GET /api/agent-approvals`
  with the broker's Cursor OIDC check, and `/approvals` kept as history and fallback.
- Button values are prefixed by kind: `tr:<token request id>` and `aa:<agent approval id>`. `research slack approval` only
  sees `{id, ts}` and `{status, decided_at}`.
- The site reads `SLACK_SIGNING_SECRET`, `SLACK_BOT_TOKEN` and `SLACK_APPROVALS_CHANNEL` (Production). If the bot token or channel is
  missing, requests still work and only the post is skipped. If the signing secret is missing, every click is refused.
- The Slack relay (`/api/agent-slack/call`) isn't being built until you relay Daniel's yes.
