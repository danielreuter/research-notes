---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-verifier · kind: handoff · from: vllm-cross-call-check (partition checker owner) · updated: 2026-09-27T06:40Z

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

**The program format is now specified: `packages/verity/src/verity/ir/PROTOCOL.md`** ([PR #120](https://github.com/danielreuter/verity/pull/120), stacked on #111). Every rule has a vector in `tests/ir/format_vectors.json`, checked by `tests/ir/test_format_spec.py`. No digest moves. The earlier gaps, each with where it is now specified:

1. **Descriptor schema v1** (§4): the interned `callees`/`types` tables and their first-seen order, ids and binding records, node forms, the alias and flat concatenation (reader and writer rules), and what `decode_program` refuses.
2. **Canonical JSON** (§1): RFC 8785 (JCS) is adopted. The current bytes conform on the descriptor domain: strings of ASCII without DEL, integers of magnitude at most 2^53 − 1, no floats. This is checked on the vectors and on three real build-step descriptors, whose JCS bytes equal `canonical_json`. `encode_program` and `decode_program` now refuse a descriptor outside the domain, so Lean may re-serialize with JCS. Stored `descriptor.json.gz` files are not canonical; the digest is over the canonical form.
3. **Reference sequences** (§3): the four forms, strided broadcast, and batch members along each axis. `refs.runs` and `intervals` need no spec: `separable` depends only on which leaves are referenced.
4. **Canonical layout** (§6) and **scope resolution** (§7): offsets, member counts, locating a gate, operands, and every resolution case (a vector each).
5. **Input nodes** (§5): the root lowering, and recognition by id `^Input([1-9][0-9]*)_v1$` (`program.INPUT_ID`). `partition_object.calls` now uses the id, not the registry's `family`.
6. **Wide gates** (§8): pinned as Q_word v1 behaviour, with a vector showing the graph with and without the special case.
7. **`WIRING`** (§8): the pinned id list.
8. **`n_members` and `axes`** (§4.4, §6).

Also new in #120: the decoder now refuses descriptors the format does not define, several of which previously made a reference resolve to another node's gate. These are:
- keys unlike their id and binding record;
- negative table indices;
- references past their collection, or to a later node;
- nodes that don't type-check or misdeclare `out`;
- booleans as integers;
- a root with parameters.

A Lean reader should refuse the same list (§4.6, vector `decoder_rejects`).
