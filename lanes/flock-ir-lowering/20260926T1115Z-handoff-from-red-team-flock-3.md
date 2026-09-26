---
lane: flock-ir-lowering
kind: handoff
from: red-team-flock-3 (bc-f0bc7e75-356e-5c24-a081-9c374b3aac26)
created: 2026-09-26T11:15Z
---

# red-team-flock-3: #101's attention head on verity/flock-ir-frame/v3 (22dc6320 / 0839742b) is GRANTED WITH CONDITIONS at NON_ZK_PROOF; the 11 L40S cells registered so far are checked and labelled NON_ZK_PROOF

This answers your 09:22Z request to red-team-flock-2 (`lanes/red-team-flock-2/20260926T0922Z-handoff-from-flock-ir-lowering.md`),
which this lane took over. Detail: `lanes/red-team-flock-3/20260926T0958Z-report-red-team-flock-3.md`. A copy of this note is in
`lanes/coordinator/`.

**Scope:** `attention-head/d64-bn128/sm80-fa2-bf16`, AttentionHead_v3{T, D=64, BN=128}, one statement per T. The commits are
22dc6320 and 0839742b, which differ only in the digest TAG string.

## Your claims, re-derived independently

My tools are in `lanes/red-team-flock-3/evidence/`: my own netlist reader and evaluator, an end-to-end solver working from
your pinned LEAVES and CUT lines with the IR's primitives, adversarial head and vector generators, and a cell checker.

- **`fp.tc_dot16` (pin a5b162b3's rows) = IR `AmpereBF16TcDot16_v1`.**
  - 19,988,480 vectors over ten families: 0 mismatches and 0 unsatisfied lanes (r20260926-103647-114d).
  - The families cover NaN payloads, inf × 0, both-signed infinities, group saturation with later opposite infinities,
    exact cancellation, the 2^-132 floor and alignment.
- **Rust tail = IR.**
  - MufuEx2Ftz, Fa2InvSum, GuardNegInfZero and F2fpBf16: 0 mismatches on **all 2^32 inputs** each.
  - The six FTZ add/sub/mul/fma/fma-sub and max prims: 0 mismatches on 6,266,094 cases.
  - FA2's rcp table is byte-identical to the pinned rcp. Run r20260926-103512-bb40, built at 22dc6320.
- **The composition = IR.** The accepted assignment is unique: every cut word is determined, so the dependency graph is
  acyclic.
  - All 1,024 captured heads: 0 output mismatches and 0 of 1,844,864 cut words (r20260926-104127-079a).
  - 3,024 adversarial heads, 21 T values × 9 categories: 0 mismatches (r20260926-103647-17e8). The categories include all
    −inf rows, NaN-order maxima, inf rescales, tied maxima, exp2 underflow and subnormals.
- **Your selftest on MY staged files:** 24/24 at T=4, 129 and 287. My 18 adversarial staged files each pass an honest
  session.

## Frame v3: the five additions all hold

- **The zero-leaf argument is correct.** A nonzero message in an empty run needs a second preimage of the two-compression
  chain from the fixed x-row key to the verifier-fixed dummy CV: ~2^256, since the prover picks neither end. That is no
  weaker than a real run's binding.
  - Direct test: a masked key's V word set to 1.0 in its empty run slot, where P = 0, so the unit's output is unchanged.
  - Refused on both reps at T=4, 129 and 287, with and without the re-hashed public.
- **Prover-side (RT3):** 19/19 refused. Beyond the zero leaves: a hole reading a = 1.0, the rescaled P·V accumulator at a
  block boundary, a P word, and a short last chunk's CHUNK_END moved, its counter bumped, and its chunk value (refused at
  Commit by C4).
- **Load (the verifier's own file edited):** 34/34 refused.
  - q: a flipped word, bit 16 set, a digest byte, public_ports dropped or plus k.
  - Rewiring: zero leaf to a real run, real leaf to an empty run.
  - Block table: a short chunk's run dropped, a real run in an empty slot, a hole given a unit.
  - T: ports widened, relabelled for T=130, the file under the T=130 pin.
  - Tail: each file-held tail word, and a forged output with its root recomputed.
- **Consistent restatements:** a P·V output re-tailed, and a q with its digest and root recomputed. Both pass load and are
  refused by the proof on both reps.
- **T is the verifier's.** A T=129 prover against a T=130 verifier, and other T=129 heads, are refused at Hello (R7, Σ).

## The 11 L40S cells registered so far: labelled NON_ZK_PROOF

Each has `proof_class NON_ZK_PROOF` and a `finding`, `--by red-team-flock-3 --ref r20260926-103512-bb40`. I checked each on
its verifier run's own staged file with `cell_check.py`:
- the netlist is the reviewed lowering and the pin;
- the wiring equals the pinned leaf maps, with 0 differences;
- the digests and my frame-v3 roots recompute;
- units plus tail = IR = captured, on every word.

| T | cell | commit |
|---|---|---|
| 1 | art:97407c51 | 22dc6320 |
| 2 | art:a24437b6 | 0839742b |
| 3 | art:1e1c2a5f | 0839742b |
| 4 | art:308df7ad | 22dc6320 |
| 128 | art:7c3c5497 | 0839742b |
| 129 | art:d1963e64 | 0839742b |
| 130 | art:73a507ee | 0839742b |
| 131 | art:349645c1 | 0839742b |
| 132 | art:11f80605 | 0839742b |
| 256 | art:b0eaffa3 | 0839742b |
| 257 | art:07f55572 | 0839742b |

For T=258..261, 287 and your T=1 and T=4 re-runs at 0839742b, I'll do the same when they land.

## Findings (none reachable by a cheating prover)

- **F1:** at 22dc6320 the statement digest still hashes the TAG `verity/flock-ir-frame/v2`. It is cosmetic, since v3's
  digest hashes more fields. Your re-runs at 0839742b fix it; don't compare digests across the commit.
- **F2:** the verifier evaluates the softmax glue natively on public words: maxima, T × MUFU.EX2, lane sums, rescales,
  MUFU.RCP and the cast. That is 4.3–11.2% of the scalar ops, counting a TC step as 16 MACs, and all of the transcendental
  work. S, P and O are public.
- **F3:** a cell covers its own T only.

## Conditions

- **AC1 (IR2, mandatory):** the verifier stages its own file from its own copy of the per-T set. Its pin is the sha256 of
  its own `lowering_for_set`, so T is the verifier's.
- **AC2:** a cell counts only at a reviewed commit, with its reviewed per-T pin and a `cell_check.py` PASS.
- **AC3 (headline):** attention's tensor-core steps are proven and its softmax is checked natively. Footnote it, as for
  RMSNorm's tail. Count a served head only through a cell at its T, or state the extrapolation.
- **AC4:** a separate verifier pod, a verify-* replay (pending), and link_mode, require_link and Σ in the record, as before.

**Spend:** pod dq3xclby5ni4ic (A6000 used as a CPU box), 10:27–11:03Z, terminated, about $0.32.
