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

History: the whole notes tree is its own git repo, separate from the code repo, with no remote yet. `research notes watch
--snapshot` (the coordinator's watcher) is its only committer. `.gitignore` and a 1 MB cap keep it to text; dumps go to the store.
Size on 2026-09-24: 30 MB of tracked text, 10 MB packed history.

- `LANE-CONTRACT.md`: how every lane works. Read it first.
- `bench-instances.md`: which instances ref a bench run carries and whether Table 2 counts it (frozen, instance-equiv, tile).
