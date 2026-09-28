lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-28T22:13Z · to: research coordinator (bc-8ece7cde)

# #334 (verdict caching + warm Lean deps) is built; there's been no 32 GB CPU stock since 21:25Z. Can I borrow a check pod for the measurements?

- **#334** (`cursor/check-verdict-cache-4d78` at `97a7e780`, stacked on #134) does Daniel's two calls:
  - per-package Lean audit verdicts, keyed on complete inputs and audited on a hermetic scratch tree on a miss;
  - per-target circuit-check verdicts, on traced reads with an untraceable guard;
  - warm `.lake/packages` per pod, under manifest + toolchain;
  - `LEAN_NUM_THREADS` from the pod's cores.

  It changes nothing in `tools/lean/`; the split is agreed with lean-organization.
- **Measured locally:** the real audit on a hermetic scratch tree of the verifier's Lean package passes in 75 s, and is reused
  in 0.0 s.
- **What's missing:** the cold and warm `check` times on 32 GB. RunPod has had no 32 GB CPU shape since 21:25Z; my loop tries
  every shape every 3 min. You have four check pods up (vy-coord-check3 to 6).
- **Ask:** either let me use one between trains for about 2 hours (I'd name it in my checkpoint and leave it as I found it), or
  record the runs yourself:
  1. **cold:** `uv run python tools/check/check.py --record --on POD` from a checkout of 97a7e780, on a fresh pod or after
     `rm -rf ~/.cache/verity-check`. It takes about 50 min;
  2. **warm, same commit:** the same command again. It should take 1 to 2 min;
  3. **warm, a docs-only commit and a soundness-only commit on top:** the same command. It should take 1 to 2 min and about
     5 to 10 min.

  Each run's `result.json` records the steps' times and cache hits.
