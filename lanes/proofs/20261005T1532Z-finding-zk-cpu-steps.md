---
id: proofs/20261005T1532Z-finding-zk-cpu-steps
campaign: flock
lane: proofs
kind: finding
status: done
repo: danielreuter/verity
origin: bc-b63aca89-377c-5e17-99a5-ace054ba29d0 (zk-cpu-steps, for the proofs coordinator bc-8416bc72)
---

# `--zk`'s two single-threaded CPU steps off the critical path (K = 4096 and 14,336, node 1)

**Question.** Does C-Flock's `--zk` prove at K = 4096 drop from about 5.2 s to about 1.8 s on node 1 when the mask-rank check
(`zk_veil::mask_rank_ok`, about 2.5 s a session, `ZKRANK`) and level 0's hiding draw (`level0_zk`, about 1.0 s) come off the
critical path, with byte-identical proofs and every session still accepted by serve, upstream's `replay --zk` and Lean's
`verify --zk`?

**Answer.** Yes, with one more step than the two named. At K = 4096 the `--zk` prove goes from 4.739 s to 1.880 s (median of 3
timed sessions after 1 warm, the same job, the same node), the session from 6.58 s to 3.74 s; at K = 14,336 from 3.548 s to
2.346 s. The mask-rank check is 2 ms a session where it was 2.2 s (K = 4096) and 0.6 s (K = 14,336). Parallelising the
level-0 draw alone (0.058 s, from about 0.8 s) left a 0.47 s wait: `make_zkrep` cloned the whole `Level0Zk` (four 2^22-word
extra lanes, 256 MB) once per rep on one thread. Writing those copies on rayon's threads takes the wait to 0.18 s. Proofs are
byte-identical across the three builds: `prover_is_deterministic --zk --gpu` gives the same transcript digest (stream messages
and coins, the link, both reps' proof SHA-512s) in each build, pinned with `--expect-transcript`. Every session was accepted
by serve, and the last `--zk` session of each build and size by upstream's `replay --zk` and Lean's `verify --zk`.

## Changes (branch `cursor/zk-cpu-steps-95d4` off main 378453fb3)

- f6997de29, ee2638800, 2b34204a1: `backends/flock/pod/86-zk-cpu-steps.sh` (85-rec-reprice.sh's statements and loopback
  machinery; builds keyed by their sources as 85 keys them; STEP=build | prove | lean). The before build is f6997de29, whose
  live crate is main's.
- 5c491f8a2: `mask_rank_ok` inserts each word's row into an echelon basis (a vector per pivot column, its lowest set bit) and
  stops once the rank is `128 k`. That is the column count, so the result is the Gauss–Jordan's exactly. The old function
  stays in the tests as the oracle, checked on random, repeated, zero, Boolean, too-short and empty inputs and at the proved
  sizes (2048 blocks × 2^17 and 512 × 2^19, release only).
- b7a476bb5: `level0_zk` draws its lanes on rayon's threads, in 4096-word pieces, with one copy of the `ProverRng` per worker
  (`ProverRng::f128s_lanes`). Test: each lane equals the sequential `f128s` at its address, for lane lengths that end inside a
  ChaCha20 block, at a piece's end and inside a later piece, and after the generator has read other streams. `ZKL0` prints
  the draw's time.
- 8d8c26fb3: `make_zkrep` writes each rep's copy of the extra lanes on rayon's threads, and `zk_prepare` prints `ZKPRE`.
- 1d54bed32: live `PROTOCOL.md` §6, `mask_rank_ok`'s cost.

## Results (node 1, `vy-nebius-1`, RTX PRO 6000 sm_120, CUDA 13.3.1; prover on 16 cores, verifier on the job's other 16)

Builds: before 5c9218d04c285b4c (main's live crate), after dfae70f600a9cf7b (the echelon rank check and the parallel draw),
after2 4f4efe413970c2cd (plus the parallel per-rep copy). The level-0 wait is rep 0's `prove_s` minus its `t.prove` bucket:
the `--zk` preparation's time after the witness is ready.

K = 4096, N = 2048 (m = 35, k_log = 24), r20261005-161736-5c59 (art:1779537b4762224c0de5ef44d2e651d467ccd4050eff432e30918a3ad16a9c80):

| | before | after | after2 |
|---|---|---|---|
| `--zk` prove_total_s | 4.739 | 2.187 | 1.880 |
| ZKRANK s / session | 2.180 | 0.002 | 0.002 |
| level-0 draw (ZKL0) s | not printed | 0.058 | 0.058 |
| level-0 wait s | 0.832 | 0.472 | 0.183 |
| `--zk` session_s | 6.58 | 4.07 | 3.74 |
| `--zk` serve verify s | 5.60 | 5.79 | 5.80 |
| M0 prove_total_s / session_s / serve verify s | 0.838 / 0.996 / 0.314 | 0.767 / 0.874 / 0.260 | 0.756 / 0.856 / 0.269 |
| serve verdicts (`--zk`, M0) | 4/4, 4/4 | 4/4, 4/4 | 4/4, 4/4 |
| upstream `replay --zk` | accepted, 15.1 s | accepted, 14.4 s | accepted, 14.3 s |
| Lean `verify --zk` (r20261005-164516-8952) | accepted, 109 s | accepted, 109 s | accepted, 109 s |
| transcript digest | dc75aed4… | dc75aed4… (pinned) | dc75aed4… (pinned) |

A second K = 4096 job, r20261005-155947-8f55 (art:66146905b79304b51b2e71db409855d76994f6142fadbe4ad317c5abf526daba), before and
after only: `--zk` prove 4.965 / 2.410 s, ZKRANK 2.220 / 0.002 s, level-0 wait 0.965 / 0.608 s, session 6.47 / 4.28 s, serve
verify 4.68 / 5.63 s, M0 0.788 / 0.780 s. All verdicts accepted, and the same digest in both builds.

K = 14,336, N = 512, r20261005-162739-8d44 (art:2d4fbce6a6cde16cbdd21756eaa81b631c8b4f75d6c5b649d633c8b45a61f98d):

| | before | after | after2 |
|---|---|---|---|
| `--zk` prove_total_s | 3.548 | 2.681 | 2.346 |
| ZKRANK s / session | 0.594 | 0.002 | 0.002 |
| level-0 draw (ZKL0) s | not printed | 0.059 | 0.059 |
| level-0 wait s | 0.799 | 0.454 | 0.169 |
| `--zk` session_s | 6.34 | 5.54 | 5.19 |
| `--zk` serve verify s | 9.17 | 9.37 | 9.28 |
| M0 prove_total_s | 0.770 | 0.810 | 0.790 |
| serve verdicts (`--zk`, M0) | 4/4, 4/4 | 4/4, 4/4 | 4/4, 4/4 |
| upstream `replay --zk` | accepted, 41.3 s | accepted, 44.1 s | accepted, 45.4 s |
| Lean `verify --zk` (r20261005-164522-ba6d) | accepted, 317 s | accepted, 316 s | accepted, 316 s |
| transcript digest | 673b37f9… | 673b37f9… (pinned) | 673b37f9… (pinned) |

Builds: r20261005-153137-feee (before, and both statements staged: shape 430e5aad with M0 statement digest 2602e07c…, the
baseline's, and shape bac929c3), r20261005-155357-a60a (after), r20261005-161240-0785 (after2). Lean (sources
463f4dea3955a270): r20261005-164516-8952 (art:b292141df4ff02cfe9a335eac06bc58f751fef7a4debbf4e362f771b0dc65737), r20261005-164522-ba6d
(art:09d9161217612de17628f6e7157df8187ce92eca7afe6a89275d939dfd305475).

## What it means, and what is left

- Today's before build is a little faster than the rec-reprice baseline on the same statement (4.74–4.97 s against 5.21 s at
  K = 4096, 3.55 s against 4.06 s at K = 14,336). The node and the machinery are the same; the difference is between runs.
- After this change the session is bounded by the verifier, not the prover. Serve's `--zk` verify takes 5.8 s at K = 4096 and
  9.3 s at K = 14,336, and the sessions overlap only because serve verifies several at once (`FC_VERIFY_AHEAD`).
- What `--zk` still adds over M0, per rep at after2: rep 1 encodes and commits again (0.165 s; M0's rep 1 reuses rep 0's
  commitment, and `--zk` turns that off), the inner proof's replay (0.09 s at K = 4096, 0.35 s at K = 14,336), and the 0.18 s
  level-0 wait. The first session's `ZKPRE` is 1.4 s, the cold allocations, and it falls in the warm session.
- No prover identity, statement digest or recorded vector changed: the statement digests are equal across builds (M0
  2602e07c…, `--zk` 09a9cb86… at K = 4096), and proof bytes are equal (1,179,202 per rep at K = 4096, 1,179,330 at
  K = 14,336).

## Tests (head 1d54bed32)

- `check_build.sh` and `check_build.sh test` on the last Rust commit (8d8c26fb3): `cargo check` passed in all three feature
  sets. flock-live `--lib --release` passed: `sha512` 82 passed, 1 ignored; `sha512,glue,seed-injection` 89 passed, 2 ignored.
  The upstream crates' tests all passed.
- `suites.py verity-flock repository` at 1d54bed32, with nothing cached: `verity-flock` had 587 passed and 11 skipped (all
  opt-in heavy checks), and `repository` had 42 passed.

The draft PR's title and body are in the Project store at `internal/zk-cpu-steps-pr-body.md`, for the coordinator to open.
