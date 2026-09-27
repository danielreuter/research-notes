---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T08:10Z

# Merge requests: PR #120 @ 460f0650 (`verity/ir/PROTOCOL.md`, the program format spec) and PR #131 @ 6f488790 (`Q_template_instance(s)` v0): APPROVE, after #111

Both come from vllm-cross-call-check (handoffs `vllm-coordinator/20260927T0640Z-…-format-spec.md` and `…T0740Z-…-q-template-instance.md`).
- **Stacking:** both on #111 @ 034ca061. Retarget to main once #111 lands.
- **Merges:** each merges cleanly into main 928790af, and they merge cleanly with each other.

## PR #120: the program format as a maintained spec, with pinned vectors

- **What it adds:** `packages/verity/src/verity/ir/PROTOCOL.md` (333 lines) with `format_vectors.json` / `test_format_spec.py`. It
  specifies:
  - canonical JSON (RFC 8785 JCS on the descriptor domain);
  - Input nodes by id;
  - the forward-reference decode rule.
  - This closes most of the "defined only by code" list in the partition-object amendment (flock-verifier's Lean port).
- **The risk was the 217-line `codec.py` change, and nothing of record moves:**
  - `codec.program_digest` over the stored descriptors of #101's record Build (`art:9cb3a4df…`) is identical on main + #111 and on
    main + #120: request `ccc21347…` (= the record), step `03ace66f…`, workload `a2b43bde…`.

## PR #131: one-stage's template-instance queries as named partition/v1 queries

- **What it adds:** `Q_template_instance` v0 (`{template}`) and `Q_template_instances` v0 (`{templates}`) in core
  `partition_object.py`, 6 lines in the codec, and pinned vectors plus tests.
- **Purpose:** root's 07:13Z ruling, one canonical `verity/partition/v1` envelope. The lane reports that the A1 and A2 digests reproduce.
- It adds queries only, and changes neither `Q_word` v1 nor any digest of record.

## Tests (both)

My jdiff of main + #111 against main + #120 + #131, over `packages/verity/tests`,
`integrations/vllm/tests/{query,pipeline,program,check,regression,commit}`, the lints, by-name, imports and `backends/flock/tests`:
- 4,083 tests; 66 new, all pass;
- 0 changed outcomes, 0 new failures or skips.
- The regression suite's digest pins are included.
