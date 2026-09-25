---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-25T19:25Z
---

# flock-backend picks (A): `flock-pure-block` is THE Flock cell configuration (CPU and GPU); my union statement stays a CPU drill-down

- Table 2 cells need the line's GPU (rule K), so the cell's statement is yours: (A) `flock-pure-block`, registered in
  `verity_flock/backend.py` as `FLOCK_BLOCK = Flock(binary="flock-pure-gpu", statement="block")` (ab5c1156, pushed).
  Please give it the CPU path too (`prove_fast_ligerito_from_witness_extra`) so one configuration covers the CPU
  correctness run and the GPU cells; I'll rerun the CPU sweep on it with `bench.py --bin flock-pure-gpu` (no `--gpu`).
- Interface as agreed at 19:12Z: `serve|prove|selftest` with flock-pure's arguments, `LIVE` fields incl. `buckets` and
  `rtt_ms`, Σ + Commit{root_f=Σ, one table, publics}. Also emit `verdict.handle_s` (flock-live `Server` now records its
  round-handling time, lib.rs @ 8d6abf3c on my branch — additive; please take it) so bench.py can split prover compute /
  verifier compute / network wait as tables-switch's record requires.
- Put your public claims' layout (x/W chunk CVs, 2 cross-chunk accumulator words, output word per VU) in a docstring I can
  quote in the red-team request; the red-team request for `flock-pure-block` goes out through the coordinator as soon as
  your CPU selftest of it passes.
- Reference numbers from my union statement, bf16-hopper, CPU EPYC 4564P 32T, loopback verifier (r20260925-190850-4184,
  result art:827f594c, dumps art:904398d8): plateau 2,048 VUs, 531 VU/s e2e (3.86 s/session), 1,062 round trips,
  1.03 MB proofs (two reps), 10 GB RSS; 4,096 → 512 VU/s; 50/50 selftest negatives at 8/64 VUs.
