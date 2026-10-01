---
id: 20261001T2034Z-draft-from-proofs-ir-qcall-pr-body-213f4361b
campaign: verity
lane: proofs
kind: draft
status: open
repo: danielreuter/verity
origin: proofs-ir (bc-6cd83494)
---

# Draft PR body for `cursor/proofs-qcall-95d4` at `213f4361b` (base `main`)

to: proofs (bc-8416bc72). From proofs-ir. I can't open the PR from this VM: `gh` is read-only and I have no PR tool. Please
open it with base `main` and the title and body below. The branch is pushed, and `main` (`e221350fd`) has not moved past it.
`check --record` is `r20261001-203205-c3c1` on vy-nebius-1, launched 1:32 PM PDT. I'll post its verdict as a checkpoint.
Everything under the rule is the body.

**Title:** verity.ir: `Q_call` v1, the partition query cut along Calls with at most 32 bits out of a proof unit

---

Adds `Q_call` v1 (`{"name": "Q_call", "version": 1, "params": {"X": 32}}`), the partition query Daniel agreed on at 12:25 PM
PDT (brief: `note:proofs-ir/20261001T1931Z-handoff-from-proofs-qcall-partition-query`).
- A proof unit has at most X = 32 output bits and unbounded inputs.
- The cut runs along Calls: a Call that fits is one unit; otherwise it is cut into its body nodes, then a call node into its
  callee's body, and a batch or scan into its members or iterations.
- Program inputs and constants are in no unit. Every other gate is in exactly one.
- A recompute across units is reported, never refused.

`Q_word` v1 and v2 are unchanged: their vectors, digests and verdicts are byte-identical, and no recorded partition object
changes.

## What's in it

- **Spec:** `verity/ir/PROTOCOL.md` §11, a delta on §8 and §10.
- **Reference** (`verity.ir`):
  - `cut`: `CallGates`, `call_units`, `evaluate_call`, `call_committed`, `check_call_cut`, with the algorithm in its docstring;
  - `partition_object`: `Q_CALL`, `call_query`, `CallPartition`; `evaluate`, `locate` and `verify` dispatch on it, and
    `verify` reports `recomputed_across` as under `Q_word` v2.
- **Vectors:** `tests/ir/qcall_vectors.json` (178 KB) and its writer `test_qcall_vectors.py --write`.
  - A word program and a Boolean program, each at two values of X.
  - One case per rule and per refusal (§11's last paragraph lists them).
  - Every served-commit check, and the malformed objects `validate` refuses.
- **circuit-check:** every Definition records `q_call`: units, committed gates and bits, `recomputed_across`, redundant gates
  and codes, or `inapplicable`.
  - A refusal is a warning (`partition/q-call-inapplicable`).
  - A code from Q_call's own verify fails the check (`partition/q-call-<code>`).
  - The log line shows `q_call=Nu/Bb`, for example `ok definition F32Add_v3 failures=0 warnings=0 q_call=1u/32b` and
    `ok definition SiluMul_v3{I=8} failures=0 warnings=0 q_call=8u/128b`.
- **The README Glossary:** Port, Element, Partition, Proof unit and Instrumented program (before and after below).
- **Not in this PR:** the Lean verifier's partition check. It still refuses an unknown query version, which is right until a
  follow-up ports it with lean-agreement.
  - The port is small, about 200 lines in a new `Flock/Qcall.lean`: the interval recursion over the layout, a per-gate walk that
    reuses `Extract`'s operands without the folding or wiring rules, dispatch, and the existing `Partition.validate` invariant.
  - Its agreement check is against `qcall_vectors.json`.

## Rules the IR left open, pinned in §11

- **A pass-through output** resolves to a parameter of the Call or to a constant, not to a computing gate. It is no output of any
  unit: the value is the Call's input or the program's literal.
- **A scan's carry** follows from the reads. An iteration's returned carry is an output of that iteration when the next iteration
  reads it, and of the Call when it is the final carry. A carry passed through unchanged resolves to the scan's `init`, so it
  is a pass-through.
- **A call node with no computing gates** (it only rearranges parameters or returns constants) is no unit.
- **A unit with no outputs** (a dead gate) is still a unit, since every computing gate is in exactly one.
- **An unread parameter leaf** is in the input unit and is not committed.
- **A root `batch` or `scan`** is refused (`why: "root-form"`), as §8 refuses it; a root Call must be a `call` or `primitive` node.
- **Inputs and constants of any width** are allowed. The width rule applies only to computing gates.
- **Recompute keys:** a parameter leaf's token is `("i", leaf)` and a constant's is `("c", primitive id)`, so equal constants are
  equal operands. Units are numbered by Call, then in layout order. Served commits are numbered by the Call's computing gates in
  layout order.

## Refusals

`Q_call` refuses a program, with `QueryInapplicable`, in three cases:
- `gate-too-wide`: a computing gate wider than X. The detail names the Call, Definition, local gate, primitive, width and X.
- `root-form`: a root `batch` or `scan`.
- §8's other applicability refusals (not topological).

**No standard program is refused.** None of the Calls measured below has a gate wider than 32 bits.

## Measurements

All figures are on this head. `Q_word` v1 is `{X: 16, W: 32}`, v2 is v1's cut, and Q_call is `{X: 32}`.
- *Bits* are committed bits.
- *Recomputed across* counts the gate pairs computing the same value in two units, as `verify`'s `detail["recomputed_across"]`
  reports them.
- *Constant-derived* gates are computing gates computed from constants alone.

| Call | Gates | `Q_word` v1 units / bits | v1 verdict | v2 recomputed across | **Q_call units / bits** | Q_call recomputed across (constant-derived + other) | Constant-derived gates |
|---|---|---|---|---|---|---|---|
| `F32Add_v3` | 2,322 | 547 / 577 | passes | 0 | **1 / 32** | 0 | 0 |
| `DotBf16_v3{K=64,DOT=HopperBF16WgmmaDot16_v2}` | 94,729 | 31,346 / 31,376 | `gate-recomputed` | 110 | **1 / 32** | 0 | 256 |
| `GemmCoordinate_v3{K=64,DOT=HopperBF16WgmmaDot16_v2}` | 94,908 | 1 / 16 | passes | 0 | **1 / 16** | 0 | 256 |
| `Gemm_v3{K=32,N=3,DOT=HopperBF16WgmmaDot16_v2}` | 142,632 | 3 / 48 | `gate-recomputed` | 7,104 | **3 / 48** | 7,616 (512 + 7,104) | 768 |
| `SiluMul_v3{I=8}` | 68,544 | 8 / 128 | passes | 0 | **8 / 128** | 0 | 0 |
| `AttnBlockSoftcap_v3{D=16,NVIS=1,FIRST=True,BN=16,CAP=50.0,DOT=HopperBF16WgmmaDot16_v2,CHECK=True,TANH=MufuTanh_v2,EX2=MufuEx2Ftz_v2}` (as `pins.json` binds it) | 442,404 | 137,848 / 138,387 | `gate-recomputed` | 29,407 | **24 / 751** | 32,438 (30,727 + 1,711) | 31,777 |
| `AttnBlockSoftcap_v3{…,NVIS=16,FIRST=False,…}` | 1,507,583 | 473,107 / 473,737 | `gate-recomputed` | 83,939 | **165 / 5,007** | 77,913 (14,062 + 63,851) | 14,962 |
| Boolean attention block `AttnBlock_v8{D=16,NVIS=16,FIRST=False,BN=16,DOT=HopperBF16WgmmaDot16_v2,CHECK=True}` | 1,286,559 | 400,387 / 401,017 | `gate-recomputed` | 67,585 | **133 / 3,983** | 76,009 (12,238 + 63,771) | 13,026 |
| Word attention block `AttnBlock_v5{same,DOT=HopperBF16WgmmaDot16_v1}` | 150 | 72 / 2,048 | passes | 0 | **133 / 4,000** | 0 | 0 |
| Word softcap block `AttnBlockSoftcap_v2{NVIS=1,…,DOT=HopperBF16WgmmaDot16_v1}` | 47 | 19 / 592 | passes | 0 | **24 / 752** | 0 | 0 |

Every Q_call row verifies (`verify` ok, no codes).

- **Constant-derived gates add no committed bits** in any Call. They add recomputes instead: each unit that reads a
  constant-derived value computes it again. That is 30,727 of the softcap block's 32,438, mostly the 16 PV wgmma members each
  recomputing about 1,771 gates of the QK `DotBf16` node. Folding them into literals in the program removes those recomputes,
  and needs no query rule.
- **Former wiring gates add no committed bits.** None of these Calls has a wiring gate.
- **No gate is wider than 32 bits** in any of them.
- **Recomputes that are not constant-derived** (`AttnBlock_v8`'s 63,771) come mostly from sibling Calls reading one operand. The
  16 QK `DotBf16_v3{K=16}` nodes all read Q, and each of nodes 1–15 recomputes 1,776 gates of node 0 that are computed from Q
  alone (26,640 in all). The remaining 37,131 are spread over 145 other node pairs. `Q_word` v2 reports the same kind of pairs
  (67,585).

### The attention block against the word Program's 72

**Under `Q_call` the Boolean block and the word block cut identically:** 133 units for `AttnBlock_v8` and `AttnBlock_v5`, and 24
for the two softcap blocks. The Boolean block has 17 fewer committed bits (3,983 against 4,000) because each of its 17
`MufuEx2Ftz_v2` Calls has a 31-bit output: the sign bit is a constant 0, a pass-through, so it is not committed. The softcap
block's one bit (751 against 752) is the same.

**It is 133, not 72, because of the model, not a bug.** `Q_word` v1 merges a gate into its only consumer's unit, so the word
Program's 150 gates come out as 72 units. `Q_call` has no merge step: a Call that doesn't fit is cut into its body's nodes, and
each node that fits is one unit. The block's body has 120 nodes (16 QK dots, row maxima, exponentials, sums, conversions, PV
dots), and most become units. Getting near 72 would need a merge rule, such as merging a node into its only reader while the
result still fits X. That is a change to the agreed model, so it is not in this PR.

The brief's 440,027 `Q_word` v1 units for the Boolean block were measured on the older `_v2` definitions; its `DotBf16_v2{K=64}`
row likewise reads 32,634, against 31,346 for `_v3` here.

## Glossary, before and after (README)

- **Port.**
  - Before: "a named array of fixed-width elements on the boundary of a circuit definition; each call binds it to gates of the
    caller."
  - After: "a named array of fixed-width elements on the boundary of a circuit definition, one of its parameters or results; each
    call binds it to gates of the caller. A Call's result ports are the first place a partition tries to cut: under `Q_call` a
    Call whose results fit in X bits is one proof unit."
- **Element.**
  - Before: "one fixed-width member of a port, such as 16 bits. A format labels elements, a leaf serializes whole elements, and no
    proof unit splits one."
  - After: "one fixed-width member of a port, such as 16 bits. A format labels elements, and a leaf serializes whole elements. A
    partition does not read elements: a proof unit's boundary is counted in bits, so a unit may commit some of an element's bits
    and not others. The rule that bounds a unit is its output width (see Proof unit)."
- **Partition.**
  - Before: "a division of a program's gates into proof units, each gate in exactly one (`verity/partition/v1`,
    `verity.ir.partition_object`). It is a named query on the program: the object holds the program's digest and the query's
    name, version and parameters, such as `Q_word` v1 `{X: 16, W: 32}`, and a verifier evaluates the query itself. The committed
    set, every gate read across a unit boundary plus the program's outputs, follows from the partition and is never stored."
  - After: "a division of a program's computed gates into proof units, each in exactly one (`verity/partition/v1`,
    `verity.ir.partition_object`). A gate with no inputs, a program input or a constant, is in no unit: the input commitment
    certifies inputs, and a unit reads a constant's value from the program (`Q_word` also leaves out its structure: wiring, and
    gates computed from constants alone). It is a named query on the program: the object holds the program's digest and the
    query's name, version and parameters, such as `Q_call` v1 `{X: 32}`, which cuts each Call down its hierarchy until every
    unit has at most 32 output bits, or `Q_word` v1 `{X: 16, W: 32}`. A verifier evaluates the query itself. The committed set,
    every gate read across a unit boundary plus every value a Call returns, follows from the partition and is never stored."
- **Proof unit.**
  - Before: "one part of a partition, proved on its own. A unit is incorrect when its committed outputs differ from its gates
    applied to its committed inputs. An audit's verifier draws the proof units to prove."
  - After: "one part of a partition, proved on its own: a set of gates S whose inputs in(S) and outputs out(S)
    (`verity.ir.parts`) are ordered bit strings, counted in bits at any gate width. Under `Q_call` its outputs are at most X = 32
    bits and its inputs are unbounded. A unit is incorrect when its committed outputs differ from its gates applied to its
    committed inputs. An audit's verifier draws the proof units to prove."
- **Instrumented program.** "a tap on every committed element" becomes "a tap on every committed gate".

"No proof unit splits an element" is replaced by: a partition counts bits, not elements, and the one rule is the output width.

## Tests

- `packages/verity/tests/ir`: 282 passed, including the 14 new `test_qcall_vectors.py` tests.
- `tools/circuit_check`: `test_q_call_is_recorded_per_call_and_refuses_a_gate_wider_than_32_bits` and its neighbours pass.
- `check --record`: `r20261001-203205-c3c1` (verdict to follow).
- Review: red-team-proofs-554 is asked to read the committed set's derivation and the recompute report
  (`note:red-team-proofs-554/20261001T2034Z-ask-from-proofs-ir-review-qcall`).
- No lean-agreement is needed: nothing under `backends/flock/` changes.
