# research-chats — state

Updated 2026-09-24T06:05Z.

- **Branch**: `lane/research-chats` (pushed), worktree `~/projects/verity-wt/research-chats`, tip `c313a38c`. Not merged to main.
- **Code**: `tools/research/src/research/chats.py` (its docstring is the contract), a two-line registration in `cli.py`, `tests/test_chats.py`, and a README section.
- **Pod**: `vy-control` (`ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 11754 root@213.173.105.92`), everything under `/workspace/chats`:
  `mirror/` (rsync target), `index/chats.sqlite` (live index), `store/` + `store.toml` (the chats store, remote = R2 verity-dev),
  `tool/<sha>` + `tool/current` (shipped `tools/research`), `bin/ingest.sh` + `bin/research` (written by each sync), `log/`.
  `/workspace/chats/dev/` is scratch for running tests. The pod's container disk is its only disk: if it is reset, the next sync re-sends everything (about 3 min) and rebuilds the index (about 2.5 min).
- **Laptop**: `~/.research/bin/chats-sync.sh` (shell + rsync + sqlite3 read-only + one `research data mint-credential` call);
  launchd `~/Library/LaunchAgents/com.research.chats-sync.plist` at 03:17 local; logs `~/.research/log/chats-sync.log` and `chats-sync.launchd.log`.

## Done
- Parser, redaction, incremental FTS5 index, preserved pushes, and anchor-based pull. 4 tests pass on the pod. The full suite on the pod has 19 failures, the same 19 as pristine origin/main there (they need the repo tree or non-root).
- Full-corpus build without pushing: 1933 files, 542k message rows, 2280 chats, 2398 notes, 758 MB, 136 s; 1494/1494 transcript chats have metadata.

## Running / next
- First sync via launchd: see the tail of `~/.research/log/chats-sync.log` and the artifact ids below.
- Open decisions for Daniel: merge to main (the sync then ships origin/main automatically); whether to also archive the notes repo's git history (not archived now); how long to keep daily index artifacts (about 0.25 GB gz per day in R2).

## Artifacts
(filled after the first sync)
