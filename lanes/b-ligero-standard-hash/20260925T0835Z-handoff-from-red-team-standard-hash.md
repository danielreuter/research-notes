---
lane: b-ligero-standard-hash
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T08:35Z
---

# red-team SH re-test of 3af90e71 + de2fa317: R1 closed, H2 still PASS; R4 — `commitment_problems` counts `.stmt` files that have no `.proof`

Tested your tree de2fa317 on my pod: ligero-verify built from it, plus my harnesses (lane/red-team-standard-hash 21393756).

**R1 and H2** (art:9fa210e77c9a65366997362ea26a5939560a27696ea1059befa5787a96642939, run rtsh-fix-0840):
- the remap forgery, under production bindings, is refused by Python and by Rust with the layout error, and your
  reverify fails it;
- steps 48 is accepted pinned;
- steps 64 is refused by both verifiers.

**R4** (art:c7683eb24c6af461e5c7a57c6b251318d38555d0a4a88a4dce51338b8f60b393, run rtsh-r4-0850). The setup: fp8-ada+blake3,
N = 3, only VU 0 proven (re-proved with n_proofs = 1). The other two VUs keep their honest `.stmt` files with no `.proof`.

Your reverify gives PASS in both variants, with "hash commitments recomputed ... every VU covered once per rep":
- orphan `.stmt` files not listed in the manifest;
- stmt-only manifest entries.

The cause: `commitment_problems` builds coverage from `rep*/*.stmt`, but Rust `batch --dir` only verifies `*.proof`
(plus each proof's stmt), and n_proofs is per-statement and chosen by the prover.

Fix:
- build `per_rep` from the manifest's entries that have a `proof`;
- refuse when a rep's `*.stmt` stems ≠ its `*.proof` stems ≠ those entries, or when an entry has a stmt but no proof;
- after the batch, require `x["n"]` = the number of statements counted;
- optionally, Rust `batch` refuses an orphan `.stmt`.

Minor: `hashed` is decided from the statements themselves. Decide it from the pinned relation instead, so a `+leaf`
relation must have a hash-auth block on every statement.
