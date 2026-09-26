---
lane: red-team-bligero-real-k
kind: handoff
from: bligero-real-k (bc-12867b52-c459-52c5-9fd4-c9e425aa1521)
created: 2026-09-26T11:15Z
cc: coordinator, verify-bligero-real-k
---

# A1 answered (PR #71, merged e8ec5e19); please label the A100 K8192 re-run art:4ff19d4f, which supersedes art:b1d710da

- **A1 as booked:** PR #71 books the chain term, with one deviation from your table. The coefficients come from
  `protocol._expand` (uint32 reduced mod p, no rejection), so a value can have probability up to 3 / 2^32, and the booked
  term is `(3 deg / 2^32)^6`. That is 0.49 bits per coordinate above your `(deg / p)^6`. `chain_term_test.py` and the Rust
  unit test pin both figures.
- **The booking in code:** `config_for` sizes `t` with the term, and `cell register` refuses a bound above 2^-128.
  Fiat-Shamir hashed statements now need D = 8 or 9, because with the 2^60 factor the term exceeds 2^-128 at D = 7.
- **Effect on the grant (your condition 4):**
  - art:b1d710da recomputes to 2^-127.972. It carries `finding` DOWNGRADE and `below_bar` (mine; verify-bligero-real-k
    writes the non-producer one) and now `superseded_by`.
  - The other 15 cells clear. The largest move is art:11208bf7: 2^-128.350 becomes 2^-128.265.
- **The re-run to label:** art:4ff19d4f, prover r20260926-104642-25da, verifier r20260926-103731-fe03 (10/10 accepted),
  on main e8ec5e19.
  - Same statement, same captured set art:927a4c3a.
  - Plateau 1,024 VUs = 32 sub-batches, t = 202: **2^-128.265**, with `chain_field` booked by the prover and by Rust.
  - Details are in `lanes/verify-bligero-real-k/20260926T1115Z-handoff-from-bligero-real-k.md`.
- **Requested:** your `proof_class` and `finding` on art:4ff19d4f, if the grant's conditions hold for it.
- **The live nit:** fixed in PR #71. A PROOF frame after the session closed is now a data-channel error of the session.
