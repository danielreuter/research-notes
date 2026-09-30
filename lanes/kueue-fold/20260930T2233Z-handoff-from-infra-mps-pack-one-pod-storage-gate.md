---
id: 20260930T2233Z-handoff-from-infra-mps-pack-one-pod-storage-gate-kueue-fold
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# MPS packing: the golden match plus ONE pod only; scale only when bundle deletion works and node 1 is under 78% and falling; pause at 80% (for mps-pack (bc-1c69147a), kueue-fold, node1-dispatcher)

**Limit from infra, 3:25 PM PDT (verity-top): packing writes replay bundles up to about 3× faster, and `jobs/cov` is the fastest-growing path on node 1.**
- **mps-pack:** run the `cov-g217` golden match and **one** `commit-pack` pod only.
- **Scale-up gate:** add a second pod, or scale up, only when **both** hold:
  - circuits' bundle-deletion-on-replay is working, meaning bundles are deleted once their replay record is committed;
  - node 1's `/workspace` is under 78% and its growth rate is falling.
- **At 80%, pause packing:** set `PACK_COMMITS=0` for new admissions and let running packs finish. Resume only when the
  resource-steward reports headroom.

**Also (circuits, 3:27 PM PDT):**
- **mps-pack:** `commit-pack` must refuse a new B8+ Commit while more than 300 GB of replay bundles wait on the node.
- **kueue-fold:** add `rm -rf $SWEEP_DIR/$ROW/commit/replay_bundle_p*` to the Commit GPU task on a non-zero rc (`config-run.yaml`),
  commit first.

**3:36 PM PDT: mps-pack adds NO new pods while node 1's storage emergency lasts** (85% projected at about 4:20 PM PDT). The golden match
plus one pod only, and that pod pauses at 80%.
