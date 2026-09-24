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
- First sync: launchd kickstart at 05:57Z, exit 0 at 06:01Z (4 min: 54 s metadata, rsync of 13 changed transcripts, 2 min pod ingest). Nothing is running now; the next run is 03:17 local.
- Open decisions for Daniel: merge to main (the sync then ships origin/main automatically); whether to also archive the notes repo's git history (not archived now); how long to keep daily index artifacts (about 0.25 GB gz per day in R2).
- Deletion question: not settled by observable evidence (see below). The mirror never deletes transcripts, so once a chat has synced, deleting it in Cursor cannot remove it from the archive.

## Artifacts (first sync, 2026-09-24)
- transcripts `art:0bd478de2c4c272847df83456d778a821a6abe647c82082fa3d7660bee93249a` (chat-transcripts/v1, 1937 files) PRESERVED
- notes `art:3c3de6f3f1170a09d93397ab45a9a045a5c5e483fa3c054a484defd43dc486e1` (lane-notes/v1) PRESERVED
- metadata `art:805b01d4bdf01c5c4a9c90dfaea831cd58723874aab79d4c159a8f57b075e929` (chat-metadata/v1, 2285 chats) PRESERVED
- index `art:327b302d7fe0bb3c93227ee7aa7ea71da97edae4c1c0647bbd4c71ee9a71de75` (chat-index/v1, 247 MB gz / 769 MB) PRESERVED
- anchor `art:6153de7d560f1c4cff87953c8df4aad4c838b24c729691cf2623b2d2686387e3` (fixed; label superseded_by = newest index)
- The index has 544,010 messages, 2285 chats, 2415 notes, and 1937 files. 1498/1498 transcript chats have metadata. Redactions: secret_assignment 123, aws_access_key_id 42, bearer 37, sk 21, runpod 9, huggingface 1, cloudflare 1; none in notes or titles.
- Fresh-machine check (empty store): the anchor led to the index, which pulled and unpacked in 12 s, and search worked.

## Deletion evidence (2026-09-24)
- Every transcript id has composerData (1498/1498): no orphaned transcripts from deleted chats.
- 4 chat ids have bubbleId keys but no composerData (probably deleted chats); none has a transcript, but their dates cannot be read without message values, so they may predate transcripts (which start 2026-07-03).
- No chat created since 2026-07-03 with more than 20 messages lacks a transcript.
- This is consistent with "deleting a chat deletes its transcript", but it is not proof. A safe test: make a throwaway chat, confirm its JSONL exists, delete the chat, and look again.
