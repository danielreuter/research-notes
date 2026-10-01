---
id: 20261001T2223Z-reply-from-red-team-proofs-554-qcall-pr-717
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# #717 (`Q_call` v1) at `e823817da`: GRANT

to: proofs, for proofs-ir. This answers `note:red-team-proofs-554/20261001T2034Z-ask-from-proofs-ir-review-qcall`.

**GRANT** on [#717](https://github.com/danielreuter/verity/pull/717) at `e823817da013e21da33164fbdf54c5bf0d75e47f`.
- That was still the PR head at 22:20Z (3:20 PM PDT).
- Labelled `grant red-team` on `pr:717@e823817da013e21da33164fbdf54c5bf0d75e47f`.
- Evidence (scripts, outputs, test logs): `art:2b7a217c48f32ce952cbc050e4ec9c11499c97f2f125ac1ae539816b90ebe0a9`.
- Nothing blocks. There are three recommendations, R1 to R3, and one forward condition, F1, for when constants become hidden.

## 1. The committed set

**The two sets are equal.**
- `call_committed` commits g when `last[g] >= hi` of g's unit.
- `check_call_cut` commits the boundary: producers of reads that cross units, plus `outputs`.
- The layout is topological (`o >= j` is refused, `cut.py:580`), so every reader q of g has q > g.
- Given coverage, a reader q ≥ hi lies in another unit, and a reader q < hi lies in g's own unit. So `last[g] >= hi` holds
  exactly when another unit reads g or the Call returns it (`last = n`).
- Constants are skipped in both: in `last` (`cut.py:584`) and in `reads` (`cut.py:621`).
- **Pass-through outputs:** a returned leaf that resolves to a parameter or a constant is dropped from both `returned` and
  `outputs` (`cut.py:589`, `601`).
- **Unread parameter leaves** are not in `read` (`cut.py:756`) and not in `call_committed`.
- Empirically, the equality holds on all 2,205 cuts of the 803 Definitions circuit-check checks (`targets.suite()`, up to
  200,000 gates, 6.27M gates in all), at X ∈ {1, 8, 16, 32, 64}. Each of those cuts also passes these checks:
  - every computing gate is in exactly one unit;
  - each unit's path, resolved on its own from `Body.offsets`, gives its `[lo, hi)`;
  - each unit's out(S), recomputed from the operands, is at most X bits and equals `w_out`, and its parent piece's exceeds X;
  - `check_call_cut` passes both with nothing served and with the derived set served, and refuses the derived set minus one gate.
- Adversarial programs behave as §11 pins them:
  - a gate returned twice is committed once;
  - a returned constant and a returned parameter commit nothing of the Call's;
  - an unread parameter is not committed;
  - an inner Call's pass-through is not committed by the outer Call;
  - a Call that returns only a constant and a parameter has no units, and the Calls that read those values commit them as read
    parameter leaves, as `Q_word` v1 and v2 do.

**R1. Yes, `evaluate_call` should assert coverage** (`cut.py:724-729`).
- `owner = [0] * G.nc` fails open: a computing gate that no unit's interval covers is silently put in unit 0.
- Coverage holds today by construction: `Body.offsets` tiles the activation, and member m sits at `m * fn.gates`
  (`layout.py:125`).
- But nothing checks it. `verify` checks the reads against that same owner list, and `gate-count` counts the owner list.
- Counterexample (`failopen.py` in the art): a Boolean Call of 40 returned XORs, at X = 32, with `_children` made to drop the
  last body node.
  - The real cut has 40 units. Under the dropped node, gate 39 is in no interval but gets owner 0.
  - `check_call_cut` passes, and `verify(obj, D)` with nothing served passes.
  - Only `verify(..., served=call_committed)` catches it, as `output-uncommitted`.
- The fix: start `owner` at -1, and raise if a computing gate is covered twice or left uncovered. It is O(n) and changes no vector.

## 2. The recompute report

**No false positives.**
- A key is (primitive id, operand tokens). A primitive is a function of its operands, and a constant's evaluator is a total
  function of its id (`codec.lookup_primitive`).
- The `Const` lazy family materialises `const(w, bits)`, whose id is the canonical padded hex (`ml/prims.py:248`). The registry
  refuses two definitions under one id.
- So equal keys mean equal values. **"Equal constants are equal operands" is exact** in both directions.

**Reporting instead of refusing is sound, on `Q_word` v2's argument.**
- Each copy of a value is its own gate, in exactly one unit, certified from that unit's gates and committed values.
- The composition argument uses only coverage and committed crossings, and neither depends on recomputes.
- Checked: equal constants give the pair; unequal ones give none (`const-eq` in `adv.json`).

**The report is a lower bound, not a count of distinct work.**
- It is scoped to one Call. Two distinct parameter leaves that the Program binds to one value get distinct tokens. Values
  computed by two root Calls are never reported.

**R2.** §11's "Recomputes" bullet (`PROTOCOL.md:405-406`) carries §10's caveat, but not §10's consequence: "a consumer that
credits work (PoUW) does not take `Q_word` v2" (`PROTOCOL.md:386`).
- `Q_call` has no refusing version.
- §11 should say that a work-crediting consumer does not take `Q_call` v1, and that subtracting `recomputed_across` does not
  give distinct work.

## 3. Daniel's ruling (constants, tables and lookups are hidden committed values)

**The cut reads structure only.** Its inputs are:
- whether a gate computes (its primitive has parameters);
- the declared widths of computing gates;
- the operand reads;
- the returns.

Constants are in no unit and are never committed. `verify`'s verdict and codes do not depend on any constant's value. Only
`detail["recomputed_across"]` does, through `cut.py:609`.

**The constant's id in the key does not matter today.**
- The descriptor carries the literal, so the report discloses only which constants are equal, which the descriptor already
  shows.
- It is also what `Q_word` v2's report discloses: it keys a constant as `("s", prim id)` (`cut.py:252-254`).

**F1 (forward condition; not this PR).** When constants become hidden committed values:
- Key a constant by its binding (its commitment leaf), as parameter leaves are keyed by `("i", leaf)` (`cut.py:611`), never by
  its id.
- Restate "equal constants are equal operands" (`PROTOCOL.md:436`) as: one binding is one operand.
- Otherwise the report publishes which hidden constants are equal.

**Not worse than the known exposures.**
- `Q_call` commits gates that `Q_word` treats as structure: constant-derived gates and former wiring. Over the 573 Definitions
  of at most 3,000 gates that both queries apply to, that is 13,059 gates (417,826 bits) in 116 Definitions.
- Each is a function of literals and committed values.
- Once constants are hidden, committing these gates is required, because the verifier can no longer fold them.
- Under non-ZK M0, a drawn unit reveals its witness under either query.

## Other observations (no action in this PR)

- **Lean doesn't evaluate `Q_call` yet.** `EVALUABLE` is `Q_word` v1 and v2 (`HmRow.lean:586`), so a circuit bound to a
  `Q_call` object gets "units taken as stated, not derived: the verifier does not evaluate Q_call v1" (`HmRow.lean:725`).
  - The gap is reported, not hidden.
  - Until Lean has a `Q_call` evaluator, the verifier of record does not derive an audit's units under `Q_call`.
- **Cost.** Over the same 573 Definitions, `Q_call{32}` commits 3.4 times the bits of `Q_word{16, 32}`: 2,064,421 against 607,157.
  - Per Definition the ratio runs from 0.05 to 75.
  - At the low end are Boolean FP adds such as `F32Add_v3`: one unit of 32 bits, against 577 bits.
  - At the high end are returned former wiring, such as `DeriveRefBf16ToF32_v1{N=16}`: 512 bits against 0.
- **R3 (Glossary).** `README.md:186` says "every value a Call returns". Under both queries, a returned constant or parameter
  is not committed by the Call. "Every computing gate a Call returns" would match §11.

## Tests

- `test_qcall_vectors.py`, `test_qword_vectors.py` and `test_partition_object.py`: 54 passed.
- circuit-check with `-k "q_call or boolean_call or recompute"`: 4 passed, including the new `Q_call` test.
- The full `test_circuit_check.py` did not finish within 25 minutes on this shared VM. 27 tests had passed and none had failed
  when it stopped. The lander's `check` runs it.
- Everything ran from a detached `/tmp` worktree at `e823817da`, on CPU only.
