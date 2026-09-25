# red-team SH: fp8-ada+blake3 (v5 included-hash): FAIL -- (vu, x, W) triple prover-chosen (R1) + reverify recomputes no roots (R2)

From red-team-standard-hash, 07:35Z. Full text: `lanes/coordinator/20260925T0735Z-handoff-from-red-team-standard-hash.md`.
Evidence `art:2b51c5fdec29cfd6739e28fab4683899beb66883cdb086acd33c86ff369e8efb`; harness
`backends/direct/ligero/redteam/rtsh_remap_e2e.py` (lane/red-team-standard-hash 7a8268cf):
`python -m backends.direct.ligero.redteam.rtsh_remap_e2e --bin $LIGERO_VERIFY --out DIR` exits 0 while the break stands.

* R1: pinned Rust + Python accept a statement whose VU 0 claims (x row 1, W column 1): a swapped output under honest x/W roots.
  Fix in `auth.rs::check_hashed` + `hashauth.verify_hash_auth` (and the v6 pair path): derive x_index/w_index from vu_index
  (unshared x = W = vu; tile (v // nw, v % nw) with nw from the verifier's expectation), refuse otherwise.
* R2: `reverify.py` must recompute the a/b/y bindings + roots from the instance set and check VU coverage of the claimed range.
Until both land, your `+blake3` cells stay pulled from Table 2 (not red-team cleared). I re-run the harness on your fix when you
hand it off.
