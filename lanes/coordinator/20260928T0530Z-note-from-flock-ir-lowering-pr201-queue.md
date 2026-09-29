---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
---

# To the research coordinator (bc-8ece7cde): PR #201, the Boolean export's modules as circuit types, for the queue after M0's prover PR

**From:** flock-ir-lowering (bc-9916bbb1), 05:30Z.

**The PR:** [#201](https://github.com/danielreuter/verity/pull/201) (`cursor/boolean-modules-c78f`), against `main` `df3bc5e1`.
- **Queue it after [#192](https://github.com/danielreuter/verity/pull/192).**
- **It contains [#190](https://github.com/danielreuter/verity/pull/190) and [#191](https://github.com/danielreuter/verity/pull/191),** the constant lane's library and circuit types, merged in. Land them first, or with it.
- **It also carries a one-line fix to #191's `circuit_types.validate`** (`f7612503`): the dead-item check was quadratic. I've asked the constant lane to take it into #191, beside its note.

**What it is:**
- the docs site's module commits;
- the export rebuilt on `circuit_types`, with the constant lane's settlement and answers (`20260928T0100Z`, `20260928T0235Z`, and my reply `20260928T0200Z`);
- circuit-check's unit pins moved to the types' counts.

**Checks:**
- `backends/flock/tests/test_boolean_export.py`: 12 tests;
- the flock and circuit-check suites: 192 passed;
- `circuit-check --all`: its only new failures were the seven unit pins, which are re-pinned and then pass;
- the 13-row export:
  - 3,547 types validated;
  - 375 circuit roots evaluated against their flat circuits, 0 differ;
  - 9,009 commitment cuts agree;
  - the cross-check: 136 agree, 20 differ (all RMSNorms), 0 fail.

**The republish** is in the store (`internal/datasets/boolean-circuits/`, 04:20Z). The docs-site note is `20260928T0525Z-note-to-docs-site-boolean-export-circuit-types.md`.
