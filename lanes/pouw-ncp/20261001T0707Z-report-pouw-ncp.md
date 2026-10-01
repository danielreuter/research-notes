---
lane: pouw-ncp
kind: report
created: 2026-10-01T07:07Z
status: open
---

CHECKPOINT 5a7f8affa (07:07Z) [open] bc-2f661c92 on branch cursor/ncp-sm120-687a: ported the NCP-FP8 D-3s chain to sm_120a on pearl_c_sm120's mainloop (arms: plain, core, store, fused BLAKE3; no spills; 128/32 QMMA). Profile run r20261001-070654-8dfe is on node 2, untimed and preemptible, because node 1 isn't reachable through the queue (kueue-fold's executor isn't built). Prior: hashing every D-3s word costs at least ~130x on sm_120 with BLAKE3, so going under 20x needs about 8x fewer bound bytes.
