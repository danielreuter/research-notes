# routes.d: who can be messaged by name on Slack

One file per name, `<name>.json`, written by `research slack inbox open` (and closed by `inbox close`); never edit by hand.
A post in #agent-coordination that starts with `@<name>` rings a doorbell (a one-line pointer) in that name's inbox thread,
`inbox_ts`, which its holder subscribes to. The rule and its guards are `route_targets` in verity's
`tools/research/src/research/slack.py`, pinned by `tools/research/tests/slack_routing_vectors.json`; the console site's
events route reads these files raw (`https://raw.githubusercontent.com/danielreuter/research-notes/main/routes.d/<name>.json`).
Owner: comms.
