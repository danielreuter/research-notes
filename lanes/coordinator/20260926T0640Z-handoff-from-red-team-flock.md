---
lane: coordinator
kind: handoff
from: red-team-flock (bc-fe5a9310-de4b-51d4-a285-8f1317ef0f04)
created: 2026-09-26T06:40Z
---

# red-team-flock: the four FP8 real-K cells on the spine input sets meet PB1–PB4, CN1 and CN2, labelled NON_ZK_PROOF; the old four now carry `superseded_by`

**Cells:**
- fp8-ada on the 4090: art:5d2a91a7 (K 2048, 4 proofs) and art:ab115376 (K 8192, 2 proofs).
- fp8-hopper on the H100: art:66d2412c (K 2048) and art:1c520240 (K 8192).

**Conditions:**
- **PB1:** the records name verifier commit 3a073d74. It descends from e4f631bd and has no `backends/flock` change, so
  it includes the NV1, CN2 and CN3 admission checks.
- **PB2:** the records report the union bound: 2^-193.44, 2^-194.44 and 2^-195.44.
- **PB3:** my replay, run r20260926-061513-ad9c, was a CPU build on an A4000 pod used as a CPU box, because there was no
  CPU stock.
  - All 48 recorded sessions were accepted.
  - All 16 negatives were rejected.
  - My binary's sha, 87dc4fb6, equals the verifier's recorded binary.
- **PB4:** every proved session has exchange, require_link and the cell's Σ. The verifier and prover hosts differ.
- **CN1:** every verifier file has out == y << 10.
- **CN2:** the largest proof is n × VUs = 15,360.

**Supersession:** the old four (43986c5d, c0999f7f, c200eef3 and c4d03dd5) carried SUPERSEDED only as free text in a
`finding`.
- Neither the vocabulary's key nor the tables read that text. The vocabulary's key is `superseded_by`, and
  `store_tables.py` does not filter on supersession at all.
- I wrote `superseded_by` labels pointing at the new arts: 43986c5d → 5d2a91a7, c0999f7f → ab115376, c200eef3 → 66d2412c
  and c4d03dd5 → 1c520240.
- **Still needed:** tables will only drop the old four once `store_tables.py` honours `superseded_by`. That is a
  flock-backend / tables change.
- The new records have `derived_from.supersedes = null`.

Pods: the A4000 is terminated. Two duplicate pods, created by the retry loop, were terminated within minutes. About $0.15
in total.
