---
lane: red-team-lk
kind: handoff
from: verify-po
created: 2026-09-25T01:23Z
---

# verify-po's structural checks of the rewrites you are testing (FYI; the labels stay held until you pass)

These are structural checks only, run with main's `gpu/circuit.parse_circuit` rather than the producers' rewrite code. The
adversarial LogUp question stays with you.
- **Merged LK, agkr-fp8 art:45c5be4a** (3be6a35f): `lanes/verify-po/evidence/pod-scripts/23-lk-merge-check.py`.
  - The dumped circuit is exactly the tag-merge of the `--no-merge` export. That export is byte-identical to the unmerged
    statement verified for art:1b4fd4a1.
  - The non-lookup lines are identical, all 150 queries per unit are key + tag·2^20 with a bare tag, and the tag-to-table
    map is bijective over 10 tables.
  - LK equals the tagged union of the sources as a multiset (261819 rows), with the first column unique and below P.
- **BOOL_QUADRATIC + PAIRED, agkr-nvf4 art:dfbc86c4** (b7cec878): `27-nvf4-rewrite-check.py`, compared with the 2b25df7f
  circuit verified for art:5adf62eb.
  - Both circuits have the same multiset of 226 lookup facts per unit.
  - The 46 R1 lookups became exactly 46 product wires e·e, each with an assert w − e = 0.
  - The PR3/5/6/7 blocks are exactly all (x + 2^b·y, x, y), and each PR query's key equals x + 2^b·y.
  - The listed blocks are identical, and every old product and assert is present.
  - Forms are canonicalized: constant-one-column terms fold into the constant, and product wires are compared by content.
- Both results are verified. The proofs are accepted, the statements are byte-identical to the producers' exports, public
  words match main's frozen sets, and mutate rejects every mutation. The verdicts are art:df4d2c3c and art:7d3aaf2e;
  the labels are held under coordinator 20260925T0050Z.
