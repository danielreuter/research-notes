---
id: 20261001T1931Z-handoff-from-proofs-qcall-partition-query
campaign: verity
lane: proofs-ir
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Build `Q_call` v1: proof units of at most 32 bits out, cut along Calls (Daniel's go, 12:25 PM PDT)

to: proofs-ir (bc-6cd83494-c180-583c-83f9-ef70e4b3f19b). From proofs. Daniel agreed this model with proofs in chat
between 11:22 and 11:52 AM PDT, and said "go on all of the above" at 12:25 PM PDT. It replaces item 7 of
`docs/boolean-native-simplifications.md` (the element cut) in proofs' store, whose §7 now opens with the ruling.

## The model

1. **A proof unit** is a subcircuit with an ordered input and output bit string: in(S) and out(S) as `verity.ir.parts`
   defines them, counted in bits at any gate width (a `Value<32>` word gate is 32 bits, a Boolean gate 1). **The one
   rule:** w_out(S) ≤ X = 32 bits. Inputs are unbounded, so there is no fan-in rule, and v1's wide-gate convention
   (`cut.WIDE_FAN_IN`, `PROTOCOL.md` §8) goes.
2. **The verifier derives the partition** from the program and X alone.
3. **The cut runs along Calls.** Each root Call (a non-Input root node, §5.2) is one unit if its outputs fit. Otherwise its
   body's nodes are the pieces. Each piece is one unit if its outputs fit, and is otherwise cut the same way: a call node
   into its callee's body, a batch into its members, a scan into its iterations.
4. **A gate with no inputs is an input.** Program inputs and constants are in no unit and never committed; the verifier
   reads a constant's value from the program. Every other gate is in exactly one unit. So the `WIRING` list goes, and gates
   computed only from constants (structure today) are proven like any other gate.
5. **No wide gates for now:** a primitive gate whose own output exceeds X bits makes the query inapplicable, with a named
   code. Nothing more.

Also agreed:
- No convexity check: a node's gates are convex in a topological body.
- The width is the only rule. A value computed in two units is reported as `Q_word` v2 reports it (`recomputed_across`),
  never refused, and v2's caveat carries over: a consumer that credits distinct work (PoUW) reads that report.
- It's a new query version. v1 and v2 stay pinned, and no recorded partition object changes.

## What to build

Branch `cursor/proofs-qcall-95d4` from origin/main.

- **Spec:** `verity/ir/PROTOCOL.md` §11, every rule above pinned, written as a delta on §8 and §10. Where the IR leaves a
  rule open (a scan's carry, a pass-through output), take the simplest reading, pin it, and list it in the PR body.
- **Reference:** in `verity.ir` (`cut`, `partition_object.QUERIES`, `verify`'s codes), with the algorithm in its docstring.
- **Vectors:** `tests/ir/qcall_vectors.json`, one case per rule and per refusal, on a word and a Boolean program. Cover:
  - a Call that fits, one that splits into sub-Calls, a batch, a scan, and a pass-through output;
  - a constant read by two units, and a constant-derived gate read across units (committed now);
  - a gate wider than 32 bits, and a recompute across units, reported.
- **circuit-check:** evaluate the new query per Call: units, committed bits and refusals.
- **The Glossary**, in the same PR and rolled out (AGENTS.md: a changed term is updated and rolled out in one change).
  - The entries are README lines 170–189: Port, Element, Partition, Proof unit, and Instrumented program's "a tap on every
    committed element".
  - "No proof unit splits an element" no longer holds; say what replaces it.
  - Put the before and after in the PR body. Daniel reads it.
- **Your `docs/boolean-ir.md`:** correct its "Partition checker" paragraph to point at the new query. Its "`Q_word` v1
  applies unchanged" is wrong for Calls wider than 16 bits.
- **Not in this PR:** the Lean verifier's partition check (`backends/flock/verifier/lean/Flock/Partition.lean`). It refuses
  an unknown query version, which is right until a follow-up ports it with lean-agreement. Say in the PR if the port is
  small.

## Measure, in the PR body

For each Call below, give units and committed bits under `Q_word` v1 `{X: 16, W: 32}`, v2 and the new query:
- `F32Add_v3`, `DotBf16_v3{K=64,DOT=HopperBF16WgmmaDot16_v2}`, `GemmCoordinate_v3{K=64}`, `Gemm_v3{K=32,N=3}`,
  `SiluMul_v3{I=8}`, and `AttnBlockSoftcap_v3` as `pins.json` binds it;
- circuits' Boolean attention block (440,027 units under v1, against the word Program's 72).

For each Call, also say how many committed bits come from constant-derived gates and from former wiring gates, and list
any gate wider than 32 bits. If constant-derived gates add committed bits, the remedy is to fold them into literals in the
program, not a new query rule: give the count.

proofs' counts at X = 32 under today's cut (`verity_vllm.query.word.unit_rule`, W = 32, on `e221350fd`):

| Call | Units | Literal constants | Constant-derived gates |
|---|---|---|---|
| `F32Add_v3` | 1 | 0 | |
| `DotBf16_v3{K=64}` | 1 | 1 | 256 of 94,729 |
| `GemmCoordinate_v3{K=64}` | 1 | | |
| `Gemm_v3{K=32,N=3}` | 3 | | |
| `SiluMul_v3{I=8}` | 8 | | |
| `AttnBlockSoftcap_v3{D=16,NVIS=1,FIRST=True,…}` | 118,147 | 4 | 31,777 of 442,404 |

A blank cell wasn't counted. The attention block shatters today because the cut promotes shared bits one at a time. Under the new query it should come
out near the word Program's count; if it doesn't, say why.

## Review and landing

- red-team-proofs-554 reads the diff: the committed set's derivation and the recompute report. Ask in its lane.
- A PR with a passing `check --record`, then the PR captain. Nothing under `backends/flock/` changes, so no lean-agreement.
- One checkpoint line when the spec and vectors are pushed, one at the PR, and one at the check.
- **Tell me** with a `needs-proofs:` line in `lanes/proofs/` if a standard program is refused, or if the counts look wrong.
