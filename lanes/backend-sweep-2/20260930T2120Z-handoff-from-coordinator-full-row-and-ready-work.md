---
id: 20260930T2120Z-handoff-from-coordinator-full-row-and-ready-work
campaign: verity
lane: backend-sweep-2
kind: handoff
status: open
repo: danielreuter/verity
origin: old research coordinator (bc-8ece7cde), relaying @proofs (bc-8416bc72) 2:13 PM PDT
---

# backend-sweep-2: prove the whole K=2048 row, 4 chunks at once; keep >=6 GPU-h ready; post hourly GPU-h

@proofs's five points (under Daniel's 2:06 PM PDT targets; node 1 keeps >=12 GPU-h ready):
1. (b) doesn't stop at the 5% agreement: record where 3 chunks agree, then prove all 50,346 statements (~14.1 GPU-h, inside root's budget). Still stop on a failed chunk.
2. Up to 4 (b) chunks at once, in the `backfill` tier, so chunks take GPUs as Commits free them. Commits and M0 benches keep priority.
3. (a): 60 deployments is right (58 was the 11:41 AM count); include every deployment labelled pass.
4. Keep >=6 GPU-h of proofs work ready beyond what runs: as (b) drains, queue whole-row proving of the next-largest Llama-3.2-1B GEMM coordinates, same build and labels.
5. Post hourly GPU-h ready and used in feed.log; if a chunk fails, tell @proofs at once through the coordinator (a `-handoff-from-backend-sweep-2-chunk-failed` note in lanes/coordinator/).

**Done by the coordinator at 2:19 PM PDT** (you were unreachable): points 1 and the parallel half of 2.
- `wholerow.json`: `parallel` 4, `stop_on_agree` false (backup `wholerow.json.bak-2118Z`).
- `bin/sweep_feed.py` (backup `bin/sweep_feed.py.bak-2118Z`): the 5%-agreement stop only applies when `stop_on_agree` is true; the first time 3+ chunks agree it writes `b-agreed.json` in the feeder state and shows its time as `b.agreed`.
- Feeder restarted in tmux `backend-sweep-2-feed`; chunks r0, r2500, r5000, r7500 are written.

**Yours:** the `backfill` tier for (b) items (they still go to `provers` at priority `dev`), point 4, point 5, and a check that (a) takes all 60 once its gate passes.
