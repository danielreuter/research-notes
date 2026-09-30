---
id: build-v2-kv/20260930T1612Z-friction-merge-queue-not-in-lane-contract
lane: build-v2-kv
kind: friction
status: open
---

# A lane that follows AGENTS.md and the lane contract writes a merge-request note, but the merge queue only admits `research queue ready`

- **What happened:** I sent #517's merge request as `note:20260930T1436Z-merge-request-build-v2-kv-517`, the way `AGENTS.md`
  ("Only the research coordinator merges `main`") and `kb/LANE-CONTRACT.md` describe.
- **What I found 90 minutes later:** `research queue status` listed #517 as "not marked ready at a309b142". Its README says
  `research queue ready PR` "replaces the merge-request note", and that `tools/check/queue.toml` requires a `vllm-coordinator`
  grant for `integrations/vllm/`. By then `main` had also moved 117 commits and conflicted with the branch again.
- **What I did:** merged `main` again (872be036), marked the head ready, asked for the grant, and marked the note superseded.
- **Cost:** about 90 minutes in the queue and one more merge of `main`.
- **Better abstraction:** one line each in `AGENTS.md` "Checking and merging" and in the lane contract. For example: to merge,
  run `research queue ready <PR>` at the head; ask each role that `research queue status` names for its grant; there is no
  merge-request note. Or `research notes checkpoint` could print the lane's PRs from `research queue status`.
