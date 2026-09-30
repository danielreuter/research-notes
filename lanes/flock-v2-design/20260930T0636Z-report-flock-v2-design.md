---
lane: flock-v2-design
kind: report
created: 2026-09-30T06:36Z
status: final
---

CHECKPOINT ce7eb155 (12:47Z) [final] 12:52Z FINAL: flock-m0-v3 on cursor/host-unit-eval-c9e2 tip ce7eb155 (no PR). Quiet #10 r20260930-122715-eaf3 at 48 vCPU: 8.56e6/1.91e5 (same-job control 8.72e6/1.92e5); best noisy #8 r20260930-103535-64c1 7.91e6/1.75e5 at 18 vCPU; all 10 attempts gate pass and labelled. Design note 20260930T0717Z-draft-host-unit-eval (also in flock-netlist and the store): about 7.4e6/1.6e5 predicted from the phases, about 6.9e6/1.5e5 with the upload in pieces (not measured), 4.9e6/1.1e5 upper bound with unit-slot slack (a statement change)
CHECKPOINT 7f663241 (12:45Z) [final] 12:47Z FINAL: flock-m0-v3 on cursor/host-unit-eval-c9e2 tip ce7eb155 (no PR). Quiet a10 r20260930-122715-eaf3 at 48 vCPU: 8.56e6/1.91e5 (control 8.72e6/1.92e5); best noisy a8 7.91e6/1.75e5 at 18 vCPU; all 10 attempts gate pass, labelled. Design note 20260930T0717Z-draft-host-unit-eval (in flock-netlist and the store): predicted 7.4e6/1.6e5 from phases, about 6.9e6/1.5e5 with the upload in pieces (not measured), 4.9e6/1.1e5 upper bound with unit-slot slack (a statement change)
CHECKPOINT 7f663241 (12:31Z) [open] 12:32Z quiet run a10 r20260930-122715-eaf3 (job 177, ce7eb155, 48 vCPU, cached binary f8176f0f7e8e2948, same-job control FC_ZLIN_BYTEWISE=1) running; circuits on Hold; gate K=2048 accepted
CHECKPOINT 7f663241 (12:15Z) [open] 12:14Z quiet run (ce7eb155, 48 vCPU, same-job control) submits about 12:27Z
CHECKPOINT 7f663241 (11:54Z) [open] 11:54Z waiting for the quiet hour; my SkyPilot tunnel had dropped and is reopened; launch slots free now (4 cells STARTING); quiet run submits about 12:27Z
CHECKPOINT 7f663241 (11:31Z) [open] 11:35Z design note: backlog item 'host-slot upload in pieces' (prefetch copies in 8 MB pieces so the prove's 29 cudaDeviceSynchronize + 78 cudaFree per process wait at most one piece; predicted about -6%, not measured); quiet run ce7eb155 at 48 vCPU submits about 12:27Z; launch-slot risk handed to the steward
CHECKPOINT 7f663241 (11:14Z) [open] 11:14Z a9 r20260930-105700-18d4 (ce7eb155, M0's a121fefe kernel): 8.08e6/1.81e5 vs same-job control 8.10e6/1.79e5, noisy node, gate pass, labelled attempt 9; binary f8176f0f7e8e2948 cached for the 12:30Z quiet run
CHECKPOINT 7f663241 (10:57Z) [open] 10:57Z a8 labelled (flock-m0-v3 attempt 8, d4566f7c: prefill 7.91e6, decode 1.75e5 vs same-job control FC_ZLIN_BYTEWISE 8.25e6/1.83e5; art:fa040c51 art:560238fa); M0 fixed the same kernel (a121fefe), so my branch takes theirs verbatim (2e39b66c); a9 (ce7eb155, M0's kernel + control) queued as job 160 to cache the quiet binary
CHECKPOINT 7f663241 (10:46Z) [open] 10:46Z cancelled stuck job 140; resubmitted a8 as job 151 (fv2-a8b, r20260930-103535-64c1, d4566f7c): built, gate passed, main sweep running, same-job FC_ZLIN_BYTEWISE control next; lesson added to nebius-infra/lessons.md
CHECKPOINT 7f663241 (10:28Z) [open] 10:28Z a8 (job 140, a7 + FC_ZLIN_BYTEWISE same-job control) was admitted borrowing, evicted by circuits' reclaim, and has sat in SkyPilot's relaunch for 20 min with no workload; waiting; design note has #7 and the unit-slot-slack backlog item
CHECKPOINT 7f663241 (10:07Z) [open] 10:07Z a7 labelled (flock-m0-v3 attempt 7, acc580a2 16-byte z_lincheck transpose: gate pass, rep-1 t.witness 0.019->0.0015 s K=2048, 0.038->0.0031 s K=8192; metric 8.63e6/1.87e5 above #4 because every other phase ran 10-40% slower on a busy node; art:d576494a art:8d54d54b); a8 = a7 + same-job control FC_ZLIN_BYTEWISE=1 (d4566f7c) queued as job 140
CHECKPOINT 7f663241 (09:44Z) [open] 09:44Z lever: chunk_zlin_transpose (z_lincheck bit transpose) stores 1 byte/thread at 128 B stride: ~19 ms/rep at m=33, 38 ms at m=34 (#4's rep-1 t.witness), ~10-12% of prove; rewrote it 16 B/thread with two 8x8 bit transposes (acc580a2, byte-equal on host k_log 7..13, NVRTC sm_120 compiles); fv2-a7 (#4's config, new key c3a2a9c1) queued as job 133
CHECKPOINT 7f663241 (09:34Z) [open] 09:36Z tip 91b6283f = 1ef30bf5 (prefetch reverted) + origin/infra/nebius 4e96ed05 (current templates; binary key d18cc4b5ed3d82b6 unchanged = #4's); told M0 its c918a68f carries the prefetch (note:20260930T0933Z-handoff-from-flock-v2-design-revert); next: unit-slot slack design, quiet re-measure at 12:30Z
CHECKPOINT 7f663241 (09:26Z) [open] 09:37Z a6 labelled (flock-m0-v3 attempt 6, steady state depth 2 RUNS=8: prefetch neutral 8.79e6 vs control 8.74e6; art:522effbf art:7b4a33b7); best stays #4's config; quiet-hour plan (48 vCPU, fallback 16) handed to M0
CHECKPOINT 7f663241 (09:04Z) [open] 09:05Z a5 labelled (flock-m0-v3 attempt 5, device prefetch: t.witness -0.024/-0.028 s per statement, hidden by +-0.05 s arithmetic noise; metric 9.07e6/2.01e5 vs control 8.75e6/1.92e5; art:3a5c5a6d art:102392c7); a6 steady-state (depth 2, RUNS=8) queued as job 112
CHECKPOINT 7f663241 (08:35Z) [open] 08:36Z a4 labelled (flock-m0-v3 attempt 4: prefill 8.23e6, decode 1.81e5 = device bound; control 1.00e7/2.20e5; art:12996d64 art:07b6c51a); handoff to M0; a5 (device prefetch of host slots, 0375d7cf) queued as job 106
CHECKPOINT 7f663241 (08:14Z) [open] 08:16Z a3 labelled (flock-m0-v3 attempt 3: prefill 1.382e7, decode 3.081e5, gate pass, check sweep accepted; art:fd7816b5 art:71cef652); a4 (prepin + same-job base control) running as r20260930-080425-c735
CHECKPOINT b822c538 (08:05Z) [open] 08:10Z v3 #3 fused write + tile (r20260930-075001-a713): prefill 1.38e7, decode 3.08e5 vs #2 without it 2.36e7/5.49e5, gate digests = M0's; still host-bound only through the pipeline's cold burst; #4 (FC_HOST_PREPIN=1 + same-job BASE, b822c538) queued as job 76; design note updated in lanes/flock-netlist
CHECKPOINT 13a1479e (07:50Z) [open] 07:57Z fv2-a1 (r20260930-072120-266c) measured: prefill 1.95e7, decode 4.53e5 vs M0's 209f 2.17e7/4.90e5 (K=8192 prebuilt 5.16->3.13 s); job failed after its sweeps on a script bug (fixed 13a1479e); fused host-slot write committed (c5ec5953), queued as fv2-a3; read M0's 0701Z handoff: my lines use flock-m0-v3
CHECKPOINT e227b321 (07:34Z) [open] 07:37Z job 36 fv2-a1 gate passed (both shapes accepted, one_pass=true), m34 sweep running; M0's 209f shows K=8192 host-bound when pipelined (witness_prebuilt 5.16 s/4 > prove 0.61 s), the lever's target; queued job 45 fv2-a2 (tile 4x4, BATCH_ANDS 2^33, depth 4, CHECK=1)
CHECKPOINT e227b321 (07:19Z) [open] 07:2xZ: one-pass eval64_flat pushed (482c83d3, f5d6b77c; byte-identical, tests pass); design note:20260930T0717Z-draft-host-unit-eval handed to M0; Kueue job 36 fv2-a1 pending
CHECKPOINT 7f663241 (06:58Z) [open] 07:00Z: no reply from M0 yet; M0's Kueue trees leave ir_block/circuit/gpu_circuit untouched, so the host unit eval lever stands; branch cursor/host-unit-eval-c9e2 cut, implementing single-pass CSR eval64
CHECKPOINT 29f691be (06:44Z) [open] handoff to M0 posted (lanes/flock-netlist/20260930T0644Z-handoff-from-flock-v2-design.md): lever = host witness build witness_s (41% of M0's prefill 3.48e7, r20260930-054739-26cc): pipeline next statement's build + faster eval64; next: prototype on infra/nebius-based branch
CHECKPOINT 29f691be (06:36Z) [open] started 06:36Z (agent bc-37a1971b): setup done (notes direct); reading M0 state; next: handoff to M0 asking what it's on, then pick lever (decode shapes first)

## Handoffs received

- `20260930T0701Z-handoff-from-flock-netlist.md` (M0: use `flock-m0-v3`, not v2): done. All ten attempts are labelled
  `ov.line=flock-m0-v3`.
- `20260930T0910Z-handoff-from-flock-netlist.md` (M0: v2 folded into v3; don't time the cold burst; go ahead with
  `prove_circuit.cuh`; re-measure v3's best in the quiet hour): done. Prepin is in v3, #5–#10 kept the gate on, and #10 is the
  quiet-hour run.
- `20260930T1035Z-handoff-from-flock-netlist.md` (M0's `a121fefe`, the same transpose fix): my branch carries it verbatim
  since `2e39b66c`. Answered in `lanes/flock-netlist/20260930T1100Z-handoff-from-flock-v2-design-zlin.md`.
- `20260930T1044Z-handoff-from-nebius-infra-steward-pull-infra-9540e031.md` (pull `infra/nebius` 9540e031): done in
  `ce7eb155`.
- `20260930T1110Z-handoff-from-flock-netlist-nsys-m35.md` (M0's Nsight breakdown and ranked levers): its API counts are the
  basis of the design note's backlog item on uploading the host slots in pieces. No reply needed.
