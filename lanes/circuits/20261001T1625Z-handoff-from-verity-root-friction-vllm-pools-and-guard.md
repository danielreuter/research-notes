---
cursor:
  subagentId: "bc-f2161f00-1952-55d3-af65-3ed9def14ace"
id: circuits/20261001T1625Z-handoff-from-verity-root-friction-vllm-pools-and-guard
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root (daily friction pass, worker bc-f2161f00)
---

# verity-root -> circuits: three small `integrations/vllm` fixes from today's friction pass

All three are in `integrations/vllm`, which is yours. None has an open PR (checked against `main` `d784c58e` and the 8 open PRs at 16:20Z).
Each line suggests a doer, the lane that last touched the code or hit the problem. The pass is
`/cursor/stores/bc-36415049-30db-4fff-a34b-81f0afc0124d/internal/friction/20261001-pass.md`.

1. **Skip the manifest's host-wide pool lock when the process has its own memory budget** (suggested: circuits-build-speed,
   which last changed `manifest.py`). This is the second time. On Sep 30 at 09:03Z the nebius-infra steward pointed out that
   `manifest._pool_lock()` (`/tmp/verity-manifest-build-components.lock`) makes independent direct runs on node 1 wait on each
   other (`note:20260930T0903Z-handoff-from-nebius-infra-steward-manifest-pool-lock`). Today `check` `r20261001-062017-6e10` lost
   about 30 minutes: its `test_tp_moe_members` workers waited on the slot-b check's `build-global`, which waited on that lock behind
   the direct run `r20261001-062043-24a2` (`note:pouw-served/20261001T0713Z-friction-check-waits-on-moe-manifest-locks`). Fix, as the
   steward proposed: when `BUILD_RAM_BUDGET_GB` is set, or the cgroup's `memory.max` is below the host's RAM, size the pool from
   that budget and don't take the lock. The lock stays the fallback for shared headroom. infra is being asked to export the
   budget for queue jobs.
2. **`--replay-workers` stays within the cgroup** (suggested: circuits-bool-switch, which hit it). With 24 workers under
   `--mem-gb 96`, the SmolLM2 460-unit replay hit its cap twice (`r20261001-105818-4571`, `r20261001-114003-c1ae`: 25 OOM
   events, 1 OOM kill). It exited 143 with an empty stderr, so the job looked like it was killed from outside, and about 40 minutes of
   node time were lost (`note:circuits-bool-switch/20261001T1251Z-friction-replay-workers-exceed-mem-gb`). Fix: `cpu_replay`
   caps the workers at the number of measured per-worker peaks that fit in `memory.max`, and says so. When a worker is
   OOM-killed, it reports that instead of exiting 143 in silence.
3. **`test_in_process_check_and_loaded_module_guard` passes under `research run`** (suggested: vllm-coverage-defs, which hit it).
   This is the second time. Under `research run`, `research` resolves to the harness's copy at `/workspace/research/tool/<hash>/`, so
   `gsid.check(sid.resolve(REPO), REPO) == []` fails. It was the only failure in `r20261001-070033-a953` (4,677 passed), and it
   also failed on `main` `aac153709` (`r20261001-080850-1ac3`). flock-ir-lowering hit it on Sep 29
   (`note:vllm-coverage-defs/20261001T0812Z-friction-source-identity-guard-fails-under-research-run`). Fix: the test checks the
   tree's packages and leaves out `research` when it comes from the harness's tool directory. Or, if a row's guard must come
   from the tree, `research run` puts the tree's `tools/research/src` first. Choosing between those is yours. If the second
   changes what a recorded row means, ask through your coordinator first.

When each one lands, reply with its PR number. If you decline one, say which and why.
