---
id: r20-proof/a-logup-union/20260922T0909Z-finding-redteam-urgent-epilogue-tables
campaign: r20-proof
lane: a-logup-union
kind: finding
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/gkr/REDTEAM_URGENT_epilogue_tables.md
---

# URGENT (lane a-logup-union, 2026-09-22 ~09:15Z): v2 epilogue range lookups were never proved -- any public word forgeable

**Who should read this**: coordinator, `lane/red-team-3`, `lane/a-gpu-v2`, `lane/a-gpu2`, anyone quoting an a-v2 number.

**What**: in `backends/gkr/src/main.rs` the instance's table list was segment 0's (`segs[0].circ.tables`, the unit
circuit). The epilogue circuit's tables (`R16`, `R15` in checker v2; `R15` in v1) were therefore *not* part of the
lookup argument: no multiplicities committed, no fractional GKR, no verifier evaluation. In v2 the unit circuit does
not use `R16`, so the epilogue's `hi`, `lo`, `rem`, `hi + carry` (`R16`) and `hi2` (`R15`) range checks were absent
and the cast `y32 -> y16` was unconstrained beyond linear identities.

**Attack** (fixture `fixtures/redteam-3/logup-union/forged_epilogue_hint/`, test
`v2_forged_public_word_via_epilogue_hint_is_rejected`): with honest unit rows, set `hi += 1`, `lo -= 2^16`, fix `lsb`,
`hi2`, `rem` from the linear identities, claim word `y16 + 1`. **Accepted** by the pre-fix binary in Clear and PCS
mode; by induction any word in `[0, 2^16)` is claimable for any input. This is a total break of the v2 VU statement
as implemented (not of the protocol on paper: PROTOCOL.md 12.1 says "multiplicities ... over BOTH segments" -- the
code did not do what the document says for a table that only the epilogue queries).

**v1**: `R16` is a unit table, so the epilogue's `R16` queries were covered; the missing `R15` on `hi2` is implied by
`hi in R16` and `lsb` boolean (`hi2 = (hi - lsb)/2 < 2^15`). No v1 forgery from this; v1 numbers stand.

**Fix**: `Instance::new` unions every segment's tables by name (commit on `lane/a-logup-union`, 16/16 tests incl. the
forgery). Honest-run cost: +2 instances (2^17, 2^16 leaves at B = 4096), +98,304 committed multiplicities: < 1 % of
the lookup bucket. The a-v2 timings are therefore approximately right, their soundness label was not.

**Ask of red-team-3**: (1) confirm rejection on your binary; (2) add "every table referenced by any segment's queries
has a logUp instance" to the transcript checklist -- the check is one line (`assert every query table in
inst.tables()`, now structural); (3) look for the same shape elsewhere (B's direct backend, the GPU provers'
`bb_export` -- does `gpu/prover.py` take its table list from the unit circuit alone?).
