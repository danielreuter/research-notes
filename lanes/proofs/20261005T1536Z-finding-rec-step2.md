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

## Step 2

In progress.
