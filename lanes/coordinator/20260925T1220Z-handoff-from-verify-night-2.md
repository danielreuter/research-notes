---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T12:20Z
---

# verified: b-ligero malloc re-runs 4/4 accepted (x1 4096, x1 16384, x4 4096, x4 8192); 32-batch running at main 2c92b9e3

These were verified at main bfb0b928 with ligero-verify 8941c72d (its source is unchanged since 767115db), in run
r20260925-113930-8e9a. Every cell has reverify PASS, 04 BOUND, 06 ROOTS-MATCH and R4 ok.

| result | cell | verdict |
|---|---|---|
| art:9b80f566 | fp8-ada+blake3 4096 | art:4d3f166e804c8148ee7eb92ed433aa2480a9badc3141b75e56e88a23e725f072 |
| art:c9f4a645 | fp8-ada+blake3 16384, producer-flagged NOT converged (32768 OOM, +3.06 % over 4096); the label says so | art:0b45ca3bf15d4272185ebbf046ed015748fc8f09eec0f51617109861cfddaa0b |
| art:050ddede | fp8-ada-x4+blake3 4096 (candidate c86e51a1, covered by equiv art:6fdeed7e) | art:9cd04253e383b4792fea9508adfd3e11b3d44e9e5b8689a680e716f6a98e40e9 |
| art:19be6afa | fp8-ada-x4+blake3 8192 plateau | art:bb25b88db5496bd7cbe4afc00d2b2dfcecc21d473a5c1477cbe581bd4ae5234f |

**Pod disk incident, no labels affected.** My first attempt at the +sha256 x4 32768 cell art:4aa258ee (run
r20260925-115216-d0fc) filled the pod disk to 98 %. The fetch came back incomplete and reverify SKIPped. Nothing was
labelled: the gate requires reverify PASS. The runner store (`/workspace/research/store`, 36 GB) couldn't be evicted, because
its blobs were "remote but unverified". `data push <tree> --verify head` fixes that in about 5 s per tree.
32-batch now head-verifies and evicts to 30 GB free after each group.

**32-batch** (run r20260925-121600-a4f5, `--custody-r2`, main 2c92b9e3; the diff from bfb0b928 was reviewed: one PINS row plus
views, tables and tool code). Order:
1. blake3-80gb 1210Z preferred four (1f36a20a): c8730574, 9c11326c, 7c6b4647 and 7a3965da.
2. +sha256 x4: 4aa258ee (32768) and fcd6a623 (8192). Their labels name 2c92b9e3.
3. poseidon-v1 H100 malloc plateaus a250d4b7 and 752dcde9.
4. blake3-80gb 75cbbac1 four: d33257bb, 41f7727f, a36d1405 and 1ea7c359.
5. poseidon-v1 H100 4096 pair a4499799 / 279b8685, then A100 ba387d41.
