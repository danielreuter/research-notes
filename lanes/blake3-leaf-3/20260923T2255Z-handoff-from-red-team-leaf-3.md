# red-team-leaf-3 -> blake3-leaf-3 (22:55Z): no finding on the leaf; inherit the shared steps pin

* **Role key, half-block pairing, malformed-frame domain: no break** at 1db0008 / 4d8668b
  (`lane/red-team-leaf-3` `backends/direct/ligero/redteam/leaf3_blake3_frame.py`, exit 0).
  * Malformed digest rows map to `SHA-256(MALFORMED_TAG || elems)`.
  * No malformed frame collides with a well-formed BLAKE3 root.
  * Roles are separated.
  * Half-block parity comes from the carried position (Rust mirror read).
* **H2 (shared, BLOCKING):** the pinned verifier does not bind `statement.steps` (`verify.rs:1077`). For BLAKE3 I found no
  collision (the header frames `n_chunks`), but a pinned `+blake3` accept does not fix K until steps is pinned per relation.
  The fix is going into shared code (verify-rs-3 / ajtai-leaf-3); re-pin if your digests change, and add one steps-mismatch
  negative.
* **Table 1 line:** binding = BLAKE3 collision resistance with role-keyed, `n_chunks`-framed leaves, plus SHA-256 collision
  resistance for the tagged malformed-frame domain. Deterministic digests, not hiding.
