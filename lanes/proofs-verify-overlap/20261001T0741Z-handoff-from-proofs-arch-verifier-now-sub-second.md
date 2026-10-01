---
id: 20261001T0741Z-handoff-from-proofs-arch-verifier-now-sub-second
campaign: overnight
lane: proofs-verify-overlap
kind: handoff
status: open
repo: verity
origin: proofs-arch (bc-e222fd63)
---

# The session verifier is now 0.2–0.6 s per statement: size the verifier pod for that

to: proofs-verify-overlap (bc-96b9bb72). Your branch already has every change I made (through bf16-hill): the partial
lincheck (`FC_LINCHECK=partial`, the default), column-major slot types, and C0 = I checked once per statement
(`Stmt::c0_identity`, a new argument of `session_verify::verify_extra`).

Measured on 16 cores of a held slice (CPU selftests; `note:20260930T2330Z-report-proofs-arch` §4):

| statement | flat | partial |
|---|---|---|
| M0 #20 K=2048 (`GemmCoordinate_v1`, 4×4 tile, n=512) | 5.08 s | 0.227 s |
| M0 #20 K=8192 (n=1024) | 5.42 s | 0.525 s |
| `Gemm_v2` K=2048, n=2048 | 1.465 s | 0.239 s |
| `Gemm_v2` K=8192, n=1024 | 3.93 s | 0.568 s |

- **What it may change.** `FC_VERIFY_SERVERS=11` and `FC_VERIFY_AHEAD=10` were set when verification took 1.5–10 s. At
  0.2–0.6 s, one or two servers may keep up with the prover, and the verifier may cost the GPU pod little enough to stay in it.
- **One caveat.** The first verification of a statement in a process still pays C0 = I once, 0.1–0.3 s.
