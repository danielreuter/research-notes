---
lane: flock-link
kind: report
created: 2026-09-25T14:30Z
status: final
---

CHECKPOINT 4b560b2b (15:32Z) [final] L1-L4+F2(+F3) implemented, tests+negatives all pass (8/64/4096 VUs), F1 cross-pod sessions accepted; 4096-VU linked session 3.8-4.1 s CPU; no GPU route (a) (Flock-CUDA lacks wiring+link opening). lane/flock-link@4b560b2b; pods terminated; ~$1.0
CHECKPOINT e2cf612b (15:06Z) [open] L1+L2+L4 selftest all-pass at 8/64 VUs (r20260925-145411-c083); F2 pinned union+GPU-unit verifiers all-pass; L3 one-session two-table all-pass (lane/flock-link e2cf612b). 4096-VU timed sessions: prover vy-flock-link-prover, verifier on vy-flock-link-ver (F1), runs r20260925-150605-e857 / -150543-6536
CHECKPOINT a52fcf2d (14:54Z) [open] L1 exchange + L2 both-rep link claims + L4 BLAKE3 chunk-chain circuit implemented (lane/flock-link a52fcf2d, Flock patch in backends/flock); honest accepted, 23 negatives reject at 8 VUs; recorded run r20260925-145411-c083 (selftest 8/64, 4096-VU timing) on vy-flock-link-cpu
CHECKPOINT 33e4d8d1 (14:36Z) [open] plan: Flock patch (eq-weighted link claims appended to union-circuit merged opening, both reps), flock-live Commit(root_F,root_B)->points->Link(y) exchange, BLAKE3 chain circuit (wired CVs/params/endpoints), pinned verifiers; CPU pod next
CHECKPOINT 33e4d8d1 (14:30Z) [open] started 14:35Z; env set, inbox empty; reading re-audit conditions + backends/flock/live; branch lane/flock-link from origin/main

# flock-link: L1–L4 and F2 for flock-128-r2's route (a), CPU; ready for re-audit

## Summary
- **All five conditions have code, tests and negatives on the CPU path** (verity `lane/flock-link`, base `origin/main`
  @ 33e4d8d1; tip in the FINAL block). Every negative rejects and every honest session accepts, at 8, 64 and 4,096 VUs
  (BF16, K = 1536). F3 (hardening) is in too.
- **Timing, 4,096 BF16 VUs (393,216 BLAKE3 compressions, dense m = 33), one linked two-rep session, 16 vCPU EPYC 9575F:**
  3.79–4.08 s prove (both reps), 4.0 s session wall against a verifier process on loopback; 11.4 GB peak RSS. The same host's
  plain BLAKE3 union with live coins (no circuit, no link claims) is 2.60–2.80 s, so chain glue + link claims + honest-zero
  padding cost about 1.45×. The link claims themselves are about 15 ms per rep (ring switch of two extra claims); the wiring
  argument runs beside the zerocheck.
- **F1 evidence:** three 4,096-VU sessions verified on a separate pod (vy-flock-link-ver, not the prover's) with
  `link_mode: exchange`, `require_link: true` and a non-null `link_sha256`; all accepted, verify 0.17–0.73 s. Across data
  centres the ~1,070 coin round trips at ~63 ms made each session 70 s: live coins need a same-DC verifier.
- **Not done: the GPU.** Route (a) has no GPU end-to-end time. Flock-CUDA proves only non-union `prove_ligerito`, so it has
  neither the wiring argument (L4) nor a way to open the link claims (L2). L3 is implemented and tested as one CPU session
  over two tables; no GPU pair ran. Details under "What is not done".

## Code (all under `backends/flock/` on `lane/flock-link`)
- `flock-link-b684b12.patch` (Flock b684b12; also `evidence/flock-link-b684b12.patch`), about 190 lines:
  - `proof::LinkClaim { point: M coords, value }` and `eq_skip_weights`: a fully multilinear claim on the padded union
    witness, opened as a ring-switched claim whose 64 skip weights are the eq tensor of `point[0..6]`.
  - `pcs::verify_batch_merged_weighted`: the merged verifier with explicit skip weights (the old entries map their
    `SkipPoint`s onto it, byte-identical).
  - `prover::prove_fast_ligerito_union_circuit_linked(.., link: LinkHook, ch)`: the hook runs right after the statement
    binding (root absorbed, no coin drawn) and returns the claims; they join this proof's merged opening. With a hook the
    padded buffer is honestly zeroed (the claims fold it at points random over the dummy rows).
  - `verifier::verify_ligerito_union_circuit_linked(.., link)`.
- `live/src/lib.rs` (the session library): `Req::Commit`, `LinkSpec`, `Binding::Circuit`, `LinkCtx`, the
  `statement_publics` hook, F3.
- `live/src/bin/flock-link.rs`: the linked statement, its verifier, the prover, `serve | prove | selftest`.
- `live/src/bin/flock-live.rs`: F2 (`selftest-f2`, `serve-union`, feature `verity-unit`), F3 negatives.
- `verity_unit.rs` (flock-bench's census-unit table, with an explicit-profile prove), `pod/` (setup, run script, netlist
  exporter).

## The protocol as implemented
1. `Hello`: the verifier's config, now including Σ (the link statement digest: scheme, Λ, N, m, the circuit and registry
   digests, the leaf digests), m and the point count.
2. `Commit { root_F, root_B per table, public words per table }`. The server refuses it twice, without root_F, or
   unless it carries every configured table's root together (L1, L3). It checks each table's public words against its own
   statement (C4 endpoints, below), records the publics digest the proof must bind, then draws **two points of m
   GF(2^128) coordinates from the OS**, its own coin slot, and returns them.
3. `Link(y)`: one y per table and point, refused before the points or with the wrong length.
4. Flock's rounds. Every coin is refused until y has arrived (R5). Each rep's first round must bind exactly the committed
   root_B (L1) and rep 0's root (R1), the configured registry digest, counts and circuit digest (F2), and the publics digest
   from step 2 (C4).
5. At `Finish` the replay hands the recorded points and y to the statement verifier, which appends the two link claims to
   **each** rep's merged opening (L2). A rep whose opening doesn't match the recorded y fails on its own.

**The linked statement** (L4, C4). Operand rows: 2·vus rows of K 16-bit words (x rows, then W columns). The linked
position of bit i of word k of row l is `(l·K + k)·16 + i`, the agkr-bound Λ_F order. Each row's leaf is plain BLAKE3 of
its bytes (LE words); for K = 1536 that is 3 chunks, 48 compressions. Flock proves one circuit over one BLAKE3 table:
- row `l·48 + block` is that block; the message words are private inputs;
- inside each chunk, out_lo(j) is wired to cv(j+1); the chunk's first cv is wired to the public fixed IV;
- every params word (counter, block_len = 64, flags START / 0 / END) is wired to a public fixed constant for that position;
- each chunk's output chaining value is a public output.

The verifier builds the shape itself, pins its circuit digest in the binding, and checks the public chunk values against
its configured leaf digests natively (the parent compressions with PARENT and ROOT flags), in `Commit`, before drawing the
points. So Λ_B is `pos = row·512 + u ↦ Flock bit ((4 + u/128) << ν | row)·128 + u%128`, fixed by the verifier-built
shape (`Chain::embed`), and every bit of every word is linked (A16).

## Checklist: condition → code → test
Test names are `NEG` cases of `flock-link selftest` unless marked; each ran at 8 and 64 VUs in
r20260925-145411-c083 and r20260925-152531-76b3.

| cond | what holds | code | tests (all as expected) |
|---|---|---|---|
| **L1** real exchange | root_F and every root_B, then the points (the verifier's own OS coins), then y, then Flock's coins; root_B is the root each rep binds | lib `handle(Commit)`, `handle(Link)`, `handle(Round)` R5 gate and root_B check | `root_b_other_than_bound_root`, `roots_committed_twice`, `no_root_f`, `y_before_points`, `coins_before_y`, `points_fresh_per_session_same_roots` |
| **L2** link claims in both reps | two GF(2^128) points; both reps open z^(r_k) = y_k in their merged opening with their own live coins (drawn after y), so each rep's reduction is a fresh round-by-round bound: about (2^-122)^2 ≈ 2^-244 for the reduction, (m/2^128)^2 = 2^-246.4 at m = 28 for Schwartz–Zippel | patch (`LinkClaim`, weighted merged verify, linked prove/verify), bin `ChainVerifier::verify`, `link_eval`, `Chain::embed` | link neg 10: `y1_tampered`, `y2_tampered`, `y1_y2_tampered_same_delta` (each rejected by **both** reps: `link_neg10_rejected_by_each_rep`); link neg 2: `z_bit_differs_from_y_source` (both reps); `rep1_prover_claims_other_y` accepted, because the opening carries no y and both reps check the recorded one |
| **L3** one session for several tables | one Σ, one `Commit` with every table's root before the points, one y per table; the second table's root comes from a commit-only pass (its prove stops at the binding, and the commit is deterministic) | lib `handle(Commit)` table-set check, bin `server_tables`, `session_l3` | `l3_two_tables_one_session`, `l3_points_before_second_root`, `l3_second_table_binds_other_root`, `l3_second_table_y_tampered` (only table 2's reps fail), `l3_tables_proofs_swapped` |
| **L4** chain glue and endpoints (C4) | chained CVs wired, IV and params wired to fixed publics, chunk outputs public and checked natively against the leaf digests before the points; circuit digest and publics digest bound | bin `Chain::new`, `statement_publics`, lib `Binding::Circuit` parse | link neg 13 `forged_middle_block_honest_endpoints` (wiring GKR rejects, both reps); link neg 14 `chunk_end_flag_dropped`, `wrong_counter`, `wrong_block_len`; `public_chunk_value_forged` (refused at Commit) |
| **F2** pinned production verifiers | CPU census unit + BLAKE3 union: registry digest of both types, counts [n, units], Fast100; GPU unit table: the netlist's statement digest and Flock-CUDA's Fast100 / batch 6 / SHA-256 | bin `f2::UnionStmt`, `UnionVerifier`, `GpuVerifier` | `flock-live selftest-f2` (n = units = 4096, hopper_bf16, other netlist hopper_e4m3, GPU nbl 14): `union_honest`, `union_other_counts`, `union_other_netlist`, `union_fast_profile`, `union_blake3_only_statement`, `gpu_unit_honest`, `gpu_unit_other_netlist`, `gpu_unit_fast_profile` |
| F3 (hardening) | child streams refused at parent position 0 or before the rep root's binding round | lib `handle(Open)` | `flock-live selftest`: `fork_at_parent_position_0`, `fork_before_root_binding` |
| kept | R1, R2, R7, cross-session replay on the linked statement | lib | `reps_with_different_witness`, `fast_profile_proofs`, `cross_session_replay_both_reps` (link neg 15) |

The GPU unit proofs in F2's test are made by the CPU `prove_ligerito` in the GPU statement's shape (same protocol and
serialization as Flock-CUDA's), so the pins are tested without a GPU. The legacy `flock-live selftest` (the stub link) still
passes all cases.

## Runs and artifacts
All preserved (`research data preserved` rc 0). Pods: vy-flock-link-cpu, vy-flock-link-prover, vy-flock-link-ver.

| run | what | art |
|---|---|---|
| r20260925-145411-c083 | selftest 8 and 64 VUs, all pass (the 4,096 session was OOM on 32 GB) | art:dd643a3e |
| r20260925-151657-580f | prover: selftest 8/64, F2 at n = units = 4096, 3 × 4,096-VU sessions against the verifier pod | art:b81a5cf2 |
| r20260925-151503-8ce1 | verifier pod (F1): the 3 session records, all accepted | art:00da1ce8 |
| r20260925-152224-3fdf | timing, loopback verifier: 3 × 1,024 and 3 × 4,096 VUs | art:e0506435 |
| r20260925-152531-76b3 | selftest 8/64 (L3 cases included), F2, legacy selftest with F3, plain BLAKE3-union baseline at 393,216 | art:6994068d |
| r20260925-152801-e345 | PCS_TRACE phase split of two 4,096-VU sessions | art:255cbe45 |

Earlier: setup r20260925-143752-6075 (art:3112e35c), r20260925-150134-308a (art:251dbf8a), r20260925-150236-2893
(art:65d49832); failed 4,096 attempts r20260925-145704-f557 (art:92801ac0; OOM), r20260925-150605-e857 (art:9bc80e68;
verifier not yet listening), r20260925-151041-b073 (art:5dc82778; the island blow-up, 124 GB); verifier run
r20260925-150543-6536 (art:ffde37a3; only port probes).

**Timing (4,096 BF16 VUs, EPYC 9575F 16 vCPU, loopback verifier process):**

| line | prove, both reps | session wall | notes |
|---|---|---|---|
| linked chain (L1 + L2 + L4), live | 3.79 / 3.82 / 4.08 s | 3.97–4.42 s | 11.4 GB RSS; 1,070 round trips, 1.9 MB up, 53 KB down; proofs 461 KB per rep |
| plain BLAKE3 union, live (no circuit, no link) | 2.60 / 2.69 / 2.80 s | – | in-process verifier |
| plain BLAKE3 union, FS fast100 × 2 | 2.21 / 2.60 / 2.74 s | – | |

Per rep (trace): witness 0.15 s, commit 0.27 s, zerocheck + lincheck ∥ wiring 0.55 s, opening 0.70 s (ring switch of all
four RS claims 28 ms). 1,024 VUs: 1.00–1.19 s per session.

## What is not done, and what the re-audit should look at
- **GPU (L2, L3, L4 on Flock-CUDA): not done.** Flock-CUDA at b684b12 proves non-union `prove_ligerito` only. Route (a)
  on the GPU needs (i) the wiring argument (product GKR over the cell space) on the device or beside it, and (ii) the
  eq-weighted link claims in its opening (the host already calls `open_claims…`; the claim list and skip weights are host
  data). The GPU pair (unit + BLAKE3) can use the L3 session as is once one process proves both tables and knows both roots
  before the first coin: the commit-only trick needs an FFI commit entry, because a panic can't unwind through CUDA.
  **So route (a) has no GPU end-to-end time.** The CPU Flock side is 3.8–4.1 s at 4,096 VUs. agkr-bound's prime side with
  its σ link was 1.53 s on A100 (art:bd3d8b2c). Adding those two numbers is not a measurement.
- **root_F is a stand-in** (SHA-256 of a tag). The prime proof has to take its link points from this session's record
  instead of its own FS transcript. agkr-bound's §17 draws **one GF(2^256)** point from its transcript; this Flock side
  opens **two GF(2^128)** points (L2's "both reps" option). One side has to change: the prime σ form runs as-is with two
  points (256 σ values either way).
- **Leaf format:** plain BLAKE3 of the row bytes (no prefix). agkr-bound's operands-committed statement uses
  `sha256/row/v1` (prefix64 + SHA-256). Aligning them is a statement choice; C5 (both sides derive Λ) holds on this side.
- **Where to attack:**
  - `Chain::embed`: the fixed word-column coordinates (4 + u/128), and `LinkClaim` over the padded M space.
  - The honest-zero padding requirement: without it the link claims folded dirty dummy rows. This is enforced in the
    patch, not checked by the verifier. My reading is that a dishonest prover gains nothing from dirty padding: the
    merged transport checks every claim against the dense stack, where dummy rows are implicit zeros. Please confirm
    that.
  - L2's claim that the two reps' reductions are independent.
  - The commit-only pass in L3.
  - Whether `statement_publics` (C4) before the points is the right place.
- **C8** (the accountant's whole-proof sum) and C3 (Flock at 2^-128 under campaign accounting) are unchanged by this lane.

## kb candidates (for the coordinator; cloud lanes don't edit kb/)
- `kb/flock-prover.md`, a new section:
  - Flock's `ShapeBuilder` independence islands give each island a value buffer over every wire. That is quadratic in
    the island count: 107 GB at 4,096 islands and 2,048 VUs, versus 6 GB without islands. Don't declare one island per
    leaf.
  - Link claims (`flock-link-b684b12.patch`) need honest-zero padding in the union prover's padded buffer.
  - A linked two-rep BLAKE3 chunk-chain session at 4,096 VUs (m = 33) takes 3.8–4.1 s on 16 vCPU Zen5 against 2.6–2.8 s
    for the plain live union.
  - Live coins across data centres (~63 ms RTT, ~1,070 round trips) cost 70 s per session.
- `kb/live-verifier`: two RunPod CPU pods in different data centres measured ~63 ms per coin round trip
  (r20260925-151657-580f).

## FINAL

~~~text
tip: lane/flock-link @ 4b560b2b (base origin/main@33e4d8d1)        merge-with: none
known-failures: tests/test_repository.py::test_no_tracked_blob_exceeds_limit (on main too)    pod: terminated 15:19Z (cpu), 15:24Z (ver), 15:33Z (prover); ~$1.0
artifacts: art:dd643a3e art:b81a5cf2 art:00da1ce8 art:e0506435 art:6994068d art:255cbe45 art:3112e35c art:251dbf8a art:65d49832 art:92801ac0 art:9bc80e68 art:5dc82778 art:ffde37a3
~~~

L1, L2, L3, L4, F2 (and F3) are implemented with tests and negatives on the CPU path. All pass at 8, 64 and 4,096 VUs.
Three 4,096-VU sessions were verified on a non-producer pod with the link required. The linked session costs 3.8–4.1 s at
4,096 BF16 VUs (16 vCPU). There is no GPU route (a) time: Flock-CUDA lacks the wiring argument and the link-claim opening.

Handoffs received: none (inbox empty at 14:35Z, 14:54Z, 15:06Z). Handoff written:
`lanes/coordinator/20260925T1530Z-handoff-from-flock-link.md` ("flock-link: L1–L4 + F2 implemented, ready for
re-audit").
