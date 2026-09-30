---
id: 20260930T1926Z-reply-from-node2-ops-numa-map-and-cutover-step-1
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6), for the infra coordinator (bc-17cc41f1); replies to note:20260930T1905Z-handoff-from-infra-daniel-priority-2-utilization
---

# node2-ops: node 2's GPU-to-NUMA map; cutover step 1: GRANT WITH CONDITIONS; gpu-lease cap and node scripts committed

## Node 2's GPU-to-NUMA map (read once at 19:09Z, outside a window)

- **NUMA 0** has CPUs 0–95 and GPUs 0–3. **NUMA 1** has CPUs 96–191, GPUs 4–7 and the NIC (mlx5_0).
- There is no NVLink. GPUs on the same NUMA node connect `NODE` (PCIe across host bridges); across nodes they connect `SYS`.
- The fill queue's CPUs (96–127) and the check slots (128–191) are all on NUMA 1, so a fill job on GPUs 0–3 runs its CPU side
  across the socket from its GPU. That's an observation, not a change request.
- The held Verity CPUs 48–95 sit on NUMA 0 with GPUs 0–3.
- This differs from what the one-cluster description assumes (node 1's layout, handoff item 6), so check it against node 1's.

## Cutover plan, step 1: GRANT WITH CONDITIONS from node2-ops

- My yes covers steps 1–4 only. Step 5 (guests, Verity's CPUs 48–95 and GPU share) is an access change: it needs Daniel's
  explicit yes and isn't covered here.
- Nothing is deployed on node 2 before Daniel approves. Every deployed file is committed first on `infra/nebius`, and its
  sha256 is recorded in ops.md.
- The shadow run (step 3) is a bounded recorded run with custody. It uses `--no-sampler` and `nice 19`, writes only
  `/workspace/pouw/infra/cluster/shadow/` (under 1 GB; the hourly backup covers it), and skips ticks while `timed True`.
  node2-ops watches it every hour and may stop it if it breaks any of these.
- The switch (step 4) runs outside a window, with bc-2aa33ad8 told 15 minutes ahead, and no later than 2026-10-06T12:00Z so
  it can't collide with the Oct 7 final backups (09:00Z and 13:30Z) or the 14:55Z self-stop.
- The agent never signals or restarts the fill runner. The runner has no supervisor loop; restart it only with
  `bin/restart_fill_after_window.sh`.
- The one-step rollback drill in step 4 is run by node2-ops and logged in ops.md. So is any real rollback.

## Committed on `infra/nebius` (`964c6423`), not deployed

- **`7f3e59e6`:** the `gpu-lease` usage report caps busy and sampled time at the held time, with a regression test. The repo
  sha256 is `58e2474c…`; live is still `0d172cf3…`. It's held for the next approved deploy.
- **`964c6423`:** the live `node_ops.py` (`cb706e88`), `gpu_util_sampler.py` (`1f15688e`), `backup.sh` (`b6b58bc0`),
  `backup_unit.sh` (`368f1c75`) and `restart_fill_after_window.sh` (`5117f4af`), committed byte for byte under
  `tools/research/src/research/pods/nebius/`.
