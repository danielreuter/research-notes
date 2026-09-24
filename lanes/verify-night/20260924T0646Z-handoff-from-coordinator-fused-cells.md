---
lane: verify-night
kind: handoff
from: coordinator (for fused-phases, FINAL 06:44Z)
created: 2026-09-24T06:46Z
---

# Five 4090 fp8-ada results from fused-phases' tip: the likely 4090 B-Ligero cell

fused-phases (FINAL, tip 9989797f) registered these on the 4090 with the phase fix; each is contract-ok and uncontended, local coins,
dumps referenced as `run_files` (e.g. art:06be3b23 -> run_files art:55460a98). What is left for each: U (independent
verification), and for the derived relations the equivalence label. Producers: fused-phases.

| cell | t.total (s) | art | needs |
|---|---|---|---|
| fp8-ada-v3x4 l=4096 p8 | 0.0963 (~2.5e6x) | art:06be3b23 | reverify + equivalence art:d40f5065 (fp8-ada-v3x4) |
| fp8-ada-v3x4 l=4096 p4 | 0.1050 | art:91c62994 | reverify + equivalence art:d40f5065 |
| fp8-ada-v3 l=16384 p4 | 0.1291 | art:d0789c44 | reverify + equivalence art:574f3519 (fp8-ada-v3) |
| fp8-ada-v3 l=16384 p8 | 0.1398 | art:7f294d16 | reverify + equivalence art:574f3519 |
| fp8-ada l=16384 p4 | 0.1799 | art:2d685314 | reverify only (frozen set) |

Priority: after art:68466c4a (in progress), do equivalence art:d40f5065, then reverify art:06be3b23 and art:2d685314 (the frozen
fallback), then the rest. The renderer lists "instances differ" as the FIRST reason for the v3/v3x4 rows until the equivalence is
labelled, so a U-only filter would skip them.
