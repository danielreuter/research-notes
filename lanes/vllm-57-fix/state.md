---
lane: vllm-57-fix
repo: verity (~/projects/verity), worktree ~/projects/verity-wt/57-fix
branch: lane/vllm-57-fix (off origin/lane/vllm-cleanup-2 = 38122d1f), pushed to origin + pod remote sw57
pod: vyv-sw-57 (ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 12152 root@202.181.159.235), checkout /workspace/verity
---
# vllm-57-fix: running state

Task: #57 v2 Commit local_replay fix (432 promoted model/out identities_without_rows + form (B) None; snapshot-steps gap);
#67 follow-on if same cause. Spec: pod /workspace/lane/BRIEF.md; facts /workspace/lane/sweep-status-0205Z.md.
Schedule: 20260924T0545Z-from-coordinator-schedule.md (57-cause 07:00Z, 57-fix 09:00Z, 57-pass 10:00Z, 57-ready 10:30Z, 67-pod 10:30Z, 67-pass 12:30Z).

## Checkpoints
- CHECKPOINT 57-cause MET 05:56Z -- offline repro on the pod (logs /workspace/lane/logs/repro_{pop,oracle}_base.log; script evidence/pod-scripts/repro57.py)

## Root cause (#57 Commit 8cb4, from the offline reproduction at base 38122d1f)
Two independent failures; the first is already fixed on staging, the second is the fix of this lane.
1. `population_scope identities_without_rows x432 (model/out)`: the sweep's Commit ran source 014563ac, whose replay addressed Program rows
   by the v1 rule. At 38122d1f (v2 addressing in sampled_replay.ProgramIndex, rule `v2-query`, program_dir correspondence) the same
   Programs + manifest reconcile exactly: query_checks ok, identities_without_rows 0, vus_outside_query 0, rows_disagree 0, accounted, 163484/163484.
   No code change needed; the rerun at the tip confirms it.
2. `population_gaps ... form (B) result None`: form (B) (oracle_compare) left 45,360 instance_outputs not compared (reproduced exactly: compared 114,480):
   - 44,928 = "ambiguous producer: 2 instances of NarrowF32ToBf16_v1 per row" under every fused norm (input_layernorm, pre_feedforward_layernorm, model.norm; members 0/1);
   - 432 = `model/out` "no fold instance of this op at this step": the embed scale (Bf16MulScalarTensor_v1) is hinted `model.normalizer` by the fold, its v2 identity is `model/out`.
   Cause: the oracle selects a producer by the manifest row's v1 annotations (producer_operand / producer_ordinal; promoted + consumers).
   A `v2-query` manifest (v1_bridge.request_manifest) carries none of them, so the oracle can neither pick among the fused norm's two
   narrowings nor resolve the embed scale through its consumers.
Fix (in progress): derive the same facts from the Programs of record by dataflow at Commit time (v1_bridge.population: producing Call
family, first-operand producer family, reading modules outside the producer's module) and merge them where the manifest row declares none;
the oracle resolves a member through the Value (consumer operand -> producer output, M-0721(1)'s mechanism) when the fold has no instance
of the producer family under the identity's path.

## Tip
- 38122d1f (= staging); fix uncommitted in the worktree (oracle_compare.py, commit_delta.py)

## Done
- worktree + pod remote set up; pod checkout fast-forwarded to 38122d1f.
- pod-side pilot worker loop is stopped (/workspace/lane/STOP_WORKER 05:40Z); its idle `agent worker` pid 37762 left alone.

## Running
- none

## Next
- commit + push fix; offline oracle repro with the fix (repro57.py oracle-fixed); snapshot-steps derivation in row_pod.sh; tests; Commit-only rerun.
