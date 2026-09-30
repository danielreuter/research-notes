---
id: 20260930T2154Z-handoff-from-kueue-fold-idle-in-lease-list
campaign: verity
lane: node1-fill
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# node1-fill: node 1's idle-GPU list is now machine-readable, in `/workspace/usage/infra-pool-n1.json` (`monitors`, refreshed every 5 min)
- **At 2:52 PM PDT:** 5% GPU busy over 5 min. Five `gpu-idle-in-lease` flags (≥5 min at under 10% util):
  - GPUs 1, 2 and 4: vllm-epoch-run's `nd-vllm-epoch-run-{f53f4a4305,130d4c4a53,53e6ca0596}-gpu-0` (`config-run@9c6a41948938`, with 49–92 GB loaded);
  - GPUs 3 and 7: backend-sweep's `nd-backend-sweep-{495608b1bf,12de9d8f6e}-prover-b-0` (93 GB each).
- The monitor is report-only; it never stops anything. For T1, use it however helps.
