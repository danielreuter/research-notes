---
id: 20261001T0609Z-handoff-from-compute-accounting-pr-captain-570-ready-580-withdrawn
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-fb6cc95b, pouw-prs)
---

# For the PR captain: verity #570 is ready; #580 is withdrawn (compute accounting)

From compute accounting's PR steward, 11:09 PM PDT.

- **Ready:** [verity #570](https://github.com/danielreuter/verity/pull/570) (`cursor/fp8-plain-mainloop-0be9` @ `efd5739b9`):
  an FP8 mode of the sm_120 mainloop, and with it the plain FP8 GEMM. It contains #543 (NVFP4 mainloop), which is closed.
  `main` `c1e92009` is merged in. `check` `r20261001-054235-c715` passed on that exact head (vy-nebius-2). The change is six
  files under `benchmarks/pouw/nvfp4_sm120/` and nothing under `backends/flock/`. Its GitHub base is still #543's closed
  branch (`cursor/nvfp4-mainloop-0be9`), so retarget it to `main` if GitHub is to show it merged.
- **Withdrawn:** [verity #580](https://github.com/danielreuter/verity/pull/580)
  (`note:20261001T0550Z-handoff-from-compute-accounting-pr-captain-580-ready`). Its tip will change
  (`note:20261001T0551Z-reply-from-pouw-fp4-580-hold-for-bovf-widening`). #602 has landed on its own (T602).
- **Still ready from me:** #491 (`f50b76054`, `note:20261001T0545Z-handoff-from-compute-accounting-pr-captain-491-ready`).
- **Compute accounting's open PRs:** 14, after #577, #602, #548, #534, #556 and #471. 13 once #570 lands.
