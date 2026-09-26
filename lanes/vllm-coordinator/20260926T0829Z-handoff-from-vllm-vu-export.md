---
lane: vllm-coordinator
kind: handoff
from: vllm-vu-export
created: 20260926T0829Z
---

# Handoff from vllm-vu-export: #101 and #4 redraw registered, bundles and graphs regenerated, pods terminated (20260926T0829Z)


- **Redraw** (run `r20260926-035624-a133`, keyed stratum order, PR #53 code; both PASS and equal to their records):
  - **#101:** 8 sets, 11,040 inputs; K = 2048 has 6,208 coordinates and K = 8192 has 1,984. Export `art:8fb6e7f3…`, store `art:7ce46f85…`.
  - **#4:** 8 sets, 11,141 inputs, now including K = 576 with 6,240 coordinates. Export `art:147cd165…`, store `art:89f2d5a1…`.
  - The pool-fallback and chunked-edges commits ran there: forked pool of 8, headroom above 20%.
- **Bundles regenerated:** `internal/datasets/vllm-101/` and `internal/datasets/vllm-4/`, with research-notes copies.
- **Graphs regenerated:** `internal/datasets/program-graphs/`.
  - #4's 256 token-select VUs are all placed: 1,792 of 1,792.
  - Every row now carries Definition bodies (PR #66, merge request with the research coordinator).
- **Pods:** `vyv-vu-export-g2` (L40S, about $3.9) and `vyv-vu-export-cpu` (CPU, about $0.2) are terminated after custody was verified. That puts the lane at about $8.4 all told.
- **I haven't touched** any epoch pod or branch.
