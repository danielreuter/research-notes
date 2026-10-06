---
lane: rec-ksweep
kind: report
created: 2026-10-06T02:31Z
status: open
---

CHECKPOINT none (03:18Z) [open] 03:19Z: builds done for all four K (16384: k_log 26, N=512, 2.2 GB circuit, 13:08 at 47 GB). inner k2048 got a GPU 03:18Z; inner k4096 next in FIFO. Pool is 2 GPUs (borrow window expired), so each step's leases interleave with other lanes.
CHECKPOINT none (03:00Z) [open] staged k2048 (untiled, N=2048) r20261006-024622-0722, k8192 (N=1024) r20261006-025009-dce9; staging k16384 r20261006-030016-e828. inners k2048 r20261006-025029-49cd, k4096 r20261006-025059-d2d2 queued for GPUs (pool 2, 4 waiters)
CHECKPOINT none (02:43Z) [open] build k4096 passed r20261006-023110-4fee (statement 2602e07c = rec-step2's). inner k4096 r20261006-023920-0f34 waiting for a GPU: node1 pool is 2 GPUs, both vLLM preemptible leases to ~03:30Z. build k2048 r20261006-023932-05e2 staging
CHECKPOINT none (02:31Z) [open] started: build K=4096 r20261006-023110-4fee on vy-nebius-1 (rec-step2 b6139d9b6, FLOCK_WORK=/workspace/jobs/rec-ksweep). m<=35 (circuit.rs M_MAX) forces N=2048,2048,1024,512 at K=2048..16384; next inner K=4096
