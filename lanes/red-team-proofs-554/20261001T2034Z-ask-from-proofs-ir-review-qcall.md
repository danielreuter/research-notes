---
id: 20261001T2034Z-ask-from-proofs-ir-review-qcall
campaign: verity
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: proofs-ir (bc-6cd83494)
---

# Review ask: `Q_call` v1's committed set and recompute report (`cursor/proofs-qcall-95d4` at `213f4361b`)

to: red-team-proofs-554. From proofs-ir, on proofs' brief (`note:proofs-ir/20261001T1931Z-handoff-from-proofs-qcall-partition-query`,
Daniel's go at 12:25 PM PDT). proofs opens the PR from `note:proofs/20261001T2034Z-draft-from-proofs-ir-qcall-pr-body-213f4361b`;
until then, review the branch. Its `check --record` is `r20261001-203205-c3c1`.

**What changed.** `Q_call` v1 is a new query (`PROTOCOL.md` §11, the reference in `verity.ir.cut` under "Q_call v1" and
`partition_object.CallPartition`). A unit is a gate interval with at most X = 32 output bits. The cut runs along Calls, then body
nodes, then a callee's body or a batch's or scan's members. Inputs and constants are in no unit, and there are no wiring, folding or
wide-fan-in rules. `Q_word` v1 and v2 are untouched.

**Please read two things.**

1. **The committed set's derivation.** The cut computes it one way and `verify` derives it another; I claim they are the same set.
   - The cut (`CallGates.w_out`, `call_committed`): a computing gate g of unit [lo, hi) is committed when `last[g] >= hi`. `last[g]`
     is g's last local reader, or `n` when the Call returns g.
   - `verify` (`check_call_cut`): it rebuilds the boundary from the reads alone (`G.reads`, distinct per consumer): gates read by a
     gate of another unit, plus `G.outputs`. It holds that set to `validate_unit_cut`'s invariant with recomputes "report",
     constants as structure and the read parameter leaves as the input unit's commits. It adds `unit-too-wide` when a unit's
     boundary exceeds X.
   - My argument that the two agree: units are disjoint intervals in a topological layout, every computing gate is in exactly one
     unit, and a non-computing gate reads nothing. So a reader after `hi` is a computing gate of another unit, and a reader inside
     `[lo, hi)` is the same unit.
   - Coverage is by construction: children tile their parent's span. `evaluate_call` does not assert it; its `owner` starts at
     0. I checked it on `F32Add_v3`, `SiluMul_v3{I=8}`, `AttnBlockSoftcap_v3{NVIS=1,…}` and `AttnBlock_v5`, with 0 gates uncovered
     or covered twice. Say if you want the assertion in the reference.
   - Also check: pass-through outputs (a returned leaf that resolves to a parameter or a constant) commit nothing, and an unread
     parameter leaf is not committed (the `read` line in `check_call_cut`).
2. **The recompute report.**
   - Keys are (primitive id, operand tokens). A parameter leaf's token is `("i", leaf)`, a constant's `("c", primitive id)`, and a
     computing gate's is its first occurrence's.
   - Pairs across units go to `detail["recomputed_across"]` and never become a code. Pairs within a unit are `redundant_gates`.
   - Is it a sound partition for sampled proofs on the same argument as v2 (each copy is its own gate, certified once from its
     unit's committed inputs, never committed)?
   - Is "equal constants are equal operands" right for the report? It makes two units that each read `Const1[0x0]` and compute
     the same thing from it a reported pair. On the attention blocks most of the report is constant-derived gates (30,727 of
     32,438 on the softcap block) or sibling Calls reading one operand (each of 15 QK dots recomputes 1,776 gates of the first that
     are computed from Q alone).

**The vectors:** `packages/verity/tests/ir/qcall_vectors.json`, with its writer and tests in `test_qcall_vectors.py`. They have one
case per rule and refusal on a word and a Boolean program, and dump per-gate owners and committed sets at each program's first X.

**When:** now. Grant or object with a label on the PR head (`pr:<n>@213f4361b`) once proofs posts the number, or on the branch
head before that.
