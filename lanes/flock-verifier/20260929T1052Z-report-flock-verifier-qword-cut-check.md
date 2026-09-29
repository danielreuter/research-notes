---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

id: 20260929T1052Z-report-flock-verifier-qword-cut-check · lane: flock-verifier · kind: report · status: current ·
repo: danielreuter/verity · origin: #176 (`cursor/flock-verifier-cut-check-7ab3`), moved out of
`backends/flock/verifier/PROTOCOL.md` §16.7 and §16.10 for its 128 KB cap

# The Lean verifier's cut check and `Q_word` v1 over the verifier's own program: the full text and the evidence

PROTOCOL.md §16.7 keeps the normative summary; the reference is core's `verity.ir.cut` and `verity.ir.partition_object`
(#111, #120). This is the text #176 carried, as it was at `4a080b22`.

## §16.7

**One Call's cut against its graph** (`Partition.checkCut`, `flock-verify cut-check`; reference `verity.ir.cut.check_cut`,
PR #111). The graph is the Call's computing gates: declared widths `w`, the reads between them, the returned gates, the
Call's parameters and the gates that read them, the parameters returned as they are, the total and structure counts, and
the recomputed pairs. The cut is a unit per computing gate (`owner-length` if not one per gate). The invariant runs with
the parameters as the input unit and, unless served values are given, the committed set derived from the cut: a value is
committed exactly when another unit reads it or the Call returns it. Then the width rule (`Q_word_v1{X, W, EXTRAS}`,
today `(16, 32, 0)`): for each unit `u`, with `ob` the summed `w` of its boundary gates (another unit reads them, or the
Call returns them) and `og` their number, `u` passes when `ob ≤ X + EXTRAS`, or `og = 1` and `ob ≤ W + EXTRAS`; else
`unit-too-wide`, with `(u, ob, og)`. `cut_check_agree.py` checks codes and too-wide units against the reference on random
graphs (7000 agree).

**`Q_word` v1, the partition query** (`Flock.Qword`, `flock-verify evaluate`; reference `verity.ir.cut` and
`verity.ir.partition_object`, #111), over each Call's graph:
- **The flat cut** (`cutWord`). The returned computing gates, first occurrence in return order, are packed greedily into
  runs of at most `X` declared bits (a wider gate is a run alone); each run is an output unit and heads its gates. Then,
  repeatedly: every gate starts at its head's unit or −1, and backward each gate without a head takes the unit its consumers
  agree on (−2 when two differ). The producers of edges from a −2 gate into a unit, ascending, become committed units. If
  there are none, each gate still at −1 joins the one live unit its unheaded producers are all in, and every gate still at
  −1 heads its own dead unit. The producers of edges across units that head nothing, ascending, then become committed units
  (the dead units are dropped and the pass repeats); if there are none, the cut is final. Units are numbered as created:
  outputs, committed in promotion order, dead last.
- **A Definition's cut.** A primitive is one unit, or none when it is structure (no parameters, or wiring). A separable body
  is its nodes' members' cuts, in node then member order. Any other body is the flat cut of its graph.
- **The Program's units.** By Call (the root body's non-Input nodes in order), then within the Call's cut. `locate` maps a
  unit to its Call, its unit within the Call's cut, and its path `(node, member, unit)` through separable cuts.

`qword_agree.py` checks these against core's objects on random graphs, Definition trees and Programs (3500 agree), and on
#111's pinned vector (owners, units, committed sets, population, `locate`).

**Over the verifier's own copy of the program** (`Flock.Program`, `Flock.Extract`, `flock-verify qword-program`):
- **Decoding.** The program is decoded from its `verity-ir/descriptor/v1` bytes by #120's rules: the canonical JSON domain,
  types, reference sequences and aliases, the decoder's refusals, the layout and scope resolution.
  - Primitives are taken as the descriptor declares them, since the verifier evaluates none. An `Input<w>_v1` must declare
    no parameters and `Value<w>`.
- **Applicability.** A program that is not topological is no computation, so every query is inapplicable to it
  (`Prog.orderViolation`, core's `order_violation`). Its first reference that names neither a parameter nor an earlier node
  refuses it, walking the bodies breadth-first from the root, callees in node order. A root `batch` or `scan` node is
  inapplicable too.
- **Each Call's graph** is built as core's `CallGraph` builds it:
  - a primitive Call as one gate reading its parameters;
  - operands resolved in layout order, a gate reading itself or a later gate refused;
  - wide gates (more than 4096 operands) external, listing only their operands inside the Call;
  - constants, wiring, and values computed from constants alone as structure;
  - recompute tokens exact: an input by its identity, a structure value by its key, a computing value by its first gate,
    a wide gate by itself;
  - reads through structure, and the returned values.
- **Evaluation.** Separable bodies and the memo by Definition feed the cut above.
- **Each Call's cut** (`Extract.checkCalls`, `qword-program [X [W]] --cuts`). As `partition_object.verify` runs `check_cut`,
  each Definition's cut is checked once, on its Call's whole graph (a separable Call's too, since two members can compute
  one value), with the derived committed set:
  - **the partition invariant:** every computing gate in exactly one unit, and no value computed in two units
    (`gate-recomputed`). With the derived committed set, the invariant's other clauses hold by construction;
  - **the width rule `(X, W, 0)`:** each unit's boundary is at most `X` bits, or one value of at most `W` bits
    (`unit-too-wide`, with the unit, its bits and its values).
  - The check's graph has no input table. With the derived committed set, the Call's parameters (input gates) fail no
    clause: every read of one and every returned one is committed, and their count cancels from the gate count.
  - The recompute table is held by each key's hash, and a gate matches an earlier one only when their keys are equal, so
    the tokens stay exact. #101's LM-head `Gemm` (16.5M gates) is checked in 100 s at 9 GB; all of #101 in 152 s.
- **`qword_program_agree.py`** checks all of it against core's `decode_program` and `partition_object.evaluate`:
  - #111's pinned vector, every field of every Call's graph, owners, units and committed set, and `locate`;
  - #120's format vectors: the wide-gate graph, the forward references (both refusals' details), and all 31 decoder
    refusals refused;
  - #111's `qword_vectors.json`: all 8 evaluations (population, owners digest, and each Call's graph, owners, kinds,
    units and committed set), the 3 order refusals' details, and the root batch and scan refused;
  - each Call's cut against core's `verify`: `qword_vectors.json`'s 3 pinned cut refusals, and its 10 programs at 5
    `(X, W)` (the failing Calls, their codes and too-wide units), 19 of the 50 refused for their cuts;
  - #101's cuts (`--cuts`) against core's `check_cut` at `X = 16`, `W = 32` and `16`, per Definition: the codes, the
    too-wide units, and the graph's computing gates, recomputed pairs, committed set, widest boundary and boundary gates.
    - All 16 Definitions agree. At `W = 16`, `Attention`, `GumbelTopPTokenSelect` and both RMSNorms fail the width rule,
      with the same units.
    - The three largest `Gemm`s (1.05M, 2.1M and 16.5M gates) exceed 15 GB in core, so core checked them on a 256 GB pod
      (run `r20260927-201750-7e04`). The LM-head took 35 min and 208 GB in core; Lean takes 100 s and 9 GB;
  - a real #101 descriptor (the Llama-3.2-1B step Build, `art:a4ea1a18`): all 167 Calls' units, and every Definition's
    owners and flat graph by SHA-512, in 14.5 s.

Still ahead: the leaf positions.

## §16.10: the partition finding

- **The partition finding.** Every verdict of such a statement carries `partition = {rule, query, digest, units, note}`.
  `units` is `derived` when the verifier derived the statement's units itself, given `--program`:
  - **the template queries,** as above;
  - **`Q_word` v1** (`Flock.Extract`, `Flock.Qword`, §16.7):
    - the program must be the object's;
    - the query must apply: every Call is a `call` or `primitive` node, and the layout is topological;
    - every unit the header's `units.indices` claims must lie in the population and be one whole activation of the circuit's
      template. That is, the innermost Definition on its `locate` path is the template, and the template's cut is exactly
      one unit, so the instance proves the unit's computation.
    - every Call's cut must hold the partition invariant and the width rule on its whole graph (`Extract.checkCalls`,
      §16.7), as core's `verify` requires. A failing cut refuses the partition, naming the Call and its codes.
    - Set 10's object is over the RoPE subcircuit's own program (`57fab977`), whose root batches primitives. `Q_word` v1
      doesn't apply to it, and the verifier refuses it with `--program`, as core's `evaluate` does.
  - Any other query is not evaluated. Then, and without `--program`, `units` is `as stated`, with the reason in `note`, and
    an audit reports it as a gap, not a complete check.
