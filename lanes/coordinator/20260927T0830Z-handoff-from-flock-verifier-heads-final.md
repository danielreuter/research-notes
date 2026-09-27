---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-27T08:30Z

# Heads final for audit: #118 `d13f8f71`, #126 `ee00f064`, #129 `4d4fb5c1`

These heads are final. The stack is #113 (not changed since `9d0d53df`), then #118, #126 and #129.

- **#118 `d13f8f71`**: M0's SHA-512 statement format up to PR #83 `25519ba1`:
  - hm96-sha512 rows, SHA-512 digests and record fields, salted Merkle openings;
  - the e2e bindings: classes, `program_sha512`, and `verity/partition/v1` objects with open query names;
  - GEMM's layout: packed ranges, `out_net`, `leaf_cuts`;
  - template partitions derived from the verifier's own program (`--program`; #131's vectors 16 of 16);
  - the verdict's partition finding;
  - a parallel agreement job (`agree.py --jobs`, `ci.py --session-jobs`), with outputs byte-identical to a sequential run.

  Agreement sets 8 to 13: 25/25, 25/25, 21/21, 2/2, 2/2 and 27/27. The recorded runs are `r20260927-064449-6059` (sets 8
  and 9), `r20260927-070106-614e` (set 10) and `r20260927-074433-43a6` (set 13, on a CPU pod).
- **#126 `ee00f064`**: the width rule on one Call's cut: #111's `check_cut`, 7000 of 7000 random graphs.
- **#129 `4d4fb5c1`**: the `Q_word` v1 evaluator over Call graphs: 3500 random cases and #111's pinned vector.

Next, stacked on #129: `Q_word`'s graph extraction from #120's program format, so `Q_word` verdicts can say derived.
