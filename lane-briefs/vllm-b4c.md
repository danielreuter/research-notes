---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-b4c (engine and hooks: re-gate after c1), successor of b4b

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-b4c`, the successor of `vllm-rf-b4b` (its session ended at the 9:03 AM PT laptop
> restart). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-b4c.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-b4c open "..."`) within 10 minutes.

## Predecessor and branch
- b4b: agent bc-892f86c5 (itself successor of b4, bc-95aa165d). Notes: `$RESEARCH_NOTES/lanes/vllm-rf-b4b/STATE.md` and
  READY.md. Both describe the pre-c1 head `2908cca1`, which was fully gated.
- Head: `lane/vllm-rf-b4b` @ **`5c05ff6d`**, rebased at about 14:50Z onto main `8b3537d5` (c1). The rebase resolved a
  conflict in `p10_size.json`, and it auto-merged c1's hunks in `commit/committer/native_host.py`, `native_collect.py` and
  `pipeline/commit.py` (merged sizes: native_collect 1924, native_host 2572, padding_steps 914).
  - It merges cleanly with `origin/main` `8a3aa083`; everything after `8b3537d5` is outside `integrations/vllm`.
- Create `lane/vllm-rf-b4c` at `5c05ff6d` only if you must commit. **Lane `vllm-rf-b5vab` is stacked on `5c05ff6d`**, so
  if you commit, tell it in a handoff.

## Pods (yours; registered, guard 90)
| Pod | RunPod id | $/h | State at 16:10Z |
|---|---|---|---|
| `vyv-rf-b4b-cpu` (cpu, 32 vCPU class) | cjzaq3ploo8kok | 1.28 | created 14:57Z, **never bootstrapped** (`/workspace` empty) |
| `vyv-rf-b4b-g1` (1x L40S) | nplcyinf9r2si8 | 1.09 | created 14:57Z, **never bootstrapped** |

## Next (the re-gate b4b started, then the merge request)
1. Bootstrap both pods with `$RESEARCH_NOTES/lanes/vllm-rf-a1/baseline.md`'s recipe, plus `pytest-xdist==3.8.0`. Check
   the L40S has driver 580 / CUDA ≥ 12.9. If it doesn't, replace it using b2v's `tools/create_cuda.py` pattern
   (c4irb's STATE.md, pod g1).
2. On cpu, head `5c05ff6d` and base `8b3537d5` on the same pod: lints (expect 47 passed at head), then gate (b), then
   `baseline-jdiff.py`. The rule is no new failure, error, skip or skip reason. **Keep both XMLs on the pod:** head
   `5c05ff6d` is b5vab's gate (b) base.
3. On g1: the #101 GPU smoke at head. The record is program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`,
   commit PASS, and non-interference 992/992.
4. Update READY.md for `5c05ff6d` (keep the `2908cca1` evidence and say what carries over), then send the merge-ready
   handoff.
5. **Hand over, don't terminate:** both pods go to `vllm-rf-b5vab` (cpu for its gate (b), g1 for its #101 smoke).

## Budget
$8 of new spend (about 2 h of both pods, plus bootstrap). b4 and b4b spent about $13.5 of the original $25.
