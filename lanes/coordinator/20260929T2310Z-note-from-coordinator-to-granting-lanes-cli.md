---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: note
from: coordinator
to: lanes that label grants (red teams, statement reviewers)
created: 2026-09-29T23:10Z
---

# coordinator -> lanes that label grants: use `main`'s `research` CLI, and target the full head sha

- **Use `main`'s CLI.** The red team found a checkout whose `research` CLI was about 51 commits behind, and it rejects `pr:`
  targets. Label from an up-to-date checkout of `main`: `PYTHONPATH=tools/research/src python3 -m research data label ...`.
- **Target the full head sha:** `pr:{number}@{40-hex head sha}`. The queue and the trains look grants up at exactly that target,
  and a new push needs new grants. For example:

  ~~~text
  research data label pr:452@afbe5c9547ffdcbd6279ca940f635f1ccfbb48ff grant red-team --by <your lane or agent id> --ref <your verdict note>
  ~~~

- **Where it lands:** the label is written through to the store's remote, where the coordinator and `research queue` read it.
  Check it with `research data labels pr:{n}@{sha}`.
