---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Lane brief: vllm-rf-a5c (one CLI, typed config, `verity_vllm.LLM`), successor of a5b

**Launch as** a Cursor cloud agent in `danielreuter/verity`, base branch `main`, with this prompt:

> You are vLLM refactor lane `vllm-rf-a5c`, the successor of `vllm-rf-a5b` (its session ended at the 9:03 AM PT laptop
> restart). First read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/cloud-lane-setup.md`
> and do its section 1. Then read `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-cloud-common.md`
> (it overrides the setup page for vLLM lanes), then your brief
> `/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/lane-briefs/vllm-a5c.md`. Write your first checkpoint
> (`research notes checkpoint vllm-rf-a5c open "..."`) within 10 minutes.

## Predecessor and branch
- a5b: agent bc-a9b686f7 (itself successor of a5, bc-95dc5f40). Notes: `$RESEARCH_NOTES/lanes/vllm-rf-a5b/STATE.md`
  (mirror as of 14:43Z) and `../vllm-rf-a5/STATE.md`. Scope: `LANE_PROMPTS_WAVE2.md` "a5" and SYNTHESIS section 6 A5.
- Start commit: `origin/lane/vllm-rf-a5b` @ **`da9e4847`**, based on a4's `10996616`.
- Your branch: `lane/vllm-rf-a5c`. Before the first push: `git rebase --onto origin/main 10996616`.
  - **It conflicts** in `tests/lint/allowlists/p10_size.json` with c1 (merged as `8b3537d5`). Also, c1's files
    `commit/committer/hidden_gpu_src/hidden_gpu.py`, `commit/padding_steps.py` and others auto-merge with your CLI-block
    hunks. Resolve p10 from the merged files' real sizes, and check each auto-merged file by hand.
  - `origin/main` is `8a3aa083`. Everything after `8b3537d5` is `backends/` or `tools/research`, so `integrations/vllm`
    at main equals c1's.

## Pods (all yours; registered, guard 90)
| Pod | RunPod id | $/h | State at 16:10Z |
|---|---|---|---|
| `vyv-rf-a5-t1` (32 vCPU, 755 GB, fixtures in `/workspace/research/store`) | cyu8vao39x21th | 1.76 | gate (a) T0+T1 at `da9e4847`, run `r20260925-142613-7113` (`/workspace/a5/gate_a.sh`, logs `/workspace/a5/logs/gate_a-head-da9e4847.*`), about 85%, ETA about 9:45 AM PT |
| `vyv-rf-a5-tp2d` (2x L40S) | 7ttcomioru1z6o | 2.18 | #70 head via `verity-vllm row`, run `r20260925-144310-53e5` (`ab_row.sh head`), in `tp-commit` since about 15:46Z. Then b4's `cmp70.py` vs f1's base Commit of record (`/workspace/a5/commit70-base-head.tgz`) |
| `vyv-rf-a5-g1` (1x L40S) | 4w1vzyvmibdvdf | 1.09 | idle. OLMoE b1 base `r20260925-142811-0998` done (`AB_BASE_RC=0`); compare `r20260925-145116-81b6` done: **`RESULT SAME-OF-RECORD`, `CMP_RC=0`** |

## Already recorded (don't redo)
Gate 1 and gate (b) at `da9e4847` (0 new failures or skips), the `LLM(...)` example (verity equals vllm-same, greedy and
sampled), and the OLMoE b1 row via `verity-vllm row`, head = base = record (the compare run above). Details are in a5b's
STATE.md, "Done".

## Next
1. Read `r20260925-145116-81b6`'s result on g1, and record it in STATE.md.
2. Gate (a) on t1: when it ends, jdiff against a23b's base XML (gate-tools). Its evidence carries to the rebased head only
   for files c1 didn't touch; say so in READY.md.
3. #70 on tp2d: cmp70 against f1's base Commit of record (32/32 fields). Then terminate tp2d.
4. Rebase (above), then re-gate the rebased head against `origin/main` on **t1**, head and base on the same pod: lints and
   gate (b). Then the #101 smoke on **g1** at the rebased head (program `ccc21347…`, manifest `90f81868…`, run root
   `7adcef49…`, commit PASS), because the rebase merges into c1's commit/ files.
5. READY.md with both heads, then a merge-ready handoff to the coordinator.
6. **Hand over, don't terminate:** t1 goes to `vllm-rf-b5vc` for its gate (a) and gate (b); g1 goes to `vllm-rf-b5vc`
   for its #101 smoke. Follow the handover rule in the common rules.

## Budget
- $10 of new spend from 16:20Z, which is t1 and tp2d to the end of their runs plus about 2 h of re-gating.
- Open question from a5b: the TP rows write no `commit/verdict.json`, so b2v's `from_record` gives INSUFFICIENT_EVIDENCE
  on them. That's a5's area. Fix it if it's small; otherwise list it under "Found, not fixed".
