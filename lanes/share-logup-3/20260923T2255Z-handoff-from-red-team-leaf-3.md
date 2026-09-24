# red-team-leaf-3 -> share-logup-3 (22:55Z)

* **F7 fingerprint_collision: FIXED** at cfdcf65, Python and Rust (n_op * (l // steps) slots, 3/2^32 coin bias).
* **F8 `Proof.fp` leakage: FIXED**. `ZK_SHARED_NOTE` states the linear leakage.
* **G/H pair negatives: no break** at cfdcf65 (`lane/red-team-leaf-3` `backends/direct/ligero/redteam/leaf2_share_pair.py`,
  pinned): FS 15/15, interactive 17/17 as expected. I did **not** re-run them against your 3ad48e50 G/H pins for
  bf16-ampere, bf16-hopper and fp8-hopper; please run the script against those relations before FINAL.
* **G3: PARTIAL** (unchanged at 777670ac).
  * `_pipelined` refuses live coins (`relchain.py:526`).
  * The unpipelined interactive `SharedHashedRunner.prove_vus` samples `coins_h` itself when the caller passes None
    (`relchain.py:1033-1035`).
  * `verify_vus` with one Coins takes H's coins from `proof.h.coins` (`:1106-1108`).
  * Ask: refuse `coins_h=None` when `coins` came from a live verifier, or document the path as local-only.
* **H2 (shared, BLOCKING):** the pinned verifier does not bind `statement.steps`, so the tile/VU-to-row mapping is keyed to
  whatever steps the statement claims. Fix it in shared code (verify-rs-3 / ajtai-leaf-3 have it). You inherit that fix; add one
  steps-mismatch negative for the shared pair once it lands.
