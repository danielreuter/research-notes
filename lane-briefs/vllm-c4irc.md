---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-c4irc (IR analyses to core, phase 2), successor of c4irb

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-c4irc`, the successor of `vllm-rf-c4irb` (its session ended at the 9:03 AM PT
> laptop restart). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-c4irc.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-c4irc open "..."`) within 10 minutes.

## Predecessor and branch
- c4irb: agent bc-53dac16f (itself successor of c4ir, bc-fbcf78e2). Notes: `$RESEARCH_NOTES/lanes/vllm-rf-c4irb/STATE.md`
  (14:59Z) and READY.md (draft, gate (a) PENDING).
- Head: `lane/vllm-rf-c4ir` = `lane/vllm-rf-c4irb` @ **`793f14af`** (phases 1 and 2, on main `33e4d8d1`). The subtrees
  equal the gated `7313e799`, so gates at `7313e799` vs `10996616` carry over to `793f14af` vs main.
- **No code work is expected.** Create `lane/vllm-rf-c4irc` at `793f14af` only if you must commit. Otherwise the merge
  request names `lane/vllm-rf-c4ir` @ `793f14af`. It merges cleanly with `origin/main` `8a3aa083`, which includes c1.

## Pod (yours; registered, guard 90)
| Pod | RunPod id | $/h | State at 16:10Z |
|---|---|---|---|
| `vyv-rf-c4ir-reg` (cpu3m 32 vCPU, 256 GB cgroup, fixtures in `/workspace/research/store`) | oh3k08zb07i38u | 1.76 | gate (a) T0+T1 at `7313e799`, run `r20260925-120631-fb6b` (`inputs/reg_gate_a.sh`), JUnit at `/workspace/research/runs/r20260925-120631-fb6b/gate_a.xml`. It was on the qwen3-4b-fp8 rows at 16:10Z; c4irb projected the end at about 17:10Z (10:10 AM PT) |

`baseline-jdiff.py` and a23b's base XML are at `/workspace/` on this pod.

## Next
1. When gate (a) ends, compare `gate_a.xml` with `/workspace/gate_a-t0t1-base-72884c8a-samepod.xml.gz` on the pod,
   test by test (`baseline-jdiff.py`).
2. Custody: the run predates `--custody-r2`. As c4irb did, launch a `--custody-r2` run on the same pod that copies the
   old run dir into its own. c4irb's `tools/custody_copy.sh` was a laptop file, so recreate it. Record the run_record
   `art:` id, and check `research data preserved`.
3. READY.md: fill the gate (a) row, and move the status off DRAFT. Then send the merge-ready handoff for
   `lane/vllm-rf-c4ir` @ `793f14af`, which supersedes phase 1's `cfe0ae63`.
4. **Hand over, don't terminate:** reg goes to `vllm-rf-b5vab` for its gate (a). The fixtures stay in the pod's store,
   so leave `/workspace/research/store` and the venv. If b5vab isn't running, drain and terminate reg.

## Budget
$3 of new spend (reg to the end of gate (a) plus the custody run).
