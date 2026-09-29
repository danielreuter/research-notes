---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: checkpoint · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-29T20:50Z · re: `lanes/vllm-epoch-run/20260929T2033Z-answers-from-vllm-coordinator-67-68-and-4-label.md`

**#4's label** is on the remote: `art:7b437ce1…` has `class=GREEN` by `daniel`, ref `r20260929-194627-4b5f`, plus a `note` label "reclassified FAIL -> GREEN: Daniel, 2026-09-29T20:12Z, via root". `class` was not in the vocabulary, so this write used `--off-vocab`.

**The regenerator PR** is [#439](https://github.com/danielreuter/verity/pull/439), head `39beebd0`:
- `store_io.class_label` returns the newest `class` label by `daniel` on the row's record-of-record trees (meta `role=record`, `row_id`);
- `lift_expected.py` prefers it to INDEX.json and writes `class_source` on every row;
- `class` is added to `research.store.vocab` (verification, GREEN | FAIL);
- a test uses a stand-in vault with INDEX FAIL: a label by `daniel` gives GREEN, and no label (or one by anyone else) gives FAIL.

The recorded `check` has not been run.

**#68 resumes on its own pod, not a new one.** 2× L40S SECURE has had no stock all day (#23, #67), and #68's pod is that shape, with the venv, the checkpoint and its Build on disk. So after the 20:53Z cut and its store, the resume runs on the same pod as a new `epoch_row.sh` job at `14f027c3`: 1 pair, cap $6.50 from its start, the same guards, deadlines, store and record stage. Its build stage rebuilds the row dir from the Build already there: the same file set the store holds as the Build tree, stored again with the resume. The earlier job's Match and Commit are moved aside. Match reruns, then word check, Commit, store and record. The earlier job's evidence and custody are kept, and its spend ends at the resume's start. #67 still waits for stock (SECURE, cap $6.50, 1 pair, Build `art:9adf9818…` restored from the store), ahead of #23.
