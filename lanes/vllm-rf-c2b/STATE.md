---
id: vllm-rf-c2b/state
lane: vllm-rf-c2b
kind: state
agent: bc-b15365e1 (Cursor), coordinator bc-ba6cec03
updated: 2026-09-25T14:25Z
---
# c2b (Definition library, D8/D9, decision 3a): state

> **Coordinator, 14:20Z: a4 is MERGED** (main `33e4d8d1`; its `integrations/vllm` and `packages/verity` trees are identical to `10996616`). Rebase now: `git fetch origin main && git rebase --onto origin/main 10996616 lane/vllm-rf-c2b`, then `git push --force-with-lease`. Gate evidence gathered on 10996616 carries over unchanged, so record both heads in READY.md.

**c2b succeeds c2 (bc-568d82f4, hung at the 12:30Z host disconnect). Start commit `11c3e500` (`origin/lane/vllm-rf-c2`).**
c2's STATE is at `../vllm-rf-c2/STATE.md`; its evidence stays at `../vllm-rf-c2/evidence/` (not copied).

> **COORDINATOR, 12:26Z, URGENT (laptop disk at 1.5 GiB):** STOP `research fetch --all` and every other laptop-side fetch or copy of run outputs, now. Launch new runs with `research run --on ... --custody-r2`: the pod publishes the attempt and every run file to R2 itself, and the pod guard accepts that. Inspect results on the pod (ssh) or read them from R2; plain `research fetch {run}` is for status only. Keep XML and evidence in your notes under about 5 MB. Remove local copies you already fetched only once R2 has them.

> Deadline 2026-09-25T17:00Z (LANE_PROMPTS_WAVE2).

- Worktree `~/projects/verity-wt/rf-c2b`, branch `lane/vllm-rf-c2b`.
- **Base: main `33e4d8d1`** (a4 merged at 14:13Z). Rebased with `git rebase --onto origin/main 10996616` at 14:16Z, pushed with `--force-with-lease`.

## Commits (pushed, rebased; c2's id -> c2b's)
- `f6bf88c7` -> `56a32533` registry cites core for the duplicated Definitions.
- `e0fc636f` -> `dfd3e8ec` P1 lint reads `@composite` ids.
- `d838f4c4` -> `d5219087` `verity.ml.scalar`.
- `5e21eead` -> `4d053f01` `verity.ml.prims` E4M3 cast + Hopper E4M3 k32 step. **Pre-epoch head: merge up to here.**
- `11c3e500` -> `dedf5313` epoch (re-baseline), alone at the tip.
- Rebase check: `integrations/vllm` and `packages` trees are byte-identical to `5e21eead` / `11c3e500`; `git patch-id --stable`
  of the lane diff is equal before and after (full `8699d19d…`, pre-epoch `6d2cced7…`). Main's other changes since
  `10996616` are outside `integrations/vllm` and `packages` (backends/, benchmarks/, tools/research, one root test).

## Done in c2b
- 14:06:48Z gate (a) `r20260925-105303-d711` (at `5e21eead`, `vyv-rf-c2-reg`) ended rc 0: 73 passed, 85 skipped, 33 deselected,
  11,618 s. cgroup peak 156.6 GB (256 GB pod).
- jdiff on the pod (`evidence/gate_a-5e21eead/`): vs a4 head `10996616` identical (no outcome, skip-reason or id change);
  vs a23b base `72884c8a` 158/158 same outcome, only the 2 known TP-row `manifest_digest` skip rewordings (main `5cc0506e`,
  the same two a4 reported).
- Custody: the run predates `--custody-r2` (its local attempt names no run record; attempts are immutable). From the pod with a
  minted 1 h delete-free key (deleted 14:14Z): pushed the attempt as is (events + resources telemetry, PRESERVED
  sha256-readback) and a separate `run-record/v1` of all 16 run files, `art:6b5ef88ed51fc0eae5adb659e422b80e10d3c1f0916fe36c7f7171c6a0722622`
  (PRESERVED; matches the run dir byte for byte). Checked from the laptop with `research data preserved`.
  Script: `tools/custody_gate_a.py`.
- 14:15Z `vyv-rf-c2-reg` TERMINATED (`research pods drain`: 1/1 preserved). No `vyv-rf-c2-*` pod left.

## Spend
- cpu $3.33 + g1 $1.42 + reg 10:28Z-14:15Z at $1.76/h ($6.66) = **~$11.4 of $25**. No c2b pods.

## Running
(nothing)

## Next
- READY.md (done), final message.

## Open questions
(none)

## Found, not fixed
- See c2's list (in READY.md). New: runs launched before `--custody-r2` have a local attempt with no run record, so
  `research data custody RUN --publish` returns "already" and then fails verify; the only route without a laptop fetch is a
  separate run-record artifact (done here), which the attempt does not name.
