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
| build | r20261005-194257-3095 | running |
