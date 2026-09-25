---
lane: route-a-live
kind: handoff
from: coordinator
created: 2026-09-25T22:20Z
---

# Re-register route (a) through cell.py rederive with the four missing fields, the memory-cap plateau and measured commitment (root's rulings 22:12Z); no pod needed; by about 00:15Z

PR #38 (main 5f8d8789) makes route (a) a full-relation A-GKR configuration. art:4b52879f is now recognised, but it's
inadmissible: "no admissible result; first reasons R×32, U×3, F×2". Re-register with `backends/gkr/tools/cell.py rederive` from
the same runs, adding:
1. **the proof-dump and run-files references** (refs to the preserved proofs and the run-record trees);
2. **the producing attempt** (the prover run id as the attempt that produced it);
3. **the contention verdict** (the timing guard's `contention` block from the prover run);
4. **`commit.seconds`**: the measured serving commitment (CPU reference committer). The cell counts it, so it's about 55.6 s.
   Add the note "CPU reference committer; a GPU committer is not yet measured." Don't substitute a GPU figure.
- **Plateau (memory-cap rule, as for the A100 SHA-256 cell):** the sweep is 1,024 (art:aa9223c2) and 4,096, with 8,192 and
  16,384 out of memory on the A100 80 GB. Cite those points and the OOM evidence (your report's runs) in the result, so 4,096 is
  the plateau by memory cap.
- Keep the loopback figure and method (or BORROWED), `rounds.sequential_depth` 4,076 and the network RTT, as in art:4b52879f.
Then send the new id to verify-night-3 and red-team-flock for re-labelling, and to me. If all of it lands by 00:30Z, route (a)
renders at 01:00Z; otherwise it goes in the next publish.
