---
id: proofs/20261005T1532Z-finding-zk-cpu-steps
campaign: flock
lane: proofs
kind: finding
status: in-progress
repo: danielreuter/verity
origin: bc-b63aca89-377c-5e17-99a5-ace054ba29d0 (zk-cpu-steps, for the proofs coordinator bc-8416bc72)
---

# `--zk`'s two single-threaded CPU steps off the critical path (K = 4096 and 14,336, node 1)

**Question.** Does C-Flock's `--zk` prove at K = 4096 drop from about 5.2 s to about 1.8 s on node 1 when the mask-rank check
(`zk_veil::mask_rank_ok`, about 2.5 s a session, `ZKRANK`) and level 0's hiding draw (`level0_zk`, about 1.0 s) come off the
critical path, with byte-identical proofs and every session still accepted by serve, upstream's `replay --zk` and Lean's
`verify --zk`?

**Branch** `cursor/zk-cpu-steps-95d4` off main 378453fb3:

- f6997de29: `backends/flock/pod/86-zk-cpu-steps.sh` (85-rec-reprice.sh's statements and loopback machinery; builds keyed by
  their sources; the "before" build is this commit, whose live crate is main's).
- 5c491f8a2: `mask_rank_ok` as an incremental echelon basis that stops once the rank is `128 k` (the column count, so exact).
  The old Gauss–Jordan stays in the tests as the oracle (random, repeated, zero, Boolean, short, empty inputs; the proved
  sizes 2048 × 2^17 and 512 × 2^19).
- b7a476bb5: `level0_zk` draws its lanes on rayon's threads in 4096-word pieces, one `ProverRng` copy per worker
  (`ProverRng::f128s_lanes`); test: equal to the sequential `f128s` at every address. `ZKL0` prints the draw's seconds.

**Baseline** (85-rec-reprice.sh STEP=inner INNER_PROXY=0 on `cursor/rec-reprice-95d4`): r20261005-071603-4d28 (K = 4096):
`--zk` prove 5.212 s (ZKRANK 2.489 s a session, level-0 wait 0.915 s), session 7.50 s, serve verify 6.90 s; M0 prove 0.728 s,
session 0.876 s. r20261005-081442-dc2b (K = 14,336): `--zk` 4.06 s (ZKRANK 0.69 s, level 0 1.06 s).

## Runs

- r20261005-153137-feee: STEP=build at f6997de29 (before, key 5c9218d04c285b4c), CPU, done. Staged K = 4096 (shape 430e5aad,
  M0 statement digest 2602e07c…, the baseline's) and K = 14,336 (shape bac929c3) at N = 2048 and 512; Lean flock-verify
  built (sources 463f4dea3955a270).
- r20261005-155357-a60a: STEP=build at ee2638800 (after, key dfae70f600a9cf7b), CPU, done.
- r20261005-155947-8f55: STEP=prove K=4096, BUILDS before and after, GPU, done. `--zk` prove 4.965 → 2.410 s (ZKRANK 2.220 →
  0.002 s; the level-0 draw itself 0.070 s, ZKL0), but rep 0's level-0 wait only 0.965 → 0.608 s. Every session accepted
  (serve), upstream replay --zk accepted for both builds, `prover_is_deterministic --zk --gpu` transcript digest dc75aed4… in
  both builds (pinned: byte-identical proofs and transcripts). M0 0.788 → 0.780 s.
- The remaining wait: `make_zkrep` cloned the whole `Level0Zk` (the four 2^22-word extra lanes, 256 MB) once per rep on one
  thread (VM probe: 130–170 ms a clone, 43 ms written on rayon). 8d8c26fb3 writes each rep's copy on rayon's threads and
  prints ZKPRE (zk_prepare's seconds).
- r20261005-161240-0785: STEP=build at 2b34204a1 (after2, key 4f4efe413970c2cd), CPU, done.
- r20261005-161736-5c59: STEP=prove K=4096, BUILDS before, after, after2, GPU, done. `--zk` prove 4.739 / 2.187 / 1.880 s,
  level-0 wait 0.832 / 0.472 / 0.183 s (after2's ZKPRE 0.155 s), ZKRANK 2.180 / 0.002 / 0.002 s, session 6.58 / 4.07 /
  3.74 s, serve verify 5.60 / 5.79 / 5.80 s; every session accepted, replay --zk accepted, transcript digest dc75aed4… in
  all three. M0 prove 0.838 / 0.767 / 0.756 s.
- r20261005-162739-8d44: STEP=prove K=14336, the same three builds, GPU.

## Results

Pending.
