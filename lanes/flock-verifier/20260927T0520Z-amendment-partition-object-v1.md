---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-verifier · kind: handoff · from: vllm-cross-call-check (partition checker owner) · updated: 2026-09-27T06:05Z

# Amended §2 of `20260927T0445Z-draft-partition-checks-spec.md`: `verity/partition/v1` names a query, P = Q(C) (PR #111)

This amends §2 of that note; the note itself is unedited, since it is another agent's. Daniel decided at 05:28Z that the partition is a named query on the program, which the verifier evaluates itself. This replaces the 05:20Z "cuts table" text.

~~~text
{"format": "verity/partition/v1",
 "program": "<SHA-512 of the program>",
 "query": {"name": "Q_word", "version": 1, "params": {"X": 16, "W": 32}}}
~~~

- **Digest:** `SHA-512("verity/partition/v1\0" ‖ canon(object))`, where canon is `verity.ir.codec.canonical_json`. The object is 236 bytes. No owners, cuts or units are stored.
- **Program:** SHA-512 over the canonical descriptor (`codec.canonical_json(codec.encode_program(program))` with `annotations` removed; schema `verity-ir/descriptor/v1`). These bytes are the evaluator's input.
- **The evaluator:** `verity.ir.partition_object.evaluate(program, query)`, with the algorithm written out in `verity.ir.cut`'s module docstring. In short:
  1. **Calls** are the root body's non-Input nodes, in order. Each Call is its Definition's activation in a one-Call Program whose parameters are inputs.
  2. **Evaluate(fn):**
     - a primitive is one unit, or none when it is structure (no parameters, or its id is in `WIRING`);
     - a separable body is its members' cuts, in node then member order;
     - any other body is `cut_word(CallGraph(fn), X)`.
  3. **`CallGraph`:**
     - removes structure (constants, values computed from constants, `WIRING`) and re-points reads through it;
     - treats gates with more than `WIDE_FAN_IN` operands as wide;
     - detects recomputes with **exact interned structural ids** (no hashes);
     - records outputs and returned inputs.
  4. **`cut_word`:** returned gates are packed into output units of at most X bits. A backward pass assigns owners; conflicting producers become committed units; dead gates join their producer's unit or head their own. Units are numbered as created.
  5. **Units** are numbered by Call, then within the Call's cut. `Partition.locate(i)` bisects the Calls' prefix sums, then descends through a separable cut.
  6. **The committed set is derived:** a value is committed exactly when a unit other than its producer's reads it, or it is returned.
- **`verify(obj, program, served=None)`:** runs `validate`, checks the program digest, evaluates, and per Definition applies `check_cut`:
  - the invariant, via `partition.validate_unit_cut`;
  - the width rule in bits (ob ≤ X, or og = 1 and ob ≤ W), code `unit-too-wide`;
  - `served` is held to the derived set (`committed-unread`, `read-uncommitted`, `output-uncommitted`).
- **`validate`:** exactly `format`, `program`, `query`; the query a known (name, version) with exactly its parameters, each a positive int.
- **Versioning:** any change to the query's behaviour bumps its version.
- **Pinned vector:** `packages/verity/tests/ir/partition_vectors.json`, checked by `test_the_pinned_vector_bytes_in_graph_and_partition_out`.
  - It holds a six-Call program's descriptor bytes: wiring, a two-unit output, a same-unit recompute, a separable batch, constants, and a committed interior value with a dead gate.
  - For each Call it gives the graph (`total`, `structure`, `n`, `keep`, `width`, `prim`, `src`, `dst`, `input_reads`, `outputs`, `returned_inputs`, `recomputed`), then `owner`, `units` and `committed`.
  - It also gives the object and its digest `0eb7a6d3…`, the owners digest `555cd351…` (`SHA-512("verity/partition/v1/owners\0" ‖ canon([[call, owner], …]))`), and `locate` for every unit.
  - The test decodes the bytes alone (`codec.decode_program`) and checks every field.
- **Scale:** evaluation time and peak memory with core's stdlib evaluator on one CPU, against the program's serialized size (its instance sequence).
  - #101: 333 distinct specializations in 41.5 s (1.3 GB peak), giving 273,995,039 units, equal to the program graph's count. The program is 41.6 MB of instance JSON (1.6 MB gzipped, r19 Build).
  - #74's largest request Program: 1,167 distinct specializations in 664 s (1.3 GB peak), giving 5.44 G units. The program is 1.84 GB of instance JSON (121 MB gzipped).
  - Most of the time goes to one flat attention-head cut per T.

**Not yet specified tightly enough to port** (the codec and layout are defined by code, not a written spec):

1. **Descriptor schema v1.** `codec.py` cites `docs/vllm-poc/descriptor-codec.md`, which isn't in the repo. The v1 features are defined only by code:
   - the interned `callees` and `types` tables;
   - the `{"alias": [k, a]}` reference-sequence alias;
   - flat concatenation splicing.
2. **Canonical JSON.** It is Python `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=True)`, with no written rules for escaping, number form (ints only) or key order (code-point order). The codec's own docstring says it isn't a frozen external spec. Lean hashing the exact bytes it receives is safe; re-serializing isn't, until this is written down.
3. **Reference sequences.** The JSON forms (`affine`, `strided`, `explicit`, `concat`), `Strided`'s zero-stride broadcast, and `refs.runs` / `intervals` (used by `separable`) exist only in `refs.py` and `intervals.py`.
4. **Canonical layout.** Defined only in `layout.py`:
   - gate numbering of the root: Input nodes first, then the program function inlined into the root by `program._lower_root`;
   - `body.offsets`;
   - batch member layout, and one gate per primitive member;
   - scan node layout;
   - `resolve` of `("p", …)` refs through scopes and of `("n", k, leaf)` through a callee's returned refs, including parameter pass-through.
5. **Input nodes.** They are recognised by the decoded primitive's `family == "Input"`, which comes from the registry, not the descriptor. Lean needs the rule: ids `Input<w>_v1`.
6. **`WIDE_FAN_IN = 4096` and `_wide_operands`.** A layout constant plus a performance special case changes the graph: a wide gate's outside operands aren't listed and it never matches a recompute. It is pinned in Q_word v1, but it should go when the query is next revised (v2).
7. **`WIRING`** is a pinned id list: `Bf16ToF32_v1`, `F32BitsShl23_v1`, `F32Fabs_v1`. Its bit-rearrangement property is checked by a vLLM test on the registry, not derivable from the descriptor.
8. **`n_members` and `axes`** for batch and scan nodes (`parts.n_members`).
