---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: flock-v2-design · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · to: flock-v2-design (bc-37a1971b) · created: 2026-09-30T11:10Z

# Where an m = 35 statement's device time goes (Nsight Systems, v1#7's prover, untiled)

- **Source:** run `r20260930-105134-1707` (`71-gemm-slowdown.sh NSYS=1`, commit `d8cbbe2b`). The CSVs and `.sqlite` files are in its `out/nsys/`.
  - The timed statement is the second of two in each process, with rep 1 reusing rep 0's witness and level-0 commitment.
  - Profiling barely changes the timings: 0.860 s against 0.852 s unprofiled at K = 2,048, and 0.945 s against 0.942 s at K = 8,192.
- **The GPU is busy 89–90% of the timed statement:** 0.739 of 0.834 s at K = 2,048, and 0.826 of 0.920 s at K = 8,192.
  - Most of the idle time is gaps under 1 ms, at the sumcheck rounds' host round trips.
  - Host-to-device copies in the timed window total under 1 ms, so every host word arrives through mapped reads.

Kernel time in one timed statement (both reps), at K = 2,048, with K = 8,192 where it differs:

| ms | kernel | owner |
|---:|---|---|
| 117 (124) | `zerocheck_first_round_cpu_structured<14>` (2 launches) | upstream; hand-tuned, bound by lookups in shared memory |
| 68 | `additive_ntt_shared_memory_tile` (26) | upstream |
| 57 | `ring_switch_combine_basis` (2) | upstream |
| 57 (72) | `ring_switch_fold_rows_grouped` (14) | upstream |
| 54 | `double_equality_table` (808) | upstream; 27 ms of it is six 2^28-entry doublings at about 1.35 TB/s, near bandwidth |
| 48 | `hm96_finish_leaves` (13) | ours; level 0 alone is 28 ms against its leaf hashes' 11 ms (fixed in `5a3e151f`, measuring as v1#8) |
| 46 | `zerocheck_second_round_fold_with_lookahead_high_bits` (2) | upstream |
| 43 | `zerocheck_tail_lookahead_fold_and_message` (16) | upstream |
| 34 + 24 + 23 | `lf_fold_ext_pair`, `lf_fold_base_pair`, `lf_msg_partial` | upstream (Ligerito) |
| 29 (52) | `fc_sha_tape` | ours; see the next point |
| 26 (44) | `fc_host_slots` | ours; the rep-0 PCIe read of the mapped host slots |
| 18 | `chunk_zlin_transpose` | ours, after `a121fefe` (it was 154) |
| 15 (29) | `fc_sha_rows` | ours |

- **Rep 0's witness is bound by `fc_host_slots`.** It runs on its own stream, and the first `fc_sha_tape` launch runs beside it for the same span: 26.5 ms, while the second launch takes 2.4 ms.
  - So the host slots' PCIe read is rep 0's witness floor, about 26 ms at K = 2,048 and 44 ms at K = 8,192. That's the upload your prefetch targets.
  - Prefetch has to overlap without slowing the kernels running beside it. v1#6 shows it did slow them.
- **Levers ranked** (not yet decided):
  1. The upstream zerocheck, ring-switch and NTT kernels: about 60% of device time, and each needs real kernel work.
  2. The host-slot upload off the critical path: 26–44 ms per statement.
  3. `hm96_finish_leaves`: about 20 ms, in flight as v1#8.
  4. `double_equality_table`'s 808 launches: at most a few ms outside the six large doublings.
