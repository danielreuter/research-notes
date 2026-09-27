---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-cross-call-check · kind: handoff · to: vllm-coordinator (cc: flock-verifier, M0) · created: 2026-09-27T05:20Z

# PR #111 merge-ready (after #98): `verity/partition/v1` in core, plus the checker's references in `verity.ir.cut`; nothing moves

[PR #111](https://github.com/danielreuter/verity/pull/111), branch `cursor/partition-object-v1-666c` @ `ed1da435`. It is stacked on #98 (`4f87f275`); its own commits are `9415b030` and `ed1da435`. It merges cleanly with `main` `3040ac1f` and with #99.

**For M0 and the verifier.** Import from core; all of it is stdlib only.
- `verity.ir.partition_object`:
  - `build(program, cuts, classes)`, with cuts as (Call index, owner, committed);
  - `program_sha512`, `canonical`, `digest` = `SHA-512("verity/partition/v1\0" ‖ codec.canonical_json(obj))`;
  - `validate(obj)`, which checks form only;
  - `verify(obj, program, limits=(16, 32, 0))`, which derives each Call's graph and runs the invariant plus `unit-too-wide`.
- **`classes` is M0's:** pass each unit circuit file's SHA-512. The default, `unit_class`, is provisional: SHA-512(Definition id, owner value).
- `verity.ir.cut`:
  - `CallGraph` (the P1 graph reference, formerly `word.Graph`), `WIRING`, `call_scope`;
  - `fits` (P2 in bits: ob ≤ 16, or og = 1 and ob ≤ 32), `boundary_widths`, `check_cut`.
- From a vLLM `word` cut: `word.partition_object(program)`.

**Unchanged:**
- `with_word_rules` on #101, #74 and #73 gives byte-identical JSON under #98 and #111.
- No digest of record moves. Roots binding the digest wait for E6.
- The width docstring now says bits, matching the code.

**Tests:**
- core: `tests/ir/test_partition_object.py` (17, including a pinned digest vector) and all 1,136 core tests;
- vllm: `tests/query`, `test_program_graph`, the lints, and by-name;
- `backends/flock/tests`: 83 passed, 6 skipped.

**Size note:** the object stores an owner per computing gate for every Call activation. That fits M0's serving rows. For a whole vLLM request Program it would repeat each Definition's cut per activation.
