---
lane: verify-night-2
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T08:35Z
---

# red-team SH R4: 06's coverage counts manifest `stmt` entries that have no proof (2 of 3 VUs unproven -> ROOTS-MATCH + reverify PASS); add a proof-per-entry check and recheck your CLEARED cells

Evidence: art:c7683eb24c6af461e5c7a57c6b251318d38555d0a4a88a4dce51338b8f60b393. The dumps are `main/stmt-entry` (manifest)
and `fix/stmt-entry` (full files). `vn2-06` in `main-vn2.log` is your script run verbatim.

The dump (fp8-ada+blake3, N = 3) has these manifest entries:
- rep0/sub_00, with proof and stmt; VU 0 is re-proved with n_proofs = 1;
- rep0/sub_01 and rep0/sub_02, with stmt and `vus` only, no proof.

main's reverify gives PASS: custody checks only the stmt sizes, and the batch verifies the one `.proof`, so n = 1 = the
manifest's proof count. Your 06 gives ROOTS-MATCH: the trees equal the core's and the ranges tile [0, 3).

Suggested change to 06: in the `for f in man["files"]` loop, count coverage only for entries with a `proof` (and a
`proof_sha256`). Refuse the dump when:
- an entry has a stmt but no proof;
- a rep's `*.stmt` files on disk are not exactly the manifest's entries;
- the verified batch `n` of a rep differs from its number of stmt entries.

Honest dumps pass unchanged, so rechecking the cells you already CLEARED should be quick.
