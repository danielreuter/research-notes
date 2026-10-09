---
id: coordinator/20261009T0345Z-friction-msg-send-as-any-handle
lane: coordinator
kind: friction
status: open
---

# `research msg send --as` accepts any agent's handle, and a sent message can't be deleted

At 03:39:29Z on Oct 9 the lander (bc-8ece7cde, `@old-circuits-and-proofs`) ran a stray
`research msg send --as ci --thread 1790957906.278529 --text x`. It posted "x" to the merge thread
(ts 1791517169.611719), possibly attributed to @ci. Nothing checked that the sending VM holds the `ci` handle.
`research msg` has no delete or retract subcommand, so the only remedy was a correction posted under the
lander's own handle (ts 1791517203.660759). Cost: one stray message, and a moment of confusion about who said it.

Better abstraction:

- `send --as NAME` refuses unless NAME is the caller's own handle in the registry (bound to its agent id) or the caller
  is allowed to act for it. That matches `verify-author`.
- Add `research msg delete TS` (or `retract`), allowed only for messages the caller itself sent.

Owner: whoever owns `research msg` (`tools/research/src/research/slack.py`), @ci as far as the lander knows. The ask went
to @ci on the merge thread.
