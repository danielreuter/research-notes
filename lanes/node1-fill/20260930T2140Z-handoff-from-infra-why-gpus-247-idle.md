---
id: 20260930T2140Z-handoff-from-infra-why-gpus-247-idle
campaign: verity
lane: node1-fill
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# node1-fill: node 1's GPUs 2, 4 and 7 are reserved but idle. TP2's config-run holds 2 through its Build and a provers pod holds 1; this is T1's blocker

Checked at 2:38 PM PDT:
- **Reservations:** Kueue has reserved all 8 GPUs, `deployments-gpu` 5 of 5 and `provers` 3 of 3. `backfill` borrows nothing, since
  nothing is left to borrow.
- **Actually on a GPU:** only 5 GPUs have a process. GPUs 0, 1 and 6 run Commits; GPUs 3 and 5 run proofs' K=2048 chunks.
- **The idle holders:**
  - `nd-vllm-epoch-run-9c1e281bb3-config-r-0` (TP2, circuits) holds 2 GPUs through its Build;
  - one of the 4 admitted `provers` backend-sweep pods holds a GPU while in a CPU phase.
- **Waiting:** proofs' 2 chunks are in `provers`, needing 1 more GPU. 31 Commits wait in `deployments-gpu`, each needing a GPU and
  170G, with StrictFIFO.

Fastest safe moves for T1 (3:30 PM PDT), your call:
1. **Co-locate one K=2048 chunk** (about 93 GB of GPU memory) on the GPU the idle provers pod holds, if proofs confirms that pod's GPU
   phase won't start for 40+ minutes. Do the same on TP2's 2 GPUs only if circuits confirms its Build runs 40+ minutes more.
2. **StrictFIFO:** with a TP2 head at the front of `deployments-gpu`, StrictFIFO can block the 1-GPU Commits behind it while GPUs
   free up one at a time. Check whether it's doing that now, and revert to BestEffortFIFO if so, keeping TP2 from starving by
   priority instead.
3. **Report T1's likely number by 3:15 PM PDT** in `lanes/infra/`.
