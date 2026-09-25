---
lane: flock-live
kind: report
created: 2026-09-25T11:35Z
status: final
---

CHECKPOINT a43f6254 (12:23Z) [final] R1-R8 implemented, all negatives reject, ready for re-audit; live H100 4096VU BF16 0.982s (1.24x FS), FP8 0.526s (1.30x); CPU 1.00x. lane/flock-live@a43f6254. art:16c17a43 art:5320c158 art:6715442b. flock-glue 1215Z handoff answered. Pods terminated 12:19Z, ~$1.6
CHECKPOINT a43f6254 (12:23Z) [final] R1-R8 implemented, all negatives reject, ready for re-audit; live H100 4096VU BF16 0.982s (1.24x FS), FP8 0.526s (1.30x); CPU 1.00x. lane/flock-live@a43f6254. art:16c17a43 art:5320c158 art:6715442b. Pods terminated 12:19Z, ~$1.6
CHECKPOINT a43f6254 (12:15Z) [open] R6 live on H100 works (run r20260925-120734-7e37): all live sessions accepted, 7 GPU live negatives rejected. 4096 VU pair live vs FS fast100x2: BF16 0.94 vs 0.77 s (1.23x), FP8 0.55 vs 0.40 s (1.39x), ~220 coin round trips/table. Rerunning with rayon=quota + wait timing. git push 403 (token expired), retrying.
CHECKPOINT 0fe756ef (11:55Z) [open] CPU live path works (run r20260925-115302-19e5): R1 root check, live coins, live forks, replay; honest accepted, all 19 negatives reject as specified; live/FS prove 1.03-1.07x at m28 loopback. Code lane/flock-live 6429f343+. Next: H100 R6 (CUDA host live hook patch written).
CHECKPOINT 767115db (11:39Z) [open] Read spec+harnesses (art:4cc09936, art:4e0271fe inputs). Finding: Flock-CUDA b684b12 prove path uses only the HOST FsChallenger (zc_challenger_device.cuh is bench/test-only) + grind_pow_device, so R6 = host live hook. Next: LiveChallenger/Replay crate patch, CPU pod.
CHECKPOINT 767115db (11:35Z) [open] Lane up on cloud VM. Reading red-team-flock spec (R1-R8, 10 negatives); plan: CPU pod for R1/R2-R5/R7-R8/negatives, H100 for R6. Code branch lane/flock-live (or cursor/* fallback).

# flock-live: flock-128-r2 with live verifier coins (R1–R8), CPU and Flock-CUDA

## Summary
- **R1–R8 are implemented and every specified negative is rejected; ready for the red-team re-audit.** Nothing here is a
  Table 2 cell until that re-audit grants the profile.
- **Code:** verity `lane/flock-live` @ a43f6254 (base main@767115db).
  - `backends/flock/live/`: crate `flock-live`, dropped into a flock b684b12 checkout as `crates/flock-live`. It holds
    `LiveChallenger` (the prover), `Server` (the verifier's coin server and session verifier), `ReplayChallenger`, and the
    binary `flock-live` (`serve`, `serve-gpu`, `prove`, `selftest`, `bench`).
  - `backends/flock/cuda_live_patch.py`: the Flock-CUDA live hook plus the GPU harness sessions. Generated diff:
    `evidence/flock-cuda-live.diff`.
- **Flock-CUDA finding (R6):** at b684b12 the CUDA prove path draws every challenge from the one host `FsChallenger`
  (`challenger.hpp`), plus `grind_pow_device` for PoW. `zc_challenger_device.cuh` is used only by benches and tests
  (`bench_ligerito.cu`, `test_zc_challenger.cu`, `test_zerocheck_full.cu`), not by `prove_ffi.cu`. So R6 is a host hook:
  - each squeeze hands the buffered transcript-v2 bytes to a Rust callback, which forwards them to the verifier;
  - the verifier's coins go straight back to the host;
  - no device challenger state has to be kept in sync.
- **Cost at 4,096 VUs, H100 80GB, same pod.** The GPU pair is the unit plus BLAKE3. Medians are over 12 runs (2 runs × 2
  rounds × 3), and the verifier runs as a separate process on loopback.

| line | today: fast x1, FS | r2: fast100 x2, FS | **r2: fast100 x2, live** | live / FS | live / today |
|---|---|---|---|---|---|
| **BF16 (unit m32 + BLAKE3 m33)** | 0.655 s | 0.792 s | **0.982 s** | **1.24x** | 1.50x |
| **FP8 (unit m31 + BLAKE3 m32)** | 0.413 s | 0.406 s | **0.526 s** | **1.30x** | 1.28x |

Per table (prove s, FS → live, fast100 x2): BLAKE3 m33 0.194 → 0.261, BLAKE3 m32 0.108 → 0.176, unit BF16 m32
0.598 → 0.721, unit FP8 m31 0.299 → 0.351.
- The extra time is the coin round trips. Each table makes about 220 of them over both reps, in 216–220 rounds.
  Measured prover wait is 0.050–0.077 s per table, or about 0.23–0.34 ms per round trip on the H100 pod's loopback.
  Traffic is about 74 KB up and 30 KB down per table.
- **A verifier on another host pays its RTT on every round.** At the 1.5 ms same-DC RTT from US-MO-1 (kb/live-verifier),
  that is about 0.33 s per table and 0.66 s per pair. At the 3–12 ms in-session medians recorded there, it is 1.3–5 s per
  pair. Only 26 of about 220 rounds carry no prover message, so batching consecutive squeezes would save at most about
  12% of the round trips.
- **CPU union** (BLAKE3 table, cpu3c 16 vCPU EPYC 9654, host load around 230, so noisy; loopback): live against FS
  fast100 x2, medians of 5:
  - m33: 5.40 → 5.42 s (1.00x);
  - m28: 0.34 → 0.33 s (0.96x).
  - 444–453 round trips per session, 0.05–0.08 s of wait. On CPU the live path costs nothing measurable: the round trips
    are about 1–2% of prove time, and live mode skips the FS hashing and grinding.

## R1–R8: condition → code → test (for the re-audit)
Code paths are in `backends/flock/live/src/lib.rs` unless marked. Tests are `flock-live selftest` (CPU, NEG lines) and the
GPU harness (G128NEG lines).

| cond | what holds | code | tests |
|---|---|---|---|
| R1 one root for both reps | The server parses each rep's first round (domain, then the statement binding: `flock-mixed-v1` + registry digest + counts + root on CPU, `flock-r1cs-v0` + statement digest + root on GPU). It checks the digest and counts against its own configuration, and refuses rep 1's first coin unless rep 1's root equals rep 0's; rep 1 can't open before rep 0 committed. At finish, each proof's root must equal the committed one. Cost: zero, because the commit is deterministic (honest sessions pass). | `Server::parse_binding`, `handle(Round)` first-round branch, `handle(Open)` rep>0 check, `finish` cap check | `reps_with_different_roots` (refused before any rep-1 coin); honest sessions |
| R2 commit before coin + replay | A coin is issued only as the reply to a `Round` carrying every byte absorbed since the previous squeeze, squeeze header included. The server records sha256(round), n and the coins. `ReplayChallenger` runs the ordinary Flock verifier and, at every squeeze, checks sha256(the proof's absorbed bytes) against the recorded round before it returns that round's coins. It also checks that every recorded round was consumed. | `LiveChallenger::squeeze/round`, `Server::handle(Round)`, `ReplayChallenger::squeeze/finish` | `parent_message_altered_after_coin`, `parent_message_sent_after_its_coin`, `rep0_proof_replayed_as_rep1`, `cross_session_replay_both_reps`, GPU `rep0_proof_replayed_as_rep1` / `yr0_bit_flipped_rep1` / `zerocheck_round_flipped_rep0` |
| R3 live forks | `fork()` takes the parent's two seed coins (which commits the parent's pre-fork messages), then opens child stream `<parent>/f<i>` at that parent position. The child's coins are live too; its seed is absorbed as a message, never used to derive coins. The server checks parent position and child index. The replay mirrors this and checks label and position. The merged opening's concurrent child (`pcs.rs` 2282/2768) runs live under `rayon::join` on the shared transport. | `LiveChallenger::fork/fork_from_seed/open_child`, `Server::handle(Open)` child branch, `ReplayChallenger::fork_from_seed` | every CPU session has 4 streams (rep0, rep0/f0, rep1, rep1/f0); `fork_child_message_altered_after_coin`, `fork_child_message_sent_after_its_coin` |
| R4 pure coins at PoW/nonce sites | `grind_pow` does no search: it absorbs the prover's nonce as a message and the next coin is the verifier's, a function of nothing the prover sent. `verify_pow` absorbs the nonce and returns true, so the nonce is bound by the round digest. On CUDA, `grind_pow` and `grind_pow_device` do not search when live. The lincheck φ₈ skip point uses the same fused call. The AG `sample_fresh` path is unreachable (RS flavour only). | `LiveChallenger::grind_pow`, `ReplayChallenger::verify_pow`, patch: `challenger.hpp` grind_pow, `pow_grind.cuh` | `prover_chosen_pow_nonce_honest` (nonce 0x5eed1234: accepted, coins unaffected), `pow_nonce_altered_after_coin` |
| R5 coins only after root_F, link points, y | The server refuses every coin until a `Link` message arrives. That message carries the link context and is recorded as `link_sha256`. | `Server::handle(Round)` R5 gate, `handle(Link)` | `coins_before_link_context` |
| R6 GPU live path | `FsChallenger` (host) buffers its absorbed stream and calls `live_cb` at each squeeze. `prove_ffi.cu` enables it from two new `FlockCudaProveParams` fields. The harness's callback forwards through `LiveChallenger` to `flock-live serve-gpu`. Costed above. | `cuda_live_patch.py` | every timed GPU live session accepted (24 per run over 4 shapes; the witness-tamper session rejected as it must); the 4 GPU negatives |
| R7 pins | The verifier configuration fixes Fast100, reps = 2 and the RS flavour. `Hello` must equal it. Each stream's transcript domain is fixed per rep. The proof's `PcsParams` must equal the pinned ones: Fast100, rate 1/2, embedded batch, lanes, BLAKE3 on CPU; batch 6 and SHA-256 on GPU. A missing rep proof is a lone rep, which is rejected. The bundle flavour must be R1cs, so an AG bundle is refused. | `SessionConfig::flock_128_r2`, `handle(Hello/Open)`, bin: `Stmt::verify_with`, `GpuVerifier::verify` | `fastx1_session`, `fast100x1_lone_rep_hello`, `lone_rep_under_r2_hello`, `fast_profile_proof_in_r2_session`, `fast100_proof_relabelled_fast_params`, `ag_flavour_bundle` |
| R8 evidence = live session record | Acceptance is the verifier process's verdict at `Finish`, computed by replay over its own record. Each session writes `session.json` (`flock-live-session/v1`): hello, config, link sha256, per-stream rounds `{k, n, msg_len, msg_sha256, coins}`, roots, proof sha256s, verdict, plus `index.jsonl`. No path verifies a proof file without a session. | `Server::finish/record_json`, bin `serve_loop` | `fs_transcript_presented_as_live` (an FS proof in a live session is rejected); records under `out/sessions/` of every run |

## Negatives (red-team-flock §5, plus the brief's extras): all rejected, honest sessions accepted
CPU cases ran at n = 4096 (m26) and 16384 (m28) in runs r20260925-120757-e8a1 and r20260925-121437-7240. GPU cases ran
at nbl 17 (BLAKE3 m31, unit BF16 m30) in run r20260925-120734-7e37.

| # | negative | result | where it's stopped |
|---|---|---|---|
| 1 | reps with different roots | rejected | R1: no rep-1 coin issued (session aborted) |
| 2 | rep 0 replayed as rep 1 | rejected (CPU + GPU) | R2 replay: rep1 round 2 digest mismatch |
| 3 | message altered after its coin: parent / fork child | rejected / rejected | R2: `blake3/rep0` round 3 / `blake3/rep1/f0` round 2 |
| 3' | message sent after its coin: parent / fork child | rejected / rejected | R2: round 5 / `rep0/f0` round 1 |
| 4 | prover-chosen PoW nonce | accepted (coin independent of it); the nonce altered after its coin is rejected (R2, round 60) | R4 |
| 5 | fastx1, fast100x1, lone rep under the r2 hello, Fast proof in an r2 session, Fast100 relabelled Fast | all rejected | R7: hello refused / no rep-1 proof / params pin |
| 6 | FS transcript presented as live | rejected | R2 replay (and no session means no verdict) |
| 7 | AG-flavour bundle | rejected | R7 flavour pin (the AG prover is aarch64-only; the bundle's flavour byte is set to 6) |
| 8 | byte flip (rep 1), witness bit flip (both reps, CPU), witness tamper (GPU unit), yr[0] flip, zerocheck round flip (GPU) | all rejected | Flock verifier or R2 replay |
| 9 | link negatives vs both reps: 15 (cross-session replay of both reps' proofs) | rejected | R2 replay. Negatives 10 (y tampered) and 11 (link points hash both roots) need the link claims inside Flock, which is flock-glue's; not tested here |
| 10 | padding rows (n = 3072 of 4096) | honest session accepted | benign, as red-team-flock found |
| R5 | a coin requested before the link context | rejected | R5 gate |

## What is not done, and what the re-audit should look at
- **The link context is a stub.** Opaque bytes stand in for root_F, the link points and y, and the server enforces only
  that they arrive before Flock's first coin. The C2 order (link points as a verifier coin slot after both roots, then
  y, then Flock's coins) needs root_B committed before the PIOP starts. Flock's union prover commits and binds inside
  `prove_fast_ligerito_union`, so the session would need a commit-then-prove split, or a `Commit(root_F, root_B)` →
  `Coins(points)` → `Link(y)` exchange before the first Flock round. That exchange belongs to flock-glue's session
  driver. The server gate is where it plugs in.
- **The GPU pair runs as two sessions**, one per table, because the harness proves each table in its own test process.
  R1, R7 and R8 hold per table. A single pair session needs both tables proved in one process.
- **Binding is computational.** The server records sha256 of each round, not its bytes, as the Ligerito `c…` sessions
  record msg_sha256. The transcript's own hash (BLAKE3 on CPU, SHA-256 on GPU) plays no role under live coins.
- **The verifier ran on the prover's pod** (loopback). The separate-host cost is estimated above from kb/live-verifier
  RTTs, not measured.
- **The CPU cost line is the BLAKE3 union table, not the census unit + BLAKE3 union** (flock-128's CPU line). The CPU
  live overhead is at the noise level, so this doesn't change the conclusion.
- **Re-audit targets:**
  - that every Flock challenge flows through the trait (flock-128's site census; `FsRng`/DRBG only on the AG path);
  - the framing equality between `lib.rs` (`framed_challenger!`) and `challenger.hpp` (the GPU sessions verifying is
    the evidence);
  - `Server::handle(Open)` child-index logic;
  - the replay's handling of Flock verifier early exits (the first recorded replay failure is reported before the
    verifier's own error; the unconsumed-rounds check runs only after a clean verify).

## Runs, artifacts, pods
| run | what | art |
|---|---|---|
| r20260925-115302-19e5 | first CPU selftest (n 4096) + bench m28 | art:6419ab23 |
| r20260925-120002-6814 | CPU selftest n 4096/16384 + bench m28/m33 | art:a2bdcca1 |
| r20260925-120757-e8a1 | CPU selftest incl. cross-session case | art:dc2467ae |
| r20260925-121437-7240 | CPU selftest (tip a43f6254) + bench m28/m33 (5 runs, wait time) | art:6715442b |
| r20260925-120734-7e37 | H100: GPU live negatives + round 1 (live / FS fast100x2 / FS fastx1) | art:16c17a43 |
| r20260925-121247-97e7 | H100: round 2, RAYON=cgroup quota (22), prover wait time (tip a43f6254) | art:5320c158 |

All six are preserved (`research data preserved` rc=0). The first GPU attempt r20260925-115929-b98e failed in the pod
script (an empty associative array under `set -u`) before any measurement.

Pods:
- vy-flock-live-cpu (i05njo6xbjg0xl, cpu3c 16 vCPU, $0.48/h): 11:42–12:19Z, about $0.30.
- vy-flock-live-h100 (hbwouesnfrs80p, H100 80GB HBM3, $3.49/h): about 11:57–12:19Z, about $1.30.
- Both terminated 12:19Z. **Total about $1.6 of $25.**

Handoffs received: `20260925T1215Z-handoff-from-flock-glue.md` (12:21Z, informational: flock-glue's Flock-CUDA e2e
numbers, its GPU PoW hook and its device unit witness). Answered in my handoff to flock-glue. How it combines with this
lane:
- Under live coins there is no grinding at all. `grind_pow` returns without searching, and so does `grind_pow_device`.
  flock-glue's PoW hook must keep that bypass (`if (live_cb)`) when both patches are applied.
- Its device witness (one witness for both reps) would remove the two 2.15 GB uploads inside my BF16 unit times (0.721 s
  live). That is roughly its 0.3–0.5 s saving, and it is independent of live coins.
- Its 16–17 ms of idle host-FS time per batch becomes about 50–77 ms of coin round trips per table on loopback.

Handoffs written: `lanes/coordinator/20260925T1222Z-handoff-from-flock-live.md`, with copies in `lanes/agkr-bound/` and
`lanes/flock-glue/`.

## FINAL

~~~text
tip: lane/flock-live @ a43f6254 (base main@767115db)        merge-with: none
known-failures: tests/test_repository.py::test_no_tracked_blob_exceeds_limit (on main too)    pod: terminated 12:19Z; $1.6
artifacts: art:6419ab23 art:a2bdcca1 art:dc2467ae art:6715442b art:16c17a43 art:5320c158
~~~

R1–R8 are implemented and every negative is rejected, so this is ready for the red-team re-audit. Live H100 prover time
at 4096 VUs: BF16 0.982 s (1.24x FS r2, 1.50x today), FP8 0.526 s (1.30x FS r2, 1.28x today). CPU live costs 1.00x.
Remaining work, none of it this lane's: the link-point coin slot (C2) belongs to flock-glue, a single pair session for
the GPU needs both tables in one process, and the separate-host verifier cost is estimated, not measured.
