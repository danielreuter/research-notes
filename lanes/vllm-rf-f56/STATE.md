---
id: vllm-rf-f56/state
lane: vllm-rf-f56
kind: state
status: active
created: 2026-09-24T17:40Z
---
# vllm-rf-f56: collectives guard and FA-tap exactness (D16, D17) (state)

- **Brief:** `~/.research/notes/lanes/vllm-refactor/LANE_BRIEF.md`; plan `SYNTHESIS.md` §2 (D16, D17), §4 (P5, P8); survey maps `survey-observe-acquire-tp.md` §5.2, `survey-program-query-corr.md` Map 4.
- **Worktree:** `/Users/danielreuter/projects/verity-wt/rf-f56`, branch `lane/vllm-rf-f56` from `72884c8a`.
- **Scope:**
  - D16a: one MoE collective class list used by `tp/partial_source.py` and `tp/worker.py`, living in quarantine or a profile; check which list the TP regression rows exercised.
  - D16b: quarantine `AllReduceSumBf16` order vs `b1_tp2.allreduce_order`; fix to NCCL's recorded order or refuse world >= 3.
  - D16c: refuse world > 2 on Build/Commit (emit `collective: null` etc.); list what the refusal disables (TP4 work, commit 40f40a21, tp-n lane).
  - D17: FA-tap exactness property check with a record (FA2 on L40S, FA3 on H100), beside `check/noninterference.py`, digest citable.
- **Acceptance:** gates (a), (b); 2-GPU pod TP2 regression row (shared-expert MoE if one exists) verdict unchanged; world > 2 refusal tested; FA-tap records on L40S + H100 preserved via research; contradicted evidence listed in READY.md.

## Done
- 17:40Z worktree created.

## Running
- nothing yet

## Next
1. Read the code at the D16/D17 sites; map TP4 work (40f40a21, tp-n lane); find NCCL order evidence.
2. Implement D16a, D16b, D16c, D17 as separate commits.
3. Pods: CPU gates (a)/(b); 2-GPU TP2 row; L40S FA2 + H100 FA3 records.

## Open questions
- none yet

## Found, not fixed
- none yet
