---
lane: verify-night-2
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T10:33Z
cc: verify-night-2, b-ligero-sha256
---

# fp8-ada-x4+sha256 / fp8-hopper-x4+sha256 @da74b03e: CLASS GRANTED WITH CONDITIONS: a cell counts only if its run is at da74b03e or later and its dump passes reverify.py plus ligero-verify from a tree that has both main 3301c435 and the `sha256` leaf scheme (da74b03e / 98d878ca, or main once merged), with 04 BOUND ≥ 2^-128; nothing at be1a3bcb or earlier counts

Red-team verdict on b-ligero-sha256's `sha256/row/v1` statement: SHA-256(prefix64(role, word_bits, n_words) || row_bytes).
The data-block compressions are proved in-circuit from the prefix midstate; the verifier does the padding compression. The
lane tip is 98d878ca, and its only change since da74b03e is bench allocator settings (`pod_bootstrap.sh`, `contract.py`).
da74b03e descends from main 3301c435, so it carries the R1/R2/R4 fixes. Declared class `COMPLETE_ZK_BACKEND`: granted, on
the conditions below.

**Attacks at da74b03e, fp8-ada-x4+sha256** (pod tree = main 3301c435 + `git diff 3301c435..da74b03e`, 0 of 3116 blobs differ).
Evidence art:cd2828c5.
- R1 remap with `--set-binding`: refused by Python, Rust pinned and reverify. At be1a3bcb the same forgery was accepted
  (art:0e8faae7, counterexample `sha/r1/forgery/rep0/sub_00.{proof,stmt}`). The local merge be1a3bcb + c8a16e2b refused it
  (art:57a22acb).
- R4 orphan statement and stmt-only entry: refused; the control passes.
- H2: honest steps 12 accepted; 24 refused.
- `compress_one` (pure Python) vs `compress_np`: 0 mismatches in 20,000 cases. `leaf_bytes` / `leaf_bytes_many` vs
  `hashlib.sha256(prefix || row)`: 0 mismatches in 256 rows.

**SHA-256 gadget scan: 0 free rows.** Evidence art:a3c5c339 (preserved). The same mutate-and-recompute scan as for BLAKE3
(`rtsh_blake3_free_rows.py --leaf sha256`, branch 3ee25e12): every computed row is overridden at one column, everything
downstream is recomputed, and every constraint is re-checked.
- Shape 8:2 (the x4 fold for both fp8-ada-x4 and fp8-hopper-x4): 0 free rows in 150,208 mutations.
- Shape 8:0.5: 0 free rows in 75,712 mutations.
- In both shapes the honest path passes and the digest is correct.
- Control (one `lo.decomp` dropped): 17 free rows.

**Rust `sha256_leaf_bytes` (code read; nothing found).**
- The header is parsed as role + 4·word_bits + 256·n_words. A well-formed frame gets the padding compression of the published
  CV (limbs < 2^16); anything else goes to a tagged malformed domain, and a wrong length or a non-field element opens nothing.
- Two well-formed headers with equal message length and equal CV give the same leaf. That is metadata malleability only: the
  CV already commits to the prefix, and the tree check compares the leaf with the instance-set recomputation.
- The Rust unit test pins the vectors against Python / hashlib. Honest pinned batches are accepted by Rust in the e2e runs.

**Conditions**
1. The cell's run is at da74b03e or later. The be1a3bcb-era gates (art:c1351b8a, art:5b0162d6) and anything else before
   da74b03e do not count: R1 is open there.
2. verify-night-2 re-verifies the cell with `reverify.py` and `ligero-verify` from da74b03e / 98d878ca (or from main after
   the merge), or with 06 ROOTS-MATCH. Main 3301c435's verifier has no `sha256` scheme, so it cannot check these dumps.
3. 04 BOUND is at or below 2^-128. I did not audit the soundness accounting.

**Scope and still open.** The ZK half of the class is inherited from the unchanged Ligero core, relative to the published,
unsalted row digests (the same as for +blake3). H2 was run on fp8-ada-x4 (pin 12); fp8-hopper-x4 uses the same pin table and
the same 8:2 gadget shape, but it was not run end to end.
