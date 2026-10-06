---
id: review-zk-gateway/20261006T1945Z-finding-review-zk-gateway-r11
campaign: proof-service
lane: review-zk-gateway
kind: finding
status: final
repo: danielreuter/verity
origin: [pr:1303@0699540a7c50d1343aaf6d77853d2e139e634a86, pr:1323@638c24ead38727b1d70268331c3fd0ae95479b8d, pr:1339@04d003c7bf5edb72c34bfd20026dedbcfedeaac0]
---

# Red-team round 11: #1303, #1323 and #1339 on rec-step3's v1 schedule, GRANT

The contract chain moved onto rec-step3's v1 schedule (`tops`, `level0`, at most one message row a round). The spec is
`rec_live` at #1270 `2f2a58de5`, unchanged on the fold `a9c858edb`. Detail and scripts are in the store's
`private/red-team-reviews/1323/review-r11.md`. I ran everything locally, with my own `.lake`; nothing ran on a pod.

**Verdict: GRANT** at #1303 `0699540a7`, #1323 `638c24ead` and #1339 `04d003c7b`. No blocking items.

- **The definitions are v1's.** `roundAt`'s six keys and at-most-one-row limit are `schedule_for`'s and `schedule_of`'s
  round form, and the proxy pins the same six keys canonically at that round. `owes` (Σ fresh tops' nodes plus the row; a
  copy owes nothing) is what the proxy salts. Lean's program detects copies, binds the binding round to `root_B` and
  orders salts as the proxy does.
- **No honest v1 round is refused.**
  - The flat GEMM selftest's real session (`hidden-outputs`, m = 25, 188 rounds), re-driven through `rec_live.Proxy`
    under `schedule_for`: the proxy finishes it, Lean's `Flock.Firewall.run` gives the same record and calls, and the
    contract accepts all 984 items. Its 600 commitments are what `owes` derives.
  - `schedule_for`'s K = 4096 schedule (278 rounds, 218 rows, 4 copies), walked item by item, is accepted whole. A
    commitment after a copy-only round, the schedule in v0's `caps`, and a dropped row are each cut at their item.
- **The six guarantees aren't weaker in a way that matters.** Since r9b, the lock changed only in four read definitions;
  no guarantee record changed. `Holds` is stricter (v1's kind at Hello, v1's round form, a copy owes nothing). Wording
  nit: the body's "(… and be v1's)" for `holds_fixed` is true of `run`, but the theorem states it only for Hello's item
  and a round's form.
- **Refusal tests.**
  - The contract: all seven cases.
  - Program and proxy: everything except two rows. #1303's old `commits: 2` edit became `commits: 0`. My probe has both
    sides stop at that round, agreeing byte for byte.
- **#1339.** The 13-line interdiff is the README's first line only, keeping #1323's sentence. The other 7 files are
  byte-identical to r10's. Every other merge is clean. r10's `firewall.gate.from` item is still open: the harness is
  unchanged.
- **Non-blocking N1, for merge order.** The fold's row-v2 commits (`4938eb20e`, `a9c858edb`) break the chain. #1339
  merged onto `a9c858edb` is textually clean, but 7 firewall tests fail with Lean present. The cause is three v1
  constants: `Flock/Firewall.lean:186` (`rowDigest`), `:470` (the record's `tops`) and
  `firewall_transcript.py:43-45` (`row_message`). The brief's trial tree `23b0e010c` predates row v2. Whichever lands
  second restates the three. No guarantee changes, and `check` catches it.
