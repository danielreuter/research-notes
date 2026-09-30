---
id: 20260930T1935Z-handoff-from-infra-slack-approvals-route
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra)
---

# Console (bc-ddee017b): approvals move to Slack buttons; Daniel said go at 19:33Z; please build the interactivity route on the docs-site app

Daniel wants every approval to go through Slack instead of the console's `/approvals` page, because it's easier for him and
more extensible. He is setting up the Slack app now: Interactivity turned on, the signing secret copied into Vercel, and a
private `#approvals` channel. You own the website side; infra adds the agent-side command to `research slack`.

## What to build on the docs-site Vercel app (`website-docs-sage.vercel.app`)

1. **`POST /api/slack/interactivity`** is the Request URL Daniel is entering.
   - **Verify every request:**
     - `X-Slack-Signature` must equal `v0=` + the HMAC-SHA256 of `v0:{X-Slack-Request-Timestamp}:{raw body}` under
       `SLACK_SIGNING_SECRET`, compared in constant time;
     - the timestamp must be within 5 minutes of the server's time;
     - anything else gets 401.
   - **Accept a decision only from Daniel:** `payload.user.id == "U0BEN96ES8Y"`, the named human in the registry. Anyone else
     gets an ephemeral "only Daniel can decide this" and no state change.
   - **Record it:** the actions are `approve` and `deny`, and `value` is the approval id. Write the decision to the same store
     the `/approvals` page uses, so every existing consumer keeps working: the panels key, the broker approvals. Then update
     the message through `response_url` to show "Approved/Denied by Daniel at HH:MMZ" with the buttons removed.
   - The decision is idempotent, and the first one wins.
2. **Post a message for every approval request.** The site's own requests (panels key, broker) post to `#approvals` through
   `chat.postMessage` with `SLACK_BOT_TOKEN` and the channel id in `SLACK_APPROVALS_CHANNEL`. The message carries:
   - the title and who is asking (the agent's link);
   - what exactly is approved, with a link;
   - Approve and Deny buttons.
3. **Agents create and read approvals through `POST /api/agent-approvals` and `GET /api/agent-approvals/<id>`.**
   - **Auth:** Cursor OIDC, the same verification as the GitHub broker route (`/api/agent-github/token`).
   - **POST body:** `{title, text, link, requested_by}`. It creates the record, posts the Slack message, and returns `{id, ts}`.
   - **GET:** returns `{status: pending|approved|denied, decided_at}`.
   - `research slack approval` will call these; infra builds that against this spec.
4. **Keep `/approvals`** as the history view and as the fallback when Slack is down. Don't remove it.

Log the agent id, the approval id and the decision, and never tokens or signatures. Emergency stop: unset
`SLACK_SIGNING_SECRET`; every click is then refused and the page still works.

## Related, waiting on Daniel's separate yes

The Slack relay (`/api/agent-slack/call`) lets running coordinators post without having the token themselves. Its spec arrives in
this lane from the slack-via-broker worker (bc-1b17c323), addressed to bc-41cff24f; it's yours now. **Don't build it until
infra relays Daniel's yes.**

Reply in `lanes/infra/` with the deployed commit once `/api/slack/interactivity` passes Slack's URL check, so Daniel can finish
the app settings.
