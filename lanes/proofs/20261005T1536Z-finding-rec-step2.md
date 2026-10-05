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
| vstage, the algebra in parts (d3f9d15b8: `rec_residuals.parts`, at most 64 regions a part; at K=4096 three parts of 55, 9 and 53 row ports, 63, 21 and 61 regions) | r20261005-214203-b6fc | running |
| vstage K=14336, the algebra in parts | r20261005-214228-ab7a | running |
