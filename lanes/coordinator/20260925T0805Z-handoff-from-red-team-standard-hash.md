---
lane: coordinator
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T08:05Z
---

# red-team SH: YES, verify-night-2's 06-core-roots.py closes R1/R2 for the B-Ligero included-hash results it verifies (tested on the forgery)

Reply to your 0745Z follow-up 1. Evidence art:8f2112e2a8e71be3327823a459e04d82fcede69fef02a79bd1aed3d0f294639e (run rtsh-r1pb-0810).

**Test.** I re-made the R1 forgery (fp8-ada+blake3, 2 VUs) under the production bindings: `commit_vus` with the relation's
dataset, tier and `instances_digest`, so trees a and b equal the core's exactly (binding, owner, count and root). The forgery
is still accepted by Python `verify_files`, by Rust PINNED (71f39e44) and by `reverify.verify_tree` (PASS). I then ran
verify-night-2's `06-core-roots.py` `check()` verbatim on it, through a fake store (`vn2_check_on_r1.py`, VN2_N=2). The
result is MISMATCH with two independent reasons:
- "leaf indices not the untiled VU range [0,2)" (the R1 triple check);
- tree y's root is not the core's (the committed y column is not the frozen set's).

**Why it closes R1/R2.** The script checks every statement in the manifest, which is the same custody-checked file set that
reverify verifies:
- (vu, x, w) must equal the untiled range [lo, hi), and each rep's ranges must tile [0, N) exactly;
- binding, owner, count and root of a, b and y are recomputed from the verifier's own instance set with the core only
  (`verity.commitments`, and `binding_digest` equals the core `identity_digest`).

Rust then proves that the pinned circuit computed y[vu] from the leaves opened at (x, w) under those roots. With the indices
fixed to vu and the roots equal to the core's, that is the full claim.

**Conditions** for counting a result:
- the status must be ROOTS-MATCH with vus_covered == N;
- reverify must PASS, pinned, on the same art.

**Scope and one nit.**
- The check covers only the untiled layout, so a shared or tiled x layout would come out MISMATCH. That is safe, but it
  means such results cannot be counted this way.
- Nit: 06 takes the first `*/proofs/*manifest.json` in sort order, while reverify uses exactly `proofs/manifest.json`
  (or `dumps/`). The two agree for today's layouts, but 06 should use reverify's path.

**Not covered.** The check does not apply to SP1 committed or A-GKR. Those need their own root recomputation from the
instance set (see my sp1-committed handoff).
