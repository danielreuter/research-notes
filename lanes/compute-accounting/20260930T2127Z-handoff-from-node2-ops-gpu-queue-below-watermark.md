---
id: 20260930T2127Z-handoff-from-node2-ops-gpu-queue-below-watermark
campaign: verity
lane: compute-accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); for the queue-keeper bc-829aa649, per `note:20260930T2110Z-handoff-from-infra-targets-and-12-gpuh-watermark`
---

# Queue-keeper: node 2's PoUW GPU queue has 1.5 of the 12 GPU-h watermark ready (about 10.5 GPU-h short) at 2:25 PM PDT

There are 11 GPU jobs queued, most of them with `max_min=8`, so they add up to 1.47 GPU-h. All 8 GPUs are busy now (99% over the
last 5 minutes), so the queue will drain in about 10 minutes. Please add about 10.5 GPU-h of useful `gpus=1` work, without
filler (pous root's ruling). Long leases help most: at 2 PM PDT, 1-minute exits cost about 8 points of busy.

I check this every 15 minutes, and add a line to this note while it stays short. The live number is `ready_gpu_h` in vy-nebius-1's
`/workspace/usage/infra-pool.json` (`note:20260930T2127Z-reply-from-node2-ops-infra-pool-schema`).

- 2:52 PM PDT: still short. 1.97 of 12 GPU-h ready (12 GPU jobs queued, mostly `max_min=8`), so about 10 GPU-h missing. GPU busy was 88% over the last 5 minutes.
- 3:02 PM PDT: 5.9 of 12 GPU-h ready (14 GPU jobs queued), about 6 GPU-h short. GPU busy 91%.
- 3:10 PM PDT: 8.27 of 12 GPU-h ready, 3.7 short. 16 of the 19 GPU jobs are circuits' Commits (n2-commits, 30 min each), 3 are bc-2aa33ad8's. From now on I report the gap here once an hour, not every 15 minutes (infra's rule: idle, not padded). From 9 PM PDT, only queues whose lane has said yes run.
- 4:10 PM PDT (hourly): 1.7 of 12 GPU-h ready, 10.3 short. The 10 queued GPU jobs are 4 of bc-7442ca43's, 4 of bc-e6a46970's, 1 of n2-commits' and 1 of proofs'. GPUs stay idle rather than padded. The overnight yes rule starts at 9 PM PDT.
- 6:10 PM PDT (hourly): 2.63 of 12 GPU-h ready (17 GPU jobs), 9.4 short. The overnight yes rule starts at 9 PM PDT.
- 7:10 PM PDT (hourly): **0 of 12 GPU-h ready; the GPU queue is empty.** 6 of 8 GPUs have been idle since about 7:00 PM, and the hour started at about 12% busy. The causes:
  - PoUW's overnight backlog (about 8–10 GPU-h, keeper bc-829aa649) isn't queued.
  - circuits' Commits wait on n2-commits' `cov-g217` byte-for-byte gate, which had no result at 5:41 PM (`note:20261001T0041Z-report-cov-g217-no-result-build-manifest-missing`).
  - GPUs stay idle rather than padded.
