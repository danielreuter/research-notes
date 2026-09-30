---
id: 20260930T2334Z-handoff-from-circuits-hold-released
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: node-1 hold released (4:33 PM PDT); the steward reactivates B1/B8 first, then B16/B32 ≤ 4B; B64 and 7B+/MoE B32 stay off

Node 1: bundles 110 GB (< 150), disk 71%, all 8 GPUs idle. Slack thread 1790807092.688879 has the order the steward follows. Keep the same
order in your feeder:
- **First, B1 and B8:** the Qwen2/2.5 #557 set, then the top-p B8 subset and Qwen3-30B B8.
- **Then B16/B32 for models ≤ 4B.**
- **Deferred until #599's slim bundles** (label `held`, "bundle size"): every **B64** (cov-n133, g108, n002, g019), and **B32 of 7B+ or MoE**
  (cov-g061, n158, g084, g128). Don't submit new ones of either kind.
- The 150 GB hold stays, with at most 2 B8+ Commits writing bundles at once.
