---
id: 20260930T1915Z-handoff-from-console-relay-handover
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/website
origin: console
supersedes: 20260930T1910Z-handoff-from-console-relay-to-docs-site
---

# Console -> verity-root: please forward Daniel's handover order to your child docs-site (bc-41cff24f); this replaces the 19:10Z relay

Daniel ruled at 19:10Z that the console agent (bc-ddee017b, lane `console`) takes over the website remit from docs-site. The order
is `lanes/docs-site/20260930T1915Z-handoff-from-console-handover.md`: hand over its state in `lanes/console/` by 20:15Z, tell its
three workers to report to `lanes/console/`, then go idle.

- Please send bc-41cff24f one follow-up pointing at that file. Ignore the 19:10Z division-of-work note.
- Send site and console requests to `lanes/console/` from now on.
