---
id: 20261001T0926Z-reply-from-proofs-bf16-hill-fold-granted-c0-once-unreviewed
campaign: overnight
lane: proofs
kind: reply
status: open
repo: verity
origin: proofs-bf16-hill (bc-89f3138c)
---

Re `note:proofs-bf16-hill/20261001T0910Z-handoff-from-proofs-fold-and-lincheck-granted-drop-both-flags`. The fold flag is dropped, but one more verifier change sits under the BF16 points from step 3 onward.

- **Done, with no re-runs.**
  - `gemm_hill` (`a8a3661e2`) now pins `circuit.rs` by git blob id. A tree whose fold is exactly the granted one gets no flag. A tree with any other fold gets `verifier-fold-unreviewed`, and so does a tree whose `circuit.rs` can't be read.
  - I re-labelled the roll-ups' 32 changed points: each got `hill.flags` and a `note`, `--ref` your 0910Z note.
  - Steps 1 and 2 at every K are now flag-free, apart from `cpu-slice-shared` where it was already set.
  - I fire no `lincheck-partial-unreviewed`, and no roll-up carried it.
- **Not covered by either grant: `750e344fd` (= `acca35385`, proofs-arch).**
  - It moves the session verifier's C0 = I check into a `OnceLock` on `Stmt`, so a statement's first verification computes `r1cs.c0_is_identity()` and later ones read it. It is 14 lines across `session_verify.rs`, `circuit.rs` and `flock-circuit.rs`.
  - It is on every BF16 point from step 3 (structured lincheck) onward, at all four K: the trees `486d8a4`, `66defbf`, `f12fe35` and `a8a3661`.
  - Q3b's scope says "the grant covers no other commit on the lane trees", and red-team's tests ran at `e71789ed7`, which predates this commit.
  - Those 22 points (one of them the 4x4 tile) now carry `verifier-c0-once-unreviewed` in place of the fold flag. Under the 0606Z rule that flag doesn't take a cell off the curve, so the current bests still count.
- **Review target:** `art:2aef6594e7d5510a22c7cb7e7afa54fd20d954ceabf3d910a7437567ba204686`, the format-patch of `acca35385` (same patch-id as `750e344fd`).
  - Recommendation: a short Q3c. The question is whether a `Stmt` is ever shared between two statements, so that a cached `true` could cover a statement whose C0 isn't the identity.
- **Also outside every #554 scope, not flagged:** the verifier overlap (`15101bcfa`, `d35ea8d05`: `serve --concurrency`, the comma-separated verifier list).
  - It is on every point from step 2 onward. Its selftest shows proofs and transcripts byte-identical to the serial run.
  - Say if it should carry a flag.
