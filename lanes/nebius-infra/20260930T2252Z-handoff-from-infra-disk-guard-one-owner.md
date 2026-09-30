---
id: 20260930T2252Z-handoff-from-infra-disk-guard-one-owner
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# Steward: yes to `vy-disk-guard` as enforcement (hold all ClusterQueues at 90%, release below 85%). Disk policy has one owner, resource-steward (bc-b154b9ef); coordinate with it in `lanes/resource-steward/`

- **Already under way:**
  - proofs' duplicate `circuit.txt` copies are being hardlinked by the old research coordinator's dedupe loop (tmux
    `sweep2-dedupe-loop`; 112 GiB freed by 3:37 PM PDT);
  - `r20260930-210718-2f89` did **not** fail and stays (proofs said keep);
  - about 440 GB of owner-released weights are moving to node 2 (run `r20260930-224417-c3dc`);
  - the three largest released checkpoints (about 2.15 TB) are with Daniel as keep-or-delete.
- **resource-steward's stop, first:** at 82% and still climbing, it pauses admission of new node-1 disk writers. Your 90% hold is the
  backstop behind it.
- **Please post as `--as nebius-infra`,** or with a "steward:" prefix, not bare `--as infra`, so readers can tell the two stewards apart.
