---
lane: rec-ksweep
kind: report
created: 2026-10-06T02:31Z
status: open
---

CHECKPOINT none (04:16Z) [open] 04:16Z: K=4096 and K=2048 points proved (V* 7.75 s / 7.94 s, today's --zk 5.08 / 5.10 s); proxy re-measured clean (0.87 / 0.76 s); Lean k4096 (with forgeries) and k2048 running; inner k8192 and k16384 passed (k16384: GPU 82 GB, zk 4.06 s); oprove k8192 and vstage k16384 launched.
CHECKPOINT none (04:00Z) [open] 04:01Z: K=4096 reproduces: today's --zk 5.08 s (ref 5.34), V* levels 4.53 s (ref 4.75), inner prover compute 0.71 s (ref 0.71); the proxied inner's coin wait is inflated (1.6 s vs 0.22) by foreign load on shared cores 112-127, so the curve also gives the overhead with that wait removed. vstage k4096/k2048 done (V* identical in size at both: m 35, k_log 24); oprove k4096, oprove k2048, inner k8192 running. Pushed cursor/n1-lease-orphan-scope-2de2 (n1_lease never signalled an expired lease whose owner died but whose orphan child held the lock: GPU 6 held 17 min).
CHECKPOINT none (03:18Z) [open] 03:19Z: builds done for all four K (16384: k_log 26, N=512, 2.2 GB circuit, 13:08 at 47 GB). inner k2048 got a GPU 03:18Z; inner k4096 next in FIFO. Pool is 2 GPUs (borrow window expired), so each step's leases interleave with other lanes.
CHECKPOINT none (03:00Z) [open] staged k2048 (untiled, N=2048) r20261006-024622-0722, k8192 (N=1024) r20261006-025009-dce9; staging k16384 r20261006-030016-e828. inners k2048 r20261006-025029-49cd, k4096 r20261006-025059-d2d2 queued for GPUs (pool 2, 4 waiters)
CHECKPOINT none (02:43Z) [open] build k4096 passed r20261006-023110-4fee (statement 2602e07c = rec-step2's). inner k4096 r20261006-023920-0f34 waiting for a GPU: node1 pool is 2 GPUs, both vLLM preemptible leases to ~03:30Z. build k2048 r20261006-023932-05e2 staging
CHECKPOINT none (02:31Z) [open] started: build K=4096 r20261006-023110-4fee on vy-nebius-1 (rec-step2 b6139d9b6, FLOCK_WORK=/workspace/jobs/rec-ksweep). m<=35 (circuit.rs M_MAX) forces N=2048,2048,1024,512 at K=2048..16384; next inner K=4096
