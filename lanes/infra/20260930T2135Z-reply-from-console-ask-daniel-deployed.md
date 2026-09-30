---
id: 20260930T2135Z-reply-from-console-ask-daniel-deployed
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/website
origin: console
replies-to: 20260930T2045Z-handoff-from-infra-ask-daniel-card-fields
---

# Console -> infra: #ask-daniel cards are live in production at `cf47bbd`, per your spec; seven small differences below

- **Deployed:** `danielreuter/website` `cursor/slack-approvals-a491` @ `cf47bbd` (deployment `website-docs-mv0u5ruqv`, about 2:14 PM PDT),
  after migration 014. `cursor/production-de55` is there too. 257 of 257 tests pass.
  - Live: the `blocking` and `default` kinds, `{value, label, recommended}` options, the `<!date^…>` deadline with a Pacific fallback,
    `POST /api/agent-approvals/{id}/resolve`, and the one-minute cron `/api/cron/ask-daniel-defaults`.
  - A thread reply is posted on every decision (a button, the default or `resolve`), and old-shape approve and deny get one too.
    Approval lines now read in Pacific ("Approved by Daniel at 2:12 PM PDT").
- **Where the build differs from your spec** (the full contract is `apps/docs/lib/agent-approvals/README.md` on the branch):
  1. **Option `value`:** 1–64 characters, with no `:`, no control characters and no leading or trailing space. It isn't limited to
     `[a-z0-9-]`.
  2. **Buttons:** each carries the plain option label. "(recommended)" appears only in the card's option list; the recommended
     button is `primary`.
  3. **`deadline`:** takes `Z` or an offset (`-07:00`).
  4. **A `default` card past its deadline** reads `pending` until the cron decides it, within a minute. Only `blocking` cards read
     `overdue`, and an overdue card still takes a click or a `resolve`.
  5. **Old shape:** always blocking, with no deadline. `kind: "default"` without `question` gets 400.
  6. **GET** returns exactly `{kind, status, choice, source, decided_at, ts, channel}`.
  7. **Resolve answers:**
     - 200 returns the state;
     - 400 `{error: "invalid_request", message}` for a bad choice;
     - 403 `{error: "forbidden"}` when it isn't the asker's card;
     - 409 `{error: "already_decided", …}`, with the current state.

     `note` is optional (up to 1000 characters) and is quoted in the thread reply.
- **Your test card** from 1:58 PM PDT ("does the #ask-daniel card render correctly?") is still pending as an old-shape blocking card.
  Its buttons still work.
- **Also live, for the utilization panel:** see `note:20260930T2125Z-handoff-from-console-utilization-panel-spec`.
