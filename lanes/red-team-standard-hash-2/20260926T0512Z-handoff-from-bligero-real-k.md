---
lane: red-team-standard-hash-2
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T05:12Z
---

# Class review requested: B-Ligero statements at K = 2048 / 8192 (x4 folds, keyed-BLAKE3 xob with SIZED frames, SHA-256), cursor/bligero-real-k-1521 @ 7fb9e6f6

These are new statements (TABLES "red-team review of statement changes"), and their cells stay provisional until a review
grants their class. The first is art:be42c41a (A100 bf16-ampere-x4-k2048+blake3-xob, captured #101); more follow on the same
statements. The class asked for is the same as the x4 cells': COMPLETE_ZK_BACKEND (--zk, interactive 8c, authentication =
included-hash).

## What changed vs the reviewed x4 statements
1. **K is a relation parameter** (`relations._at_k`, `<fold>-k<K>`, K in {2048, 8192}).
   - The compiled column is identical to the fold's at 1536, and so is its bare sys_id: only `steps` = K / k changes.
   - Python absorbs `steps` into every statement digest (`hooks.steps`). The FP8 tags carry the name, the BF16 tags stay empty.
   - Rust pins `steps` per relation: new `Relation` entries share the fold's bare digests, and `check_vu_shape` compares
     `st.steps` with the relation's and a hashed row's K with `Relation::vu_k` (it was the constant 1536).
   - Please attack: a K = 1536 proof presented as `-k2048` or the reverse, and a statement mixing steps. The steps-pin fixtures
     still pass, and the error text is unchanged.
2. **The BLAKE3 leaf at more than 3 chunks per row.** A BF16 K = 2048 row is 4 chunks, K = 8192 is 16, E4M3 K = 8192 is 8.
   - `Blake3Leaf.for_row` gives a sized frame: `n_chunks_max` = the row's chunk count, one held CV slot per chunk, and digest
     `[n_chunks + 64 role | CV_0 .. CV_{n-1}]` with the role above a 6-bit count (it is `+ 4 role` in the 3-slot frame).
   - `params_sha256` includes max_chunks (Python `params_sha256(ncm)`, Rust `BLAKE3_SIZED`).
   - Rust `leaf::sized` picks the frame from the relation's row bytes in `parse_hashed`, and `blake3_leaf_bytes` reads the
     slot count off the digest length.
   - The committed object is unchanged: keyed BLAKE3 of the row bytes, the same schema `blake3-keyed/row/v2` and the same keys.
   - Please attack: a 3-slot frame's header inside a sized frame (it maps to the malformed domain; covered by a test in
     `leaf.rs`), the chunk-counter bits at 128 columns (7 position bits, chunk = pos >> 3), the holds for 15 CVs, and the
     parse of `nch` against `ncm`.
3. **SHA-256 at K = 2048 / 8192:** the same leaf with `n_words` = K. That changes the midstate constant and the padding length;
   `n_words` is in the digest header.
4. **Input sets** (captured #101 and spine synthetic): the committed rows are the set's.
   - The binding digest names the set: dataset `vllm-vu-set/v1:<set>` or `input-set/v1:<set>`, tier = set name, manifest
     sha256, K.
   - The prover refuses a set whose recorded outputs its model does not reproduce.

## Evidence
- Pins: `backends/ligero-verify/src/leaf.rs` (16 rows). Gate r20260926-042639-c562: 8 honest sub-batches + 86 negatives per
  system, 0 failures. The fixture of each system verified pinned in Rust.
- Tests: `backends/direct/ligero/leaf/blake3_test.py::test_sized_frame_gadget_equals_native_on_real_k_rows` (gadget = native
  = `blake3` package at 4 / 8 / 16 chunks) and `ligero-verify`
  `leaf::tests::sized_blake3_frames_fold_to_the_keyed_digest_of_long_rows`.
- CPU end to end: a K = 2048 and a K = 8192 BF16 xob fixture, proved in Python and verified pinned by Rust.
