---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator, train D (urgent)
created: 2026-09-28T17:40Z
---

# URGENT merge request, train D: PR #314, main can't build a proving flock-circuit

**Superseded (2026-09-29 08:54Z)** by `20260929T0854Z-merge-request-flock-314-289-327-on-180f8771.md`: new heads on `main` `180f8771`.

- **PR:** [#314](https://github.com/danielreuter/verity/pull/314), branch `cursor/flock-circuit-proving-build-4d6a`, head `e3001ff2`, on `main` `ac412eb8`. It's ready for review.
- **The break.** Since 1053c0c9, `view_hello` takes a type that only `seed-injection` defines. So every `flock-circuit` build without that feature fails to compile: bench, cells and the class sweep's proving build.
- **The fix** is one `#[cfg(feature = "seed-injection")]` line, and behaviour doesn't change. Nothing pinned or statement-level moves, so there's no statement reviewer.
- **The guard.** `check` gets a `flock-circuit-build` step, `backends/flock/check_build.sh`. It runs `cargo check` of `flock-circuit` in every CPU feature set a pod builds: `sha512`, `sha512,glue`, and `sha512,glue,seed-injection`, on a cached Flock b684b12 checkout.
  - On `main` without the fix, it fails with the break's error. With the fix, all three pass: 8 s warm, 20 s from a fresh clone.
  - `tests/test_check.py` pins the step (5 passed).
- **check: passed** on `e3001ff2` (18:26Z update), recorded run `r20260928-173957-713c` (rc 0, validation passed, attempt published). It covers pytest, circuit-check, **flock-circuit-build (23 s, from a fresh clone)**, lean-build, lean-unit-cut and lean-audit; lean-agreement was skipped (no bundle).
- **Not affected:** #289's GPU validation, because #289's base predates 1053c0c9.
