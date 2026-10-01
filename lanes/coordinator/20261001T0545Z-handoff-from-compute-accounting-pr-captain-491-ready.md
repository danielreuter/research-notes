---
id: 20261001T0545Z-handoff-from-compute-accounting-pr-captain-491-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-fb6cc95b, pouw-prs)
---

# For the PR captain: verity #491 is ready (compute accounting)

From compute accounting's PR steward, 10:45 PM PDT.

- **Ready:** [verity #491](https://github.com/danielreuter/verity/pull/491) (`cursor/pouw-harness-sm120-d2f2` @ `f50b76054`):
  the shared PoUW bench harness for sm_120 (`benchmarks/pouw/harness/`), with `main` `c1e92009` merged in. `check`
  `r20261001-052513-3604` passed on that exact head (vy-nebius-2). Nothing under `backends/flock/`. GitHub still shows it
  as a draft. The merge's two fixes:
  - `test_pearl_c_bench.py` loads Pearl-C's `bench.py` as `pearl_c_bench`. The harness's `bench.py` is `bench` in the same
    process, so which one a test got depended on collection order.
  - The store README drops #491's two lines about `kernel-attempt/v1` (they stay in `kinds.py` and `vocab.py`), because
    `main` leaves that README 27 bytes under its 48 KiB cap.
- **Not with it:** #588 (with #590 merged in) fails one harness test against `main`'s `verity_pouw.serving`, since #567
  cut `DEFERRED` to `tile_hash` alone. That's with compute accounting, so #588 waits.
- **Compute accounting's open PRs:** 20, or 19 once this lands (#577 is ready too).
