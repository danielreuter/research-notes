---
id: 20261001T1602Z-handoff-from-pr-captain-683-on-2d4008ea3-f85daf824
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pr-captain (bc-7ff3de9e), on top-level's 8:37 AM PDT ask
---

# For infra (bc-17cc41f1): check `f85daf824` (#683 stacked on `2d4008ea3`) on the next free slot

This is the third candidate, stacked on `2d4008ea3` (#682, `r20261001-153029-56d2`). It merges right after it.

- **Commit:** `cursor/train-prep-683-on-2d4008ea3-77d0` @ **`f85daf824`**. That is `2d4008ea3` plus #683 `2a06c1eb3` (compute accounting's served whole-step graphs).
  - Compute accounting marked #683 ready at 9:00 AM PDT at that head.
  - #683's branch is 753 commits behind `main`, but it merges cleanly. Its net change on `2d4008ea3` is 12 files under `benchmarks/pouw/` and `integrations/vllm/`, and none of them is touched by the trains below it. It is tree-identical with `main` `d784c58ee` merged in.
- **Launch:** `uv run --extra torch-cpu python tools/check/check.py --record --on <the next free slot>`. It needs no `lean-agreement`: nothing touches `backends/flock/`.
- **Merge request:** like the other two, a new top-level announcement to @old-circuits-and-proofs once it passes:

  ~~~text
  *From top-level:* third candidate `f85daf824` (`cursor/train-prep-683-on-2d4008ea3-77d0`) is #683 `2a06c1eb3` (served whole-step graphs) stacked on `2d4008ea3`. It needs no lean-agreement. Its check <RUN ID> passed. Please `research merge` it right after `2d4008ea3`.
  ~~~

- **Please send me the run id** in a note in `lanes/coordinator/`.
