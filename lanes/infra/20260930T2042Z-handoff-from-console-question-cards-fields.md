---
id: 20260930T2042Z-handoff-from-console-question-cards-fields
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/website
origin: console
---

# Console -> infra: proposed fields for #ask-daniel question cards; console is building them now, so say by 2:05 PM PDT if you want changes

Daniel approved at 1:39 PM PDT: one channel for everything that needs him, with question cards beside the blocking approvals.
Console builds the site side on the existing agent-approvals API. The channel id `C0C5UCA0S0Z` survives the rename, so no env
changes. Blocking approvals (`{title, text, link, requested_by}`) work exactly as today.

## Ask: `POST /api/agent-approvals` with `"kind": "question"` (Cursor OIDC, audience as now)

| Field | Type | Rule |
|---|---|---|
| `kind` | `"question"` | omitted, or `"approval"`, means today's blocking approval |
| `question` | string | 1–300 characters; the card's title |
| `why` | string | 1–1500 characters: why it matters |
| `options` | list of `{key, label}` | 2–4; `key` matches `[a-z0-9-]{1,32}` and is unique; `label` has 1–75 characters (Slack's button limit) |
| `recommended` | option key | required; its button is primary and says "(recommended)" |
| `default` | option key | required; can differ from `recommended` |
| `deadline` | ISO 8601 UTC | 5 minutes to 7 days ahead; the card shows it in Pacific ("Default at 2:30 PM PDT") |
| `link` | https URL | optional |
| `requested_by` | string | the asking lane or handle, e.g. `@infra` |

Returns `{id, channel, ts}`. `ts` is the card's thread: subscribe to it (`subscribe_slack_thread`) to see the answer.

## Poll: `GET /api/agent-approvals/{id}`

`{kind, status, answer, answered_by, decided_at}`. For a question, `status` is `pending`, `answered` or `defaulted`, and `answer`
is the chosen option's key. For an approval, `status` is `pending`, `approved` or `denied`, and `answer` is null.

## Behaviour

- **One button per option.** Only Daniel's clicks count (`U0BEN96ES8Y`), and the first answer wins. Anyone else gets an
  ephemeral "Only Daniel can decide this".
- **On an answer:** the card loses its buttons and says "Answered by Daniel at 2:12 PM PDT: <label>". A thread reply says the
  same, so the asker's thread subscription wakes it. `/approvals` records it in its history.
- **At the deadline with no answer:** a cron job (every minute) sets `status = defaulted`, `answer = default`, updates the card
  and posts "Default applied: <label>" in the thread.
- **Blocking approvals** also get the thread reply on approve or deny, so an asker can subscribe to their thread too.
- **CLI:** `research slack ask-daniel` (or whatever you name it) posts the body above and polls, or subscribes to `ts`.
