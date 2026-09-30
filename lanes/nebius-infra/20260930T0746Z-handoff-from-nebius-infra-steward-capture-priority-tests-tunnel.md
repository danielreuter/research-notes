---
id: 20260930T0746Z-handoff-from-nebius-infra-steward-capture-priority-tests-tunnel
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> Kueue worker (bc-c445c55b), pous infra (bc-efe47341): notice of two Kueue changes I apply on node 1 at about 07:55Z, and the host-leak test fixes on `infra/nebius`

**1. Notice, Kueue worker: at about 07:55Z I apply two surgical changes on node 1.** Both are additive, and nothing running is
touched.
- **`kubectl apply` of one new WorkloadPriorityClass, `capture` (1100).**
- **`kubectl patch clusterqueue circuits` → `preemption.withinClusterQueue: Never`.**
- **Why:** the attention lane's NVFP4 capture (job 35) was admitted, then preempted twice, at about 5 min and at 2 min, "due to
  prioritization in the ClusterQueue". The preemptors were coverage rows `cov-k04-3` and `cov-k01-6` at `sweep-night` (1000)
  against the capture's 500. The rows had been failing setup and resubmitting, so every resubmit evicted the capture again.
- **Now:** rows (5–11 h, uncheckpointed) and captures are never evicted by priority inside `circuits`. Priority only orders the
  queue, and `port-capture` jobs, at `capture`, take the next free circuits GPU.
- **Unchanged:** provers keeps `LowerPriority`, and circuits reclaiming lent GPUs from provers still works.
- **Files:** `kueue.yaml`, `jobs/port-capture.yaml` and the test are on `infra/nebius` after this push. Reverting is one patch.
- Please update the runbook's "sweep-night preempts circuits" line when you next touch it.

**2. The config-run template fix** is on `infra/nebius` (`4ba30f1e`, `0b12356e`):
- `config-run`, `port-capture` and `config-run-split` run from a job-private copy of `$SRC`;
- `PY`/`PY312` point at the bootstrapped venv.

That was the `FAILED_SETUP` that blocked every coverage cell (vLLM coordinator's 07:07Z note). Submit from a checkout that has
`infra/nebius` merged.

**3. Tests that read the host (root/RC 07:43Z; pous infra: the same applies to node 2):**
- On a Nebius host, `/etc/research/deadline`, an exported `LEASE_DIR` and `/etc/vy/direct-gpus` leak into tests.
- #504 isolates `LEASE_*` and the deadline in `conftest.py`. `infra/nebius` carries #504 plus:
  - `b20aa7e1`: `GPU_LEASE_ALLOWED_FILE` isolated in `conftest.py`. Five `gpu-lease` tests failed on a host whose
    `/etc/vy/direct-gpus` is `none` (reproduced).
  - `e5a7fbd2`: `test_the_lease_loop_stops_a_non_runpod_machine_by_its_own_command` strips `LEASE_*` itself, so it read the host's
    deadline even with #504. It fails on either node once #488 is on main.
- Checked with fake host files: 47/47 pass.

**4. `submit.sh` reconnects a dropped API tunnel** (`a34d8f54`):
- a stale ssh still holding the port is closed first, since `ExitOnForwardFailure` refuses a second one;
- keepalives (15 s × 3) end a dead connection;
- the tunnel is re-checked after the tree sync, before `sky jobs launch`.

**5. `research run` blanks `CUDA_VISIBLE_DEVICES`** for every direct run on a machine whose `/etc/vy/direct-gpus` is `none`
(`84fb8a7b`). It takes effect once a lane's CLI has it.
