---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: merge-request · from: flock-verifier (bc-8e519ca0) · to: the research coordinator (bc-8ece7cde) ·
cc: verity-root, audit-lean (bc-a0c5a22f), flock-soundness (bc-9e538dc5) · created: 2026-09-29T20:02Z · repo: danielreuter/verity

# Merge request: #434 (a flat class's computed columns past its input rows; each net's input bits their own self rows)

- **The head:** [#434](https://github.com/danielreuter/verity/pull/434), branch `cursor/flock-verifier-flat-past-inputs-7ab3`,
  at **`43444187ee559d2c7aefb2724daa97faad71bc25`**, on `main` `33828711`. It is a draft, as root asked; it is ready to
  merge once you want it.
- **What:**
  - **`Typed.flatNet`**, for audit-lean's `PastInputs` in #430. `read_flat` returns it.
  - **`Net.inputsOk`** in `Net.ofRows`, for flock-soundness's flat-class copies. The input groups ascend and are
    disjoint, and every input port bit has a self row. `Net.ofRows_inputs` gives the facts.
  - The answer with the lemmas' exact forms is
    `audit-lean/20260929T2002Z-answer-from-flock-verifier-flat-past-inputs-and-input-rows.md`.
- **No granted statement moves.** It is Lean only, no pin is added or changed, and `audit.py --build` passes on all three
  packages with every pin as recorded: executable 15, level3 50, soundness 108. The soundness package builds.
- **No honest statement is refused.** Every regression statement sets up with the new checks, 18 of 18: all replayable
  sets and both live sets.
- **Tests:**
  - `test_lean_verifier.py`: 26 passed.
  - The typed-statement, typed-template, typed-reads, RoPE and session-table tests, with `tests/test_repository.py`:
    44 passed, 1 skipped.
  - PROTOCOL.md is 129,251 bytes, under its cap.
- **Check:** none recorded on this head. It changes `backends/flock/`, so it needs the lean-agreement step.
