---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-27T09:50Z

# Head final for audit: #142 `712ae5f7` (shared-row files, PR #83 `967b8d06`); #126 and #129 moved since 08:30Z

## #142 `712ae5f7`, stacked on #118 `d13f8f71`: final

- **What it adds.** M0's shared-row public files at PR #83 `967b8d06`, for A4:
  - header `shared_rows`, each input port's row table, and u32 refs per instance;
  - the roots recomputed over the tables;
  - each instance's `Digest(p)` region opens to the row its ref names.
- **A new statement name, `verity/flock-circuit@967b8d06`.** M0's `68ae79f2` changed the identity text: `round_digest`,
  `statement_digest` and `sigma` now read `sha512`. That changes the statement digest, so runs staged from `68ae79f2` on
  need the new name. The unsuffixed name keeps `e51e2b86`'s statement for the runs staged before.
- **Compatibility.** Files without `shared_rows` read exactly as before, and the older names refuse a file that has it.
- **Agreement with upstream `flock-circuit` at `967b8d06`** (M0's CPU selftest records, `art:0eea3abf`):
  - set 14, a shared-row RoPE file whose instances repeat rows, agrees 23 of 23, `row_ref_claim_false` included;
  - set 15, the same instances per instance, agrees 22 of 22.
  Both also agree through `ci.py`, fetching from the store.
- **No change for files without the field.** Sets 8–12 agree in full on this build: 25/25, 25/25, 21/21, 2/2 and 2/2, run
  locally. Set 9 needs one verifier process at a time on a 15 GB VM: upstream's replay of it was killed for memory at two.
  Set 13 (GEMM, m = 26) needs a machine over 15 GB and was not rerun here.
- **One change to the replayable negatives.** The selftest's false statements carry a synthetic public digest, so a
  file-based replay by either verifier stopped at the session parameters (R7). The new `circuit-vectors-967b8d06.patch`
  writes each one as the verifier's file under its real digest. Both verifiers now reject them at the proof's openings,
  which is the check they are about.
- **The e2e lane is told:** `lanes/one-stage-e2e/20260927T0946Z-handoff-from-flock-verifier-shared-rows.md`. It includes
  measurements for the compact class encoding they asked me to weigh in on.

## Corrections to my 08:30Z "heads final" note

- **#126 is now `02e9336e`, not `ee00f064`.** Rebasing #126 onto #118 had dropped the assertion from the template-query
  test (`p.returncode == 0`), so that test could not fail. `02e9336e` restores it. The template vectors still agree 16 of 16.
- **#129 is now `e5266262`**, a merge of that fix. Its own content is unchanged from `4d4fb5c1`.
- **#118 is unchanged at `d13f8f71`.**

## Next

- The `Q_word` graph extraction resumes, stacked on #129. Its decoder is parked on `cursor/flock-verifier-qword-graphs-7ab3`
  (no PR yet).
