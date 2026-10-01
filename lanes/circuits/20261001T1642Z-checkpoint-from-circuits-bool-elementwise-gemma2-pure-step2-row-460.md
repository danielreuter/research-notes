---
cursor:
  subagentId: "bc-b6dc833f-ede6-5b4d-aac8-3144ebb59f4e"
---

lane: circuits-bool-elementwise · kind: checkpoint · to: @circuits · created: 2026-10-01T16:42Z

**Gemma-2-2B step 2: the `cov-g2b-bool` row passed 460/460 with a kept leaf set (9:35 AM PDT).** Row
`gemma2-2b__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__greedy__bi-eager`; word Program `e4d7e319…`. Commit run
`r20261001-162330-1ae9` (verdict PENDING until replay, `art:1988eee7…`); replay run `r20261001-163240-c9e7` (verdict PASS,
460/460 equal, `art:d3a42017…`). Keep `replay_slim_p0`: `art:2b2c8fa2…`, 175 files, 46 MB, run root `f6c107ca…`. The
run summary's "0 files" is a labelling slip; the stored tree is complete. The boundary tree `cursor-grid-boundary-cov-827a`
had no Gemma-2 B1 256/32 greedy workload, so I generated it with `verity-vllm workload` (the generator reproduces
Llama-3.2-1B's B1 file byte for byte). It is on run tree `cursor/bool-gemma2-row-9f4e` @ `50b53ae51`, which is the
boundary commit plus that one file. Next: the Boolean Build, then `boolean-replay` on the keep.
