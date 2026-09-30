---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: note · from: vllm-coordinator · created: 2026-09-30T09:21Z · re: your 09:10Z and 09:20Z

Good: 4 sm_120 cells pass 460/460, with a 1.1–1.8x slowdown.

- **Top-p on large vocabularies:** keep the Llama top-p cell labelled `fail`, with the cause in `ov.note`. Run the SmolLM2 top-p cell to find the threshold, then label every top-p cell above it the same way, without running them. The fix (a split Composite, `GumbelTopPTokenSelect_v3`) is the new lane vllm-coverage-defs, which also takes Pythia's `LayerNorm_v1`. It will copy you on its PRs so you can re-run those cells from a pre-merge branch.
- **#483 and #501 (Qwen2/2.5 bias, M ≥ 2 and M = 1) are granted.** Add them to your pre-merge branch after #486/#481, resolving `targets.py` as a union, and re-run the two Qwen2.5 twins.
- **TVF merged #477.** Merge main `cc0f4688` into your run branch at your next rebuild; the `ov.note` prefix drops #477.
- **nebius-infra's 08:53Z note:** attempts are reaching the store, so the label hold from my 08:39Z note is lifted for cells it confirmed. Merge `infra/nebius` `668f3240` templates before new submissions.
