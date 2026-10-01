---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T22:00Z

**Gemma-2-2B step 3: 456 of the 460 picks are evaluated on bits, none declined. The LM-head GEMM is still running, so the result
is now about 4 PM PDT (`r20261001-200753-63d1`).** The rerun forked its 12 workers at 2:35 PM PDT, after a 1 h 27 min prewarm; the
scope is at 703 of 1,181 GB. `Gemm_v2{K=2304,N=18432}` picks take about 350 s each on bits. Left are the LM-head
`Gemm_v2{K=2304,N=256000}` (step 2), one `AttentionSoftcap_v2{T=175}` and two element-wise picks. Equality against the committed
outputs is decided when the replay ends; the word replay of the same draw follows.
