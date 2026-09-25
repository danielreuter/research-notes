---
id: vllm-rf-b5gmb/state
lane: vllm-rf-b5gmb
kind: state
created: 2026-09-25T14:09Z
updated: 2026-09-25T14:20Z
---
# vllm-rf-b5gmb: split check/match/global_match.py (state)

> **Coordinator, 14:20Z: a4 is MERGED** (main `33e4d8d1`; its `integrations/vllm` and `packages/verity` trees are identical to `10996616`). Rebase now: `git fetch origin main && git rebase --onto origin/main 10996616 lane/vllm-rf-b5gmb`, then `git push --force-with-lease`. Gate evidence gathered on 10996616 carries over unchanged, so record both heads in READY.md.

> **Successor of b5gm** (bc-02f2939f, hung at the 12:30Z host disconnect). Agent bc-4e6d2014. Start commit `55b9d1ff`
> (`origin/lane/vllm-rf-b5gm`). The predecessor's worktrees `rf-b5gm` and `rf-b5gm-base` and its branch
> `lane/vllm-rf-b5gm` are left alone. Copied from `../vllm-rf-b5gm/STATE.md` and its READY.md draft at 14:09Z.

> **COORDINATOR, 12:26Z, URGENT (laptop disk at 1.5 GiB):** no laptop-side fetch of run outputs; `--custody-r2` on new runs.

> **Deadline** (LANE_PROMPTS_WAVE2): 2026-09-25T17:00Z, extended in steps.

- a4 base: 10996616 (a4 not in main at 14:14Z: main `b874764f`), so no rebase.
- Worktree: `~/projects/verity-wt/rf-b5gmb`, branch `lane/vllm-rf-b5gmb` = `55b9d1ff`, pushed 14:08Z.
- Budget: what remains of b5gm's $15, CPU only.

## Status: READY (14:20Z). `READY.md` in this directory. No pods left.

## Done (this lane)
- 14:08Z worktree + branch at `55b9d1ff`, pushed. No new commits: every gate had already finished on the pods.
- 14:10Z gate (a) head `r20260925-105053-df3a` (`a_head`) had finished at 13:33:50Z: pytest exit 0, 73 passed, 85
  skipped, 33 deselected, 9,759.6 s. It ran all 158 tests (the planned SIGINT at r73 never happened). `a_tail` (nohup,
  50 tests) finished 12:41:25Z: exit 0, 25 passed, 25 skipped. cgroup `memory.peak` 131.2 GB of 256 GB, no OOM event.
  - jdiff vs a23b `gate_a-t0t1-base-72884c8a-samepod.xml.gz`: 158/158 same outcome; only the 2 `manifest_digest` #70/#75
    skip-reason rewordings a4 already reported (main `5cc0506e`).
  - jdiff vs a4's `gate_a-t0t1-head-10996616-reg.xml.gz` (this lane's base): identical, rc 0.
  - tail vs full head: the 50 tail tests agree, rc 0.
  - Evidence: `evidence/gate_a/`.
- 14:12Z gate (b) head `r20260925-111421-2742` and base `r20260925-114938-c28f` (same pod `vyv-rf-b5gm-cpu`) both done:
  4,001 tests each, 3,647 passed, 51 failed, 11 errors, 286 skipped, 6 xfailed. jdiff base -> head: no outcome change,
  no test only on one side, no new failure/error/skip/skip reason, rc 0. Lint command set inside gate (b): 45/45 at
  both. Evidence: `evidence/gate_b/`.
- 14:15Z pods drained: `vyv-rf-b5gm-cpu` (`d8iv0xx7nruohu`) and `vyv-rf-b5gm-big` (`jnuvfc6j890g7v`) terminated
  (`research pods drain`, 0 unpreserved attempts). Spend estimate for b5gm + b5gmb: cpu ~4.1 h x $0.64 = ~$2.6, big
  ~3.7 h x $1.76 = ~$6.6, so ~$9.2 of $15.

## Done (predecessor b5gm, carried over)
- `55b9d1ff`: the split (see READY.md). Lints `r20260925-102424-bb2e` rc 0, 45 passed.
- GM-01 row #23 ABAB on the cpu pod: `r20260925-102545-9b89` (base1), `r20260925-103943-2969` (head1),
  `r20260925-105040-e8bc` (base2), `r20260925-110305-f7fe` (head2). Outputs byte-identical except timings;
  `global_match_global_program.json` sha256 `e5c5afba...` in all four; wall +3.6 % mean, CPU -0.05 % mean. Evidence:
  `../vllm-rf-b5gm/evidence/gm/` (hashes re-checked 14:14Z).

## Open questions
- P09 `module-cycle` entry: its member list names the new modules (count and external edges unchanged). See READY.md
  "Open question". If the coordinator reads that as the allowlist growing, the fix is outside a pure-structure split.

## Found, not fixed
- See READY.md.
- The predecessor's detached base worktree `~/projects/verity-wt/rf-b5gm-base` still exists (its READY draft said
  "removed at READY"); left alone under the restart rule.
