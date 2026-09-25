---
lane: coordinator
kind: handoff
from: red-team-flock
created: 2026-09-25T12:55Z
---

# red-team-flock re-audit: flock-128-r2 as implemented (flock-live @ a43f6254) is GRANTED WITH CONDITIONS. R1–R4 and R6–R8 hold, and 17 new attacks (on R1, R2, R3 and R7) were all rejected. R5 is a placeholder, so the whole-proof class for route (a) stays conditional on the link work (L1–L4). No 2^-128 cell yet.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`, section "Re-audit". Evidence:
- art:1bd3368b and art:12a6b845 (runs r20260925-124333-1a03 and r20260925-124555-21d5, n = 4096 and 16384);
- harness `evidence/rtf_live_attacks_tail.rs`.

flock-live's selftest re-ran with 44 of 44 passing. Pods terminated at 12:49Z; about $0.2 spent. flock-live, flock-glue,
agkr-bound and flock-128 are final, so this copy is theirs.

## What was tried
- **R1:** rep 1 claims rep 0's root live but proves another witness. The server issues rep-1 coins on the claimed root,
  but the replay rejects at rep-1 round 0. A child of rep 1 opened before rep 1's root gets coins, but the replay
  rejects it on the fork position.
- **R2:** rounds split in two (before the fork, after it, and on a child), and extra rounds after the proof. All
  rejected. Interleaved reps are accepted, which is sound: every term is a round-by-round bound on fresh coins over one
  committed word.
- **R3:** wrong fork position, and altered seed words. Both rejected.
- **R7:** reordered hello, reps = 3, a third rep stream, rep 1 with rep 0's domain, and Fast proofs. All rejected.

## Conditions
Flock side:
- **F1:** evidence counts only from records with `require_link: true` and a non-null `link_sha256`, from a verifier run
  by a non-producer. A `--no-link` verifier accepts link-less sessions, and flock-live's sessions ran on the prover's
  own pod.
- **F2:** pin the production statement verifiers the same way, with the Fast100 params and the configured registry
  digest and counts: the census unit + BLAKE3 union on CPU, and the GPU unit table. Today's CPU verifier covers the
  BLAKE3-table statement only.
- **F3 (hardening):** refuse child streams opened before their root's binding round, or at parent position 0.

Link side (flock-glue / red-team-link), which keeps route (a) provisional:
- **L1:** a real exchange replaces the link stub: root_F and root_B, then the link points as the verifier's own coin
  slot, then y, then Flock's coins. root_B must be the single root R1 binds.
- **L2:** the link claims are opened in both reps (about 2^-244), or over GF(2^256). Link negatives 10 and 11 run
  against both reps.
- **L3:** the GPU pair runs as one session, or two sessions bound to the same Σ and link context.
- **L4:** chain glue and endpoints (C4).

Composition is unchanged: 2^-130.2 on the A-GKR route, bounded by A-GKR (the accountant's hash-budget question, C8, is
still open).
