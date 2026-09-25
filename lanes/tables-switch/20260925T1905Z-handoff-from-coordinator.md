---
lane: tables-switch
kind: handoff
from: coordinator
created: 2026-09-25T19:05Z
---

# PR #32 is merged (main a1ccdecd): rebase onto it. The Flock column and the interaction standard are in, so don't duplicate them

- main `a1ccdecd` = PR #32 (40e1b9a1): the interaction record (file-verified results derive rounds 0 and network =
  bytes ÷ 10 Gb/s), the Flock column (class NON_ZK_PROOF) and all ten Table 2 cells under the default rules. Bench tests
  275 pass on the merged tree.
- The control-pod render at a1ccdecd shows all ten cells: `/workspace/steward/render-1900/` on vy-control-verity.
  The frozen tables differ from the 11:25 AM render only by 11 newly rejected candidates (B != 4096); the cells are
  unchanged.
- Your remaining scope is the parity command, the published default in steward.toml, the switch digest and the
  CHANGELOG. Merge-ready by 5:30 PM PT (00:30Z). The 6 PM switch runs only if your merge and #32 are both in.
