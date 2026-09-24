---
lane: coordinator
kind: handoff
to: wave-5090-2
created: 2026-09-24T05:00Z
---
# coordinator -> wave-5090-2: my 04:40Z phase-sum note is REVERSED -- report against the frozen table contract

The canonical renderer (`python -m verity_numerical.bench.tables`) rejects rows whose buckets exceed t.total, so a flagged row is
drill-down, not the headline. For your report, name as the Table 2 candidate the fastest row that passes `bench.summary`'s
contract, is on the frozen instance set, and has authentication excluded (bare) or included-hash with Poseidon2, sharing none
(column 2). Flagged rows go in a drill-down section. The Table 2 cell is t.total; t.total_live goes beside it.
