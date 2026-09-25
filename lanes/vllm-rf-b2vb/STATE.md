---
id: vllm-rf-b2vb/state
lane: vllm-rf-b2vb
kind: state
updated: 2026-09-25T14:20Z
---
# b2vb (one verdict and `properties/` records): state

> **Coordinator, 14:20Z: a4 is MERGED** (main `33e4d8d1`; its `integrations/vllm` and `packages/verity` trees are identical to `10996616`). Rebase now: `git fetch origin main && git rebase --onto origin/main 10996616 lane/vllm-rf-b2vb`, then `git push --force-with-lease`. Gate evidence gathered on 10996616 carries over unchanged, so record both heads in READY.md.

**b2vb succeeds b2v** (agent bc-7d05cc29, hung at the 12:30Z host disconnect). **Start commit `8d847755`** (`origin/lane/vllm-rf-b2v`).
Agent bc-9bde181d; coordinator bc-ba6cec03. Worktree `~/projects/verity-wt/rf-b2vb`, branch `lane/vllm-rf-b2vb` (pushed at
`8d847755`, no new commits so far). **a4 base: 10996616** (not in main at 14:07Z). Budget: what remains of b2v's $30.
Deadline (LANE_PROMPTS_WAVE2): 2026-09-25T17:00Z.

> **COORDINATOR, 12:26Z, URGENT (laptop disk):** no laptop-side fetch of run outputs; new runs with `--custody-r2`; inspect on the pod or from R2.

## Spend (est.)
- b2v: L40S $1.09/h 09:28Z-11:27Z (~$2.2); TP2 `vyv-rf-b2v-tp2` $2.18/h since 09:30Z (~$10.5 at 14:20Z). Total ~$12.7 of $30.

## Done by b2v (commits on lane/vllm-rf-b2v, all in 8d847755's history)
`d3f04b9d` result type, `003e1506` sealed property records, `6e33c657` world-parametric non-interference, `66eaaa50` verdict.py absorbs
commit_verdict, `5483d13b` verdict cites property records, `c461f86d` V1 = match_verdict over CheckResults, `824a9924` holdout reads
HOLDOUT_GATES, `fd9220c9`/`95515e42`/`8d847755` lint fixes. Gates: lints 45/45 at 8d847755; gate (b) head vs base no new F/skip;
gate (a) T0,T1 73 passed / 85 skipped = a23b test by test (2 skip texts renamed before the base); #101 world 1 = record;
verdict bytes of the 10 Commit rows identical at 10996616 / 824a9924 / 8d847755. Detail: `../vllm-rf-b2v/STATE.md`, `READY.md`.

## Done by b2vb (14:05Z-)
- **#70 Commit** (`r20260925-111729-3301`, tree `66eaaa50`, PAIRS=1) ended 12:20:11Z: commit FAIL rc=1 (run exit 12), pass False,
  tp run root `0b91229f06480ce4…`, replay False, linkage True, xrank False, fold_binding False, weights_pin True, tokens [True, True].
  Against f1's base Commit of record (`r20260924-221949-8668`, 72884c8a, PAIRS=3) with b4's `cmp70.py`: **32/32 equal**
  (`evidence/cmp70-66eaaa50-vs-f1base.txt`). Against the 09-22 record on the pod (57a66b1/6d9cad0c): run and per-rank roots equal;
  value_check and manifest digest differ there as they do for f1's base (pre-v2 record) (`evidence/cmp70.txt`).
- **#70 from-record** (`evidence/fr70.txt`): base `10996616` and run tree `66eaaa50` byte-identical (sha256 a7c32c87…); head
  `8d847755` = base + one inserted `properties` block citing noninterference `442979b3…` ok (diff: 10 added lines, nothing else).
  Outcome INSUFFICIENT_EVIDENCE on all three (the TP Commit writes no commit/verdict.json; pre-existing).
- **#70 world 2** (`evidence/ni70.txt`): stored record ok, digest recomputes; rebuilt at the head from the row's Match arms = stored
  digest; worlds 3 and 4 raise ValueError; `records_of(row)` = [noninterference 442979b3…, ok].

## Running
- 14:17Z: custody of the TP2 pod's 7 runs (`evidence/custody_tp2.sh`, pod pid 41412, log /workspace/b2vb/custody.log): delete-free key
  minted on the laptop (1 h), `research data custody RUN --publish` per run, key deleted on exit.

## Next
1. Custody verified (7 `.custody`) -> terminate `vyv-rf-b2v-tp2`; remove the pod's /tmp trees (die with the pod).
2. READY.md final; final message.

## Open questions
- none

## Found, not fixed
- The TP Commit (`pipeline/tp/commit.py`, a5's) writes `commit/summary.json` (delta-tp) but no `commit/verdict.json`, so
  `verdict.from_record` on a TP row gives INSUFFICIENT_EVIDENCE with program/manifest/roots empty, at base and head alike.
- (b2v's list carried over in READY.md.)
