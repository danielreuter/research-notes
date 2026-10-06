---
id: review-zk-gateway/20261006T0833Z-finding-review-zk-gateway-r5
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1270@74b2c0d3a49defabfda80b39c8547410e01e177e]
---

# Red-team round 5: #1270 at `74b2c0d3a49defabfda80b39c8547410e01e177e`: GRANT

Row G4 closes round 4's finding (`note:review-zk-gateway/20261006T0813Z-finding-review-zk-gateway-r4`).

- `498f4cf64..74b2c0d3a` is exactly the described change (3 files, +38 −7):
  - the order checks for Commit and Link come first;
  - Finish pins from the proxy's own stream counts, with no `coins.record()` read;
  - `_coin_calls` logs `record`, and the new stray test is added;
  - §10.3 gets a row and §10.5 a sentence.
- Every stray kind and every Open placement, run against the coin server's calls (refused ones included), gives a prefix of
  the honest calls. At K = 4096 that leaves 284 inner endings, so §10.5's rows are 12.09 and 80.12 bits, within the stated
  12.1 and 80.1.
- Tests: the three files pass (65). The new test fails against 498f4cf64; its loop alone departs there for every stray
  Commit and Link, and for a stray Finish between Link and the last round.
- Finished records and `schedule_of` are unchanged from 498f4cf64 on the tests' schedule, a parent with a child stream,
  and K = 4096.
- Nothing else reaches the coin server at a point the schedule doesn't fix. Timing is outside §10's rule; the network
  warden covers it.

The grant carries to a restack whose diff against this head is only the 09:00Z rename. It does not cover the `check` with
lean-agreement, which the merge still needs, or #1303. The detail and probes are in the reviewer's private store
(`red-team-reviews/1270/`, r5-*).
