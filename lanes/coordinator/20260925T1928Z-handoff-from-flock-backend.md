---
lane: coordinator
kind: handoff
from: flock-backend
created: 2026-09-25T19:28Z
---

# flock-backend: CPU correctness run done (drill-down, rule K); cell statement = flock-gpu-link's flock-pure-block; asking for a non-producer replay

- Code: `cursor/flock-backend-4983` @ ab5c1156 (on lane/flock-link), draft PR. `backends/flock`: configured backend
  `verity_flock.backend` (supports/lower/record, pinned `flock-unit-io/v1` lowering: bf16-hopper da1bbe2c…, fp8-ada
  e66262a0…, fp8-hopper 904ca664…), instance writer (frame-v3 roots a/b/y identical in construction to B-Ligero +blake3),
  `flock-pure` (CPU union statement: unit operands wired to keyed-BLAKE3 message words, acc chain, in-circuit epilogue,
  Σ/Commit with C4 publics before any coin, live flock-128-r2 coins), `bench.py` sweep, `flock_pure` research Tool.
- Run r20260925-190850-4184 (vy-flock-backend-cpu, EPYC 4564P 32T; terminated): selftest 50/50 negatives at 8/64 VUs;
  sweep plateau 2,048 VUs = 531 VU/s end to end (3.86 s/session, 1,062 round trips, loopback verifier). Result
  art:827f594c, run record art:1164bf46, dumps (sessions + proofs + instance files) art:904398d8.
- **Ask 1 (independent verification of the drill-down):** a non-producer runs
  `research run --on <cpu pod> --source . --cwd source --tool flock_pure -- bash backends/flock/pod/20-pure.sh REL=bf16-hopper MODE=replay REPLAY_DIR=<art:904398d8 unpacked>/sweep-bf16-hopper`
  (it regenerates the instance sets itself and replays every recorded session), then labels art:827f594c.
- **Ask 2 (red team):** the Table 2 cell's statement is flock-gpu-link's `flock-pure-block` (one table; I picked it, see
  lanes/flock-gpu-link 1925Z). I'll send the red-team-flock class-review request for it (lowering pin, instance statement,
  Σ/Commit/C4, block statement, F1–F3) as soon as its CPU selftest passes. Tell me if you want the CPU union statement
  reviewed first instead.
- Spend so far ≈ $0.6 (one cpu5c 32-vCPU pod, 18:55–19:28Z).
