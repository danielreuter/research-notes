---
id: 20260930T1545Z-report-flock-v4-design
campaign: overnight-sep30
lane: flock-v4-design
kind: report
status: open
repo: danielreuter/verity
origin: cursor/hs-dma-eb58
cursor:
  subagentId: "bc-8a7dff1c-37ef-5954-b12e-caa928daeb58"
---

CHECKPOINT 8393a3e2 (16:00Z) [open] A (chunked prefetch, M0's b85a8c7c on ac08812e, unmeasured) and B (FC_HS_DMA=1: rep-0 host slots by copy engine, cursor/hs-dma-eb58 8393a3e2, uncompiled) designed and handed to M0 (lanes/flock-netlist/20260930T1600Z-handoff-from-flock-v4-design.md); next: act on M0's results

# flock-v4-design: the host-slot upload off the prover's critical path

Launched 15:26Z by RC (bc-8ece7cde) on root's instruction: action 6 of `docs/gpu-utilization-postmortem.md`. Successor
of `flock-v2-design` (bc-37a1971b, ended 12:49Z). Agent bc-8a7dff1c. No GPU work of mine unless M0 asks.

| attempt | what | code | predicted | note |
|---|---|---|---|---|
| A | measure the chunked device prefetch (`FC_DEV_PREFETCH=1`, 8 MB pieces), steady state, same-job control | M0's `b85a8c7c`, on `ac08812e` | −5% to −7% in both metrics | `20260930T1545Z-draft-a-chunked-prefetch` |
| B | rep 0's host slots by copy engine into a kept staging buffer, in the session (`FC_HS_DMA=1`) | `8393a3e2` on `cursor/hs-dma-eb58` | 0 to −4%, most likely −2% to −3% | `20260930T1600Z-draft-b-host-slot-dma` |

- The link is near Gen5 DMA already: about 2.3 GB of a, b slots in 44 ms at m=35, K=8,192. B's gain therefore rests on
  freeing SMs for the compression chain, not on a faster copy.
- If A succeeds, B is moot in production.
