---
id: 20260930T2045Z-handoff-from-infra-ask-daniel-card-fields
campaign: verity
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1, Slack @infra)
---

# Console: extend `/api/agent-approvals` into the #ask-daniel card: one question, why, options with a recommendation, a default and a Pacific deadline, blocking or default

Daniel approved this at 1:39 PM PDT. There is one channel for everything that needs him: `#approvals` becomes `#ask-daniel`, and its
id `C0C5UCA0S0Z` stays the same. Infra leads, and console builds the buttons. Infra's `research slack ask-daniel` command calls
this route.

## `POST /api/agent-approvals`: new fields, all backward compatible

~~~json
{
  "kind": "blocking | default",
  "question": "one line",
  "why": "1-3 lines: why it matters",
  "options": [{"value": "a", "label": "Do A", "recommended": true}, {"value": "b", "label": "Do B"}],
  "default": "a",
  "deadline": "2026-09-30T23:00:00Z",
  "link": "https://... (the full context)",
  "requested_by": "infra",
  "agent_url": "https://cursor.com/agents/bc-..."
}
~~~

- **The old shape still works:** `{title, text, link, requested_by}` is an Approve/Deny card with `kind: blocking`.
- **Validation:**
  - 2 to 5 options; at most one is `recommended`;
  - `default` is one of the option values and is required for `kind: default`;
  - `deadline` is in the future and at most 7 days out.
- **The card's layout:**
  - **Header:** the question in bold, plus a `BLOCKING` or `DEFAULT` label.
  - **Body:** *Why:* ...; the options, with "(recommended)" on one; *Default:* X; *Deadline:* shown with
    `<!date^UNIX^{date_short_pretty} {time}|fallback in PDT>`, so Slack renders it in Daniel's local time; "asked by @handle" with
    the agent link.
  - **Buttons:** one per option, with the recommended one styled `primary`. A `blocking` card whose options are yes and no can keep
    Approve/Deny.
- **Clicks:** accepted from `U0BEN96ES8Y` only, as now. The first decision wins. The message updates to "Daniel chose *B* at
  h:mm PM PDT", and the buttons are removed.
- **The default:** for `kind: default`, when the deadline passes with no click, the record becomes `decided` with
  `choice = default` and `source = default`, and the message updates to "No objection by the deadline, so the default *A*
  applies." It's enough to apply this lazily on GET, or with a cron once a minute; the message must update either way. A
  `blocking` card never auto-decides. After its deadline it just shows as overdue.
- **Thread replies:** Daniel may answer in the thread instead of clicking. The route doesn't need to parse those. The asker follows
  its own thread (`subscribe_slack_thread`) and records Daniel's answer itself, via `POST /api/agent-approvals/{id}/resolve`
  `{choice, note}` with OIDC. That call is only allowed for the asker's own card, and it updates the message.

## `GET /api/agent-approvals/{id}`

It returns `{status: pending|decided|overdue, choice, source: button|default|thread, decided_at, ts, channel}`. `approved` and
`denied` are returned for old-shape cards.

## Please reply in `lanes/infra/`

Send the deployed commit, plus any field you change. Keep the names above if you can; `research slack ask-daniel` is being built
against them now, falling back to the old shape until your deploy is live.
