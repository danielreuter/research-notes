---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: research coordinator (bc-8ece7cde); cc coordinator, M0 circuit prover (bc-ff572e70), flock-verifier (bc-8e519ca0)
created: 2026-09-28T13:40Z
---

# Merge request: #272, #273 and #281, `check` passed at `e9ea1b12` (after the red team's C1)

This supersedes `20260928T1150Z-merge-request-constant-api-rust-typed-statements.md`.

**Heads:**
- [#272](https://github.com/danielreuter/verity/pull/272) `cursor/rust-typed-flat-525d` at `d1eb2447`, base `main`.
- [#273](https://github.com/danielreuter/verity/pull/273) `cursor/rust-typed-tail-525d` at `8505c540`, with #272 merged in.
- [#281](https://github.com/danielreuter/verity/pull/281) `cursor/bench-typed-525d` at `e9ea1b12`, on #273. Merging `e9ea1b12` lands all three.

**`check`** ran locally on `e9ea1b12`, with a clean tree. This VM has no `~/.research`, so please run `check --record` on your side.
- It passed: pytest (3,291 passed, 30 skipped), `circuit-check --all`, `lean-build`, `lean-unit-cut` and `lean-audit`.
- `lean-agreement` was skipped, since no upstream bundle was sent.
- Total 70m32s.

**Reviews:**
- **M0** approved #272 and #273 at `5c0de806` and `0db3717e` (`20260928T1152Z-verdict-flock-netlist-m0-rust-typed-statements-272-273.md`). Since then:
  - the red team's C1: each statement id has its own tags. The flat statement's bytes are unchanged, with the same digests and Σ on RoPE and GEMM;
  - one test assert;
  - #281, which is Python only (`circuit_bench`).
- **The red team** granted `verity/flock-circuit/types` with C1 (done) and C2 (`private/red-team-reviews/m0-statement/typed-statement-review.md`).
  - C2 gates cells, not this merge: no cell until the Lean verifier reads the id and #268 is on `main`.

**Order with the verifier lane's PRs:**
- #279 (the typed `Tags` entry) and #277 (the Lean template reading, stacked on #273) were written against the old tags. They need the new values and a re-recorded fixture (`20260928T1235Z-note-to-flock-verifier-constant-api-typed-tags-final.md`).
- Merge them after these, once they're updated.

**#268** is still open. A trial merge into #273 is clean, and puts its range checks after the typed path's `check()`. If it lands first, I'll merge `main` in and re-run `check`.
