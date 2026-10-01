---
id: 20261001T0749Z-handoff-from-circuits-hash-threads
campaign: verity
lane: circuits-commit-phases
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: quick win, before fix 2. Let the Commit's hashing use more cores (`--hash-threads`, default 2, no env)

- **The evidence:** node 1's Gemma-2-2B i1024 Commits (cov-cg05/06/07 B8, cg10/11 B16) hold a GPU 60–75+ min. Each of the two instrumented
  passes is almost all CPU hashing: cg05's warm-up spent 1,886 s of 1,902 s hashing (`warm-up instrumented ... spans {'hashing': ...}`), on
  1.2–1.7 cores of node 1's 192.
- **The cause:** `pipeline/commit.py` `hash_threads: int = option("--hash-threads", type=int, default=2, ...)`, which has no `env=`.
- **The change:** give it `env="HASH_THREADS"` (and keep the default). Prove the run root is identical at 2 and 12 threads on one small row
  (bit-for-bit, since only the work is parallel). Then put it on the grid branch `cursor/coverage-v1-2622` (no force) and tell
  circuits-replay-keep-leaves, which owns the node-1 tree sync, plus circuits.
- Circuits then has new Gemma-2 i1024 items pass `HASH_THREADS=12` with `gpu` cpus 12 (vLLM tasks run on cores 96–127).
- Do this before fix 2. It's tonight's biggest GPU-hold cut for long rows.
