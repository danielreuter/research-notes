---
id: 20260929T0028Z-handoff-from-pous-311-head-1cbc750a
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #311's head is now `1cbc750a`: a Commit with POUS is of record. #312 and #315 should drop `outside_program=`

Follow-up to `20260928T2358Z-handoff-from-pous-311-new-head`, after Daniel's rulings at 00:15Z. For bc-13eada34 (#312) and
bc-dd22acf8 (#315).

- **Head `1cbc750a`** on `cursor/vllm-protocol-composition-9924` (https://github.com/danielreuter/verity/pull/311). It is:
  - `4c4b8290`;
  - plus `dfb9a450`;
  - merged with `main` `5810574d` (train K2), with no conflicts. D3′ still isn't on `main`.
- **`dfb9a450`, Daniel's Q1:** POUS with sampled proofs is of record, because it is bit-identical and leaves the circuit
  untouched.
  - `Installed.outside_program`, the `Option(outside_program=…)` field, `Composition.outside_program()` and
    `verdict.protocols.of_record` are removed.
  - `verdict.protocols` is now `{"protocols": [...], "record": <composition record digest>}`.
  - **#312 (`pous.py` line 256) and #315 (`pouw.py` line 371, `tests/protocol_options/test_pouw.py` line 120) must drop
    `outside_program=` / `opt.outside_program` when they merge `1cbc750a`.** Otherwise `Option` raises `TypeError`.
  - Nothing else in `interface.py` changed.
- **Q2 (PoUW under sampled proofs): build it.** PoUW gets its own modeled circuit, and sampled proofs is its verifier.
  - The design is in the Project store, `docs/pouw/sampled-proofs-circuit.md`, by a new worker.
  - `pouw` + `sampled-proofs` stays refused through `traced_as` returning None until it lands. #315 needs no change for
    that.
- **Evidence on `1cbc750a`:**
  - the vLLM tests under torch 2.14 ran as `r20260929-001914-bb04`. They all pass except `main`'s own
    `test_no_dead_modules` (#309's `spec.py`).
  - **Recorded check: `r20260929-004620-4e07` PASSED** (00:57Z). pytest, circuit-check, lean-build, lean-unit-cut and
    lean-audit all passed. lean-agreement was skipped by name.
    - pytest and circuit-check passed from `check`'s input-keyed cache.
    - The first try, `r20260929-002004-2255`, ran check's three groups at once, and on this 15 GB VM that ran out of
      memory. The kernel killed `level3`'s 7 GB replay (exit 137) and the `verity-flock` pytest suite. Every other suite
      passed in it.
    - `verity-flock` then passed on its own (11.4 min), and the re-run's Lean audit passed alone.
- **Merge nothing yet:** D3′ comes first, then #311 merges it in and re-runs `check`.
