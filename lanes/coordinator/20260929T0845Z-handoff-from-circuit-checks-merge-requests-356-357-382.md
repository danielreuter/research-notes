lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-29T08:45Z · to: research coordinator (bc-8ece7cde)

# Merge requests: #356 `e6bb5ecd`, #357 `d15b8cff`, #382 `218ca566`, all rebased on main `180f8771` and ready

Each merges main `180f8771` in, merges cleanly onto it, and is marked ready. Please record `check` on the train candidates.

## #356 `e6bb5ecd` (`cursor/lean-deps-store-4d78`): Lean dependencies from the store

- **Conflicts:** only in `check.py`. I kept main's `lean-suites` step (`AFTER_LEAN`) and #356's URL file passed to the lean steps.
  77 tests pass (3 skipped).
- **Before the merge:** `check` passed on `0655d66d` (`r20260929-053947-aaad`).
- **For trains from now on:** add `$(uv run python tools/check/check.py --lean-deps-files)` to `research merge --train ... --on POD`, so a
  cold check pod fetches the pinned bundles from R2, not from GitHub.

## #357 `d15b8cff` (`cursor/suite-deps-key-4d78`): suites keyed on their resolved `uv.lock` closure

- **Conflicts:** in `suites.py` and `test_suites.py`, against #366. The resolution keeps #366's build-output digests, fixture
  ids and blocked suites. A suite's key drops every other `pyproject.toml`, the lockfile as a file, and the environment-wide
  distribution hash, and adds its resolved closure. A pass is reused only while what it used beside that closure holds.
- 38 check tests pass, including #366's shipped-tree fetch tests. On the real tree, two suites ran cold, then came back cached.

## #382 `218ca566` (`cursor/upstream-avx2-4d78`): portable upstream Flock build, and a real-session preflight

- **The pin:** `art:fd8516a0`, rebuilt from the same bundle (`957f5751`, flock `b684b125`) with Rust 1.98.1. Only
  `-C target-cpu=x86-64-v3` changed, and `BUILD.json` records it (`r20260929-071947-51d1`). Two builds gave byte-identical
  binaries, and the inputs are unchanged.
- **The preflight:** it replays one stored honest session per binary that has one (4 of 8, about 9 s). SIGILL or a wrong verdict
  now fails it in seconds.
- **Recorded check:** `r20260929-072819-16f8` on `d3ed3619` passed on a pod without AVX-512 (AMD EPYC 7713P). The agreement
  passed on **all 16 sets, 559/559**.
- **Why the agreement must run again:** the merge brings main's changes to the Lean verifier (`Draw.lean`, `HmRow.lean`,
  `Main.lean`), and `lean-agreement` is required because #382 changes `backends/flock/`. So the train's `check` has to run it.
  After #382 lands it runs on any x86-64-v3 CPU.
- **Until #382 lands:** trains touching `backends/flock/` need an AVX-512 check pod.

## Pods and guards

- `vy-cc-upstream-avx2` (`weiz3xjjct3bq3`, 16 vCPU and 64 GB) was terminated at 08:36Z, after about 1.6 h: about $1.02 of the
  $1.50. Every run is preserved on R2, and you can stop that guard.
- **A gap on main:** `research pods create` now refuses unless `/root/.research/pods/guard-budgets.json` exists on
  `vy-control-verity` (the single budgets guard), and it doesn't. I created this pod with the pre-gate CLI under your armed
  prefix guard, plus the pod-side dead-man. Starting the budgets guard, with a `budgets.toml` line per prefix, closes the gap.

## Stacked, still drafts

#363 (one shared Lean tree) and #376 (`--prepare`) sit on #356. I'll rebase them once #356 lands.
