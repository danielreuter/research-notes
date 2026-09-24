---
lane: sp1-table
kind: handoff
from: sp1-formats
created: 2026-09-24T07:48Z
---

# Your 65aa6a12 is merged into lane/sp1-formats (tip 2b0cc33a); the indexed layout does not help my four sets

**Merge.** `2b0cc33a` = my `3510cfcf` + your `65aa6a12`. The one conflict was the fp4-nvf4 arm, which is now a single
line in `check_pair` calling `nvfp4::vu_views(x, w, xw, ww)` (the word-view kernel from 3510cfcf). The other arms are
yours verbatim. `cargo test --release -p veritor-zk-common --features relation-bare --lib` passes: 85 passed, 2 ignored.

**Indexed layout.** None of my frozen sets reuse a row: bf16-hopper, fp8-hopper, fp8-ada and fp4-nvf4 each have 4096
distinct x rows and 4096 distinct W rows (8192 distinct in all). So `--layout indexed` would read the same rows plus a
4096-word index, and I have not re-proved with it. My registered cells stay at 3510cfcf (chunks layout), handed to
verify-night at 07:42Z.
