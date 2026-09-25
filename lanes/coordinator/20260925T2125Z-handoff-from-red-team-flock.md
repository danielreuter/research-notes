---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T21:25Z
---

# red-team-flock fifth audit: route (a) with live prime coins (PR #36 @ dec08973, art:3bfb2f58) is GRANTED WITH CONDITIONS at NON_ZK_PROOF. Live coins close my Fiat–Shamir downgrade, and the bound is 2^-130.19. One DoS: the Rust prime verifier spins forever on a record with its last prime round dropped.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "Fifth audit". No pods were needed for this
audit; I ran the gate locally from the store.

## What closes the downgrade
Every A-GKR challenge is a `Prime` round in the Flock session. That covers the GKR/LogUp coins, rho, the functional and
row coefficients, and the Ligero query set.
- The prover sends its SHA-256 transcript state, which commits every message and every earlier coin. The server answers
  with OS words below p, by rejection sampling.
- `Prime` rounds are refused before Hello and between Commit and y. Commit is refused before any prime round.
- Both verifiers replay: at every round the verifier's own state must equal the recorded one, the counts must match,
  root_F must come after exactly `before_commit` rounds, and every round must be consumed. An absorb marks the
  transcript dirty, so a coin is never used across a message.
- `challenge_bytes` and the device-side Fiat–Shamir are off. `--require-live-coins` refuses a proof without the record's
  rounds.
- The ~3,000 rounds before root_F (3,004 + 2 at 4,096 VUs) cost latency only. Each is a fresh live coin covered by the
  accountant's per-round terms; there is no ×2^60.

## My store re-run
Records art:42841b22 (verifier run r20260925-195835-65ab) with proofs art:d9666f5a (prover run r20260925-201056-1018),
paired s1–s5 to l0000–l0004, using my own `verity-gkr-verify` build at dec08973:
- prime (live replay, circuit and commitment pinned), prime_live, replayable, Σ, exchange, gated and preserved: all
  pass on 5 of 5;
- `non_producer` fails: the operator is route-a-live, the producer, as disclosed.

Negatives, all rejected:
- a proof cross-paired onto another session;
- a coin word edited;
- the state of the post-y round edited;
- `before_commit` shifted by one;
- the prime record removed (`--require-live-coins` refuses);
- agkr-flock-cell's Fiat–Shamir proof presented against a live record.

**The DoS:** with the last prime round (the Ligero query set) dropped from the record, `verity-gkr-verify` ran at 100% CPU
for more than 35 minutes before I killed it. It fills the missing round's coins with zeros and never fails. It doesn't
accept, but a gate has no verdict. It must fail fast on a missing or short round.

## Conditions
- **RA1:** the Rust (and Python) verifier returns an error as soon as a live round is missing, malformed or short,
  instead of substituting zero coins.
- **RA2:** the result's `prime.sequential_depth: 328` is stale. The rounds and depth fields for D3 must say 3,006 prime
  rounds (3,004 before root_F) plus 1,070 Flock rounds; `net.rounds` = 4,076 already does.
- **RA3: MET.** verify-night-3 labelled `verified=accepted` on art:3bfb2f58 at 20:53Z after a non-producer store re-run.
  It rebuilt the statement from the frozen instances and ran the gate with `--rust --flock`, the Flock replay included,
  on 5 of 5 sessions. My own re-run agrees on the prime side.
- **Dependency (Daniel's hash convention):** the same as the fourth audit. Counting q²/2^256 for the 256-bit hashes
  (Flock's Merkle trees, root_F/Σ, the row leaves) puts the bound at about 2^-126.5 to 2^-127.

Labels written on art:3bfb2f58: `proof_class=NON_ZK_PROOF` and a `finding`, both by red-team-flock with `--ref` pointing
to this handoff.
