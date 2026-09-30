---
id: 20260930T1945Z-handoff-from-infra-approvals-ready-to-deploy
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra)
---

# Console (bc-ddee017b): Daniel's Slack side is done (19:43Z). Deploy the approvals route and run one live button test

This follows `note:20260930T1935Z-handoff-from-infra-slack-approvals-route`. Daniel reports:
- **Interactivity** is on, with Request URL `https://website-docs-sage.vercel.app/api/slack/interactivity`.
- **Secrets:** `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN` are saved as protected **Production** env vars in Vercel. They take
  effect on the next deployment.
- **`#approvals`** is private, holds both the Verity and Cursor apps, and has channel id **`C0C5UCA0S0Z`** (not a secret). Set it
  as `SLACK_APPROVALS_CHANNEL`.

**Please do the following:**
1. Deploy `/api/slack/interactivity` plus the request posting to production.
2. Run one live test:
   - post a harmless test approval, e.g. "test: approve to confirm the Slack approvals route";
   - Daniel clicks Approve;
   - check that the record flips in the `/approvals` store and the message updates.
3. A click from anyone but `U0BEN96ES8Y` must be refused. Confirm it with a signed request replayed under another user id, or
   with the unit test.
4. Reply in `lanes/infra/` with the deployed commit, the test approval's id, and whether `/api/agent-approvals` is up.
   `research slack approval` is built against that route.

The relay route (`/api/agent-slack/call`) still waits on Daniel's yes; don't build it yet.
