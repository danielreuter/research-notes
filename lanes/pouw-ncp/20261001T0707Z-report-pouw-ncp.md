---
lane: pouw-ncp
kind: report
created: 2026-10-01T07:07Z
status: open
---

CHECKPOINT 5a7f8affa (07:14Z) [open] First numbers (r20261001-070654-8dfe; untimed node-2 guest at 2,092 MHz; bit-exact vs verity's sm_120 atom and BLAKE3; forming not timed). At 8192^3 against the 1.446 ms divisor: stacked MMA 3.18x, D-3s chain 3.58x, unfused ring stores 236x, every D-3s word hashed with BLAKE3 fused from registers 132x (vs 625x on H100 with TurboSHAKE128), R words only 69x, R every 4th atom 18.4x, every 8th 11.0x. Decode m=32 against 0.052 ms: chain 2.99x, dense 22.8x, R every 4th 4.6x. Hashing runs at the INT issue limit, so dense binding stays above 100x; going under 20x means binding fewer words, which touches gamma's counting step (assessor needed).
CHECKPOINT 5a7f8affa (07:07Z) [open] bc-2f661c92 on branch cursor/ncp-sm120-687a: ported the NCP-FP8 D-3s chain to sm_120a on pearl_c_sm120's mainloop (arms: plain, core, store, fused BLAKE3; no spills; 128/32 QMMA). Profile run r20261001-070654-8dfe is on node 2, untimed and preemptible, because node 1 isn't reachable through the queue (kueue-fold's executor isn't built). Prior: hashing every D-3s word costs at least ~130x on sm_120 with BLAKE3, so going under 20x needs about 8x fewer bound bytes.
