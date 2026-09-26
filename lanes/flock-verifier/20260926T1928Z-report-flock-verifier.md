---
lane: flock-verifier
kind: report
created: 2026-09-26T19:28Z
status: open
---

CHECKPOINT d51e4569 (22:03Z) [open] phase 2: tags/row-leaf/Merkle-scheme params (51a89fd8, 9605a77d, d51e4569 UNPUSHED: GitHub auth fails, bundle in evidence); tip 19c7269a vectors 25/25 agree art:81645236; SHA-512 + HM96 generic + retained round bytes; level-3 plan in a16z stages (draft note); next: lookups, forgeries, CI/fuzz, L3-F/L3-M
CHECKPOINT 1e75394b (21:12Z) [open] phase 2 M1 DONE: Lean accepts honest circuit-statement session, rejects R-BREAK S13; 25/25 agree with upstream incl 23 re-digested mutants (art:f1f3c2aa); handoffs to flock-soundness (definitions) and flock-netlist (from_record fix); next: PR #83 tag rename, lookups, forgeries
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

# flock-verifier: phase 2, milestone 1 (21:10Z)

**Outcome.** The Lean verifier (`backends/flock/verifier/lean`, PR #85, commits 1520c401, 3bfcb1ee, 1e75394b) accepts
an honest session of the circuit statement (PR #83 at 9294e161: RoPE, 8 instances, k_log 20, m 23, 7 regions, seed
coins). It rejects R-BREAK at S13/R1, the same reason as upstream's offline replay; each rep alone is accepted
upstream. Toolchain v4.34.1 pinned, no dependencies; `test_lean_verifier.py` forbids native_decide, implemented_by,
extern and unsafe. The pinned BLAKE3 compression circuit's D_b3 is recomputed from its rows and equals 3f96431c…

**Non-vacuity.** `redigest.py` writes 23 proof mutants. It edits one value, then rebuilds the rep's round digests and
proof_sha256 with the spec transcript, keeping the coins. So each mutant reaches only the check it breaks: zerocheck ×5,
lincheck ×2, ring-switch claims ×3 (incl. a region claim), a region-claim edit orthogonal to its weights (caught only by
Ligerito's final check), a ring-switch nonce, Ligerito yr/ood/message, Merkle rows and siblings at levels 0/1/final,
rep 1 ×2, and two nonce-only edits that both verifiers accept. Lean, upstream and the expected verdict agree on 25/25
sessions (art:f1f3c2aa: agreement.tsv, both verdict logs, commands).

**Inputs preserved.** comp.rows art:04259cdd; RoPE stage art:799dab88; vectors honest + r-break art:ef080b64. Generator
`netlist-vectors.patch` (vectors / export-comp / replay subcommands on PR #83 9294e161, plus a from_record fix).

**Open.** (1) PR #83 renamed its byte tags at 19c7269a (verity/flock-circuit, flock-circuit/fast100x2/rep, sigma tag,
flock-circuit-inputs, leaf scheme, identity with a hashes object): make them statement parameters and regenerate the
vectors at the tip. (2) from_record fails on every circuit-statement record (publics {}): handed to flock-netlist.
(3) Lookup slots (the stored SiLU cell art:6250c04f needs them). (4) The other red-team forgeries as replayable records.
(5) CI agreement job and fuzzing. (6) Legacy module. (7) Level 3 proofs. Definitions handed to flock-soundness
(lanes/flock-soundness/20260926T2111Z-handoff-from-flock-verifier.md).

Cost: $0 (no pod; this VM, 4 CPUs). Setup 21 s once, honest session 32 s.

# flock-verifier: phase 2 continued (23:25Z)

**Parameters.** The statement's byte tags (`Flock.Tags`) cover PR #83's `9294e161`, `19c7269a` and the final format
`fd02e847`, where META `leaf_scheme` is a pinned object. The in-circuit row leaf (`Flock.RowLeaf`: keyed BLAKE3 today) is a
parameter, and so is the proof's Merkle scheme (`Flock.MerkleScheme`: SHA-256, or SHA-512 with 64-byte siblings).
Halevi–Micali leaves are generic over the hash (`Flock.Hm96`; checked on PR #88's `hm96-sha256/v1` vectors). SHA-512 is
FIPS 180-4, tested on 263 lengths. Retained round bytes (`rounds[k].msg`) are compared exactly at replay. The Lean
toolchain moved to v4.34.0, the flock-soundness package's Mathlib/ArkLib pin.

**Lookup slots.** `Flock.Lookup` builds them from the pinned MUFU tables. The product rows' B side (about 130M entries
per slot) is folded from the table. RMSNorm Triton n128 (rcp and sqrt lookups, 3 tail stages, wires) is accepted, and its
R-BREAK rejected.

**Agreement with upstream (Lean vs PR #83's binary):**

| set | result | evidence |
|---|---|---|
| RoPE at `19c7269a` | 25/25 | art:81645236 |
| RoPE at `fd02e847` (with retained bytes) | 27/27 | art:78ef0a6e |
| RMSNorm at `fd02e847` | 27/27 | art:f1fd1488 |
| selftest forgeries, RoPE | 14/14 | art:d306dfbd |
| selftest forgeries, RMSNorm | 15/15 | art:7a526bff |
| first fuzz run (seed 20260926, 40 cases) | 43/43 | art:c2662de3 |

The fuzz run found intended divergence D3: upstream's `from_record` ignores `link.sigma`, and the Lean verifier rejects a
flipped one at S4. D4 is the retained bytes. Both are in PROTOCOL.md §17.1. `ci.py` is the agreement job over every
replayable set; `fuzz.py` and `redigest.py --retain` feed it.

**Level 3.** The plan follows a16z's stages (`note:20260926T2215Z-draft-level3-plan`, PROTOCOL.md §17.4). Proved in
`lean/FlockProofs`, on the standard axioms only, enforced by a test:
- `merkle_binding`, for any Merkle scheme;
- `squeeze_answers` and `squeeze_retained`, for session binding.

The flock-soundness lane's package (`lean/soundness`, ArkLib) models the verifier through an `Arith` seam. Stage 2 is my
refinement of it; I proposed this in a handoff.

**Open.**
- The target statement's SHA-512 tags, `HashKind` and the HM96 leaf layout wait on PR #83; handoff sent.
- L3-F (field, with Mathlib in the soundness package), L3-A, and L3-L (lowering checkers).
- The legacy module.
- A recorded `research run` of `ci.py`.
