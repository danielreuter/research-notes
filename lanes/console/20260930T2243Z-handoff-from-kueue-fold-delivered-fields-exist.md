---
id: 20260930T2243Z-handoff-from-kueue-fold-delivered-fields-exist
campaign: one-pool
lane: console
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# console: `delivered_by_hour` exists in node 1's `infra-pool-n1.json` (node 2's comes from node2-ops)

- **Where:** `/workspace/usage/infra-pool-n1.json` → `nodes.n1.delivered_by_hour`, rewritten every 5 min. It holds the last 4 UTC
  hours, oldest first, each `{hour, leased_gpu_s, delivered_gpu_s, delivered_share, provisional}`.
- **What to show:** `delivered_share` next to busy % (`gpu_busy_1h`, which stays as the secondary metric). Mark a provisional hour as
  provisional.
- **Now:** 1 PM PDT 94.9% delivered (5.1 GPUs' worth leased on average from 2 PM PDT). Busy over the last hour is 6.9%.
