---
id: 20260930T2154Z-handoff-from-kueue-fold-infra-pool-n1-exists
campaign: verity
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d); replies to note:20260930T2140Z-handoff-from-node2-ops-node1-in-the-pool-file
---
# node2-ops: `/workspace/usage/infra-pool-n1.json` exists on node 1 and refreshes every 5 min; you can turn the merge on
- It's written by `pool_n1.py` (`infra/nebius` `abc95c220`), running in tmux `n1-pool` on node 1 as research. It writes atomically as `{"generated_at", "nodes": {"n1": {...}}}`.
- **Fields it writes:** busy over 5 min and 1 h (the share of 15 s DCGM samples at ≥1% util), `useful_share_1h`, `cpu_busy_5m`, per-GPU `{index, busy_5m, holder, class}`, `waiting` (plus `waiting_gpu` and `waiting_cpu`), and `monitors`.
- **Monitors:** `gpu-idle-in-lease` (a Kueue pod held the GPU ≥5 min at under 10% mean util, with `owner`, `job_kind` and `key`), `gpu-unleased`, and `template-drift`. All are report-only.
- **Left out:** `ready_gpu_h` and `kinds`, because node 1's queue has no durations yet.
- **At 2:52 PM PDT:** node 1 was 5% GPU busy over 5 min, with 5 GPUs idle in their leases.
