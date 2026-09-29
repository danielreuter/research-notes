---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
lane: coordinator
kind: handoff
from: workstream-interfaces (bc-ea1c2c4f)
to: research coordinator (bc-8ece7cde), for the next train
created: 2026-09-27T19:05Z
---

# Merge request: PR #179, `verity.ir.annotations` (`verity/annotations/v0`)

- **The PR:** [#179](https://github.com/danielreuter/verity/pull/179), branch `cursor/ir-annotations-866f`, head `5980c87e`, on `main` `d69ce770`. It's ready for audit and for the next train, CPU only, $0. The website lane builds on it.
- **What it is:** one stdlib module in `verity.ir`, its tests and one AGENTS.md line. It holds names, descriptions, formats and groupings keyed by descriptor ids (`def:`, `node:`, `wire:`, `port:`, `call:` with a program digest, and `group:`), validated against a descriptor's structure only.
- **Nothing existing changes.** No digest, format, query or circuit moves. `test_attaching_moves_no_digest` pins both program digests unchanged when annotations are attached.
- **Gates:**
  - `packages/verity/tests` in full, plus `tests/test_repository.py`: 1,262 passed;
  - `test_boundaries`: it imports only `verity.ir`;
  - no circuit, so no circuit-check report;
  - `check` not run here: the merger re-runs it.
- **Split from #178.** [#178](https://github.com/danielreuter/verity/pull/178) keeps the per-unit circuit extractor. Its merge request follows once the extractor has moved into core.
