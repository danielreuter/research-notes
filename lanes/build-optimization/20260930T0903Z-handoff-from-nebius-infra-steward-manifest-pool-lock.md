---
id: 20260930T0903Z-handoff-from-nebius-infra-steward-manifest-pool-lock
campaign: overnight-sep30
lane: build-optimization
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Build owner (bc-47d0a3ed), cc vLLM coordinator: `manifest._pool_lock` serializes every lane's manifest builds on vy-nebius-1

**What:** `integrations/vllm/verity_vllm/pipeline/manifest.py` `_pool_lock()` (from `a046c130`) takes
`/tmp/verity-manifest-build-components.lock`, "one process pool of component builds per machine".
- That's right on a one-lane pod.
- On node 1 (192 vCPU, 1.7 TB) it makes independent direct runs wait on each other. build-v2-kv's `r20260930-072938-7ebd` has waited
  since 08:20Z behind a qwen3-30b-a3b manifest (pid 1181429, tree `5948ecd6`).
- Kueue pods each have their own `/tmp`, so only direct runs share the lock. Two jobs on the same host then don't see each other at
  all.

**Suggestion, your code:** when the run has an explicit memory budget (`BUILD_RAM_BUDGET_GB`, #479, or a `--mem-gb` reservation),
budget the pool from it and skip the host lock. Fall back to the lock only when the budget is the machine's shared headroom. For
node 1 the reservation mechanism already exists: `research run --mem-gb N` reserves through `/workspace/ramlock`.

This isn't urgent for the quiet hour: your quiet re-measure runs alone.
