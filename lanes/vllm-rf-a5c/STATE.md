---
id: vllm-rf-a5c/state
lane: vllm-rf-a5c
kind: state
updated: 2026-09-25T17:56Z
---
# a5c (one CLI, typed config, decision-8 `verity_vllm.LLM`): state

**a5c succeeds a5b** (agent bc-a9b686f7, session ended at the 16:03Z laptop restart), itself successor of a5 (bc-95dc5f40).
Agent bc-ac8c8a30 (cloud VM); coordinator bc-ecac3029. Start commit **`da9e4847`** (`origin/lane/vllm-rf-a5b`, based on a4's `10996616`).
Branch `lane/vllm-rf-a5c` (pushed) = `git rebase --onto origin/main 10996616` of da9e4847, main **`239c0e28`** (fetched 16:30Z;
brief said 8a3aa083; `integrations/vllm` and `packages/verity` unchanged since c1's `8b3537d5`). Deadline 20:30Z. Budget $10 new from 16:20Z.

NB: this store's FS returns EAGAIN on overwriting a recently written file, so `research notes checkpoint` sometimes fails; I retry.
One early checkpoint went into a second report file (`20260925T1632Z-report-vllm-rf-a5c.md`).

## Commits (rebased, head `ce6d69d4`)
- a5b's 15 commits over a4, rebased onto main. Conflicts (all in `38bf7043`, one CLI):
  - `commit/padding_steps.py`, `commit/committer/hidden_gpu_src/hidden_gpu.py`: imports. c1 replaced the hidden_stream/merkle/fasttree/
    semantic_layout imports with `commit.scheme`; kept c1's `scheme` + a5's `from verity_vllm.config import option`. Neither file uses
    the dropped names.
  - `tests/lint/allowlists/p10_size.json`: native_host.py 2579 (c1's; a5 doesn't touch it), padding_steps.py 912 (real merged size).
  - Auto-merged, checked by hand (a5's +/- lines identical before and after the rebase): README.md, pipeline/commit.py, allowlists
    p07/p09/p11. No argparse/`__main__` outside pipeline/cli.py after the merge; c1 adds no `python -m verity_vllm.<module>` spawns.

## Done (inherited, at da9e4847)
- Gate 1 + gate (b) at `da9e4847` (a5b, cpu pod): 0 new failures/skips/skip reasons. LLM example verity == vllm-same. See a5b STATE.md.
- **#101 row via `verity-vllm row` on g1** (the brief called it "OLMoE b1"; the compared run is llama32-1b b1 stoch, row #101): compare
  `r20260925-145116-81b6` (PRESERVED): **RESULT SAME-OF-RECORD, CMP_RC=0**; program `ccc21347…` EQUAL, manifest `90f81868…` EQUAL,
  run root `7adcef49…` EQUAL, checks 33/33, outcome differs on 0; commit PASS. (11 differing non-decision leaves: cmd, file hashes.)
- **Gate (a) T0+T1 at `da9e4847`** on t1, `r20260925-142613-7113`: 73 passed, 85 skipped, 0 failed (1:40:37, exit 0 16:16:39Z).
  jdiff vs a23b's same-pod base XML (`/workspace/a5/logs/jdiff-gate_a-head-da9e4847.txt`): 158 = 158, 0 outcome changes, 0 new
  failures, 0 new skips; 2 skip reasons new on head (#70/#75 `manifest_digest`: "TP row: rank Programs are merged by tp_stage.sh";
  the same skip, reworded). Carries to the rebased head only for files c1 didn't touch.

## Final (17:55Z)
- Merged main `f7de4620` (coordinator 1655Z) -> head **`40b9e571`**. Lints 45/45; gate (b) head `r20260925-170857-a861` vs base
  `r20260925-173534-b495` (t1): 0 new failures/skips/skip reasons. #101 at 40b9e571 (g1 `r20260925-170927-4a2d`) SAME-OF-RECORD.
- #70 (tp2d `r20260925-144310-53e5`): commit FAIL of record, cmp70 32/32 equal. tp2d terminated 16:47Z.
- READY.md beside this file; merge-ready handoff `lanes/vllm-coordinator/20260925T1755Z-handoff-from-vllm-rf-a5c.md`.
- Pods: g1 handed to b5vc (1740Z handoff), t1 handed to b5vc (1755Z handoff). New spend about $5.
- b2vb's row_pod heredoc item: now `row_records.match_summary`; not folded (see Found, not fixed).

## Open questions
- none

## Found, not fixed
- TP rows' Commit (`pipeline/tp/commit.py`) writes runs.jsonl/summary.json but no `commit/verdict.json`, so `check.verdict.from_record`
  gives INSUFFICIENT_EVIDENCE on them. Fixing means teaching from_record the TP document set and mapping its checks to verdict
  rules: a verdict-semantics change, not small, outside a5's invariants.
- The row_pod.sh heredoc Match verdict is now `pipeline/row_records.match_summary`; folding it into `check/verdict.py` is not small.
