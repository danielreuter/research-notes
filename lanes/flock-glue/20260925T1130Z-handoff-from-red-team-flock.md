---
lane: flock-glue
kind: handoff
from: red-team-flock
created: 2026-09-25T11:30Z
---

# red-team-flock: NOT GRANTED for flock-128-r2. The paper terms hold (2^-195.5 reproduced), but the two reps aren't bound to one commitment (BREAK: rep 2 can prove a different witness; demo art:8d04b53f), and the live-coin challenger doesn't exist (the verifier is Fiat–Shamir only, at most 2^-75.6). It becomes grantable with conditions R1–R8.

Report: `lanes/red-team-flock/20260925T1107Z-report-red-team-flock.md`. Demo: pod run r20260925-112210-2d3d, art:8d04b53f
(`evidence/rtf_unlinked_reps.rs`). Pod terminated at 11:24Z; about $0.07 spent.

## Verdicts
1. **Term by term: HOLDS.**
   - Fast100 queries give 2^-97.77 per run (m30: 2^-98.04), recomputed from the TOMLs. The Johnson-regime MCA is
     proven (Haböck ePrint 2025/2110; BCHKS25). The stratified sampler is exactly (1−γ)^Q.
   - The 7 fixed inner zerocheck coordinates lose nothing on the x86/CUDA RS path: the α^K·γ^j weights form a
     GF(2)-basis of F128.
   - No grinding credit is taken. The two-run arithmetic, 2^-195.5, is correct if its premise holds.
   - Separate GAP: the AG r₁ path (aarch64 only) gives the prover about 14 bits of nonce choice, even with live coins.
2. **Repetition: BREAK.**
   - Each rep commits its own root. The Mixed binding absorbs only the registry, the counts and that root, with no
     public I/O. So rep 2 can honestly prove another witness, and the error stays at 2^-97.8.
   - Fix (R1): one commitment per table, reused by both reps, or a root_rep0 == root_rep1 check before any rep-1 coin.
     The link binds that root. The commit is deterministic, so this costs nothing.
   - If the link claims are opened in both reps, red-team-link's C1 term also squares, to about 2^-244.
3. **Fiat–Shamir and live coins: GAP.**
   - No live challenger exists. The requirements are R2–R6:
     - R2: commit before coin, plus a final replay that checks every message against the coins issued.
     - R3: `fork_from_seed` must be live. The merged opening runs the multipoint/anchor child concurrently; an FS child
       seeded from the fork seed costs about 2^-122 over the two runs, which fails.
     - R4: PoW and nonce sites must return pure verifier coins.
     - R5: Flock's coins go out only after root_F, the link points and y.
     - R6: Flock-CUDA squeezes on the device (`zc_challenger_device.cuh`) and needs a live path, which hasn't been
       costed.
   - Under FS the red-team-link break stands: Flock seeds from the registry, counts and root only.
4. **Implementation: HOLDS where it exists.**
   - Profile downgrades are rejected: exact `commitment.params == expected`. The Fast proof, the relabelled params and
     rep 0 replayed as rep 1 were all rejected in the demo.
   - The padding contract is benign.
   - Merkle and transcript are BLAKE3 (32-byte, custom chained transcript). Table 1 must say so.
5. **Composition, with the fixes: 2^-130.2 on the A-GKR route, set by A-GKR.** If the accountant counts A-GKR's hash
   budget (2^-127.7), the proof misses 2^-128 whatever Flock does. The accountant must settle this (C8). On B-Ligero,
   2^-128.05 + 2^-195.5 still passes.

## Grant: NOT GRANTED. With R1–R8 and a re-audit of the live challenger: GRANTED WITH CONDITIONS
- R7: the verifier pins Fast100, reps = 2 and the RS flavour from configuration, and rejects lone reps and AG proofs.
- R8: evidence is the live session record only.

Negatives to keep: see report §5 (10 items). The first is: reps with different roots are rejected.
Until then, route (a) has no 2^-128 Flock cell.
