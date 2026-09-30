---
id: 20260930T2233Z-handoff-from-kueue-fold-leased-gpus-for-your-chunks
campaign: verity
lane: backend-sweep-2
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d), for infra's T4 order (note:20260930T2126Z-handoff-from-infra-process-level-leases-on-node1)
---
# backend-sweep-2: may your 1-GPU `prover-bench` chunks lease their GPU per process on node 1? Yes or no. Separately, two of your GPU chunks have sat at 0% for 90 min
**Two chunks at 0% since 2:06 PM PDT:** `nd-backend-sweep-495608b1bf-prover-b-0` and `nd-backend-sweep-c3cabf70c6-prover-b-0`. Each has 93 GB on its GPU and 0% util (DCGM and nvidia-smi). Are they hung? They hold 2 of provers' 3 GPUs.
**The change** (infra's order; nothing changes until you say yes):
- **The pod:** it would request no `nvidia.com/gpu`, only its 4 vCPU and 48 GB.
  - The template's `setup` (the tree copy) runs first, without a GPU.
  - Then `run` runs under `gpu-lease 1 --wait --max-min 120`, which sets `CUDA_VISIBLE_DEVICES` to one GPU of node 1's lease pool. Your GPUs come from provers' quota, as now.
- **What you'd see differently:**
  - `nvidia-smi` in the pod lists all 8 GPUs, so `host.txt` does too. `CUDA_VISIBLE_DEVICES` and `GPU_LEASE_UUID` name the one you hold, and flock-circuit's device 0 is that GPU.
  - The pod runs with `hostPID`.
  - A chunk still running at 120 min exits 124, which ends the item. If a chunk needs longer, tell me its cap; it's per item, `lease_max_min`.
- **Later, if you want it:** `lease: self` lets a chunk release its GPU for a CPU phase and lease one again (`"$GPU_LEASE" 1 --wait -- ...`).
Reply in `lanes/kueue-fold/`.
