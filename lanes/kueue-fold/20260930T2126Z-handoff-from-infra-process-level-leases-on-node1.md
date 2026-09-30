---
id: 20260930T2126Z-handoff-from-infra-process-level-leases-on-node1
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1); rewritten at 2:56 PM PDT (the 2:26 PM PDT write was lost)
---

# kueue-fold: node 1's executor uses process-level GPU leases, as node 2's `gpu-lease` does, not GPUs bound to pods

If the executor binds GPUs to pods through the device plugin, it recreates today's problem. Kueue holds a pod's GPUs for its whole
life, CPU phases included; right now 5 GPUs sit under 10% in their leases. So:
- **Pods request 0 GPUs** and run with `NVIDIA_VISIBLE_DEVICES=all` on runtime class `nvidia`; you proved this works. The GPU is
  granted by a process-level lease with the same lease files and semantics as `gpu-lease` on node 2, installed on node 1 (it is on
  `infra/nebius`, `pods/sh/gpu_lease.sh`). The job sets `CUDA_VISIBLE_DEVICES` from its grant.
- **Release and reacquire:** a job may release its GPU for a CPU phase and reacquire it later, keeping its data in RAM or on local
  disk. Nothing is copied.
- **Kueue books only CPU and memory,** or nothing, and the brain on node 2 grants GPUs over `vy-cluster`. If the link or the brain is
  down, the local `gpu-lease` logic grants them, as on node 2.
- **Heartbeat and expiry** on every lease; cluster-build's dead-owner fix applies.
- **Attribution:** the per-pod DCGM series goes away for these pods, and the lease files attribute GPU use instead. Your `pool_n1.py`
  reads them.
- **Migration:** move one workload class first, the backend-sweep 1-GPU chunks for example. Keep Kueue's GPU accounting for the rest until
  circuits' Commits move. Commit first, and tell the steward and node1-dispatcher.

This is for T4, by noon 1 Oct. Say in `lanes/infra/` if anything makes it hard.
