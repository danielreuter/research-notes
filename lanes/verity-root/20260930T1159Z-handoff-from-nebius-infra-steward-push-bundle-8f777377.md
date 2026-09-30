---
cursor:
  subagentId: "bc-fd19a2fe-4dd1-5d17-b138-509b5268e910"
id: 20260930T1159Z-handoff-from-nebius-infra-steward-push-bundle-8f777377
campaign: overnight-sep30
lane: verity-root
kind: handoff
status: open
origin: nebius-infra steward (bc-fd19a2fe)
---

# nebius-infra steward -> root: please push bundle `8f777377` to `infra/nebius`; one commit on `9540e031`, which makes the two-task coverage cell work with #536

**Bundle:** the Project store's `artifacts/nebius/nebius-infra-gpuless-build-libcuda-8f777377.bundle` (sha256 starts `9a56880ee490b131`). It verifies as okay and
requires `9540e031`. Branch: `cursor/nebius-bootstrap-cache-e910`.

~~~sh
git fetch <bundle> cursor/nebius-bootstrap-cache-e910 && git checkout infra/nebius && git pull origin infra/nebius
git merge --no-edit FETCH_HEAD && uv run tools/check/suites.py research repository && git push origin infra/nebius
~~~

**`8f777377`:** the coverage cell's GPU-less build task puts the host's `libcuda.so.1` (`/workspace/jobs/cuda-driver`) on
`LD_LIBRARY_PATH`.
- **Why:** #536 makes vLLM pick its CUDA platform without NVML, but importing it still loads `libcuda.so.1`, which a 0-GPU pod lacks.
  My first smoke Build failed on exactly that.
- **`cluster_up.sh` step 5** keeps the copy in step with the host driver. It's already in place on node 1, copied by hand at 11:02Z.
- The template header now calls two-task `config-run` the coverage default, and a new test covers it.
- `suites.py research repository` passes on `8f777377`: 2 suites, 6.2 min.

**Measured on node 1** (the sweep pre-merge `2847317c` + #536 = `3379d6d4`, merged with `infra/nebius`): a SmolLM2-135M two-task cell
PASSed end to end.
- **Build:** 5m52s with no GPU. Digests equal the GPU-visible reference (step `53aa6ed2`, workload `393e9228`, manifest `b8e18695`).
- **Commit:** 440 s, with replay 460/460 equal.
- **GPU hold:** 15 min for the first cell of a tree, 7m35s of that the one-time GPU bootstrap. About 7.5 min once the bootstrap is
  cached, against 16m48s–22m56s for one-GPU rows.

After you push, I tell the epoch-run lane and the Build lane to switch.
