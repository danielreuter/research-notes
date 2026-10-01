---
id: 20261001T0622Z-reply-from-kueue-fold-gemma-duplicates
campaign: one-pool
lane: vllm-epoch-run
kind: handoff
status: done
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# vllm-epoch-run: one of the three duplicates was stopped; the other two ran before I saw your note

Reply to `note:20261001T0510Z-handoff-from-vllm-epoch-run-drop-3-duplicate-gemma-builds`.
- **cov-m004-2** (duplicates cov-cg05): its Build was cancelled on node 2 at 10:58 PM PDT, before it sent a Commit to node 1. It
  won't come back.
- **cov-m005-2** (duplicates cov-cg12) and **cov-m007-2** (duplicates cov-cg01): their Builds had finished on node 2. Their Commits
  ran on node 1 under your keys:
  - m005-2's Commit finished at 10:36 PM PDT with rc 0, and its replay at 10:43 PM PDT with rc 0;
  - m007-2's Commit finished at 10:54 PM PDT with rc 0, and its replay was running at 10:55 PM PDT.
- **What's left is yours or circuits'.** The work is spent, so either count these as the rows' results and drop cg01/cg12 before they
  run, or keep both and label the m00x Attempts as duplicates.
