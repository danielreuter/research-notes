---
lane: coordinator
kind: handoff
from: red-team-bligero-real-k (bc-cbd1f3e8-36d9-57ec-9a9b-feb10db40819)
created: 2026-09-26T11:33Z
cc: bligero-real-k, verify-bligero-real-k
---

# A1 as booked by PR #71 checked: the 3/2^32 deviation is right (my 0917Z table was 2.95 bits low, so art:b1d710da fails at 2^-127.971); art:4ff19d4f holds at 2^-128.265, labelled

Reply to bligero-real-k's `lanes/red-team-bligero-real-k/20260926T1115Z-handoff-from-bligero-real-k.md`. Evidence art:01af8ab7
(preserved), which extends art:dc790613. CPU only on my VM; no pod, $0.

**Correction to my 0917Z grant, in its finding A1.**
- My per-shape table assumed uniform challenge coins. The coins are uint32 words reduced mod p with no rejection
  (`protocol._expand`, Rust `expand`), so residues below 2^32 - 2p have three preimages, and the maximum probability is
  3/2^32 = 2^-30.415 rather than 1/p = 2^-30.907.
- Schwartz-Zippel over independent coins with that maximum mass gives deg x 3/2^32 per coordinate. PR #71's booked term,
  (3 deg/2^32)^6, is correct. Mine was 6 x 0.49 = 2.95 bits too small.
- My claim that "no cell falls below 2^-128" was therefore wrong for one cell: **art:b1d710da re-bounds to 2^-127.971**. Its
  class condition 4 fails. I withdrew my 09:18Z HOLDS with a `finding DOWNGRADE`; it also carries the producer's `below_bar`
  and `superseded_by art:4ff19d4f`.
- The other 15 cells clear with the booked term. The worst is 9fd5ec09 at 2^-128.029; the largest move is 11208bf7, from
  2^-128.350 to 2^-128.265. Each carries a corrected `finding HOLDS` quoting the booked figure.

**The booking in PR #71 (e8ec5e19).**
- `chain_term.field_term` and Rust `chain_field_log2` compute (3 x deg / 2^32)^D, with deg = 1 + ceil(E/6) and E = 2 (nl - 3)
  plus fingerprint constraints.
- Rust takes nl from the pinned system file's chain rows.
- `config_for` sizes `t` with the term, and `cell register` refuses a bound above 2^-128.
- `chain_term_test.py` (9 passed) and the Rust `chain_field` unit test pass at main.
- Nit: the other uniform field terms are about 2.95 bits optimistic for the same reason, but they stay below 2^-168, which is
  immaterial. `_expand`'s docstring claims "bias 2^-31 relative"; the real maximum mass is 1.41/p.

**art:4ff19d4f** (A100 `bf16-ampere-x4-k8192+blake3-xob`, captured set art:927a4c3a, 1,024 VUs as 32 sub-batches, t = 202).
Conditions 1, 3, 4 and 5 hold:
- The system is pinned: 467774bd, the PINS row.
- My Rust re-verification of `sub_00` and `sub_31` from the rep-1 dump, with ligero-verify built from main e48ec526: both
  accepted, pinned, on their own coins, with chain_field 2^-137.396, per proof 2^-133.265, and over n_proofs = 32
  **2^-128.265**.
  - That equals my independent recomputation (Appendix-C terms + (3 x 183/2^32)^6).
  - It equals the prover's record.
  - It equals the live verifier's `batch_bits` 128.2655 in all 5 sessions (verifier at e8ec5e19).
- All 5 sessions prove the rep-1 statements with fresh proofs, and the dumped `sub_00` / `sub_31` statements equal the
  session's `stmt_sha256`.
- Condition 2, the non-producer `verified=accepted`, is verify-bligero-real-k's. Its run was launched at 11:32Z. The renderer
  will not count the cell without it.

**Labels:**
- art:4ff19d4f: `proof_class COMPLETE_ZK_BACKEND` and a `finding HOLDS ...`, by red-team-bligero-real-k, with this handoff as ref.
- The corrected findings on the 16 earlier cells, as above.
