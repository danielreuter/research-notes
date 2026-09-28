---
id: 20260928T2053Z-handoff-from-pouw-mvp-315-ready
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# #315 (PoUW vLLM option) is green on #311's final head and ready: land it after #311

This follows up `20260928T1950Z-handoff-from-pous-311-ready` and your `lanes/pous/20260928T2010Z-handoff-from-coordinator`.
It is from the PoUW MVP owner (bc-dd22acf8).

- **PR:** https://github.com/danielreuter/verity/pull/315, base `cursor/vllm-protocol-composition-9924` (#311), head
  `58c3bc49`, marked ready for review.
- **#311's final head `69153d43`** is merged in, and the adapter follows its interface: `EXECUTES`, `traced_as`,
  `keeps_weight_copy` and `commit_weights`.
- **check:** `r20260928-200030-ef51` on `58c3bc49`, PASSED: pytest (3,585 passed), circuit-check, lean-build,
  lean-unit-cut and lean-audit. lean-agreement is skipped because no bundle was sent. pytest started after 20:00 UTC, clear
  of the clock-dependent `test_notes` test that #324 fixes.
- **Contents:** everything is under `integrations/vllm/`:
  - `verity_vllm/protocol_options/pouw.py`;
  - `tests/protocol_options/test_pouw.py`, 14 CPU tests on fake layers;
  - the `verity-pouw` dependency (and `uv.lock`);
  - one README sentence.

  It adds no circuits, no Definitions and no Lean. The root `check` doesn't collect `integrations/vllm/tests`. From that
  directory, `tests/protocol_options`, the lints, the dead-module and import-resolution checks and the by-name rule pass:
  101 tests, #311's own included.
- **It carries #218** (merged into this branch) until #218 lands in D3′. After that, its diff against `main` is only the
  files above.
- **Default path:** unchanged. PoUW is off unless a run enables it, and beside sampled proofs it is refused until its int7
  linear has a Definition (`traced_as` is None).
- **Merge:** after #311, `research merge cursor/pouw-vllm-option-4f91`. If `main` or #311 moves first, I'll merge it in
  and re-record `check` when asked.
- **Statement reviewer:** none needed.
- **Also ready, not opened:** the #320 follow-up, `cursor/pouw-test-suites-4f91`. It gives `protocols/pouw` and
  `benchmarks/pouw` a pytest suite each, which #320's `test_every_test_file_is_in_a_suite` needs once both #218 and #320
  are on `main`. Both suites pass under #320's runner. I'll open its PR after #320 merges.
