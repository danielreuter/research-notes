---
id: 20261001T0503Z-report-proofs-ir-bf16-done-attention-started
campaign: verity
lane: proofs-ir
kind: report
status: open
repo: danielreuter/verity
origin: cursor/proofs-ir-95d4
---

CHECKPOINT 213f4361b (21:07Z) [open] Q_call v1 check --record r20261001-203205-c3c1 PASSED on 213f4361b (all steps; lean-agreement skipped); Q_call refuses 97 Definitions gate-too-wide (lifted 33-bit, TopPMaskWordx64): needs-proofs at note:proofs/20261001T2110Z-handoff-from-proofs-ir-qcall-refuses-lifted-and-topp
CHECKPOINT 213f4361b (20:38Z) [open] Q_call v1 PR ready at 213f4361b: body for proofs to open at note:proofs/20261001T2034Z-draft-from-proofs-ir-qcall-pr-body-213f4361b; red-team ask at note:red-team-proofs-554/20261001T2034Z-ask-from-proofs-ir-review-qcall; check --record r20261001-203205-c3c1 running
CHECKPOINT 46c768b2c (19:55Z) [open] Q_call v1 spec + vectors pushed: cursor/proofs-qcall-95d4 @ b307d8320 (cut.evaluate_call, partition_object Q_call v1, PROTOCOL.md §11, tests/ir/qcall_vectors.json; tests/ir 282 pass). Next: circuit-check, Glossary, measurements (running), red-team ask, check --record.
CHECKPOINT (05:45Z) BF16 slice done; attention started on `cursor/proofs-ir-95d4` at `ac15d5abf`. Design note: Phase 2, Phase 3.

- **BF16 measures:** the same committed bits as v2. That is 1,024 bits per MAC in the unit slot, and 2,048 / 4,096 for
  the statement at K = 2048 / 8192, on the study's layout. The +28 / +31 ANDs fit in alignment padding.
- **circuit-check:** green on every new Definition.
- **Slots:** the claim holds. The only cross-call sharing is the first step's zero-accumulator folding. But a Boolean step
  takes a 2^14 slot, so slots need the BF16 decode split into its own Definition. Without it, 1,568 decode ANDs leave
  6,692, which fits 2^13.
- **n-ary XOR vs `Q_word` v1:** no clash. A gate with more than 4,096 operands is wide: its operands aren't enumerated,
  and it never matches as a recompute.
- **Attention so far:** the FTZ f32 ops, `F32Max`, `GuardNegInfZero` and `DotBf16_v3` are Boolean, circuit-check green.
  `AttnBlock` / `AttentionHead` / `Attention` will be v6.
- **DECISION NEEDED (blocks the ex2 / rcp reads):** an explicit ROM Definition body is about 1.1 × 10^7 reference parts,
  or 9.5 × 10^7 XOR inputs, per 2^23 table. That is hundreds of MB in each attention descriptor.
  - Recommendation: a gate family `Rom<n>x<w>[<sha256>]_v1`, decoded lazily by id and defined in PROTOCOL §9 as the
    `_Read` construction over the table bytes.
  - The alternative is to wait for v2.
