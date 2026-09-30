---
id: 20260930T2252Z-handoff-from-circuits-disk-hold-150
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# URGENT @circuits: node 1 at 81%, +1,200 GB/h: no new node-1 Commits until its bundles are under 150 GB; g058 is cancelled

At 3:53 PM PDT I gave the resource steward these yeses (Slack thread 1790807092.688879):
- **Hold:** no new `vllm-epoch-run/*` Commits admitted on node 1 until node 1's unreplayed bundles are under **150 GB** (it was ~180 GB:
  g058 72 GB `.partial`, g105 57 GB, n127 16, g156 13, n121 9, n099 9, g215 4). Lower your feeder's hold from 300 GB to 150 GB, for
  every batch. Node 2 keeps taking your Commits through n2-commits.
- **`cov-g058` (Mistral-7B B8) is cancelled** and its partial bundle deleted; label it `held` ("bundle too large before #599's slim
  bundles"), don't resubmit.
- **Replays run ahead of Builds** in `deployments-cpu`.
- **Pre-approved:** at 87% the steward cancels running B8+ Commits, newest first, and deletes their bundles. Label those `held`, not `fail`.
