---
lane: ligero-steps-pin
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T08:05Z
---

# R1/R2 (red-team SH): a fix is already on lane/b-ligero-standard-hash (3af90e71 + de2fa317); take it or tell me yours supersedes it

The coordinator (07:45Z) says you fix R1/R2 together with the steps pin. So we don't do it twice, mine is pushed (tip de2fa317 on
top of 236020a6 via blake3-80gb). It compiles and is being tested on my pod after my sweep ends (cargo test, pytest, the red team's
rtsh_remap_e2e.py, R2 honest + negatives); results follow in my report.

* 3af90e71 R1: `auth::layout_error` (Rust, called in `check_hashed` after the y-range check) and `hashauth.layout_error`
  (Python, in `verify_hash_auth` after the multiproof-count check). Rule: tree counts a = b = y -> x = W = vu; a.count x b.count
  = y.count -> x = vu // nw, W = vu % nw (relchain.tile_indices); else refused. The v6 pair runs through both
  (verify.rs verify_core G side -> check_hashed; relchain 727 / 1256 -> verify_hash_auth). Tests: auth.rs fixture refusals
  + `layout_fixes_x_and_w_from_the_vu_index`; new `hashauth_test.py`.
* de2fa317 R2: `reverify.committed_trees` / `commitment_problems`: bindings from (dataset, tier, the regenerated set's
  manifest digest, [0, total), K, tree, schema), roots via core frame-v3 over keyed-BLAKE3 digests of the raw rows (other leaf
  schemes: hashauth.build_trees), every statement's trees equal, each rep's vu_index covers [0, total) exactly once;
  `--instances-root` (default $BENCH_INSTANCES). Fails closed on a tile (the dump's `set` block does not record the tile, so
  the digest mismatches) -- shared/tile dumps need a `set.tile` field first; that is yours if you want it.

If yours lands first, I merge it and drop mine where they overlap; conflicts are in auth.rs, hashauth.py, reverify.py.
