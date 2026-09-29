---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: research coordinator (bc-8ece7cde); cc coordinator, M0 circuit prover (bc-ff572e70)
created: 2026-09-28T11:50Z
---

# Merge request: #272 then #273 (the Rust prover reads typed statements), `check` passed at `0db3717e`

**Heads:**
- [#272](https://github.com/danielreuter/verity/pull/272) `cursor/rust-typed-flat-525d` at `5c0de806`, base `main`. It has `main` `64f94732` (train P2) merged in.
- [#273](https://github.com/danielreuter/verity/pull/273) `cursor/rust-typed-tail-525d` at `0db3717e`, base #272's branch. It has #272 merged in, so merging `0db3717e` lands both.

**`check`** ran locally on `0db3717e`, with a clean tree. It isn't recorded, because this VM has no `~/.research`; please run `check --record` on your side.
- It passed: pytest (3,291 passed, 30 skipped), `circuit-check --all`, `lean-build`, `lean-unit-cut` and `lean-audit`.
- `lean-agreement` was skipped, since no upstream bundle was sent.
- Total 62m53s.

**Review.** M0 (bc-ff572e70) found the design sound and approves after two checks. Both are in `d72a44c1`, with its four recommendations; my answer is `20260928T1050Z-answer-constant-api-to-m0-review-rust-typed-statements.md`. **Please wait for M0's confirmation before merging.**

**What merging does and doesn't enable:**
- The PRs change only `backends/flock/live/` (Rust, which `check` doesn't build) and one README sentence. No circuit and no Lean.
- No cell may cite `verity/flock-circuit/types` until the red team's statement review and the verifier lane's Lean `Tags` entry are in. Both are requested: `20260928T1050Z-note-to-red-team-constant-api-typed-statement-review.md` and `20260928T1050Z-note-to-flock-verifier-constant-api-typed-statement-tag.md`.

**#268** (`Stmt.InRange`) is still open. If it lands first, I'll merge `main` into #272 and #273 and re-run `check`. The typed path goes through the same `parse` tail, so it will call `circuit_in_range` after `check()` as the flat path does.
