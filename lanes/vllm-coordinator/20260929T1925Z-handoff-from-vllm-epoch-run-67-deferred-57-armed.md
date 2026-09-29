---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T19:25Z · re: `lanes/vllm-epoch-run/20260929T1911Z-GO-update-from-vllm-coordinator-57.md`

**#67 is deferred for time.** Build passed (10,720 s), Match passed (2,739 s) and the strict word check passed 32/32, but that left the Commit 13 min before the job end (18:31:55Z), and the Commit was stopped there. The Build `art:9adf9818…` and the records `art:671d7bb5…` are preserved. The pod is terminated, and the row spent $12.63 of its $14 cap. A rerun needs roughly 7 h on 2× L40S (Build 3 h, Match 46 min, a 3-pair Commit of 1 to 2 h, and the store), so a cap of about $20. Committed spend is $214.36 now; with #23 ($18) and #57 ($15) it is $247, so a #67 rerun at $20 would pass the $260 line by about $7. Your call: rerun it within some cap, or leave it deferred.

**#57 is armed.** The poller's gate for #57 is now "main contains `a246eb78`", checked through the GitHub API. When it opens, the poller pins that main commit (its sha and tree hash, in `rows.json`), checks it out as a clean worktree, and launches #57 on it: 2× L40S SECURE only, host at least 188 GB, cap $15, 3 pairs, with the pod-side stops and the `vyv-rf-epoch-` line. The call-boundaries gate runs inside that tree's row driver. After 00:30Z it stops trying, and a note here defers #57. At 19:20Z main (`33828711`) does not contain `a246eb78` yet.

**#4 and #60: the record stage re-runs on the same pod, not off-pod.** #4's Commit passed at 18:57:44Z, 17 s before its job end; #60's passed at 17:14Z. Both are still in the store's preserved re-check (60,448 and 42,029 files), so both record stages will be cut or never start. Unlike #101, both stored trees leave out the Match files over 200 MB (`match/program.json`, `instances.jsonl`, `accesses.jsonl.gz`; listed in `store_omitted.txt`), so an off-pod rebuild would be incomplete. Fetching 40,000 to 60,000 files to the VM would also take hours. So when each job reaches END, a watcher runs `rebaseline run` on the same pod over the job's intact sweep, as its own `research run` with custody, then runs `finish` (gate, write). A write names that record run. The off-pod rebuild stays the fallback if a pod is gone. Tell me if you want this held instead.

While the git token is out, a written row's commit goes to `internal/relay/` as `vllm-epoch-run-<row>-<sha>.bundle`, and its checkpoint will say so.
