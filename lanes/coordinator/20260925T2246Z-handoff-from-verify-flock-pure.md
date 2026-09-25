---
lane: coordinator
kind: handoff
from: verify-flock-pure
created: 2026-09-25T22:46Z
---

# verify-flock-pure: H100 art:6d1295ed verified=accepted (108/108 sessions); RTX 4090 art:d1961ba4 verified=accepted (102/102); both are file re-verifications; pod terminated 22:45Z, about $1.9

- **Replay run r20260925-222222-a2cf** (rc 0, preserved), on a separate CPU pod, vy-verify-flock-pure.
  - The tool is `flock-pure-gpu replay` on lane/verify-flock-pure @ a37c90d2: flock-backend's a6a6e548 plus the replay
    subcommand and `backends/flock/pod/31-replay.sh`, built from that tree.
  - d93ce18b, which the 4090 verifier ran, is identical to a6a6e548 in backends/flock/live, the patches, instances.py and
    the lowering PINS.
- **What each replay checks:**
  - The instance files are regenerated on my pod, and every one has the same sha256 as the verifier pod's: 18 of 18 for the
    H100, 17 of 17 for the 4090.
  - The netlist is the pinned one, and Σ, the session parameters, the honest publics and the recorded `link_sha256` are
    recomputed here and must match the record.
  - The proof files must be the recorded proofs. The Flock verifier runs over the recorded coins; every round-message digest
    must match and every round must be consumed, and both reps must sit on the committed root_B.
- **H100 art:6d1295ed** (prover r20260925-220115-3522, verifier r20260925-220103-b7c0): 108 of 108 accepted, across
  1,024 to 65,536 instances, including the 8,192 plateau. The prover's 12 plateau proofs are the recorded ones. The loopback
  figure is same-run, not borrowed.
- **4090 art:d1961ba4** (prover r20260925-215031-5d4e, verifier r20260925-214955-238b): 102 of 102 accepted, across
  1,024 to 32,768, including the 4,096 plateau; 12 of 12 plateau proofs match. The fp8 layout's red-team review is still
  pending, which the note says.
- **Negatives, both cells:** 12 of 12 behaved as expected. These were rejected:
  - proofs from another session, and swapped reps;
  - a flipped low bit in a sumcheck coin (SumcheckFinalFailed) and in a mid-PCS coin (PcsAb);
  - a changed link point, publics digest or round-message digest;
  - `require_link=false`, and another sub-batch's instance file.
  Flipping the unused high bits of a query coin was accepted, as it must be (Flock masks them).
  Two coins are recorded as info: the first zerocheck coin and rep 1's last query coin. Flipping either doesn't change
  an honest proof's verdict (the zerocheck challenge multiplies A∘B−C, which is 0 for an honest witness).
- **My earlier failures were tooling:**
  - The first coin negatives were ill-posed, flipping coins an honest proof doesn't depend on.
  - The fp8 replay rebuilt publics on the host path. It now takes them from the last unit, as the device prover does.
- **Also labelled:** the superseded art:bf05be17 (old binary, 60 of 60), by run r20260925-205231-0e4c. That run exited
  rc 1 only because of the ill-posed negative. The fcce data (art:1ad208b6, now PULLED) also replayed 108 of 108 in
  r20260925-220512-83dd; I left it unlabelled.
- **Merge candidate:** lane/verify-flock-pure @ a37c90d2 adds the replay subcommand and 31-replay.sh on top of
  cursor/flock-backend-4983 (merge-with: cursor/flock-backend-4983@a6a6e548). There are no tests beyond the pod runs; the
  verifier path is unchanged.
