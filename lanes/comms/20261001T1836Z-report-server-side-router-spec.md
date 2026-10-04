---
id: 20261001T1836Z-report-server-side-router-spec
campaign: verity
lane: comms
kind: report
status: done
repo: danielreuter/verity
origin: comms (bc-3e100045-0b60-5d20-951e-7207a989b252, under bc-7f347b4b), moved from its coordinator's agent store internal/comms/server-side-router-spec.md on Daniel's 4 Oct ruling
---

# Server-side `@lane` router on the console site: spec for console (from comms, 1 Oct 10:30 AM PDT)

Daniel approved this at 10:13 AM PDT: routing moves out of each agent's `research slack` and into one route on the
console site, next to the Slack broker (`/api/agent-slack/call`). Comms ships the sender-side version today (PR to
follow, `cursor/slack-routing-b252`), and this route replaces its doorbell step once the pilot shows doorbells wake
agents. Console owns the route; comms owns the rule, the routes table and the vectors.

## What the route does

`POST /api/agent-slack/events`, the Slack Events API endpoint for Verity's bot (app id of bot `B0C5VQ1KKFW`).

1. Verify Slack's signature with `SLACK_SIGNING_SECRET`: `v0:` + timestamp + `:` + raw body, HMAC-SHA256, with the
   timestamp within 5 minutes. Answer `url_verification` with its challenge.
2. Reply 200 at once and do the work in `waitUntil`, because Slack retries after 3 s.
3. Consider only `message` events in #agent-coordination (`C0C5RCXL66N`): plain messages, `thread_broadcast` and
   `bot_message`. Ignore edits, deletes and joins.
4. Apply the rule (below) to get the targets, then post one doorbell per target, as a reply in that target's inbox
   thread, with `username: "router"`:
   `from <author>[ (URGENT)], thread <T>[, reply <R>]: <the post>` (changed 1 Oct 11:40 AM PDT, so the reader needs no
   second read). T is the source thread's ts, R the reply's ts when the source is a reply. The post is `slack.plain`:
   its footer dropped, `<!subteam^ID|@x>` as `@x`, date tokens as their fallback, `<url|label>` as `label (url)`, `&lt;`
   `&gt;` `&amp;` unescaped, at most 600 characters, then `… (the rest: \`research msg read --thread T\`)`.
5. Make delivery idempotent without any store. Before posting, read the target's inbox thread
   (`conversations.replies`, `oldest` = 1 hour ago) and skip any target that already has a doorbell for this post (its
   `reply R`, or for a top-level post its `thread T` with no reply). That one read also enforces the cap: past 6
   doorbells into one inbox from one author in one thread in the hour, post once in the source thread, "routing @a to x
   paused here for the hour (6 doorbells) (quiet)", and once in the inbox, "from router, thread T: paused @a here for the
   hour (6 doorbells)", and stop.

## The rule (one definition, two implementations)

Comms writes it in Python (`slack.route_targets`) and pins it with vectors in
`tools/research/tests/slack_routing_vectors.json`, as input → expected targets. The TypeScript passes the same file, so the
rule never drifts. In short:

- Nothing posted inside an inbox thread routes, and doorbells never start with `@`.
- Names at the very start of a post route: `@a @b, @c ...`, or a user-group mention `<!subteam^ID>`. A name later in the
  text doesn't.
- A reply in a thread also pings the root's author, unless the replier is that author. The root's author replying pings
  the names the root addressed.
- An announcement to all (`📣 *Announcement* from @x to every handle`) pings every registry handle.
- The author is never a target. A status line (`✅ done` / `❌ declined`) pings only the root's author. A post whose
  footer says `quiet` pings no one.
- The author is the bot message's `username` for our bot, and `daniel` for Daniel's Slack user (`U0BEN96ES8Y`). Daniel's
  typed posts route too, which closes that gap.
- A name whose route is closed (a finished lane) routes to its `forward_to`.

## The routes table (changed 10:20 AM PDT: one file per name, published)

Since 10:20 AM PDT the table is one file per name, `routes.d/<name>.json`, at the top of the notes repo. It replaces
`kb/slack-routes.json`, which never existed. One file per name means two agents registering at once can't conflict. The
repo is public, so the route reads it without credentials:

- **By name:** `GET https://raw.githubusercontent.com/danielreuter/research-notes/main/routes.d/<name>.json`, where 404
  means no inbox. Cache it for 60 s. Live now: `routes.d/comms.json`.
- **Every name** (announcements to all, and the set of inbox threads):
  `GET https://api.github.com/repos/danielreuter/research-notes/contents/routes.d`, which lists `*.json`. Cache it for
  10 min, because the unauthenticated limit is 60 calls an hour.
- **An inbox thread** is also recognizable without the table: its root is our bot's post starting `Inbox for @`.

~~~json
{"schema": "verity/slack-route/v1", "name": "comms", "holder": "bc-3e100045-0b60-5d20-951e-7207a989b252",
 "channel": "C0C5RCXL66N", "inbox_ts": "1790874830.577669", "opened": "2026-10-01T17:13Z", "closed": null, "forward_to": null}
~~~

- A closed route with a `forward_to` rings that name instead, following at most 3 hops. A closed route without one rings
  nobody, and the route posts once in the source thread: "@x is finished; message its coordinator".
- **Switch-over:** `routes.d/router.json` with `"mode": "server"` tells the CLIs to stop ringing doorbells. Comms writes
  it once `SLACK_ROUTER_ENABLED` is on.

Phase 2, optional and stronger: registration through the broker. An agent calls `/api/agent-slack/register` with its
OIDC token. The route takes `holder` from the token's verified `cloud_agent_id` claim, so nobody can register a name for
another agent. That lets the table move into the site's own storage.

## What Daniel clicks once

In the Slack app's settings (api.slack.com/apps → Verity's bot):
- Event Subscriptions on, with Request URL `https://website-docs-sage.vercel.app/api/agent-slack/events`.
- Bot events: `message.groups` (#agent-coordination is private).
- Copy the signing secret into the Vercel project as `SLACK_SIGNING_SECRET`.

## Switch-over

Comms publishes `routes.d/router.json` with `"mode": "server"`. The CLI then stops posting doorbells and only registers,
posts and reads. Until the route is live, the CLI posts them itself.
