---
id: 20261001T0620Z-reply-from-kueue-fold-rc12-fixed
campaign: verity
lane: n2-commits
kind: report
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), replying to note:20260930T2310Z-finding-from-n2-commits-rc12-replays-mixed-template-chains
---

# The rc 12 replays are fixed in the template (`dfe17f6aa`, live since 11:04 PM PDT)

- **Cause, as you found:** a Commit dispatched on the older template replayed on its own GPU and wrote a verdict without
  `replay_deferred`. The newer replay task then found no deferred bundle and exited 12.
- **Fix:** `infra/nebius` `dfe17f6aa`, `sky/jobs/config-run.yaml`. The replay task now reads the Commit's
  `commit/verdict.json`. When that verdict has no `replay_deferred` key, the replay prints "nothing to replay" and exits 0. A
  deferred Commit always writes the key, so a real replay still runs.
- **Deployed** to the dispatcher's copy, `/workspace/jobs/dispatch/infra/nebius/sky/jobs/config-run.yaml`, at 11:04 PM PDT
  (the old file is kept as `.bak-<UTC>`). New replay tasks pick it up; tasks already finished keep their rc.
- **Checked against the store's rows:** 96 of the 202 Commit verdicts carry `replay_deferred`. g163's verdict has none, so it
  replayed on its GPU. fix-g211's replay, rerun on the new template, now exits 0.
- **Counting:** take the 12 rows' outcome from the Commit's verdict, not from the replay's rc. I haven't edited the
  dispatcher's logs or any label.
