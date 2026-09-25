# red-team SH: fp8-ada+blake3 (v5 included-hash, frame-v3 keyed-BLAKE3 rows): FAIL

From red-team-standard-hash, 07:35Z. Evidence `art:2b51c5fdec29cfd6739e28fab4683899beb66883cdb086acd33c86ff369e8efb`
(fixture tree + harness), harness `backends/direct/ligero/redteam/rtsh_remap_e2e.py` on `lane/red-team-standard-hash` 7a8268cf,
pod run `rtsh-r1c-0727`. Verifier: `ligero-verify` built from main 00ffe398's crate (no Rust change on my branch).

**Table 2 consequence:** every B-Ligero `included-hash` (v5/v6) statement is affected, whatever the leaf (`+blake3`, `+poseidon2`,
`+ajtai-*`, and the coming `sha256/row/v1`). The overnight `+blake3` target cell, and any blake3-80gb / b-ligero-sha256 cell on this
verify path, is **pulled until R1 and R2 are fixed** (an independent verification done with today's `reverify.py` does not count).

**R1 (BREAK): the (vu, x, W) leaf triple is prover-chosen.** A v5 statement names per VU `vu_index` (its y leaf), `x_index`, `w_index`.
Rust `auth::check_hashed` and Python `hashauth.verify_hash_auth` check only that the leaves open under the roots; nothing derives
x/W from vu and the committed set's layout (honest prover: x = W = vu unshared, `(v // nw, v % nw)` for a tile). Minimal accepted
counterexample (2 VUs, pinned sys_id 71f39e44, FS, 2^-128.x): the committed y of VU 0 is VU 1's true output (a swapped/replayed
output), the x and W roots are the honest instance set's (9331d7fb / 3a39a0e4), the statement claims VU 0 on (x 1, W 1).
Python ACCEPT, Rust `verify` PINNED ACCEPT, `reverify.verify_tree` PASS. Control: same commitment, honest mapping: rejected
(`auth: y: multiproof rejected`). **Fix:** the verifier derives the triple from `vu_index` (unshared: x = W = vu; tile: from the
verifier's expected (nx, nw)) in Rust and Python, and refuses any other; one negative per the fixture above.

**R2 (BLOCKING): independent re-verification recomputes nothing from the instance set.** `reverify.py` checks custody, the system pin
and a Rust batch accept. It never recomputes the a/b/y roots from the instance set, never checks the trees' `binding` (the frame-v3
domain, `hashauth.binding_digest(dataset, manifest, lo, hi, K, tree, schema)`) or `count`, and never checks that the sub-batches'
`vu_index` cover the claimed range. Rust reads binding/owner/count/root from the statement, so frame-v3's "verifier-derived domain"
is prover-described in B-Ligero. In the fixture above the y root differs from the honest set's and reverify still PASSES.
TABLES.md admissibility 6 requires the recomputation. **Fix:** reverify (or the Rust verifier given `--expect-roots`) recomputes the
three bindings and roots from the instance set by id and range, compares them to every statement's, and checks VU coverage.

Also routed to b-ligero-standard-hash (producer). H2 steps pin and the BLAKE3 gadget itself: no break so far (report).
