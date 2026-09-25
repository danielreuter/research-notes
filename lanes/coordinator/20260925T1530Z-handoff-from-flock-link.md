---
lane: coordinator
kind: handoff
from: flock-link
created: 2026-09-25T15:30Z
---

# flock-link: L1–L4 + F2 implemented, ready for re-audit (CPU path; no GPU route (a) time: Flock-CUDA has neither the wiring argument nor the link-claim opening)

Report: `lanes/flock-link/20260925T1430Z-report-flock-link.md`. It has the full checklist, the protocol as implemented,
runs and "where to attack".

## Merge-ready
- **Tip:** `lane/flock-link` @ 4b560b2b on danielreuter/verity, base origin/main @ 33e4d8d1. merge-with: none. It doesn't
  build on agkr-bound's branch.
- **Scope:** everything is under `backends/flock/`:
  - `flock-link-b684b12.patch` (Flock);
  - `live/` (session library, `flock-link` binary, F2/F3 in `flock-live`);
  - `verity_unit.rs`;
  - `pod/` (setup, run script, netlist exporter).
- **Behaviour changes to the existing session library:**
  - `StatementVerifier::verify` takes a `LinkCtx`.
  - A session with a `LinkSpec` requires the `Commit` → points → `Link(y)` exchange. Without one it keeps the old
    opaque link (`link_mode: "stub"` in the record). **F1 filters should require `link_mode: "exchange"`.**
  - F3 refuses forks at parent position 0 or before the root's binding round.
  - The legacy `flock-live selftest` passes unchanged.
- **Tests:** repo `tests/test_repository.py` + `test_boundaries.py` pass except the known `test_no_tracked_blob_exceeds_limit`
  (on main too). The Rust tests are the pod selftests below.

## Re-audit checklist (condition → code → test; every negative rejects, every honest session accepts)
| cond | code | tests |
|---|---|---|
| L1 exchange: root_F + every root_B → OS-drawn link points → y → Flock coins; root_B = the root each rep binds | `lib.rs` `handle(Commit/Link/Round)` | `root_b_other_than_bound_root`, `roots_committed_twice`, `no_root_f`, `y_before_points`, `coins_before_y`, `points_fresh_per_session_same_roots` |
| L2 two GF(2^128) link claims opened in **both** reps' merged openings | patch (`LinkClaim`, `verify_batch_merged_weighted`, `*_union_circuit_linked`), `flock-link.rs` `ChainVerifier` | link neg 10 `y1_tampered`, `y2_tampered`, `y1_y2_tampered_same_delta`, each rejected by both reps; link neg 2 `z_bit_differs_from_y_source` (both reps) |
| L3 several tables, one session, one Σ, joint `Commit` before points | `lib.rs` table-set check, `server_tables`, `session_l3` | `l3_two_tables_one_session`, `l3_points_before_second_root`, `l3_second_table_binds_other_root`, `l3_second_table_y_tampered`, `l3_tables_proofs_swapped` |
| L4 chain glue, counters, flags, block_len, endpoints (C4) | `Chain::new` circuit (CVs wired, IV and params wired to fixed publics, chunk CVs public), `statement_publics` (native tree check vs leaf digests before the points), `Binding::Circuit` (circuit + publics digests pinned) | link neg 13 `forged_middle_block_honest_endpoints`; link neg 14 `chunk_end_flag_dropped`, `wrong_counter`, `wrong_block_len`; `public_chunk_value_forged` |
| F2 pinned production verifiers: CPU census unit + BLAKE3 union (registry digest, counts, Fast100); GPU unit table (netlist statement digest, Fast100 / batch 6 / SHA-256) | `flock-live.rs` `f2` | `selftest-f2` at n = units = 4096: `union_honest`, `union_other_counts`, `union_other_netlist`, `union_fast_profile`, `union_blake3_only_statement`, `gpu_unit_honest`, `gpu_unit_other_netlist`, `gpu_unit_fast_profile` |
| F3 | `lib.rs` `handle(Open)` | `fork_at_parent_position_0`, `fork_before_root_binding` |
| F1 | the verifier ran on vy-flock-link-ver, not the prover's pod | 3 × 4,096-VU sessions accepted there with `require_link: true` and non-null `link_sha256` (art:00da1ce8) |

**Runs:**
- r20260925-145411-c083 (art:dd643a3e), 8 and 64 VUs;
- r20260925-151657-580f (art:b81a5cf2), selftests, F2 and cross-pod sessions;
- r20260925-151503-8ce1 (art:00da1ce8), the verifier pod;
- r20260925-152224-3fdf (art:e0506435), timing;
- r20260925-152531-76b3 (art:6994068d), L3, F2, F3 and the baseline;
- r20260925-152801-e345 (art:255cbe45), the phase trace.

## Route (a) time
- **GPU: none measured.** Flock-CUDA (b684b12) is non-union `prove_ligerito` only. The Flock side of route (a) needs the
  wiring argument and the eq-weighted link claims in the opening, and neither exists on the device. L3 for the GPU pair
  also needs one process proving both tables with both roots before the first coin, which needs an FFI commit entry.
- **CPU Flock side, 4,096 BF16 VUs (EPYC 9575F, 16 vCPU):** 3.79–4.08 s for the linked two-rep session on a loopback
  verifier. The plain live BLAKE3 union on the same host is 2.60–2.80 s.
- With a verifier in another data centre (~63 ms RTT) a session took 70 s, over 1,070 round trips.
- agkr-bound's prime side with its σ link was 1.53 s on A100 (art:bd3d8b2c). Adding the two numbers is not a measurement.

## Decisions / follow-ups for others
- **Prime side (agkr-bound's successor):**
  - Take the link points from the session record (after root_F and root_B), not from its own FS transcript.
  - Use the two GF(2^128) points this side opens, instead of §17's one GF(2^256) point.
  - Send root_F in `Commit`.
  - Today root_F is a stand-in.
- **Leaf format:** this statement hashes plain BLAKE3 of each operand row (no prefix). agkr-bound's is `sha256/row/v1`.
  One of them has to move.
- **Pods:** vy-flock-link-cpu and vy-flock-link-ver are terminated; vy-flock-link-prover is terminated at FINAL. About $1.5.
