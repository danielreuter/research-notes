---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-b1c (evaluator kernels and replay), successor of b1b

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-b1c`, the successor of `vllm-rf-b1b` (its session ended at the 9:03 AM PT laptop
> restart). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-b1c.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-b1c open "..."`) within 10 minutes.

## Predecessor and branch
- b1b: agent bc-033f1f34 (itself successor of b1, bc-910bfdb6). Notes: `$RESEARCH_NOTES/lanes/vllm-rf-b1b/STATE.md`
  (14:35Z) and its READY.md draft (14:40Z, gaps marked `NEEDS`, `R67_SHORT`, `R70_SHORT`). Scope: `LANE_PROMPTS_WAVE2.md` "b1".
- Start commit: `origin/lane/vllm-rf-b1b` @ **`8c0bec08`** (= b1's head), based on a4's `10996616`.
- Your branch: `lane/vllm-rf-b1c`. Before the first push: `git rebase --onto origin/main 10996616`.
  - The rebase is clean, but it merges into `pipeline/commit.py`, which c1 (`8b3537d5`) also changed. So the rebased
    head needs lints and gate (b) again (below).

## Pods (all yours; registered, guard 90)
| Pod | RunPod id | $/h | State at 16:10Z |
|---|---|---|---|
| `vyv-rf-b1-g2` (1x L40S, 188 GB) | l2w6439556ueod | 1.09 | #67 `r20260925-120629-a48a` (`/workspace/b1/tools/g2.sh`). Build and Match done; the **head Commit** (`pipeline.commit`, PAIRS=1) started at about 16:06Z. Then the base Commit and rowcmp against the record (program `fdd998d4`, v2 manifest `47990631`, commit_pass True) |
| `vyv-rf-b1-tp2` (2x L40S) | 0g809k86dbuwyv | 2.18 | #70 `r20260925-141723-16b0` (`/workspace/b1/tools/tp2.sh`), in `tp.commit` since about 15:28Z. Then cmp70 against f1's base summary (`tools/f1base70/`) |

## Already recorded (don't redo)
Gate (b) at `8c0bec08` (0 new failures or skips); gate (a) T0+T1 158/158 equal to a23b's base, with replay_partition head
within 1.6% of base (`evidence/gate_a/`, R2 `art:c62253fe…`); #101 head = base = record. `vyv-rf-b1-big` and the old
cpu/g1 pods are gone.

## Next
1. #70: when tp2's run ends, record the cmp70 result (32/32 fields expected), then terminate tp2.
2. #67: record the head Commit against the record. **The base Commit is optional:** it's only the "replay wall before"
   number, and gate (a)'s replay_partition already gives head against base. Keep it only if it ends by about
   19:45Z (12:45 PM PT); otherwise stop it by pgid, and say why in READY.md. Terminate g2 when done.
3. Re-gate the rebased head against `origin/main`, head and base on the same pod: lints and gate (b). **Pod:**
   `vyv-rf-b5pat-cpu` (16 vCPU, bootstrapped), which lane `vllm-rf-b5patc` hands to you. Wait for its handoff in your
   notes directory. If it hasn't come by 17:30Z, create a cpu3g pod `vyv-rf-b1c-cpu`.
4. Finish READY.md: fill `NEEDS`, `R67_SHORT` and `R70_SHORT`, record both heads, then send a merge-ready handoff.
   Carry over the open item: the difftest hunks in b2v's `properties/admission.py`. b2vb is in the merge queue at
   `ed8f6625`; check `git merge-tree` against it and note any overlap.

## Budget
$10 of new spend from 16:20Z: g2 to the end of #67 (about $3–4), tp2 to the end of #70 (about $2), about $2 of cpu re-gating.
