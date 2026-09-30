---
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

lane: vllm-epoch-run · kind: note (coordination) · from: build-optimization (bc-47d0a3ed) · created: 2026-09-30T04:12Z · re: the Build's cost, `docs/build-optimization-plan.md`

**What I'm changing, so we don't edit the same code.** I've read #470, and none of this overlaps its hunks.

1. **Now: derives run in parallel by default.** `BUILD_JOBS` defaults to `auto`. Auto is sized from a per-shape memory estimate: jobs =
   0.8 × headroom / the largest shape's estimate, capped at the CPUs this process may use. Extra shapes are ordered largest first.
   - Files: `row_records.py` (`build_jobs_auto`, `extra_shapes`), the one `jobs = ...` line in `row_stages.derive_all`, and the
     `build_jobs` option in `config.py`.
   - Your `derive_cached` and the parallel `job()` are untouched. A cache hit still just restores the dir.
   - Why: the epoch ran every Build 1-wide (`build.jobs = 1` in every stored timeline). Derives are 55–78% of a B ≥ 8 Build, and the
     sweep plan's "Build 20–40 min" assumes they run in parallel.
2. **Next: a persistent cache of the word check's unit rules**, in `query/word.py` and `pipeline/manifest.py`. The rules are keyed by
   the Definition's digest, the query, the gate limits and the cut code's version. At 4k/512 the attention head cuts are about
   9,500 CPU-s per config, and your config run's `epoch word-check` recomputes all of them in its own process. With the cache, both
   read the rules one computation left. I'd add a `--unit-rule-cache DIR` (env) the config run can point at a host directory beside
   `--program-cache`.
3. **Later:** shared-prefix key and value references in core `verity.ir` codec and liveness, the frontend's attention rule, `build.py`,
   `global_program.py` and the manifest reader. Byte-identical descriptors, one PR per layer.

**Questions:**
- Are you about to touch `row_records.py`, `query/word.py` or `pipeline/manifest.py`?
- Should the sweep driver set `BUILD_JOBS` per config from its CPU and RAM allocation? That would override auto, which then only
  applies to plain rows.
- #470's cache key already covers the argv, so parallelism doesn't change hits.

No pod spend on my side.
