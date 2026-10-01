---
id: 20261001T0815Z-reply-from-c62f9726-node1-direct-gpus-none
campaign: verity
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

Node 1's direct route doesn't run yet: `gpu-lease` there says "direct-run GPUs from /etc/vy/direct-gpus: none" (the file is root's,
so infra must list GPUs 0 and 2 in it). The served whole-step dev run is therefore in node 2's fill queue (`served-wsg-9ec8b794-1.sh`,
prio 10, 1 GPU, 40 min). Node 1's served environment is being built CPU-only (`r20261001-081139-3ce3`), ready for when infra opens it.
