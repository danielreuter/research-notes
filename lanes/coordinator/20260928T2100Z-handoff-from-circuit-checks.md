lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-28T21:00Z · to: research coordinator (bc-8ece7cde)

# Merge request (replaces 2057Z): #134 at 32f2ec5d, on #320's landing head e0389aea; land it right after #320

- **Use `32f2ec5d`** (`cursor/fast-check-4d78`). It contains #320 at `e0389aea`, with both pod fixes `b84489fd` and `e0389aea`,
  and main `a8e72c81`. The earlier `c925ac4a` lacked both fixes.
- **Order:** land #320 first. #134 contains it, so landing #134 alone would land #320 too.
- **New since c925ac4a:**
  - `check` passes `--commit` to `suites.py` in a shipped tree, as #320 does.
  - The agreement trigger leaves out `README.md` and `PROTOCOL.md` under `backends/flock/`, through `!` patterns in
    `Tool.merge_requires` shared by the gate and `check.py --record`. Nothing the agreement runs reads those files, and a test
    fails if a script starts to.
- **Tested here:**
  - After the last change, the suites I touched pass: check 16, circuit-check 21, research 476, repository 15.
  - All 17 gated suites passed on the previous head.
  - I haven't recorded `check` on 32f2ec5d; please record it on the train candidate.
- **Recording it:**
  - use a 32 GB check pod;
  - #134 changes `backends/flock/verifier/`, so add `$(uv run python tools/check/check.py --agreement-files)` to the train's
    `research merge` to exercise the agreement;
  - it needs at least 24 GB, glibc 2.34 or newer, and Python 3.11 or newer for the runner.
- **Before and after:**
  - **before:** 69 min median by the drafter's measure, serial: pytest 24, circuit-check 22, the cold Lean audit 24.
  - **after, on 32 GB with 8 vCPU:** about 25 min, bounded by the cold audit (about 24 min, plus build and unit-cut, about 1).
    It runs alongside pytest (about 12 min cold) and circuit-check (about 5 min cold, 4 jobs, measured 4.8 min on this pod
    size; about 2 s warm).
  - **when the verifier's inputs change:** add about 26 min of agreement. It's 0 s when the pod has it cached, and it's not run
    for other changes.
- **Not done, waiting for Daniel:** warm Lean dependencies per pod, verdict caching across commits, and moving the agreement after
  merge.
