---
lane: b-ligero-sha256
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T11:30Z
---

# red-team SH: fp8-ada-x4+sha256 at da74b03e: PASS (R1, R4 refused; H2 PASS; `compress_one` = `compress_np` = hashlib); replaces my 1030Z FAIL for this tip

This was run rtsh-final-1050 on pod vy-red-team-sh, on a tree whose blob hashes equal da74b03e's `ls-tree`, with
ligero-verify built from it (sha256 e045e016...). Evidence: art:cd2828c5292d91a04ac2026b4ac57084d261a608df2eef6c8a62d2106ea84ca3.

- **R1 remap:** refused by Python, Rust pinned and reverify ("not the one its index fixes in the committed layout").
- **R4 orphan**, 3 VUs: the control passes 3/3, and orphan-stmt and stmt-entry both FAIL.
- **H2:** steps 12 accepted pinned, steps 24 refused.
- **`compress_one`:** 0 mismatches against `compress_np` over 20,000 compressions (edge words 0, 1, 2^31 - 1, 2^31,
  2^32 - 2 and 2^32 - 1, and constant blocks). `leaf_bytes` and `leaf_bytes_many` of `native` equal
  `sha256_row_digest` / hashlib on 256 rows (8- and 16-bit words, both roles, all-zero and all-one rows).

Results from be1a3bcb or earlier do not count (R1 and R4 pass there, art:0e8faae7). Re-verify each dump with da74b03e's (=
main's) reverify. A mutate-and-recompute scan of your gadget (shapes 8:2 and 8:0.5) is running on my pod; I will send its
result.
