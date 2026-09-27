---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-gc (gate (b) to green, test-side only), successor of gb

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-gc`, the successor of `vllm-rf-gb` (its session ended at the 9:03 AM PT laptop
> restart). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-gc.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-gc open "..."`) within 10 minutes.

## Predecessor and scope
- gb: agent bc-707a2df4. Notes: `$RESEARCH_NOTES/lanes/vllm-rf-gb/STATE.md`. The mirror copy (14:40Z) predates its work;
  its later STATE lines are lost with the laptop copy. The pod and the WIP commit below are the record.
- Scope (`LANE_PROMPTS_WAVE2.md` "gb"): bring the gate (b) baseline to green where the cause is the test harness or the
  tree. Examples: a subprocess env without core `verity`, an order-dependent `HF_HOME`, the torch-free extraction
  missing `execution_of_workload`, paths that moved.
  - Triage every other failure.
  - No product code, no deleted or weakened tests, and no files another running lane changes. `load_workload` in
    `engine/vllm_adapter.py` stays where it is: b5vab keeps it in place for your tests.
  - Acceptance: a same-pod jdiff at head against base shows fixes only, and lints pass.

## Branch
- gb's branch `lane/vllm-rf-gb` has no commits (it's at `33e4d8d1`). Its 2 uncommitted files are on
  `origin/wip/vllm-rf-gb-1604` @ `176d3bff`: one-line edits to `tests/engine/test_gen_ov_sampling.py` and
  `tests/observe/test_gen_sampling.py`.
- Your branch: `lane/vllm-rf-gc` **from `origin/main` (`8a3aa083`, which includes c1)**. Then run
  `git cherry-pick -n 176d3bff`, review the two edits, and commit them with a real message if they're right. c1 didn't
  touch those files.

## Pod (yours; registered, guard 90)
| Pod | RunPod id | $/h | State at 16:10Z |
|---|---|---|---|
| `vyv-rf-gb-cpu` (cpu3g 32 vCPU, bootstrapped) | 0d4uj5m7e8o5cz | 1.28 | idle. Run `r20260925-145521-2b1c`: lints base rc 0, then gate (b) at base `33e4d8d1`, **51 failed / 3647 passed / 286 skipped / 6 xfailed / 11 errors** (ended 15:37Z; `gate_b-base.xml` in the run dir). An earlier run, `r20260925-144953-6bd1`, is gb's first try; check its status |

## Next
1. Classify all 62 failures and errors in the base XML: test-side or product.
2. Base for your jdiff: run gate (b) at `origin/main` on gb-cpu. c1 changed `integrations/vllm`, so the `33e4d8d1` XML
   serves for triage only.
3. Fix the test-side causes (small commits, pushed each time). Then run gate (b) at head on the same pod, and lints.
4. READY.md, listing each fix with its cause, and each remaining failure with its triage. Then the merge-ready handoff.
   Terminate gb-cpu.

## Budget
$5 of new spend (CPU only). The original budget was $12.
