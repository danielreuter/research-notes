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
- `jolt-prover.md`: Jolt (a16z): what GPU paths exist (draft PR #1618 CUDA only), security (~100-bit), building guests
  and PR #1618 on a pod, measured VU guest cycles and CPU/CUDA prove times.
- `sp1-prover.md`: SP1 6.4.0 GPU prover: building a forked chip's server, sharding knobs that do and do not work, the
  memory argument's cost per word, measured per-shard constants.
