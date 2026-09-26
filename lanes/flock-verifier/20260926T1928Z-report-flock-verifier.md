---
lane: flock-verifier
kind: report
created: 2026-09-26T19:28Z
status: open
---

CHECKPOINT 1520c401 (20:55Z) [open] phase 2 M1: Lean verifier (commit 1520c401) accepts the honest circuit-statement session (RoPE, 8 inst, m=23) and rejects R-BREAK at S13; next: re-digested mutations for non-vacuity, upstream agreement, PR #83 rename
CHECKPOINT 4f4a1aa7 (20:09Z) [open] phase 1 DONE, pushed: PR #85 tip 4f4a1aa7 (PROTOCOL.md, vectors.json, transcript_check.py; 50/50 art:430c513a; reader notes art:85c4b037); next: phase 2 Lean verifier on coordinator go
CHECKPOINT 4f4a1aa7 (20:08Z) [open] phase 1 DONE: PROTOCOL.md + vectors (50 honest sets, 20 negatives, 12 forgery runs); spec transcript check 50/50 art:430c513a; commits 715a5985 4f4a1aa7 UNPUSHED (GitHub write auth fails), bundle in evidence/; next: phase 2 Lean on coordinator go
CHECKPOINT 2431e3c1 (19:40Z) [open] phase 1: honest vectors found in store (pure-block 20+ cells, IR frame 25 cells, netlist loopback art:6250c04f); red-team forgeries incl R-BREAK art:8d04b53f are outcome+harness only; 5 upstream-reading subagents running; branch cursor/flock-verifier-spec-7ab3
CHECKPOINT 2431e3c1 (19:28Z) [open] started 19:35Z: lane flock-verifier (clean-room Flock verifier). Phase 1: PROTOCOL.md spec from ePrint 2026/1329; reading paper, b684b12 formats, live layer; next: vectors from store

# flock-verifier: phase 1 (the spec), done 20:10Z

**Outcome.** `backends/flock/verifier/PROTOCOL.md` (74 KB) specifies the verifier of record for fast100 run twice on one
root with live coins, for flock-pure-block/v2, the IR frame statements and PR #83's circuit statement, as pure, total
functions with explicit byte formats (Lean-ready; §20 maps it to modules). Branch `cursor/flock-verifier-spec-7ab3`,
PR #85 (draft), tip 4f4a1aa7 (spec 715a5985, transcript_check.py + vectors 4f4a1aa7), pushed after a transient GitHub
auth failure (bundle `evidence/flock-verifier-spec-4f4a1aa7.bundle` kept). Upstream reading notes behind the spec, for
red-team traceability only: art:85c4b037.

**Validation.** `transcript_check.py` rebuilds every round of a session from the spec alone (framing, operation order,
proof layout, T from the ring-switch recombination) and compares the recorded digests: 50 of 50 honest sets, both reps,
m 25 to 34, all rounds match (art:430c513a; table `evidence/transcript-check-50-sets.tsv`). An independent decoder from the
spec's §8 layout consumes the recorded proofs exactly.

**Vectors** (`vectors.json`): 50 honest sets (100 sessions): pure-block 23 cells (every layout), IR frame 23, sampling 2,
vllm-block 1, circuit statement 1 (art:6250c04f, loopback, os coins); 20 record-level negative recipes (12 with recorded
outcomes from art:487b77de, 8 new incl. the two intended divergences D1 root_F = Σ and D2 no extra streams); 12 red-team
forgery runs (art:8d04b53f R-BREAK, art:1bd3368b, art:12a6b845, art:20545959, …), stored as harness + verdict tables only:
phase 2 materialises them via a selftest `--dump`. Ten pre-G2 pure-block records lack committed publics (need a tooling
step). No seed-coin session exists yet.

**Coin-bit finding** (asked): rep 0 round 0's 6 coins (`r_skip`) are squeezed and never read; the last coin (Ligerito's
final claim-batching β) is read but an honest proof is insensitive to it; query coins read only the low d − c_j bits of
`lo`. Not a soundness issue; flagged to red-team-flock as FYI (`lanes/red-team-flock/20260926T1958Z-handoff-from-flock-verifier.md`).

**Ambiguities resolved from upstream** (spec §19, A1–A16): unused r_skip; vanishing on S imposed (deg 127); v† sent and
compared; (G(1), G(∞)) encoding with inv(0) = 0; pinned-coordinate placement; lincheck computes α·A0ᵀe + B0ᵀe with 64 skip
values and a fresh coin (no matrix claims); constant-wire β; per-claim ring switch + independent batching coins, no
standalone sumcheck (Ligerito's F256 sumcheck); low-7-bit packing, b_v = x^v; Ligerito over GF(2^256) with stratified
queries, cap commitments and a level-0 OOD despite Remark 11; PoW nonces are messages; statement binding; extra claims not
absorbed; root_F unchecked live; m > 35.

**Rule compliance** (spec §16.7): strict mode = the circuit statement only; pure-block and IR frame need legacy native
checks (L-CV parent trees over committed chunk values, L-ACC, L-TAIL pinned tail, L-SAMPLE). Acceptance (§17) per Daniel's
change: upstream Rust is a CI cross-validation oracle; then only the Lean verifier runs; Lean compiler/runtime recorded as a
trusted component mitigated by the agreement tests. SHA-256-on-all-paths target noted (§2.5, §16.7).

Handoffs received: none in the inbox. Sent: red-team-flock FYI above.
