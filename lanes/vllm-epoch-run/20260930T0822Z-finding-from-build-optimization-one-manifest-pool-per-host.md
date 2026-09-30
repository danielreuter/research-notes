---
id: 20260930T0822Z-finding-from-build-optimization-one-manifest-pool-per-host
campaign: overnight-sep30
lane: vllm-epoch-run
kind: finding
status: open
repo: danielreuter/verity
origin: build-optimization (bc-47d0a3ed)
cursor:
  subagentId: "bc-47d0a3ed-166c-5d3b-830d-892cdf106942"
---

# build-optimization -> vllm-epoch-run, cc vllm-coordinator (bc-ecac3029): concurrent Builds on one host queue on one manifest lock

**What:** `manifest build-global` runs its component builds in a pool under an exclusive `flock` on
`$TMPDIR/verity-manifest-build-components.lock` (`pipeline/manifest.py`, `_pool_lock`). The lock is there so two pools don't both count
the same memory headroom. As a result, only one Build per host is in its manifest component phase at any moment. Every other Build on
that host waits, and so do the vLLM suite's stored TP2 tests and any pre-warm.

**Measured on vy-nebius-1:**
- a Llama-3.2-1B B8 prefill Build's manifest step took 382 s instead of 23 s;
- an OLMoE decode Build's manifest step took 331 s instead of about 40 s.

Both were waiting on the lock, and neither is a slow manifest.

**For the sweep:** rows packed onto one host serialize their manifest steps.
- Workaround: give each row its own `TMPDIR`, as the Build benchmark now does. That drops the double-count protection, which only
  matters when a host's headroom is tight.
- Proper fix: a shared memory reservation, so each pool takes only its estimated peak (`_peak`) and pools run side by side while they
  fit. It's in `docs/build-optimization-plan.md` §4. Tell me if you want it as a PR.
