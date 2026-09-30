---
id: 20260930T1944Z-handoff-from-infra-slack-call-route-spec
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra), slack-via-broker worker (bc-1b17c323)
---

# To bc-41cff24f (docs-site app): the Slack relay route `POST /api/agent-slack/call`

**Implement only after Daniel's yes, relayed by infra.** Until then this is a spec, not a request to build.

## Why

Cursor injects secrets only when an agent starts. Coordinators that were already running when `SLACK_BOT_TOKEN` was added
(about 19:00Z) can't post, react, read threads or run `verify-author`. This route lets them call Slack through the site, on
their Cursor identity, the way `/api/agent-github/token` gives them GitHub. The client side is already built: `research slack`
uses this route whenever `SLACK_BOT_TOKEN` is absent (or `RESEARCH_SLACK_VIA=broker` is set). It's on branch
`cursor/slack-via-broker-f74a` of danielreuter/verity, at commit `4e06b0efcd54de45ac6618f924fe8a97a54ac720`, in
`tools/research/src/research/slack.py` (`BROKER`, `BROKER_METHODS`, `BROKER_MAX_BODY`, `broker_error`).

## The route

`POST https://website-docs-sage.vercel.app/api/agent-slack/call`

- Headers: `Authorization: Bearer <Cursor OIDC token>`, `Content-Type: application/json`.
- Body: `{"method": "<Slack Web API method>", "args": {"<name>": "<string>", ...}}`. Every arg value is a string; the client
  JSON-encodes nested values itself, as Slack's form encoding expects.
- Success: HTTP 200 with **Slack's JSON response unchanged**, including `{"ok": false, "error": ...}`. The client reports Slack's
  own errors.
- Broker errors: a non-200 status with `{"error": "<code>"}`, where the code matches `[a-z0-9_]{1,64}`. The client echoes only
  that code and nothing else of the body.

| Status | `error` | When |
|---|---|---|
| 400 | `bad_request` | the body isn't JSON of that shape, an arg isn't a string, or an arg is named `token` |
| 401 | `invalid_identity` | the bearer is missing, or the OIDC check below fails |
| 403 | `forbidden_repo` | the token is valid but its repo isn't `danielreuter/verity` |
| 403 | `method_not_allowed` | the method isn't in the allowlist |
| 413 | `too_large` | the body is over 65536 bytes (check the size before parsing) |
| 429 | `rate_limited` | a limit below is hit, or Slack returned 429; set `Retry-After` in seconds |
| 502 | `slack_unreachable` | Slack returned 5xx, or the network or a timeout failed |
| 503 | `slack_disabled` | the relay's token env var is unset (the emergency stop) |

## OIDC verification

Use the same verification as `/api/agent-github/token`, ideally the same function with the audience as a parameter:

- The signature is checked against Cursor's JWKS, with the same issuer constant as the GitHub route.
- `aud` must equal `https://website-docs-sage.vercel.app/api/agent-slack/call` exactly. A token minted for the GitHub route's
  audience must get a 401: separate audiences stop a token being replayed across routes.
- `exp` and `nbf` are checked, with the same clock skew as the GitHub route.
- The agent's repo claim (the claim the GitHub route reads) must be `danielreuter/verity`.

## Forwarding

- Send the request to `https://slack.com/api/<method>` as `application/x-www-form-urlencoded; charset=utf-8`, with `args` as the
  form fields and `Authorization: Bearer <bot token>`. Use form encoding, not JSON: the read methods
  (`conversations.history`, `conversations.replies`, `usergroups.list`) don't accept JSON bodies.
- Follow no redirects, and use a timeout of about 25 s.
- Read the bot token from `SLACK_RELAY_BOT_TOKEN`, which holds the same value as `SLACK_BOT_TOKEN`. With its own variable, the
  emergency stop halts agents' relaying without halting the approvals messages the site posts itself. If you'd rather reuse
  `SLACK_BOT_TOKEN`, the stop halts both.

## Method allowlist

Allow exactly these methods, the ones `slack.py` calls (`BROKER_METHODS`; a test there keeps the constant equal to the calls):

```text
auth.test  chat.getPermalink  chat.postMessage  conversations.history  conversations.replies
reactions.add  usergroups.create  usergroups.enable  usergroups.list  usergroups.update
```

The four `usergroups.*` methods are only used by `research slack groups sync`, and three of them change workspace user groups.
If Daniel wants to leave them out, `groups sync` will need the token, and the client will report `403 method_not_allowed`.
That's for his yes to settle.

## Limits

- **Size:** a request body of at most 65536 bytes (`BROKER_MAX_BODY`). The client refuses larger ones before sending. Slack's
  responses are passed through without a limit.
- **Rate:**
  - 60 calls a minute per agent (the OIDC `sub`), with bursts of up to 20;
  - 20 `chat.postMessage` calls a minute per agent;
  - 300 calls a minute across all agents.

  Keep the counters in the store the GitHub route uses for its limits, or, if it has none, as a fixed window in the site's
  existing KV. A limit hit gets a 429 with `Retry-After`.

## Logging

Write one line per call: time, agent id (`sub`), method, `args.channel` (or `args.usergroup`), Slack's `ok` and `error`, the
HTTP status, and the duration. **Never log tokens (OIDC or bot), the Authorization header, or the message `text` and other
args.**

## Emergency stop

Unset `SLACK_RELAY_BOT_TOKEN` in the Vercel project's production environment and redeploy. Every call then gets
`503 slack_disabled`, which the client reports as "the Slack broker is down or switched off". A caller that has the token itself
still works. To resume, set the variable again and redeploy.

## Acceptance

From a running Verity agent that has no `SLACK_BOT_TOKEN`:

- `research slack pickup --thread <ts> --dry-run` prints `(via the broker)`.
- `research slack read --since <ts> --limit 1` exits 0.
- `research slack verify-author --event '{"ts":"<ts>","channel":"<#agent-coordination id>"}' --why` exits 0 on a post of ours.

Then two negative checks: a GitHub-audience token gets 401, and `chat.delete` gets 403 `method_not_allowed`. Reply in
`lanes/infra/` with the deployed commit.
