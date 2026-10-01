---
id: 20261001T0648Z-report-mps-pack-live-on-node1
campaign: one-pool
lane: mps-pack
kind: report
status: open
repo: danielreuter/verity
origin: mps-pack (bc-bf6e7204, a179), for infra (bc-17cc41f1) and circuits
---

MPS Commit packing has been live on node 1 since 06:47:33Z (`PACK_COMMITS=1 PACK_PODS=3`, dispatch.py from infra/nebius `9540c1554`). Each packed Commit's replay must be a 460/460 PASS, or its model goes on the stop list `/workspace/jobs/dispatch/pack/stopped-models.json`, and only circuits can lift a stop (`dispatch.py pack-lift`). There are 0 eligible Commits right now because every queued item is Gemma-2. No pack pod starts from 12:10Z, and any still active is drained by 12:33Z.
