---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T06:30Z

# Merge request: PR #111 @ 034ca061 (`verity/partition/v1` as a named query, P = Q(C); core evaluator): APPROVE, after #98

The spec is `internal/lanes/flock-verifier/20260927T0520Z-amendment-partition-object-v1.md` (Daniel's 05:28Z decision).
- **Stacking:** #111 sits on #98 @ 4f87f275, and its own commits touch no file #98 changed outside `query/`.
- **Merges:** clean into main ae5db5d3 and with #99, #103, #106, #108 and #109. Its conflicts with #102 / #105 are #98's, in
  `pipeline/manifest.py`, already flagged.

## What I checked

- **Core boundary:** `verity.ir.cut` and `verity.ir.partition_object` import only the standard library (`array`, `bisect`, `hashlib`,
  `re`) and sibling `verity.ir` modules. The boundary tests pass.
- **`word.partition` on the core cut changes nothing:** I recomputed #101's `Q_word_v1` rules for every group of its stored program
  graph on main + #98 and on main + #111. The row and per-group rule JSON is **byte-identical** (sha256 `4f261e55…`): 273,995,039
  units, 18,805,632,558 gates, 64,169,215 committed interior words and 32 redundant gates, about 55 s per tree. The lane reports the
  same byte identity for #74 and #73.
- **Nothing of record moves:** the word check stays opt-in, and no Program, manifest, Definition or partition count changes.
- **Tests:** my jdiff of main + #98 against main + #111, over `packages/verity/tests` (including the pinned vector test
  `partition_vectors.json`), `integrations/vllm/tests/{query,pipeline,program}`, the lints, by-name, imports and `backends/flock/tests`:
  - 2,868 tests; 16 new, all pass;
  - 0 changed outcomes, 0 new failures or skips.
- **The object:** exactly `{format, program: SHA-512(canonical descriptor), query: Q_word v1 {X, W}}`, 236 bytes, with digest
  `SHA-512("verity/partition/v1\0" ‖ canon)`.
  - No owners or cuts are stored; the committed set is derived.
  - `verify` re-evaluates, then checks the invariant, the widths and a served set.

## For the flock-verifier / Lean port (not blocking)

The amendment lists eight things defined only by code: descriptor schema v1, canonical JSON, reference sequences, the canonical
layout, Input recognition, `WIDE_FAN_IN`, `WIRING` and `n_members`/`axes`. They need written specs before a Lean evaluator can hash the
same bytes. `WIDE_FAN_IN`'s graph effect is pinned in Q_word v1 and should go in v2.
