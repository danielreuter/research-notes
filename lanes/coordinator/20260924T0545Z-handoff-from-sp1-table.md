# SP1 6.x is 100-bit by its own accounting: every SP1 result (stock and TC_DOT) fails tables.py's 2^-128 rule

From lane sp1-table, 2026-09-24 05:45Z. No action needed for me to proceed; a decision for you / the user if the SP1
column should be rendered anyway.

Source: `sp1-primitives-6.6.0/src/fri_params.rs` (what the pinned `sp1-sdk =6.4.0` resolves to in `Cargo.lock`):
`SP1_TARGET_BITS_OF_SECURITY = 100`, `SP1_PROOF_OF_WORK_BITS = 16`, `CORE_LOG_BLOWUP = 2`, queries =
`unique_decoding_queries` (unique-decoding regime, i.e. provable, not conjectured: 124 queries at rate 1/4); field
KoalaBear^4, jagged PCS (`sp1-prover-6.6.0/scripts/gen_soundcalc_toml.rs`). These are compile-time constants of SP1 itself:
reaching 2^-128 means modifying SP1, which the stock column excludes.

What I record: `security.target = -100`, `security.achieved_log2 = -100 + log2(number of shard proofs)` (union bound;
a B=4096 core proof has tens of shards), with the source above in the fingerprint. tables.py will then reject the cell
with "security.target is -100, need <= -128" as well as (until verify-night) "not independently verified". I proceed
with the full contract otherwise (frozen instances, A100 SXM4 80GB, phase buckets, dumps, independent verification
handoff), so the cell is one rule away from rendering if the user so decides. Told sp1-tcdot (same SP1 core).
