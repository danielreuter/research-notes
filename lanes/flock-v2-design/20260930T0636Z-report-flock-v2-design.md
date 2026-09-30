---
lane: flock-v2-design
kind: report
created: 2026-09-30T06:36Z
status: open
---

CHECKPOINT 7f663241 (08:14Z) [open] 08:16Z a3 labelled (flock-m0-v3 attempt 3: prefill 1.382e7, decode 3.081e5, gate pass, check sweep accepted; art:fd7816b5 art:71cef652); a4 (prepin + same-job base control) running as r20260930-080425-c735
CHECKPOINT b822c538 (08:05Z) [open] 08:10Z v3 #3 fused write + tile (r20260930-075001-a713): prefill 1.38e7, decode 3.08e5 vs #2 without it 2.36e7/5.49e5, gate digests = M0's; still host-bound only through the pipeline's cold burst; #4 (FC_HOST_PREPIN=1 + same-job BASE, b822c538) queued as job 76; design note updated in lanes/flock-netlist
CHECKPOINT 13a1479e (07:50Z) [open] 07:57Z fv2-a1 (r20260930-072120-266c) measured: prefill 1.95e7, decode 4.53e5 vs M0's 209f 2.17e7/4.90e5 (K=8192 prebuilt 5.16->3.13 s); job failed after its sweeps on a script bug (fixed 13a1479e); fused host-slot write committed (c5ec5953), queued as fv2-a3; read M0's 0701Z handoff: my lines use flock-m0-v3
CHECKPOINT e227b321 (07:34Z) [open] 07:37Z job 36 fv2-a1 gate passed (both shapes accepted, one_pass=true), m34 sweep running; M0's 209f shows K=8192 host-bound when pipelined (witness_prebuilt 5.16 s/4 > prove 0.61 s), the lever's target; queued job 45 fv2-a2 (tile 4x4, BATCH_ANDS 2^33, depth 4, CHECK=1)
CHECKPOINT e227b321 (07:19Z) [open] 07:2xZ: one-pass eval64_flat pushed (482c83d3, f5d6b77c; byte-identical, tests pass); design note:20260930T0717Z-draft-host-unit-eval handed to M0; Kueue job 36 fv2-a1 pending
CHECKPOINT 7f663241 (06:58Z) [open] 07:00Z: no reply from M0 yet; M0's Kueue trees leave ir_block/circuit/gpu_circuit untouched, so the host unit eval lever stands; branch cursor/host-unit-eval-c9e2 cut, implementing single-pass CSR eval64
CHECKPOINT 29f691be (06:44Z) [open] handoff to M0 posted (lanes/flock-netlist/20260930T0644Z-handoff-from-flock-v2-design.md): lever = host witness build witness_s (41% of M0's prefill 3.48e7, r20260930-054739-26cc): pipeline next statement's build + faster eval64; next: prototype on infra/nebius-based branch
CHECKPOINT 29f691be (06:36Z) [open] started 06:36Z (agent bc-37a1971b): setup done (notes direct); reading M0 state; next: handoff to M0 asking what it's on, then pick lever (decode shapes first)
