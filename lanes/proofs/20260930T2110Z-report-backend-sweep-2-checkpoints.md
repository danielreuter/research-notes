---
id: 20260930T2110Z-report-backend-sweep-2-checkpoints
campaign: verity
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: backend-sweep-2
---

# backend-sweep-2: (a) sampled units and (b) whole-row checkpoints

One line an hour, for `note:20260930T2032Z-handoff-from-proofs-resume-backend-sweep-2-a-b`. Every result is a measurement on
the #554 draft prover key `4d568a3cb558b005`, node 1, queue `provers`, priority `dev`. Code: branch `cursor/backend-sweep-2-2ced`
(draft PR #601). The feeder is tmux `backend-sweep-2-feed` on node 1, and its counts are in `/workspace/jobs/sweep2-feed/feed.log`.
GPU-busy is DCGM utilization above 0 in a minute, averaged over the 8 GPUs (node 1's Prometheus); util is the mean DCGM utilization.

- 2:10 PM PDT: (b) K = 2,048 GEMM coordinate of Llama-3.2-1B's row, 50,346 statements, extrapolated at 14.09 GPU-h (1.00736 s a
  statement, `r20260930-180937-ab3f`). Chunks of 2,500 statements, 2 GPUs at once, stopping at 5% agreement over at least 3 chunks.
  The first two chunks (r0, r2500) started at 2:06 PM PDT. (a) 60 passing deployments on node 1 (of 82 `ov.gate=pass` labels; 21
  runs live on other machines). The first deployment (Llama-3.2-1B g232) has its draw stage written; the draw reproduces the
  record's 460 units, across 58 Call Definitions. The other 59 wait on its GPU selftest. Llama shape sweep: queued 252, done 222,
  failed 0. Node 1 before: GPU-busy 2.7% (10 min) / 4.2% (60 min), util 0.1% / 0.3%, CPU 27%.
