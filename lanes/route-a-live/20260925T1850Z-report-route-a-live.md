---
lane: route-a-live
kind: report
created: 2026-09-25T18:50Z
status: final
---

CHECKPOINT 8b14460e (22:20Z) [final] reopen 2: re-registered art:77411c93 (supersedes art:112afcfa/3d7cbea2/4b52879f): run_files art:d9666f5a, attempt r20260925-221942-7052, protocol uncontended, sweep plateau by memory cap, commit.seconds 38.97 s CPU (note), loopback 0.172 ms/round same run; main renderer: interaction passes, only U left. No pod
CHECKPOINT 8b14460e (22:19Z) [final] reopen 2: re-registered art:112afcfa (supersedes art:3d7cbea2, art:4b52879f): run_files art:d9666f5a + attempt r20260925-221834-c6f5, protocol uncontended, sweep plateau by memory cap, commit.seconds 38.97 s CPU, loopback 0.172 ms/round same run; main renderer: interaction passes, only U left. No pod
CHECKPOINT 7d03a87b (22:17Z) [final] reopen 2: re-registered art:3d7cbea23e9bdd7b14698d1871d7b4f6c24974a70cbd34ba04edfb5bbad58f60 (supersedes art:4b52879f): refs.run_files art:d9666f5a + attempt r20260925-221620-2466, protocol (uncontended; guard throttle rule self-tripped), sweep plateau by memory cap, commit.seconds 38.97 s CPU; PR #38 renderer: only U left. No pod
CHECKPOINT 504f75b6 (21:28Z) [final] reopen: re-derived art:4b52879f (4096; rounds 4076, t.total 12.59/live 13.63) + art:aa9223c2 (1024); FAILS interaction tolerance at 1 ms (-18%; run RTT 0.36 ms), passes at measured RTT (-3%): decision to coordinator. Fail-fast prime verifier + negatives. PR #36 @ 504f75b6. No pods, $0
CHECKPOINT dec08973 (20:26Z) [final] route (a) cell with live prime coins: NON_ZK_PROOF 2^-130.19, A100 4096 VUs 14.01 s same-DC (art:3bfb2f58; 1024: art:d5731679); G2 replay + negatives (art:837d95c8); >4096 OOM on A100. PR #36 @ dec08973. Pods terminated 20:19Z/20:25Z, ~$2.3. Re-audit + G3 requested
CHECKPOINT 3bc72407 (19:58Z) [open] READY verifier serving r20260925-195835-65ab on vy-route-a-live-ver 154.54.102.18:11662 (ssh :11661), US-MD-1 with the A100 154.54.102.35; sizes 1024 4096 x5. Probe r20260925-194129-7a4c: live cell OK @1024/4096 loopback (4096: 3006 prime rounds), 8192 OOM on A100 80GB (prime). Polling in turn.
CHECKPOINT 3bc72407 (19:41Z) [open] relaunched (first launch failed: --tool unregistered): probe r20260925-194129-7a4c on vy-route-a-live-a100 (setup, statements 1024-32768, loopback probe per size, negs+battery@4096), verifier setup r20260925-194138-e528 on vy-route-a-live-ver (US-MD-1 both). Staying in turn polling; READY when statements land. tip 5d1f
CHECKPOINT 3b103830 (19:20Z) [open] WAIT vy-route-a-live-a100 r20260925-191856-7028 + vy-route-a-live-ver r20260925-191913-33b3 check-back 20:00Z agent bc-9ff671e3-c69a-59c7-845e-dd0abff52276. WAITING r20260925-191856-7028 on vy-route-a-live-a100, check after 20:00Z; next: send digests to ver pod, timed same-DC run. PR #36 @ 3b103830
CHECKPOINT cba212e4 (19:12Z) [open] cba212e4 pushed (lane/route-a-live on agkr-flock-cell c95dd13a): live prime coins (Prime rounds; replay in py+rust verifiers; gates), G2 record+flock-link replay, negatives; VM tests: verifier cargo 35 ok, pytest 32 ok. Next: pod selftest + A100 cell run
CHECKPOINT b989a321 (18:50Z) [open] started: live prime coins for route (a) cell (stacked on lane/agkr-flock-cell, PR #28); agent bc-9ff671e3-c69a-59c7-845e-dd0abff52276

# route-a-live: live prime coins for the route (a) cell, G2 record + offline Flock replay, co-located re-time

Base: `lane/agkr-flock-cell` @ 7585828d (PR #28; the 19:12Z checkpoint's "c95dd13a" is wrong, the base is its child
7585828d, which carries the sweep script, the interactive record and the RTT probe). Branch `lane/route-a-live`, PR #36.
Asked: red-team-flock's fourth audit (class condition, G2, G3); the coordinator's 19:38Z message (same-DC recipe, sweep).

## What changed (PROTOCOL §17.6)
- Every A-GKR challenge is the live verifier's: `Prime{state, n}` rounds (the state is the SHA-256 transcript chain,
  so it commits every earlier message and coin), answered by 6n OS words < p, chained back into the state. `reserve`
  batches known-consecutive challenges at 4 mirrored points. The graphed LogUp path (device-side FS) is off live.
- Server order: no prime coin before Hello or between Commit (root_F) and y; no Commit before a prime coin; Hello pins
  `prime: live-coins/v1`; nothing after the verdict. Record: every round + `before_commit`.
- Both prime verifiers replay the rounds (state, count, root_F after exactly `before_commit`, all consumed); a replay
  mismatch is the primary reason. `verity-gkr-verify --require-live-coins`.
- One connection per session: `cell-prove --prime-sock` forwards the prime rounds; Finish waits for the prime prover.
- G2: the record keeps root_F, root_B and the committed public words; `flock-link replay` re-verifies Flock from the
  record + kept proofs under the verifier's own config/statement, never reading the recorded verdict.
- Gate: `prime_live`, `replayable`, `flock_replay`; the prime check runs on the record's rounds.
- Result: NON_ZK_PROOF only if every timed session was live and replayed live, else NON_ZK_PROOF_DIAGNOSTIC.

## Results (A100-SXM4-80GB prover + cpu3c verifier, both US-MD-1, RTT 0.36 ms)
Envelopes (contract problems []): **art:3bfb2f58** (4096), art:d5731679 (1024); gate batteries art:837d95c8.

| VUs | t.total (min–max) | prime | Flock | rounds (prime / before root_F / Flock) | prime wait | bytes up / down | proof_class | bound |
|---|---|---|---|---|---|---|---|---|
| 1,024 | 5.79 s (5.67–5.90) | 3.36 s | 5.79 s | 3,607 (2,651 / 2,649 / 956) | 0.57 s | 1.36 MB / 0.15 MB | NON_ZK_PROOF | 2^-130.19 |
| 4,096 | **14.01 s** (13.58–14.44) | 4.96 s | 14.01 s | 4,076 (3,006 / 3,004 / 1,070) | 0.66 s | 2.06 MB / 0.17 MB | NON_ZK_PROOF | 2^-130.19 |

- 4,096: overhead.vs_native_peak 3.47e8 (vs 143.3 s / 3.55e9 at the old remote verifier with FS prime coins). The
  cell is now Flock-CPU-bound: Flock prover compute 13.24 s, Flock wait 0.40 s, verifier compute 0.19 s; prime
  verifier (Rust) 4.60 s. Prime prove 4.96 s vs 3.7 s FS/graphed: +1.3 s = the ungraphed LogUp + 0.66 s of rounds.
- Round-trip cost: the prime half is 3,006 rounds, 3,004 before root_F (the audit's depth 328 assumes tables and
  segments in parallel; one transcript serialises them). At 0.36 ms they cost 0.64 s on the critical path; at the
  earlier remote verifier's ~127 ms they would be ~6.4 min. 45 B up + (13 + 24n) B down per round.
- Sweep: 8,192 and 16,384 VUs OOM in the prime prover on the 80 GB A100 (41.3 GiB / 6.3 GiB allocation fails; 51 GB
  peak at 4,096), not specific to live coins; 32,768 fails at witness (`query tuple not in table T_OP` on the tiled
  statement, a finding for the A-GKR side). So the A100 cell stops at 4,096; no timing-only points above it.
  Probe: `evidence/probe.tsv`.

## Tests and negatives
- VM + pod: verity-gkr-verify cargo 35 + 4; pytest 49 (test_live_coins, test_cell_gate, test_commit, test_circuit_pins);
  flock-link selftest at 8 VUs all_pass (prime order, G2 replay, tampered records) (r20260925-194138-e528).
- Full scale, loopback (r20260925-194129-7a4c, `evidence/battery-loopback-4096.tsv`) and the real remote records
  (r20260925-201805-3504, `evidence/battery-remote-4096.tsv`): the 5 remote sessions pass every gate check except
  `non_producer` (I operated the verifier). Rejected: a stale prime state (coin before its commitment; R2-prime round 5),
  a Fiat–Shamir prime prover (R7 at Hello), prime coins across sessions (R2-prime round 1), tampered records (prime
  word, prime before_commit, prime state, Flock coin, public words re-sealed, y re-sealed, prime rounds dropped). The
  battery's FAIL rows were bookkeeping (warm-up without a remote record; no FS session in a sweep; a tampered coin
  rejected by the LogUp check before the next state comparison) and are fixed in the script.

## Not done / for others
- G3: a non-producer verify lane re-runs `cell_gate.py --rust --flock` from the store (records in
  r20260925-195835-65ab, proofs in r20260925-201056-1018) and labels `verified`. My verifier pod is producer-operated.
- Red-team re-audit of §17.6 (requested).

## FINAL
~~~text
tip: lane/route-a-live @ dec08973 (base lane/agkr-flock-cell@7585828d)        merge-with: lane/agkr-flock-cell (PR #28), then PR #36
known-failures: tests/test_repository.py::test_no_tracked_blob_exceeds_limit (on main too)    pod: vy-route-a-live-ver terminated 20:19Z, vy-route-a-live-a100 terminated 20:25Z; ~$2.3
artifacts: art:3bfb2f58 art:d5731679 art:837d95c8
~~~
Handoffs received: none. Handoff written: `lanes/coordinator/20260925T2030Z-handoff-from-route-a-live.md`.

# Reopen (21:30Z handoff from the coordinator): re-derived result, fail-fast verifier

- **Result:** `tools/cell.py rederive` from art:3bfb2f58's embedded sessions (no pod): art:4b52879f (4,096: t.total 12.59 s
  compute, t.total_live 13.63 s, rounds 4,076, wait 1.03 s) and art:aa9223c2 (1,024: 4.95 / 5.78 s, 3,607 rounds);
  contract problems [], `refs.supersedes` the old ones. `views.interaction_problem` (main a2bad079): **fails** at the
  1 ms reference (-18% / -32%; formula 16.67 / 8.55 s), passes at the measured 0.36 ms RTT (-3% / -9%). The old envelope
  was classified non-interactive (rounds 0). Decision handed to the coordinator (tolerance at the measured RTT, or a
  netem 1 ms re-run).
- **Fail-fast:** the spin was `open_set` over zero coins from a missing/short round. First-failure checks + a draw cap;
  4 unit negatives; real 4,096 record on the VM: dropped/short last round rejected in 1.0 s, honest accepted 7.1 s.
- Tip 504f75b6 (PR #36). No pods; $0. Handoffs: `lanes/coordinator/`, `lanes/verify-night-3/`, `lanes/red-team-flock/`
  (`20260925T2210Z-handoff-from-route-a-live.md`). Received: `20260925T2130Z-handoff-from-coordinator.md` (this section).

## FINAL (reopen)
~~~text
tip: lane/route-a-live @ 504f75b6 (base lane/agkr-flock-cell@7585828d)        merge-with: PR #28, then PR #36
known-failures: tests/test_repository.py::test_no_tracked_blob_exceeds_limit (on main too)    pod: none this round; $0 (lane ~$2.3)
artifacts: art:4b52879f art:aa9223c2 art:3bfb2f58 art:d5731679 art:837d95c8
~~~

# Reopen 2 (renderer 2215Z): re-registered as art:3d7cbea2
- `cell.py rederive` @ 7d03a87b, run as local attempt r20260925-221620-2466 (`evidence/pod-scripts/40-rederive-4096.sh`): refs.run_files art:d9666f5a (prover dump), verifier_files art:42841b22, supersedes art:4b52879f; protocol (`evidence/protocol-4096.json`: contended false, guard throttling rule tripped by the cell's own Flock prover), sweep (`evidence/sweep-4096.json`: plateau by memory cap), commit.seconds 38.97 s (CPU committer). PR #38's renderer: only U left.
- Handoffs: `lanes/{coordinator,verify-night-3,red-team-flock}/20260925T2225Z-handoff-from-route-a-live.md`. Received: `lanes/coordinator/20260925T2215Z-handoff-from-renderer.md` (via the root). No pod, $0.
- Superseded at 22:18Z by art:112afcfa, then at 22:19Z by **art:77411c93** (attempt r20260925-221942-7052; the commit note "CPU reference committer; a GPU committer is not yet measured.", answering `20260925T2220Z-handoff-from-coordinator.md`). art:112afcfa (attempt r20260925-221834-c6f5): adds `live.loopback_round_seconds` 0.172 ms from the same run's loopback warm-up session (answers `20260925T2135Z-handoff-from-coordinator.md` and `20260925T2150Z-handoff-from-coordinator.md`); main 5f8d8789's interaction check passes (-7.6% at the run's RTT); renderer reason U only.
