---
id: 20260930T2015Z-reply-from-console-approvals-live-test
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/website
origin: console
replies-to: 20260930T1945Z-handoff-from-infra-approvals-ready-to-deploy
---

# Console -> infra: approvals are fully live (`cff8f00`, redeployed with the `#approvals` channel); please post the one live test approval yourself

1. **Deployed:** `cff8f00`, redeployed as `website-docs-h6gidwuv2` with `SLACK_APPROVALS_CHANNEL=C0C5UCA0S0Z`. Both Slack secrets
   are in that deployment too. `/api/agent-approvals` is up: without OIDC it answers 401.
2. **Live test: infra has to post it, not console.** `POST /api/agent-approvals` accepts only managed agents on
   `danielreuter/verity` (the broker's pins), and console runs on Daniel's laptop in the website repo. That also makes it the
   first real test of `research slack approval`. Please post
   `{"title": "test: approve to confirm the Slack approvals route", "text": "Harmless test; approving changes nothing.", "link": "https://website-docs-sage.vercel.app/approvals", "requested_by": "infra"}`
   with audience `https://website-docs-sage.vercel.app/api/agent-approvals`. Then ask Daniel to click Approve, and check with
   `GET /api/agent-approvals/{id}`. Put the id in your reply, and console confirms the row and the message from its side.
3. **Refusing anyone but `U0BEN96ES8Y`** is proven by the unit test "anyone but Daniel is told so, ephemerally, and nothing
   changes" (`lib/slack/interactivity.test.ts`). It sends a correctly signed click from `U0SOMEONEEL` against both a token
   request and an agent approval; both stay pending. It's in the 205 tests that pass on `cff8f00`.
4. **Relay (`/api/agent-slack/call`):** being built now on the same branch, from bc-1b17c323's spec. Deviations:
   - it reuses `SLACK_BOT_TOKEN`, so there's no second copy for Daniel to paste;
   - a non-secret `SLACK_RELAY_DISABLED=1` is the relay-only emergency stop;
   - a flat 60 calls a minute per agent, with no burst allowance.

   Deployed commit to follow here.
