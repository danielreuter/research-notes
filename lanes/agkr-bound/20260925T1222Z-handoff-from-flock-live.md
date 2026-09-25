---
lane: agkr-bound
kind: handoff
from: flock-live
created: 2026-09-25T12:22Z
---

# flock-live: R1–R8 implemented, ready for re-audit; live H100 BF16 at 4096 = 0.98 s (1.24x FS), FP8 0.53 s (1.30x FS)

Report: `lanes/flock-live/20260925T1135Z-report-flock-live.md`. It has the R1–R8 checklist (condition → code → test),
the negatives table and the costs.

**Result:**
- flock-128-r2 (Fast100 × 2) now runs with live verifier coins on both the CPU union prover and Flock-CUDA.
  - The verifier issues each coin only after it holds the preceding round.
  - It refuses rep-1 coins unless rep 1 committed rep 0's root (R1).
  - Forks get live child streams (R3). PoW sites are pure coins (R4).
  - It refuses every coin before the link context (R5).
  - It pins Fast100, reps = 2, the RS flavour and the PCS parameters (R7).
  - It accepts only by replaying the ordinary Flock verifier over its own session record (R2, R8).
- Every red-team-flock §5 negative is rejected, plus the brief's extras (message after its coin, replayed coin, FS as
  live, lone rep, Fast proof, cross-session replay of both reps). Every honest session is accepted.
- **Flock-CUDA:** the b684b12 prove path uses only the host `FsChallenger`. `zc_challenger_device.cuh` is bench/test-only.
  So R6 is a host callback, and no device challenger has to change.
- Nothing here counts as a Table 2 cell until a red team re-audits the live challenger.

**Cost at 4,096 VUs, H100, same pod** (the verifier is a separate process on loopback; 12 runs each):

| line | today fast x1 FS | r2 FS | **r2 live** | live/FS | live/today |
|---|---|---|---|---|---|
| BF16 (unit m32 + BLAKE3 m33) | 0.655 s | 0.792 s | **0.982 s** | 1.24x | 1.50x |
| FP8 (unit m31 + BLAKE3 m32) | 0.413 s | 0.406 s | **0.526 s** | 1.30x | 1.28x |

- The overhead is about 220 coin round trips per table, at 0.23–0.34 ms each on loopback.
- A verifier on another host pays its RTT on every round. At 1.5 ms that is about 0.66 s per pair; at 3–12 ms, 1.3–5 s.
  Budget for that in any cell that uses a remote verifier.
- CPU union: the live path costs nothing measurable (1.00x at m33).

**For the coordinator (merge-ready):**
- tip: verity `lane/flock-live` @ a43f6254 (base main@767115db).
- Files: `backends/flock/live/` (Rust crate built inside a flock b684b12 checkout) and `backends/flock/cuda_live_patch.py`.
  No Python package, test or CI change.
- Tests are the pod runs: `flock-live selftest` (all_pass at n 4096 and 16384, art:6715442b) and the GPU harness
  (art:16c17a43, art:5320c158).
- Known failures: `tests/test_repository.py::test_no_tracked_blob_exceeds_limit` (fails on main too, from ligero-verify
  fixtures).
- Behaviour changes: none outside the new directory.
- kb suggestion for kb/flock-prover.md, a "Live coins (flock-live)" section, with the source being this handoff:
  - Flock-CUDA's prove path draws challenges only from the host `FsChallenger`.
  - A live session is about 220 round trips per table (both reps), about 74 KB up and 30 KB down.
  - The live overhead is 1.24x (BF16) and 1.30x (FP8) of FS on the H100 pair.

**For flock-glue:**
- R5 is a gate: the server refuses coins until a `Link` message arrives. That message carries an opaque stub today.
- The C2 order is: link points as a verifier coin slot after root_F and root_B, then y, then Flock's coins. It needs
  root_B committed before Flock's first round.
- Flock's union prover commits and binds inside `prove_fast_ligerito_union`. So your session driver needs either a
  commit-then-prove split, or a `Commit(roots)` → `Coins(points)` → `Link(y)` exchange added to `flock_live::Server`
  before the first rep round. That exchange is where link negatives 10 and 11 become testable.
- Negative 15 (cross-session replay against both reps) already passes.

**For agkr-bound:**
- Route (a)'s Flock term has an implementation of the live-coin profile. It is still not granted, pending the re-audit.
- With the re-audit, the composed figure stays red-team-flock's 2^-130.2 (A-GKR-bound).
- Price the live verifier's RTT into the prover time (above).
