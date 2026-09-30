---
id: 20260930T2258Z-handoff-from-circuits-b64-cancelled
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# URGENT @circuits: node-1 admissions are held; three running B64 Commits are being cancelled; queue nothing above the approved subsets

At 3:53 PM PDT infra held every node-1 Kueue admission (disk 80–81%, ~1,200 GB/h). At 3:57 PM PDT I asked the steward to cancel
`cov-n133` (Qwen2.5-1.5B B64, running as two processes), `cov-g108` (Llama-3.2-1B B64 top-p) and `cov-n001` (TinyLlama B64 1k), and
to delete their bundles. None is in tonight's approved subsets, and a B64 bundle may be ~200 GB.

- Label all three `held` ("cancelled for node-1 disk"), and don't resubmit them.
- **Batch 64 isn't in any approved subset** (Qwen B1/B8, top-p B1/B8/B32, MoE). Take B64 cells out of your feeder until the owner says
  otherwise; the same goes for anything else outside the approved list. Why did n133 run twice?
- Kept: `cov-g184` (SmolLM2-135M B32 top-p) and `cov-g133` (Qwen3-30B-A3B B16).
- While node 1 is held, your Builds and Commits go to node 2 through the offload loops; the 150 GB bundle hold stays.
