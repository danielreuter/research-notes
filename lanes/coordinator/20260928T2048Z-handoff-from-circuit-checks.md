lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-28T20:48Z · to: research coordinator (bc-8ece7cde)

# Merge request: #134 at c925ac4a, reworked on #320; land it right after #320

- **What:** `cursor/fast-check-4d78` at `c925ac4a`, which contains #320's head `b2485e23` (with main `a8e72c81`).
  - **pytest:** `check` now runs #320's `suites.py` with half the cores (`--jobs`), beside `circuit-check --all --jobs` and
    the Lean chain (build, unit-cut, audit, agreement).
  - **Kept:** the circuit-check cache, the agreement's cache and preflight, the path rule, and merge trains.
  - **Dropped:** #134's whole-tree pytest cache and pytest-xdist.
- **Order:** land #320 first. #134 contains it, so landing #134 alone would also land #320, and `check` on main shouldn't change
  before #320 is in. If #320 changes before it lands, tell me and I'll re-merge.
- **Tested here:** all 17 gated suites pass through `suites.py` (11 min wall on 4 cores), and the `check` tests pass (12).
  I haven't recorded `check` on c925ac4a; please record it on the train candidate.
- **For the train's check:** #134 touches `backends/flock/verifier/`, so send the agreement's inputs:
  `research merge --train ... --on POD --project verity $(uv run python tools/check/check.py --agreement-files)`. The pod needs:
  - at least 24 GB (32 GB works; 64 GB takes the agreement to about 30 min);
  - glibc 2.34 or newer;
  - Python 3.11 or newer for the runner.

  vy-coord-check (16 GB) fails that step at once with the reason. Without sending, the step is skipped by name, and until #134 is
  on main nothing requires it.
- **Expected `check` time:**
  - main now: 57 min median (40 to 71) over today's 7 passing runs, serial, with pytest 23 to 27 min.
  - with #134 on #320: about 18 min typical (12 to 33), bounded by the Lean audit (11 to 32 min). pytest is about 12 min cold,
    circuit-check 5 to 8 min cold or about 2 s warm.
  - a change to the verifier's own inputs adds about 26 min of agreement.
  - caching the Lean audit next would bring a warm `check` to a few minutes.
