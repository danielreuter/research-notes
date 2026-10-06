---
id: red-team-outer-shape/20261006T0820Z-finding-red-team-outer-shape
campaign: proofs
lane: red-team-outer-shape
kind: finding
status: final
repo: verity
origin: pr:1315@e3f7a643a9ef60a50cfcdd9534cb42b1add425c7
---
# Red team, PR #1315 (a fixed outer shape by padding): GRANT WITH CONDITIONS

Head `e3f7a643a9ef60a50cfcdd9534cb42b1add425c7` of `cursor/outer-shape-95d4`, base `cursor/rec-step3-95d4` at `2730170682d2`.
The details, probes and logs are in the agent store's `private/red-team-reviews/1315/` (`review-detail.md`).

The code is sound, and the filler forgery is refused by serve, upstream `replay --zk` and Lean (runs r20261006-073154-8c34
and r20261006-072405-f1ba). Every condition is a correction to the PR body, so the head doesn't move.

Conditions (PR body only):
1. Scope "the real instance count stays the prover's". The outer proof's shape and the inner session's record don't show R.
   The inner statement's `pub-N.bin` does, through its `shared_rows` and refs, so R is visible to whoever reads that file,
   which today includes the verifier's side computing V*'s `v`.
2. Say that nothing yet compares the statements a verifier is sent with `rec_shape.outer(cap)`. Only the tests and the CLI
   call it.
3. Say that a filler's output is the class lowering's own, checked by staging's satisfaction check, not against the
   reference.
4. Replace the PENDING lines with the results: the forged filler is refused on algebra parts 0 and 1 by serve,
   `replay --zk` and Lean, and part 2, which the forgery leaves alone, is accepted.

Non-blocking:
- The cap is opt-in: with no `REC_CAP` there is no check. A deployment must require it.
- `check` doesn't read the inner instance count. An unpadded statement with the cap's m passes; the outer shape is the same.
- No second R has been measured at the cap. The record's shape doesn't depend on R by construction (Hello, coin counts).
- Inner-session timing at a small R (fewer distinct shared rows to hash) belongs to the scheduled release.
- V*'s `v`, and the link's `y` before #1270, are values computed from the hidden statement. That predates this PR.
