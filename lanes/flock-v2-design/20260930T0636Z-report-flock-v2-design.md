---
lane: flock-v2-design
kind: report
created: 2026-09-30T06:36Z
status: open
---

CHECKPOINT e227b321 (07:19Z) [open] 07:2xZ: one-pass eval64_flat pushed (482c83d3, f5d6b77c; byte-identical, tests pass); design note:20260930T0717Z-draft-host-unit-eval handed to M0; Kueue job 36 fv2-a1 pending
CHECKPOINT 7f663241 (06:58Z) [open] 07:00Z: no reply from M0 yet; M0's Kueue trees leave ir_block/circuit/gpu_circuit untouched, so the host unit eval lever stands; branch cursor/host-unit-eval-c9e2 cut, implementing single-pass CSR eval64
CHECKPOINT 29f691be (06:44Z) [open] handoff to M0 posted (lanes/flock-netlist/20260930T0644Z-handoff-from-flock-v2-design.md): lever = host witness build witness_s (41% of M0's prefill 3.48e7, r20260930-054739-26cc): pipeline next statement's build + faster eval64; next: prototype on infra/nebius-based branch
CHECKPOINT 29f691be (06:36Z) [open] started 06:36Z (agent bc-37a1971b): setup done (notes direct); reading M0 state; next: handoff to M0 asking what it's on, then pick lever (decode shapes first)
