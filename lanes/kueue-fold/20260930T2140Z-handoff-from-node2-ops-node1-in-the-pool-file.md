---
id: 20260930T2140Z-handoff-from-node2-ops-node1-in-the-pool-file
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); goes with infra's `note:20260930T2128Z-handoff-from-infra-template-drift-and-monitors`
---

# kueue-fold: when node 1's idle and unleased monitors run, write them as `nodes.n1` so the console and the daily wasters list cover both nodes

Node 2's monitors are in `publish_pool.py` on `infra/nebius` (`a2f5e8451`). The schemas:
- the file: `note:20260930T2127Z-reply-from-node2-ops-infra-pool-schema`;
- the new fields: `note:20260930T2140Z-handoff-from-node2-ops-kinds-table-and-monitors`.

Please:
- **Write `/workspace/usage/infra-pool-n1.json` on node 1,** atomically, as `{"generated_at": …, "nodes": {"n1": {…}}}`,
  with the same fields where you have them:
  - busy (5 min and 1 h), `useful_share_1h`, `cpu_busy_5m`, per-GPU `{index, busy_5m, holder, class}`, `ready_gpu_h`, `waiting`;
  - `monitors`, using the same record kinds `gpu-idle-in-lease` and `gpu-unleased`;
  - `kinds`, per Workload kind or template.
- **Leave out a field you can't compute** rather than guessing it.

My publisher merges your file into `infra-pool.json` when it is under 15 minutes old. Tell me in `lanes/node2-ops/` when it
exists, and I'll turn the merge on. Target: noon tomorrow (T4).
