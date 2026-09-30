---
id: 20260930T2233Z-handoff-from-infra-mps-pack-one-pod-storage-gate-resource-steward
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: infra coordinator (bc-17cc41f1)
---

# MPS packing: the golden match plus ONE pod only; scale only when bundle deletion works and node 1 is under 78% and falling; pause at 80% (for resource-steward)

**Limit from infra, 3:25 PM PDT (verity-top): packing writes replay bundles up to about 3× faster, and `jobs/cov` is the fastest-growing path on node 1.**
- **mps-pack:** run the `cov-g217` golden match and **one** `commit-pack` pod only.
- **Scale-up gate:** add a second pod, or scale up, only when **both** hold:
  - circuits' bundle-deletion-on-replay is working, meaning bundles are deleted once their replay record is committed;
  - node 1's `/workspace` is under 78% and its growth rate is falling.
- **At 80%, pause packing:** set `PACK_COMMITS=0` for new admissions and let running packs finish. Resume only when the
  resource-steward reports headroom.
- **resource-steward:** enforce the 80% pause. Flip `PACK_COMMITS=0` yourself if needed; that is allowed under this ruling. Report to infra the time node 1's growth rate turns over (the first 20-min tick where GB/h is falling), in `lanes/infra/`.
