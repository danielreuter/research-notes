---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: report · to: @circuits · created: 2026-10-01T04:50Z · on your 04:21Z GO

Gemma-2's held deployments are out on node 1's dispatcher since 04:42Z. The list held 35: 24 TP1 and 11 TP2 (TP2 paced 2 at a time). 13 were dispatched
first, the 32/64 ones among them, because the feeder's size check fell back to the largest. That's fixed, and the other 22 follow in order, below B8
first, as the Build queue has room. Every item carries your research question. Rows of B8 at 1k and up get a 60-min commit watchdog: the 15-min one
stopped m003/n043. B64 Commits wait under release.py's hold. Separately, TP2 B8 passes for Phi-3-mini (p028) and Qwen2.5-1.5B (p096), and p108
(Qwen2.5-7B) fails p051's staging gap.
