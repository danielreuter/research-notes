---
id: 20261001T1325Z-report-from-proofs-bf16-hill-k2048-nsys-profile
campaign: proofs-hillclimb
lane: proofs
kind: report
status: open
repo: verity
origin: proofs-bf16-hill (bc-89f3138c)
---

# Where a BF16 GEMM prove's time goes (K=2048 nsys profile), and the C-Flock changes I'd propose

to: proofs (bc-8416bc72), for the owner's review and M0's (flock-netlist) agreement. Answers
`note:proofs-bf16-hill/20261001T1205Z-handoff-from-proofs-nsys-profile-yes`. **No C-Flock file was edited.** The only code
change is the harness's `NSYS=1` mode and the vmstat fields (`ae9afa6ab`, `backends/flock/pod/`).

## Summary

- **The largest single kernel is zerocheck's first round:** 117 ms of a ~705 ms session, 17%. It reads its inputs at
  about 12% of the GPU's DRAM bandwidth.
- **The largest idle cause is waiting for the verifier's live coins**, not Ligerito's own host code. There are 287 coin
  rounds per session, at 0.18–0.28 ms each untraced, against a 0.02–0.03 ms ping. That costs 53–79 ms per session at K=2048
  (7–11%) and 28–38 ms at K=16384 (3–4%). About 62% of it falls inside Ligerito.
- **K=16384's step-4 best holds on a clean slice.** The clean re-run gives 2.70e7, between the original pair (2.61e7 and
  2.77e7), with no compaction stalls and no direct reclaim.

## Runs and evidence

- **Profile:** `r20261001-125609-50f5`.
  - Node 1, K=2048, step 6, 64 GiB, 16 cores.
  - 25 sessions, all accepted.
  - nsys 2026.1.3 traced CUDA only (no CPU sampling) around the prove process.
  - Evidence: `art:ee5f916a410bf307fa06ba1d9b320b1caa9a8c105a7d35f9f28a49641779d05e` (preserved). It holds the
    `.nsys-rep`, its SQLite export, the `nsys stats` CSVs, the run's stamps, and every analysis script with its output.
  - The run is labelled `campaign`, `subcircuit`, `question` and `nsys.profile`.
- **Clean re-run:** `r20261001-125609-f010`.
  - K=16384, step 4, 128 GiB.
  - Placed at 12:55:57Z, after NUMA node 1 showed 839 GiB free and 0 compaction stalls/s.
  - 25/25 accepted, proofs byte-identical, recorded in the roll-up.
- **The tracing cost** is 43–61 ms per session: median e2e 0.765 s traced, against 0.704–0.722 s for the same step
  untraced.
  - Most of it is coin wait: `wait_e2e_s` is 106 ms traced and 53–79 ms untraced.
  - Kernel times hardly move: zerocheck takes 232 ms traced and 220–226 ms untraced.
  - So the shares below come from the untraced runs' own phase timers (61f0, 9094, 4a30). The trace is used only to split
    each phase into kernels, copies and idle time.

## Item 1: does K=16384's 2.61e7 hold on a clean slice?

**Yes.** `f010` gives **2.70e7**, prove-only 2.39e7, against the original step-4 pair:

| Run | Overhead | Prove-only | GPU utilisation |
|---|---|---|---|
| `6c85` | 2.61e7 | 2.31e7 | 0.66 |
| `a0e0` | 2.77e7 | 2.51e7 | 0.66 |
| `f010` (clean re-run) | 2.70e7 | 2.39e7 | 0.74 |

- Its `host_vmstat` over the timed sessions is `compact_stall` 0 and `pgsteal_direct` 0.
- The step-4 spread is therefore 2.61–2.77e7. The 3.66e7 and 3.94e7 re-runs (`5c86`, `a048`) were host memory pressure.
- 2.61e7 stays the best, and 2.70e7 is now the clean-slice reference.

## Where a session's time goes (K=2048, step 6)

The prover's phase timers come from the untraced runs; GPU busy and idle come from the trace. Times are ms per session,
both reps together. A session is one witness and one encoding commitment, then per rep: zerocheck, lincheck, ring switch
and Ligerito.

| Phase | Prover timer, untraced (61f0 / 9094 / 4a30) | Share of 705 ms | GPU busy, trace | GPU idle, trace | Main kernels (ms, trace) |
|---|---|---|---|---|---|
| zerocheck | 220 / 221 / 226 | 31% | 207 (89%) | 26 | first round 117 (2 launches), second round 46 (2), tail 43 (16) |
| Ligerito | 206 / 197 / 216 | 29% | 126 (57%) | 96 | `lf_fold_ext_pair` 34, `lf_fold_base_pair` 24, `lf_msg_partial` 23; 1,121 launches |
| encoding commitment | 93 | 13% | 102 (98%) | 2 | additive NTT 68 (26), `hm96_finish_leaves` 33, `sha512_staged_merkle_leaves` 14 |
| ring switch | 70 / 70 / 72 | 10% | 90 (86%) | 14 | `chunk_ring_fold_rows_split` 26, `chunk_ring_combine_basis_split` 21, `chunk_zlin_transpose` 17; one 4.3 GB device-to-device copy |
| witness | 69 / 70 / 70 | 10% | 39 (90%) | 4 | `fc_sha_tape3` 28, `fc_host_slots` 26 |
| lincheck | 28 / 28 / 33 | 4% | 20 (56%) | 16 | `linear_check_partial_fold_shared` 9, `linear_check_compressed_column_fold` 6 |
| outside the six timers | 15 | 2% | | | |

**At K=16384 (`f010`, 847 ms e2e) the same statement size (m = 35) gives the same phases**, with three differences:

- Lincheck takes 72 ms (8.5%).
- The witness takes 97 ms.
- 89 ms (10%) is outside the six timers. This profile doesn't cover it.

**What the GPU idle is.** The trace shows 161 ms of idle per session. I split it by what the launching thread is doing
(`analysis/idle.txt`, `analysis/gaps_next.txt`):

- **About 100 ms is the prover waiting inside a coin request.**
  - Host-only stretches of 50 µs to 2 ms total about 100 ms, matching `wait_e2e_s` (106 ms).
  - With live coins, every Fiat–Shamir squeeze is one TCP request to the session's coin server, `LiveChallenger::round`
    in `backends/flock/live/src/lib.rs`, called from the CUDA host challenger's `live_cb`.
  - Of those stretches, 62 ms fall in Ligerito, 18 in zerocheck, 11 in lincheck and 2 in the ring switch.
  - In Ligerito, the round trip sits before every fold round (`lf_fold_ext_pair`: 44 gaps per session), every claim-batch
    glue (`lf_glue_base` and `lf_glue_presplit`: 36), and the query and out-of-domain samples.
- About 15 ms is launch overhead: gaps under 50 µs, plus the time inside `cudaLaunchKernel`. There are about 2,000
  launches per session.
- About 9 ms is allocator calls on the critical path:
  - a `cudaFree` at the start of the witness (4.3 ms);
  - 34 `cudaMalloc` and 33 `cudaFree` calls inside Ligerito (3.1 ms);
  - a `cudaMalloc` after the last kernel (1.5 ms).
- About 10 ms is inside synchronous `cudaMemcpy` calls while no copy runs: the calls' own cost, around 510 small copies per
  session.
- About 20 ms is a few long host-only stretches (over 2 ms each), in Ligerito (12 ms) and before a copy in the ring switch
  (8 ms). The trace has no NVTX ranges, so it can't say whether they are slow coin rounds or host work.

## Proposed C-Flock changes (for the owner's review and M0's agreement; nothing edited)

Each share is of the untraced K=2048 step-6 session (705 ms), with the K=16384 step-4 figure (847 ms) where it differs.
They overlap only where noted.

1. **Zerocheck's first round** (`zerocheck_first_round_cpu_structured`, `cuda-ghash/zerocheck_round1_cpustyle.cuh`).
   - Cost: 2 × 58 ms, 17% of the session (14% at K=16384), and 53% of zerocheck's kernel time.
   - It reads a, b and c once: 3 × 4 GiB at m = 35 in 58 ms, about 0.22 TB/s against the RTX PRO 6000's ~1.8 TB/s.
     So it's bound by its arithmetic or its table lookups (log/antilog tables in shared memory, the 64 KB convert table in
     L2), not by DRAM.
   - First step: one `ncu` run of this one kernel (one launch, a few minutes) to find its limiter. The launcher's comment
     says W = 14 warps per block was tuned against the register file, so the occupancy cliff is known.
   - Expected: 2× faster saves 58 ms (8%); half of DRAM bandwidth would save about 88 ms (12%).
   - The second round (46 ms) and the tail (43 ms) go into the same `ncu` pass; I give them no estimate before it.
   - This is the change M0 most needs to agree, since the kernel's small, medium and outer layout follows the statement's
     layout.
2. **Live-coin round latency** (`backends/flock/live`: the coin server's reply path, and where the verifier processes run
   relative to it).
   - Cost: 287 rounds per session at 0.18–0.28 ms each, against a 0.02–0.03 ms ping (`open_rtt_ms`). The server's own
     handling is about 0.01 ms per round (`verdict.handle_s` is 2–4 ms per session).
   - Per-call wait is 0.10–0.13 ms at K=16384 with 2 verifier processes, and 0.18–0.28 ms at K=2048 with 11, all on the
     same 16 cores. So the hypothesis is that the server waits to be scheduled behind verification. The server isn't in
     this trace, so that's unconfirmed.
   - First step: server-side timestamps per round (receive, reply).
   - Then, if confirmed: answer coins from a thread that never waits behind verification (its own core, or the verifiers
     at lower priority).
   - Expected: at 0.04 ms per call, saves 41–68 ms (6–10%) at K=2048 and about 16 ms (2%) at K=16384.
   - It also removes most of Ligerito's, lincheck's and zerocheck-tail's idle time, so items 3 and 4 below assume it.
   - A CUDA graph or batched launches would **not** recover this time: each round's coin depends on the message before it.
3. **Ligerito** (`cuda-ghash/ligerito_f256.cuh`), beyond item 2:
   - **Fuse each fold with the next round's message.** `lf_msg_partial` (23 ms) makes another pass over arrays the fold
     has just written; zerocheck's tail already fuses the two (`zerocheck_tail_fold_and_message_split`). Expected about
     15–20 ms (2–3%).
   - **Host steps off the critical path.** Expected about 10–15 ms (1.5–2%) together:
     - preallocate the per-level buffers once, instead of 34 `cudaMalloc` and 33 `cudaFree` calls per session;
     - read the three 16-byte values of each out-of-domain sample in one copy, not three synchronous ones;
     - build the induce weights on the device (`lf_build_eq_host` plus a `std::map` merge today);
    - move each level's openings (gathered rows, Merkle paths, salts) to a side stream; from the code, the next level reads
      only the query positions and α.
4. **Lincheck at K=16384.**
   - At K=2048, lincheck is 28 ms (4%): 20 ms of kernels, and its idle is 30 coin rounds (item 2).
   - At K=16384 it is 72 ms (8.5%); that growth is not in this profile.
   - I'd choose the lincheck change from a **K=16384 profile**: the same harness (`NSYS=1`, 128 GiB, one job), which would
     also show the 89 ms outside the phase timers. It is ready to place; it needs the owner's yes.
5. **Launches and allocations across phases.**
   - CUDA graphs for the fixed kernel runs between two coin rounds: the ring switch has 470 launches per session, Ligerito
     1,121. Expected up to about 15 ms (2%).
   - A stream-ordered pool or a session-persistent arena in place of the remaining `cudaMalloc` and `cudaFree` calls
     (witness start, after the last kernel). Expected about 6 ms (1%).
6. **Ring switch.**
   - A 4.3 GB device-to-device copy per session costs about 5 ms (0.7%), if an alias or the consuming kernel can replace it.
   - A host step of about 4 ms per rep before a copy (8 ms, 1.1%) needs a name first (item 7).
7. **NVTX ranges per phase and per coin round** in the prover. With no profiler attached they cost next to nothing. With
   them, the next profile splits phases and rounds without the heuristics this one needed: sessions cut at the witness
   kernels, phases at anchor kernels, rounds by gap length.
8. **The encoding commitment** (13%, 98% busy: NTT 68 ms, Merkle leaves 47 ms) gains only from kernel efficiency. It needs
   an `ncu` run before anyone gives an estimate, and I'd put it after items 1–4.

If items 1–3 land at their expected values, a K=2048 session drops from about 705 ms to about 515–580 ms (−18 to −27%). At
K=16384, items 1, 3 and 4 matter most (item 2 is only 2% there).

## What I'd do next (only on a yes)

- **One `ncu` run of zerocheck's first round** at K=2048 (one GPU, a few minutes).
- **One nsys profile at K=16384** (128 GiB, for lincheck and the 89 ms outside the phase timers).

Both reuse `ae9afa6ab`'s harness and change nothing in C-Flock.
