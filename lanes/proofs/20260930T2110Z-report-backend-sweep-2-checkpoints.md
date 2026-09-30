---
id: 20260930T2110Z-report-backend-sweep-2-checkpoints
campaign: verity
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: backend-sweep-2
---

CHECKPOINT cc21a7d94 (22:34Z) [open] 3:35 PM PDT: (b) is verifier-bound (prover +6.6%, GPU 87% idle); owner deciding trim/stop. lean-audit question confirmed to cluster-build. Daniel's M0-chart questions: worker drafting. Node 1 disk 78%, dedupe loop running. Inbox 2209Z/2222Z/2230Z acted on.
CHECKPOINT cc21a7d94 (22:02Z) [open] 3:03 PM PDT: node 1 (b) chunks 0/2500 advancing but GPU-light (~1.2 CPU cores, GPU mostly 0%): asked old RC about M0 pipelined-witness settings; node-2 guests cut to #1936 K=8192 x3 (infra restoring its stage), non-GEMM held pending owner. Inbox 2135Z data-movement reply folded into internal/data-movement/proofs.md.
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
- 3:00 PM PDT: (b) 689 statements proved, all accepted, in chunks r0 `r20260930-210621-2a46` and r2500 `r20260930-210627-d1e9`.
  The prover averages 1.093 s a statement (median 1.027 s), 8.5% above the extrapolation, so the whole row measures 15.29 GPU-h
  against the extrapolated 14.09. A GPU is held about 9 s a statement, though, not 1: the loopback verifier checks each proof in
  series, single-threaded, in about 7 s (M0's per-shape record shows the same 7 s). So the whole row would hold GPUs for about
  125 GPU-h in this harness, and each 2,500-statement chunk about 6 h. The feeder now stops on the prover's time (`1c1578013`).
  (b) has held 1.7 GPU-h. It stops at 4 GPU-h (about 4:05 PM PDT) unless it reaches 5% first. (a) The first deployment's stage
  (`r20260930-210718-2f89`) reproduced the 460 units in the job and is staging its shapes (147 so far); the other 59 wait on its
  GPU selftest. Llama shape sweep: queued 272, done 252, failed 0. GPU-busy 7.8% (10 min) / 4.4% (60 min), util 3.1% / 1.1%.
- 4:10 PM PDT, final: stopped since 3:51 PM PDT (Daniel, 3:49 PM PDT: "forget about the vLLM deployments"; `sweep2-feed/STOPPED.json`).
  (b) got 1,598 statements, all accepted, before the stop. The prover averages 1.0927 s (+8.5% vs 1.00736 s; median 1.023 s, +1.6%),
  so the whole row is 15.28 against 14.09 GPU-h extrapolated. The GPU was held 3.70 GPU-h, 8.34 s a statement, because the loopback
  verifier (6.85 s) runs in series: 116.6 GPU-h for the whole row. Evidence in
  `art:17e200ddeb15987449bfa58ec2be108580841386d302951a9c1a9a0c9fe5eb3c`, labelled on it and on runs `r20260930-210621-2a46`,
  `r20260930-210627-d1e9` and `r20260930-214647-a70b`. (a) never reached its GPU selftest: the first deployment was staged, but its
  prove job was deleted in the stop. At 4:00 PM PDT I restarted the feeder before I had read the stop; it wrote one CPU stage job and
  one CPU sweep stage, and I deleted both within 3 minutes (no GPU used). The feeder is off again, and nothing of this lane is
  queued or running. Llama shape sweep at the stop: queued 302, done 272, failed 0. Node 1 after: GPU-busy 2.6% (10 min) / 4.1%
  (60 min), util 1.1% / 1.6%.
