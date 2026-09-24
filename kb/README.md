# Knowledge base

Topic docs that stay true: anyone (lanes, coordinator) edits them in place. Everything else under `~/.research/notes` is
dated history, organized by lifetime and owner:

| Where | What | Who writes |
|---|---|---|
| `kb/<topic>.md` | living docs: the lane contract, runbooks, measured facts, decisions | anyone; correct in place, cite sources |
| `lanes/<lane>/` | a lane's report (append-only checkpoints + FINAL), `evidence/`, `binding.json` | that lane (the coordinator when it is dead) |
| `lanes/<lane>/*handoff*.md` | messages to that lane; `research notes inbox` / `checkpoint` show the unread ones | the sender |
| `lanes/coordinator/` | briefs (one per campaign or wave), coordinator state, messages to the coordinator | coordinator / senders |

Conventions: one topic per file, kebab-case names (`live-verifier.md`, `pods-4090.md`); a fact carries its source
(`art:`, commit, report path); a campaign's durable conclusions move here at its end.

- `LANE-CONTRACT.md`: how every lane works. Read it first.
