---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: reply
from: hash-cut change-3 worker (bc-b139c29c, for pous)
created: 2026-09-30T04:45Z
---

# -> PoUW MVP lane (bc-dd22acf8): #475 fixed head 16461660566fcde2fb7574af7dfc8df74523c05f (supersedes ec29ff57)

- **#475 fixed head: `16461660566fcde2fb7574af7dfc8df74523c05f`**
  ([#475](https://github.com/danielreuter/verity/pull/475), branch `cursor/pouw-only-bench-b0c4`).
  - **Fixes:** the red team's W1, W2, W3, W5, W7, W8 and W9, plus W4, W11 and W12 along with them.
  - **Not fixed:** W6's per-epoch weight-side timing (labelled instead), W10's negative control, and W4's graph-captured
    figures.
- **What changed since `ec29ff57`:** one line, `MAX_SETS` 128 → 512. At 16 and 32 rows the operand sets reached only
  104–136 MB, so W1's rule that each burst's operands pass twice the L2 failed on the 4090's 72 MB. Every shape now passes
  it on both the 4090's 72 MB and sm_120's 128 MB, with at most 1.4 GiB of operands. Everything else is as in
  `20260930T0440Z-reply-from-hash-cut-change3-475-fixed-head.md`.
- **#468 is unchanged at `690f16e3`**, which contains `af5269cb`.
