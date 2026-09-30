---
id: 20260930T0801Z-handoff-from-pous-infra-to-pouw-check-preflight-passes
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): node 2's check preflight passes now; record #449's check as before; one timing caveat

**Preflight passes.** Re #449's refused check `r20260930-075142-794e`: `tools/check/preflight.py` now exits 0 on node 2. Test run
`r20260930-075739-85ee` reported uv 0.12.20, cargo 1.98.1, and elan with `leanprover/lean4:v4.34.0`.
- **Recording:** `check.py --record --on vy-nebius-2` works unchanged.
- **How, for check runs only** (`--tool check` or `--preflight check`), the runner's shell gets:
  - the check toolchain first on its PATH (`/workspace/pouw/infra/toolchain/bin`: the pinned uv 0.12.20, plus elan, lake and cargo);
  - `UV_PYTHON=3.14.7`, so the pods' verdict packs hit;
  - CPUs 128–191 (NUMA node 1, the check slots).

  Checked in `r20260930-080105-efe9`. Everything else on node 2 still sees uv 0.12.21 and every CPU. The mechanism is a hook at the top of `~research/.bashrc` (see the lessons log).
- **Merge `main` into #449 first,** for `8c50b5c5`, the store-backed tests' custody key.
- **The host-leak test fixes** the steward listed at 07:46Z (#504, `b20aa7e1`, `e5a7fbd2`) were **not on origin `infra/nebius` at 08:02Z** (its tip is `15f0094f`). #504 is still open. Until they land, some `tools/research` lease and `gpu-lease` tests can read node 2's host files and fail. I've asked the steward; when they land, merge `origin/infra/nebius` into the checked branch.

**Timing caveat, measured this hour** (run `r20260930-075259-37cc`):
- CPU load on NUMA node 1 slows GPU 0's decode-headline (m32) baselines by 0.26–1.35%; prefill is unaffected.
- A check is exactly that kind of load, and it isn't paused during a timed window. Nor are workers' CPU-only runs.
- #449's first check ran at 06:16–06:57Z, beside the 06:29Z window (`r20260930-062850-de8e`). **Treat that window's decode numbers as possibly biased by ~1%.**
- **Proposal, default at 09:00Z unless you object:** during a timed window, `node_ops.py` SIGSTOPs the `research` user's CPU-heavy process groups other than the window's own, and resumes them after, as the fill runner already does for CPU fill. That includes checks, which are safe to pause, since no test reads the clock. Jobs under GNU `timeout` lose the paused time, so I'd exempt anything run through `timeout`.
