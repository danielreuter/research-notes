---
lane: coordinator
kind: handoff
from: red-team-flock-2 (bc-089339bc-4846-55b6-96c9-a15fd7a4a241)
created: 2026-09-26T05:40Z
---

# red-team-flock-2: PR #54 @ 34d02ae3. IR1 and IR2 are MET. rmsnorm-fused-cuda (9dbeb747) and rmsnorm-triton (b2155f3f) are GRANTED WITH CONDITIONS at NON_ZK_PROOF (relation-only), and rope/silu under v2 are byte-identical to what I granted. New: IR4 (the Rust verifier pins no cut structure: an eps-forged file verifies) and IR5 (tail add/mul NaN selection)

This answers your 05:02Z request, which replaces the 04:35Z one. The report is
`lanes/red-team-flock-2/20260926T0233Z-report-red-team-flock-2.md`, section "RMSNorm". A copy of this note is in
`lanes/coordinator/`.

- **rope / silu under flock-ir-unit/v2: CONFIRMED.** Regenerated at 34d02ae3, the 6,273 and 3,073 rows are byte-identical
  to the 25d8e464 / 5bb4a943 files I granted; only the header changed (one input group and one output group, the same
  words). The pins 2eaa652f / 3b1ed294 match. Your 11-case selftest passes on my own files (rope 256 units, silu 8,192).
  The earlier grant carries.
- **Evidence:**
  - VM: fused units, 240 rows.
  - Run r20260926-052455-c086 (art:3591d6ef), a CPU build of 34d02ae3 plus my `rtf2-tail` harness: the tail primitives,
    Triton units, load checks, selftests and tampers.
  - All harnesses are in `lanes/red-team-flock-2/evidence/`: `tail_diff.py`, `rtf2_tail.rs`, `rms_check.py`,
    `cut_tamper.py`, and `pod-scripts/50-rms-tail.sh`.
- **The tail interpreter (`ir_tail.rs`) against the IR primitives, bit for bit on the same host:**
  - **RsqrtApprox, MufuSqrtFtz, DivFullRcp: 525,824 cases each** (every exponent × sign × 1,027 mantissas), **0
    mismatches**.
  - **F32Div, F32Fma, DivFullScaleA:** 61,440 each (specials, NaN payloads, the 2^±126 thresholds), **0 mismatches**.
  - The tables regenerate to the pinned 218fc04d / 4e017678 / c4083814.
  - **F32Add and F32Mul differ exactly when both operands are NaN:** 23,253 and 21,869 of 61,440, which is my
    generator's P(both NaN) of 0.380 and 0.355. Rust returns the first operand's quieted NaN; the IR (numpy) returns the
    second (DISCREPANCIES S1).
  - This is **unobservable in both pinned tails.** Every NaN reaching a compared cut word passes through RsqrtApprox
    (fused) or F32Fma then MufuSqrtFtz (Triton), which canonicalize it, and the 60 NaN-scalar rows passed the load check.
    → **IR5.**
- **End-to-end (the crux): HOLDS.** On **630 adversarial rows** (fused 240 + 260, Triton 130), the Rust verifier's
  load-time `check_cuts` reproduces the IR evaluator's cut words: no file was refused. The rows cover 13 families:
  near-eps, NaN / inf elements, overflow, underflow, res = −x, zero rows, weight specials, subnormals, random words. They
  include 120 zero and 60 NaN scalars. My own evaluation of `tail_program` with the IR primitives equals the IR's cut
  words on every row.
- **Units: HOLD.** Against the IR evaluator, with my own v2 parser and evaluator, outputs and cut outputs (the warp
  aggregates) bit-exact:
  - fused: **7,680 unit lanes** (240 rows × 32);
  - Triton: **1,040** (130 rows × 8).

  Both have **0 mismatches and 0 unsatisfiable.** Structure: topological, no free rows, and the port groups tile
  contiguously (fused in [0,32)+[32,33), out [2528,2544)+[2544,2545); Triton in [0,64)+[64,65), out [8928,8960)+[8960,8961)).
- **Cut accounting: HOLDS for what it checks.** 9 of my 10 load-time tampers are refused, each with the right reason:
  - tail reordered;
  - an op reading itself;
  - tail truncated;
  - an unknown primitive;
  - a tail write to a unit's word;
  - two units producing one word;
  - a moved cut port;
  - instances × upi ≠ units;
  - a unit reading another unit's aggregate.

  `extra_cut_word` (34 declared words) is accepted. It's benign: word 33 is a tail temporary nobody reads. See IR4.
- **Selftests:** 13/13 on fused and Triton (my small files, m 26), including your four new cut cases.
- **Bound:** m = 20 + nbl for fused (2 units per block) and 21 + nbl for Triton (1 per block), with strict schedules for
  m 22–35. So at most 2,048 rows per proof for either, at about 2^-195.5 per proof.
- **Conditions:**
  - **IR4 (before any cell):** the Rust verifier pins none of the cut structure. The tail program, its constants (N, eps),
    the cut in/out maps and `cut_words` all come from the file header.
    - Demo: a fused file with the tail's eps set to 1e-3 (its header still names `eps1e-05`), the scalars recomputed with
      the IR primitives and all 128 units' outputs recomputed, is **ACCEPTED** by `flock-ir-block`, load and proof, both
      reps. Only IR2's byte-compare with the verifier's own staging refuses it.
    - Fix: pin a sha256 of the canonical `cut` object (tail program, maps, words) with the netlist, per template in PINS
      and checked like `--pin`, or move it into the v2 netlist so the netlist sha covers it.
  - **IR5 (before any other cut template):** make `ir_tail` F32Add / F32Mul select NaN payloads exactly as the IR does (or
    canonicalize on both sides), and add two-NaN vectors to the Rust tests. A tail whose add or mul result is itself a
    compared cut word would diverge today.
  - **IR2:** MET procedurally. The verifier stages its own file, and `check_staged` compares header and body byte for
    byte. It stays mandatory for any evidence.
  - **IR3:** open. There's no Table 2 cell before the unit IO is committed (`verity/flock-ir-frame/v1`, with its own
    review).
- **Labels:** a `finding` on art:7342c52d (your H100 all-4 run at 76b7cbb2), art:44d7c8d0 and art:a4f38fc0 (the rope
  verifier and prover runs at 34d02ae3), by red-team-flock-2, `--ref` r20260926-052455-c086. There's no `proof_class`:
  the statement is relation-only (IR3).
- **Pods:** vko4u1d4zbjhd3 (cpu3c 16), 05:17–05:40Z, terminated. The first run, r20260926-051928-5f2d, failed on the pod
  image's Python 3.11 (verity needs 3.12) and is superseded.
- **For the coordinator:**
  - flock-backend's 04:52Z note to my lane lists eight new-layout Chunk(n) cells (art:43986c5d, c0999f7f, 149cdaf9,
    673c1835, c767e092, bbb95342, c200eef3, c4d03dd5). They fall under red-team-flock's Chunk(n) grants, and none is NVFP4,
    so I haven't labelled them. Please route them to red-team-flock.
  - My earlier pre-check (bf16-hopper-wgmma rows = bf16-hopper's, 0 / 129,571) bears on the two H100 wgmma cells.
