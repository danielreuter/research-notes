---
lane: coordinator
kind: handoff
from: laptop-coordinator
created: 2026-09-24T20:22Z
---

# laptop coordinator -> Project coordinator: the user wants you to know exactly which tables he expects: kb/TABLES.md; also the laptop disk is at 3.3 GiB

1. **Tables.** `kb/TABLES.md` is now the one standing spec. It covers:
   - the three frozen tables and the three drill-downs, and the only way to render them;
   - every rule the user set;
   - what "complete" means, and today's gaps.

   The gaps that need lanes:
   - **A-GKR:** H100 FP8, 4090 FP8 and 5090 NVFP4.
   - **SP1:** every row, at 2^-128. If SP1 cannot honestly reach it, D1 should say so.
   - **B-Ligero:** keep improving both columns.

   My 18:10Z handoff did not point you at this spec; it was buried in campaigns/morning-tables/BRIEF.md §1-3. Please make
   every lane that touches results read it, and send the user renders only.

2. **Laptop disk: 3.3 GiB free at 20:12Z**, below the memory guardian's 3.5 GiB kill floor, so large processes running on
   the laptop get killed. It was 16 GiB at 18:00Z. The causes:
   - swap at 15.8 of 17.4 GB (RAM pressure);
   - Cursor's state.vscdb at 79 GB, growing about 1 GB/h;
   - worktrees: ~/projects/verity-wt 8.6 GB (vLLM) and verity-main-wt 4.9 GB.

   While this lasts, keep laptop work minimal and remove any worktree a lane no longer needs. Remote-state step 3 (pods
   fetch code by commit) and moving lanes to cloud agents also relieve it.
