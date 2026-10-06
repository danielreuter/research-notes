---
id: proofs/20261005T1536Z-finding-rec-step2
campaign: flock
lane: proofs
kind: finding
status: active
repo: danielreuter/verity
origin: bc-2a00fbff-762d-5c36-a641-1bbff50ddb4d (rec-reprice, for the proofs coordinator bc-8416bc72)
---

# Recursion rollout step 2: V*'s algebra reads the inner's messages and sums, the comb is public

Question (rollout plan §3 step 2): once the algebra's private words come only from registered reads of the inner's c_k and
openings, the consistency sums come out of the openings, and the inner circuit's combination is a public input the verifier
computes, is V* sound for the inner session (every forged message, sum or combination rejected by serve, Lean and upstream
replay), and what does V* cost then at K = 4096, m = 35 against the 5.85 s outer prove (note:proofs/20261005T0633Z-finding-rec-reprice)?

## Step 1: the restack onto the layout move (done)

- `cursor/rec-algebra-95d4` (#1081): 600a5eebc merged with the move's base 2095960db by hand (one conflict,
  `circuit_check/targets.py`: both the gf2k and the Merkle roots), then `tools/move/restack.py --onto origin/main`, clean:
  d4c745660, pushed as a fast-forward. Its tests pass on the moved tree (test_rec_algebra 11, test_boolean_gf2k 11,
  test_refs_take 40).
- `cursor/rec-reprice-95d4`: restack.py's base and script steps clean, its merge onto d4c745660 conflicted (add/add in
  InnerClaims.lean and inner_claims.json, the root list in targets.py) and was resolved by hand with f0dde01ec as the base:
  13b7a04d1. On top, 454e3cd86: the rec pod scripts' PYTHONPATH gains the catalog, the kernels and experimental (rec_algebra
  imports verity_catalog). The rec tests pass on the moved tree (34 passed, 2 skipped).

## Step 2: the commits (`cursor/rec-step2-95d4`, on rec-reprice 454e3cd86)

- db6c38e3a: the rec proxy commits each round's free message as one row under one salt (c_k = one commitment a round).
- 9a46bd243 (a): `RecOpen_v2` adds each opening's consistency terms to a running sum the prover registers as one chain
  (`rec-acc`): GfScale moves into RecOpen (ports `acc` in, `coef` public, `acc_out` out), and `rec_outer` stages a level
  against the chain with the verifier's coefficients. circuit-check RecOpen_v2{LANES=8,H=1}: ok, 0 failures (warn
  redundant-gates/ir 16,600; not lowered, about 1.48M ANDs over the 60,000 budget), 2,338 s.
- 5a1d6500d (b): `InnerRepCheck_v1{S}` reads one row port per absorbing round (`m<i>`, a registered read of the round's c_k,
  `rec-c<i>`), the chain's rows either side of the rep's openings (`acc0`, `acc1`), and v public with the comb last.
  circuit-check InnerRepCheck_v1{S={046a3fe0d3f7}}: ok, 0 failures, 26 vectors, 0 mismatches, pinned at 2,187 ANDs, 293 s.
- d45a47fb8 (c): `tests/lean/InnerFold.lean` computes the extra claims and each rep's comb from the inner statement and the
  coins alone (no proof read; matches InnerClaims' dump on the fixture, opt-in test 14:06 interpreted), and
  `verity_flock.rec_vstage` stages V*'s statements from the public record beside the prover's rows, sums and salts, with the
  three forgeries; 85-rec-reprice's `vstage` step replaces `ostage` and `alg`.

Local smoke at m = 25 (the fixture session): the verifier's values 3.2 s, coefficients 0.3 s, the rounds' entries 0.02 s;
the algebra (78 ports, 2,704 products, unit 6.99M rows) holds on both reps and its unit agrees with the reference, staged in
281 s at 13.4 GB; the forged comb stages the same circuit with rep 0's residual 1 nonzero.

## Step 2: the runs (node 1, TAG=k4096s2)

The prover's key moved with the layout move (47340c664cec521f to 5c9218d04c285b4c), so the build step runs again.

| step | run | status |
|---|---|---|
| build | r20261005-194257-3095 | passed: binary 1fb79808 (key 5c9218d04c285b4c), Lean 463f4dea3955a270, inner m = 35, k_log 24, nbl 11, 2,048 instances, circuit 567 MB |
| inner (proxy M0 ×(1+3), replay, rec_vstar; loopback M0 and --zk ×(1+3)) | r20261005-194909-c4fb | passed: proxy prove 0.931 s, session 0.969 s, 218 message rows (one a round), 278 rounds; replay accepted; rec_vstar 1,118 openings; M0 0.755 s; `--zk` 5.34 s prove, 7.53 s session, 6.87 s verify (rank 2.49 s), every session accepted, replay --zk accepted; prover cores 99% busy before each |
| vstage (InnerFold, points, the verifier, alg, forgeries, 7 levels; JOBS=3) | r20261005-195948-5376 | passed (19 min): points 0.65 s; InnerFold 1:38 at 3.0 GB, 6 extras; verifier rows 6.0 s, coefficients 0.39 s, entries 0.04 s; InnerRepCheck_v1{S={5c7461729881}} 111 ports, 2,940 products, unit 7.51M rows (log 23), circuit 816 MB, holds on both reps, unit agrees, 5:16 at 13.8 GB; L0-L6 RecOpen_v2 every query opened and summed against one chain; forged sum (row 559): L0 [rep 1, q 0] and L6 [rep 0, q 31] not summed, residual 10 on both reps; forged comb: residual 1 on rep 0; forged message: one bit of m0's row in inst.bin, pub.bin and registered.json the honest ones |
| build K=14336 (N=512) | r20261005-200059-d507 | passed: m = 35, k_log 26, nbl 9, 512 instances, circuit 1.93 GB, staged 10:20 at 41.4 GB |
| oprove (8 statements ×(1+3), 5 forged ×1, replay --zk) | r20261005-202003-8103 | levels L0-L6 accepted by the prover, serve (4/4) and replay --zk (prove 0.37-1.31 s, serve verify 0.82-1.57 s); the algebra, honest and forged, never proved: the GPU prover takes 64 region claims and the algebra has 125 regions (CUDA 202, link refused), so serve's R7 'no proof' is vacuous; forged sum L0 and L6 stopped by the honest prover's own ZK self-check (batched constraint), also vacuous |
| inner K=14336 | r20261005-202036-af66 | passed: m = 35, k_log 26, 512 instances; proxy prove 0.889 s (222 message rows, 282 rounds), replay accepted, rec_vstar accepted; M0 0.752 s; `--zk` 3.67 s prove, 6.58 s session, serve verify 9.98 s, replay --zk accepted; GPU peak 81.7 GB |
| build (e61704bf4, 5d6034e7a: the prover's region-claim cap 64 → 2,048, two per region of the verifier's 1,024 in range; FC_ZK_SELF_CHECK=skip for a forgery's prover) | r20261005-204822-8403 | passed: binary d2dd3a9a (key 06eddbab6529717e); the restaged inner statement is the same (circuit bfce5c43, public 69ac1551, digest 2602e07c) |
| vstage K=14336, the algebra alone | r20261005-204925-f05e | passed: InnerFold 4:51 at 9.85 GB (6 extras); InnerRepCheck_v1{S={411cbf3083ae}} 113 ports, 2,944 products, unit 7.52M rows, circuit 818 MB, holds on both reps, unit agrees, 5:35 at 13.8 GB; verifier rows 5.2 s |
| oprove on the 2,048-claim prover (forgeries FC_ZK_SELF_CHECK=skip) | r20261005-210107-34e7 | L0-L6 accepted by the prover, serve 4/4 and replay --zk (prove 0.40-1.20 s); forged sum L0 and L6 now proved and rejected by serve and replay --zk ('zk inner: the batched constraint fails'); the algebra, honest and forged, aborted: 'coin tree: round 256 of circuit/rep0 (7 coins) is outside the committed schedule': --zk's coin schedule is 256 rounds a rep (coin_spec_of, Lean Zk.coinSpec), each region is two claims and each claim a ring-switch round, and a rep's other rounds are 107-122 (this run's sessions: m = 29, 6 regions, 242 rounds; m = 32, 10 regions, 288), so a statement takes at most about 70 regions; the algebra has 125 |
| oprove K=14336, the algebra | r20261005-210125-02c4 | the same abort |
| vstage, the algebra in parts (d3f9d15b8: `rec_residuals.parts`, at most 64 regions a part) | r20261005-214203-b6fc | passed: points 0.66 s; InnerFold 1:37 at 3.0 GB, 6 extras; verifier rows 5.4 s, coefficients 0.38 s, entries 0.05 s; L0-L6 RecOpen_v2 (436/212/142/106/86/72/64 instances) every query opened and summed; p0 {S={b4fe4eff4f85}} 55 ports, 63 regions, residuals 0-6, 1,057 products, unit 2,854,913 rows, 324 MB; p1 {S={cc83d4a3e73c}} 9 ports, 21 regions, residuals 7, 8, 9, 12, 1,409 products, 3,616,769 rows, 408 MB; p2 {S={9189915bcf20}} 53 ports, 61 regions, residuals 10, 11, 474 products, 1,175,553 rows, 165 MB; every part holds on both reps and its unit agrees, 6:20 at 10.5 GB; forged comb: p0 residual 1 on rep 0; forged message: p0's m0, rep 0, word 0, bit 0; forged sum (row 559): p2 residual 10 on both reps, L0 [rep 1, q 0] and L6 [rep 0, q 31] not summed |
| vstage K=14336, the algebra in parts | r20261005-214228-ab7a | passed: InnerFold 4:59 at 9.85 GB; p0 {S={3915be1e4dd4}} 54 ports, 64 regions; p1 {S={0d757299bb0a}} 10 ports, 24 regions; p2 {S={11a5c1ad9398}} 53 ports, 61 regions; every part holds on both reps, 6:08 at 10.7 GB |
| oprove K=4096 (10 statements ×(1+3), 11 forged sessions ×1 with FC_ZK_SELF_CHECK=skip, replay --zk) | r20261005-221419-ad0a | passed: every honest session accepted by the prover, serve (4/4) and replay --zk; every forgery rejected in exactly its affected statement (table below) |
| oprove K=14336, the algebra in parts | r20261005-221931-87b2 | passed: p0 0.985 s prove, p1 0.943 s, p2 0.888 s (m 28, k_log 25 each), serve 3.13/3.11/2.86 s, 4/4 accepted, replay --zk accepted |
| lean K=4096 (`verify --zk` on every session; JOBS=3) | r20261005-224601-2a56 | passed: every honest statement accepted, every forgery rejected in exactly its affected statement; four 'no verdict' entries are the pre-split sessions' directories left on the pod by r20261005-210107-34e7 (v-sess/alg, forged-*-alg: Lean finds no `v/…/alg/circuit.txt`, which the parts layout no longer writes) |
| lean K=14336, the algebra in parts | r20261005-224610-bae1 | passed: p0, p1, p2 accepted (verify 49.2/79.0/43.8 s, setup 30.5/75.8/25.5 s); the same stale `alg` entry |

## Step 2: the answer

V* is sound for the inner session on every forgery tried, and the honest session is accepted by all three verifiers. Each
forgery is rejected by serve, upstream `replay --zk` and Lean `verify --zk` in exactly the statement it touches; V* rejects
when any of its statements does. The forgeries' provers ran with `FC_ZK_SELF_CHECK=skip`, so every rejection is the
verifier's own (the honest prover's self-check had stopped forged sum L0 and L6 in r20261005-202003-8103).

| forgery | statement rejected | serve and replay --zk | Lean verify --zk | the other statements |
|---|---|---|---|---|
| comb (rep 0's residual 1) | alg-p0 | zk inner: the batched constraint fails (⟨c, Y⟩ ≠ t + β τ) | the same | alg-p1, alg-p2 accepted (they hold no comb-dependent residual 1) |
| message (one bit of m0's row, rep 0) | alg-p0 | opening: RingSwitch(ClaimMismatch) | opening: ring-switch claim 2 mismatch | alg-p1, alg-p2 accepted (they read no m0) |
| sum (chain row 559) | L0, L6, alg-p2 | zk inner: the batched constraint fails | the same, for all three | alg-p0, alg-p1 accepted |

Cost at K = 4096, m = 35 (node 1, GPU prover on loopback, medians of 3 timed sessions after 1 warm, prover cores 3-28% busy
before each; Lean `verify --zk` once a session, 3 at once):

| statement | prove | session | serve verify | bytes (both reps) | host / GPU peak | Lean verify | Lean setup |
|---|---:|---:|---:|---:|---:|---:|---:|
| L0 RecOpen_v2 (m 32) | 1.195 s | 1.596 s | 1.224 s | 2,132,852 | 9.37 GB / 11,133 MiB | 59.3 s | 80.7 s |
| L1 (m 31) | 0.746 s | 1.126 s | 1.065 s | 2,052,484 | 5.87 GB / 6,845 MiB | 60.3 s | 63.1 s |
| L2 (m 31) | 0.738 s | 1.138 s | 1.046 s | 2,035,972 | 5.83 GB / 6,929 MiB | 53.3 s | 60.0 s |
| L3 (m 30) | 0.544 s | 0.857 s | 0.959 s | 1,934,452 | 4.57 GB / 4,705 MiB | 43.3 s | 42.6 s |
| L4 (m 30) | 0.546 s | 0.852 s | 0.907 s | 1,926,196 | 4.16 GB / 4,669 MiB | 34.9 s | 36.1 s |
| L5 (m 30) | 0.512 s | 0.789 s | 0.863 s | 1,934,452 | 3.85 GB / 4,691 MiB | 31.0 s | 36.0 s |
| L6 (m 29) | 0.467 s | 0.760 s | 0.916 s | 1,693,300 | 3.25 GB / 3,577 MiB | 29.6 s | 29.3 s |
| alg-p0 InnerRepCheck_v1 (m 29, k_log 26) | 1.368 s | 2.866 s | 5.194 s | 2,164,276 | 9.28 GB / 14,591 MiB | 53.6 s | 34.4 s |
| alg-p1 (m 28, k_log 25) | 0.853 s | 1.820 s | 3.181 s | 1,704,884 | 6.14 GB / 8,055 MiB | 50.8 s | 43.7 s |
| alg-p2 (m 28, k_log 25) | 0.929 s | 1.867 s | 3.092 s | 2,035,124 | 5.24 GB / 7,735 MiB | 33.0 s | 18.6 s |
| levels | 4.747 s | 7.119 s | 6.980 s | 13,709,708 | | 311.8 s | 347.8 s |
| algebra | 3.151 s | 6.553 s | 11.468 s | 5,904,284 | | 137.4 s | 96.7 s |
| V* (outer) total | 7.898 s | 13.672 s | 18.448 s | 19,613,992 | 9.37 GB / 14,591 MiB | 449.2 s | 444.6 s |
| phase 1's V* (r20261005-082407-16e7) | 5.846 s | 9.889 s | 12.934 s | 14,867,840 | 12.4 GB / 15.4 GiB | 595.2 s | |
| inner, ZK off, against the proxy (r20261005-194909-c4fb) | 0.931 s | 0.969 s | in V* | | | | |
| today's `--zk`, same build and node (r20261005-194909-c4fb) | 5.34 s | 7.53 s | 6.87 s | | | | |

V* at step 2 costs 7.90 s of prove against phase 1's 5.85 s (1.35×): the levels 4.75 s against 4.30 s (+0.45 s, GfScale
fused into RecOpen_v2 and the chain's ports; phase 1's first run was 4.73 s) and the algebra 3.15 s against 1.54 s (+1.61 s).
The algebra's growth is its three sessions, each with the prover's per-session floor (L6, the smallest level, is 0.47 s), and
its registered reads: 117 row ports, each a digest region of two claims, which serve verifies (5.2 s for p0's 63 regions).
Outer over the inner's ZK-off prove: 8.48× (phase 1 6.68×); outer over today's `--zk`: 1.48×. Lean's numbers are a newer
build than phase 1's (463f4dea against 88a84ea1) and ran 3 at once, so they are not like for like.

K = 14,336: the algebra's three parts prove in 2.816 s (5.548 s session, 9.105 s serve verify, 5,824,668 bytes, Lean verify
172.0 s); V*'s RecOpen levels depend on m alone, so K = 4096's stand, and V* is 7.56 s (phase 1 6.05 s).

What's left for step 2: a red-team grant and a `check --record` with lean-agreement (the coordinator's); fewer algebra parts
(a verifier-side `coinSpec` with more rounds a rep, Rust `coin_spec_of` and Lean `Zk.coinSpec`, would let one statement carry
the 125 regions, but it changes the Lean verifier, which this step does not; without it, a grouping that shares fewer row
ports between parts: the three parts carry 145 regions against the whole's 125).

Step 3 (plain SHA-512 leaves climbing to salted tops, the `top` and `top-salt` forgeries, the GPU decoder and `rec_vstar`
fail-open fixes): note:proofs/20261006T0420Z-finding-rec-step3.
