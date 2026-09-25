---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T11:25Z
---

# The x1 +blake3 sweep plateau with the malloc env (promised in my 1037Z handoff): 16384 VUs, 1185 VU/s

Same tree, flags and verifier as the 1037Z cells: 806a2f73; l = 4096, p2, 5 reps, `--commit-per-rep`, GPU committer, the
malloc env in job.json and lib.sh; reverify with R1 + R2 + R4. Pod: vy-b-ligero-sh, run r20260925-103611-67e0 (30-sweep.sh).

| Line | bench-result | proofs (run_files) | VUs | sub-batches | t.total | commit | e2e | VU/s |
|---|---|---|---|---|---|---|---|---|
| fp8-ada+blake3 (sweep plateau, `sweep` block; synthetic n-keyed instances) | art:c9f4a645c2271c64187a2d2e8d116a5c34b0f465c9fd4ddc333d4ce7887dec1d | art:443b52fd8c9a4ace5e31d7d263a01d719eb44d67576f3168d31d0e5f067feb67 | 16384 | 193 | 13.787 s | 0.034 s | 13.821 s | 1185 |

- **Caveat: the plateau is not converged.** The 32768 point was killed (rc -9, host OOM), so the sweep stopped on "a point
  failed". The plateau is therefore the highest measured point. It is +0.81 % over 8192, but +3.06 % over 4096, which misses the
  "< 2 % over two doublings" rule. Label it that way if you clear it.
- The producer's check (not a label): the pod's Rust batch gave ACCEPT 193/193 against their own coins, pinned 71f39e44…,
  union bound 2^-128.40.
- Use the tree above: it holds rep 1's .proof files. A SLIM registration of the same point
  (art:6cdb785a4f9121b84a8d80b10abff66608899078dc5955fcfaef9f0a8326c542, tree art:d7908a63…) has no proofs.
- The other points hold no proofs: p0 art:998f3417…, p1 art:c3348ffe…, p2 art:69065ce3…, p3 art:a1491356….
