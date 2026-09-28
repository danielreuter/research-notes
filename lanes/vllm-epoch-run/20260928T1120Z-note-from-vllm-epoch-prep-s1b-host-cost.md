---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-run · kind: note · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T11:20Z · cc vllm-coordinator

# What S1b adds to #74's and #57's Commits (the GO for both is the vLLM coordinator's)

- **#74:** about 22 min of host time once per Commit to plan at attach, then about 3.4 min per Commit (0.4 s per B=8 decode step).
  - Host RAM: 5.9 GB peak for the plan, and ~6.3 GB while committing.
  - Commit volume: +0.7 MB per token.
  - Eager execution only: the source is a forward pre-hook, and pre-hooks don't fire under CUDA graphs.
- **#57:** about 16.4 h of host time per Commit, past the 90-minute stop.
  - Under the vLLM coordinator's 07:25Z rule it goes to the follow-up epoch with its old record kept, so don't size a pod for it today.
  - For the follow-up epoch: its peak at the logits step is now 1.4 GB, not the ~10 GB planned, and it adds ~24 GB of commit volume per Commit.
- **Both need S1b ([#253](https://github.com/danielreuter/verity/pull/253)) on main.** Its check follows the S-stack's.
