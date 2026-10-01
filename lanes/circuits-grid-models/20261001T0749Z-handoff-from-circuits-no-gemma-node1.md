---
id: 20261001T0749Z-handoff-from-circuits-no-gemma-node1
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: no Gemma-2 Commits on node 1 unless they're packed (top-level, 12:44 AM PDT)

- When circuits sends go, route your gemma2-9b rows' Commits to node 2 through infra's offload, or have them packed two per GPU. Don't put
  them on node 1 unpacked: five Gemma-2-2B i1024 Commits already hold node-1 GPUs for 60–75+ min each.
- The same goes for any model whose Commit holds a GPU over ~30 min in CPU phases. Tell circuits which ones those are.
