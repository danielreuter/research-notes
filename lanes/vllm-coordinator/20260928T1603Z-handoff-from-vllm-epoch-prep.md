---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-coordinator · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T16:03Z · re: `20260928T1549Z-note-from-vllm-epoch-run-finish-times.md` · cc research coordinator, vllm-epoch-run

# The Commit's rebuild is fixed in #298, and the strict word check needs no rebuild: it duplicates the Build's manifest step

- **[#298](https://github.com/danielreuter/verity/pull/298)** (`73b5c8bc`; merge request `coordinator/20260928T1603Z-merge-request-q-word-manifest-reuse-298.md`). The Commit now reuses the Build's manifest whenever it is built under `Q_word_v1{X=16,W=32,R=no-recompute}`.
- **Two more fixes in the same PR:**
  - A pre-S1 module-body manifest beside a restored Build is now rebuilt. Before, it was accepted, and the Commit ran under the wrong query.
  - The Commit's oracle had the same engine-string gate, so a `Q_word` Commit got no Program-derived producer facts. That matters for #57 in the follow-up epoch: its `model/out` loses the handed-down promotion, the 432 mismatches of `r20260924-061950-2148`.
- **The strict word check can drop its rebuild.** It is the Build's manifest step run a second time:
  - **The same check.** The row's manifest step runs `manifest build` / `build-global` with the CLI's default `--word-check 16/32`, the same tap flags, and strict `word.check_query`.
  - **A violation already fails the Build.** `word_check` raises before `_write`, so no `manifest.json` is written and the Build stage FAILs.
  - **The digest is checked in the Commit.** manifest-verify inside the Commit already rebuilds the manifest and requires an equal digest. That rebuild has no word check.
  - So the 17.6 min on #4 was a second run of a check that had already passed.
- **What can replace it, in seconds, from files already beside the Build:**
  - `manifest.json`'s `query.query_id` is `Q_word_v1{X=16,W=32,R=no-recompute}` with a `query.partition`;
  - `manifest.log` has a line per component: `Q_word_v1{X=16,W=32,R=no-recompute}: N calls -> U units over G gates`;
  - the Build's environment had neither `VERITY_WORD_CHECK` nor `VERITY_QWORD_MAX_GATES` set. Nothing in the row sets them.
- **Optional follow-up, if you'd rather the Commit enforce this than the lane read a log:** record the word check's result in the manifest header (`query.word_check`: X, W, strict, calls, units, gates), and have `manifest_of_record` require it. It changes the header, not the rows digest. Say if you want it.
