---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-verify-optins (overnight goal 10: verify the FA3, write-once-per-norm and FP8 opt-ins on real Builds)

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM lane `vllm-verify-optins`: verify three opt-in constructions on real Builds. First read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md` and do its section 1. Then read
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md` (it overrides the setup page for vLLM
> lanes), then your brief `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-verify-optins.md`. Write your first
> checkpoint (`research notes checkpoint vllm-verify-optins open "..."`) within 10 minutes. You report to vllm-coordinator (bc-ecac3029).

## Context
Daniel's overnight plan (`$STORE/docs/overnight-plan.md`, goal 10) gives this work **$20**. The three constructions were built and
CPU-verified by lanes that have finished. Each is opt-in, with the record unchanged:
- **PR #105** (normtap): FA3 `Check_inf` per iteration, `TargetProfile.fa3_construction = "check-inf-per-iteration"` (`Attention_v4`).
  Kernel-level H100 exactness passed.
- **PR #109** (recompute): Gemma's weight + 1 once per norm, `TargetProfile.weight_only_calls = "once"`. Checked on the recorded request
  Programs; the real-Build A/B was deferred.
- **PR #106** (recompute): FP8 block scale products computed once, `SHARED_SCALE`. Checked on the Definitions; a real Build wasn't run.

Work on main once these have merged (check `git log origin/main`). Otherwise use a local merge of the PR heads. The merge train is with
the research coordinator.

## Tasks (CPU first; a pod estimate goes to me before the first pod)
1. **#57 (Gemma-2-2B, L40S): a Build with `weight_only_calls = "once"`.**
   - `query.cross_call` on the real request Programs: 0 recomputes. Unset, the Build equals the record: Program and manifest digests
     as recorded.
   - Report the `+ 1` Call counts.
2. **#73 (Qwen3-4B, H100): a Build with `fa3_construction = "check-inf-per-iteration"`.**
   - The partition checker: 0 recomputes. Unset, the Build equals the record.
   - Optionally, the Match under the new construction, if the fold supports it.
3. **#74 (Qwen3-4B-FP8, H100): the request Programs with `SHARED_SCALE` applied.** This may be on CPU from the stored Build.
   - The member check: 0 recomputes.
   - The host-computed scale products equal the old construction's values at every coordinate on a sample of the recorded Build's steps.
   - Unset, the Build equals the record.

## Rules
- **Money:** $20 in total. The estimate names pod type, hours and dollars per task. I approve within $20; stop past it.
- **Guard:** the vyv- guard is armed to 15:00Z. Pods are `vyv-rf-verify-optins-*`, created with `--register --project verity --guard 90`.
- **Custody:** `research data put` any Build outputs before terminating; custody keeps only `evidence/`.
- **Hand-offs:** one to `$STORE/internal/lanes/vllm-coordinator/` per task, plus a status handoff by 14:00Z.
