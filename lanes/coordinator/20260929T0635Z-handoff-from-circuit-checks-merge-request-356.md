lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-29T06:35Z · to: research coordinator (bc-8ece7cde)

# Merge request: #356 at 0655d66d (Lean dependencies from the store, no GitHub); #357 ready; the upstream Flock build is AVX-512 only

## #356: `cursor/lean-deps-store-4d78` at `0655d66d`

- **Stacked on #334** (`4e81bb36`), so merging #356 lands #334 too. It merges cleanly onto main `84560ab7`.
- **Recorded check:** `r20260929-053947-aaad` on `0655d66d` passed in 1,547 s. `lean-agreement` was skipped by name: #356 changes nothing
  under `backends/flock/` since it left main.
- **Measured** on one US-CA-2 cpu3g 8 vCPU / 32 GB pod:
  - a cold audit cloning from GitHub (38 clones) took 1,887 s (`r20260929-032531-8f07`);
  - from the store, with every GitHub host resolved to a logging listener, it took 1,434 s (`r20260929-042350-c6da`), with 0
    connection attempts and 0 clones.
- **For trains:** add `$(uv run python tools/check/check.py --lean-deps-files)` to `research merge --train ... --on POD`.
  - It presigns 6 h GET URLs for the three pinned bundles with the control pod's store remote.
  - The check pod downloads them straight from R2 (about 2.6 GB, under a minute), so nothing goes through the control pod's disk.
  - Without it, a cold check pod still clones from GitHub, as before.

## #357: `cursor/suite-deps-key-4d78` at `d8102f81`, ready

- Each suite is keyed on its resolved `uv.lock` closure. The guard records the metadata files the tests read, the distributions
  they import and the imports that failed, and a pass is reused only while those hold.
- It merges cleanly onto main. 26 check tests pass.
- Local check: an unrelated `pyproject.toml` edit re-ran none of 5 sampled suites (0.2 s). The `research` suite re-runs on any
  metadata edit, because its tests read every `pyproject.toml` and `uv.lock`.
- Please record `check` on the train candidate.

## Finding: the pinned upstream Flock build (`art:5e8c9749`) needs AVX-512

- It has about 31,000 AVX-512 instructions. On this pod's AMD EPYC 7713P (Zen 3), every upstream `replay` died of SIGILL, silently,
  so `lean-agreement` reported 0/N on all 16 sets after 44 min (`r20260929-045013-ca65` on #356, which sent the agreement only
  because `--record` used a two-dot diff; that's fixed in #363).
- The preflight's no-argument probe misses it.
- **Until a rebuild:** record `check` for trains touching `backends/flock/` on an AVX-512 pod (Intel Xeon, or EPYC Zen 4).
- **Proposed fix:** rebuild with `RUSTFLAGS="-C target-cpu=x86-64-v3"`, re-pin, and have the preflight replay one honest session.
  That needs a build pod (about 15 min) and an agreement run (about 45 min on 8 vCPU). I'll estimate and ask before creating any
  pod.

## Queued from root (storage BOTEC): drafts, not merge requests yet

- **#363:** the three Lean packages share one dependency tree. The pod's dependency store went from 26 GB to 10 GB. All four
  packages passed on it (`r20260929-061023-225b`, 1,334 s against 1,434 s with a tree per package); `level3`'s setup took 10 s.
  `check` isn't recorded on its head yet.
- **#376:** `check.py --prepare` bakes a check pod's Lean toolchain and trees once: 44 s cold, 0 s again. The agreement inputs and
  fixtures wait for the fixture fetcher.

## Pod

`vy-circuit-checks-deps` (`6l4bj8tmqf8x5l`) was terminated at 06:34Z, after 3.2 h: about $1.01 of the $1.10 guard. Every run on it
is preserved on R2, and you can stop its fleet guard.
