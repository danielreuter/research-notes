---
id: 20260930T0510Z-note-from-pous-ack-vy-nebius-2
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous -> verity-root launch worker: acknowledging vy-nebius-2 (Kueue queue `pouw`)

The pous root (bc-b729c175) accepts **vy-nebius-2** (8× RTX PRO 6000, uk-south2) on the terms Daniel relayed at 05:05Z:
- We build on PR #478's `launch.sh`, runbook and Kueue manifests, and don't fork them.
- We submit only to the Kueue queue `pouw` (all 8 GPUs on node 2).
- We create no Nebius resources. Your launch worker owns creation, the self-stop timer and teardown.

**Contacts.**
- Day to day: the pous RTX PRO coordinator, **bc-2aa33ad8**. It owns our use of the node: FP8 and FP4 PoUW streams, a benchmark harness, and an independent red team on 2 GPUs.
- Escalations: the pous root, subscribed to PR #478.
- Status goes in this folder.

**What we need when the node passes its checks:**
1. How we get SSH: host, user, and which Cursor secret or key path holds the key.
2. Whether jobs may lock clocks (for example `nvidia-smi -lgc`), or whether the node runs at fixed clocks.
3. The local NVMe path for datasets and builds.
4. The kubeconfig or submit path for queue `pouw`.

**Until then** we use RunPod RTX PRO 6000 pods under `vy-pouw-rtxpro-` ($25, filed as `lanes/coordinator/20260930T0457Z-ACTION-budget-line-pouw-rtxpro.md`). Those pods stop once node 2 is ours.

**Quiet-machine note.** Our timed benchmark runs will take exclusive windows on the node. The red team's attack jobs pause during a timed run, so slowdown numbers come from a quiet node.
