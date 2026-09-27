---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator (cc: flock-verifier) · created: 2026-09-27T06:40Z

# PR #120: the program format spec, `verity/ir/PROTOCOL.md`, with every rule pinned; stacked on #111; no digest moves

[PR #120](https://github.com/danielreuter/verity/pull/120), branch `cursor/ir-format-spec-666c` @ `460f0650`, base `cursor/partition-object-v1-666c` (#111 @ `034ca061`). Retarget it to `main` once #111 merges.

**What.** `packages/verity/src/verity/ir/PROTOCOL.md` is a maintained spec beside the codec:
- §1 canonical JSON and the digests;
- §2 types and leaf order;
- §3 reference sequences, strided broadcast, and batch members along each axis;
- §4 descriptor schema v1: the interned `callees`/`types` tables and their first-seen order, ids and binding records, node forms, the alias and flat concatenation (reader and writer rules), and the decoder's refusals;
- §5 the root, and Input nodes recognised by id;
- §6 the canonical layout, with member counts and topological order;
- §7 scope resolution, one vector per rule;
- §8 Q_word v1's conventions: Calls, the wiring list, and wide gates as v1 behaviour.

Every rule has a vector in `tests/ir/format_vectors.json`, checked by `tests/ir/test_format_spec.py` (49 tests). The test also restates canonical JSON as an independent RFC 8785 serializer, leaf order, reference expansion, batch members and the interning order. `python packages/verity/tests/ir/test_format_spec.py --write` regenerates the file.

**Canonical JSON: RFC 8785 JCS adopted.** The current bytes conform on the domain descriptors use: ASCII without DEL, integers of magnitude at most 2^53 − 1, no floats (float statics are `{"f64": hex}` strings).
- Checked on the vectors and on the three build-step descriptors of `art:7e51cdad` (gemma2-2b, llama32-1b, smollm2-135m; 1.4–4.9 MB canonical). Their JCS bytes equal `canonical_json`, they decode strictly, and they re-encode byte-identically with unchanged program digests. Evidence: `~/.research/notes/lanes/vllm-cross-call-check/evidence/format_real_check.{py,json}`.
- Stored `descriptor.json.gz` files are not canonical (they're written with spaces); the digest is over the canonical form.
- `encode_program` and `decode_program` now refuse a descriptor whose free-form parts leave the domain.

**Code changes that make the spec true.** No digest moves: `partition_vectors.json` is unchanged and passes.
- **Input nodes by id.** `program.INPUT_ID = ^Input([1-9][0-9]*)_v1$` and `is_input` are now used by `partition_object.calls` and `Program.input_gates`. The decoder materialises an Input id ahead of the registry, so `Input016_v1` no longer decodes as `Input16`.
- **`decode_program` refuses what the format doesn't define.** Each refusal is a vector (`decoder_rejects`):
  - definition keys unlike their id plus binding record;
  - node forms, keys and counts outside the spec;
  - negative table indices;
  - references past their collection, bounded by each node's declared `out`;
  - backward-only aliases violated;
  - nodes that don't type-check or misdeclare `out` (each node is rebuilt through `defs.Builder`);
  - booleans used as integers;
  - a root with parameters.
- **Forward references still decode.** A node reading itself or a later node is what the global-match checker's red-team fixtures (G3/G4/G8) must name, so the decoder accepts it. `cut.CallGraph` now refuses a Call in which a gate reads a later gate of the Call (vector `forward_reference`).

**Tests.** The same runs on #111's branch give the same failures.
- `packages/verity/tests`: 1182 passed.
- Default suite: 2870 passed. The only failures are 7 `tools/research` tests (rsync/pythonpath/store; identical on #111's branch) and the `torch`-only `backends/gkr` module.
- `integrations/vllm/tests`: the 15 failures this branch first caused (global-match forward-reference fixtures, `compact`, a codec test) are fixed. The remaining 11 failures also occur on #111's branch or depend on test order (`test_lifted_tiny::test_specified_list_is_closed` passes alone). 18 modules need `torch`.

**For the Lean port.** Read §1–§8 and replay `format_vectors.json`. Refuse the §4.6 list. Hash canonical bytes: parse, then serialize with JCS; the domain guarantees that equals the writer's bytes.
