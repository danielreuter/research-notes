---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# 22:45Z

- Verdicts: #86 approve (merge first), #90 approve, #92 HOLD for the sampler recompute fix (asked vu-export). #86->#92->#90 clean on `748c3cd6`, lints 39/39.
- Tap plan: normtap -> guarded max FA2/FA3 (cap $12); new lane vllm-rf-moetap -> router softmax + TP vocab mask (cap $8, brief lane-briefs/vllm-moetap.md); vu-export -> sampler fix (CPU, $3). Estimate about $17-20, caps $23 total, against about $48 left. No pods until approved.
