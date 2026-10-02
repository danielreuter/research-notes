---
id: proofs/20261002T0650Z-handoff-from-proofs-730-lean-registered-test-never-ran
campaign: value-hiding
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/flock-hidden-outputs-95d4@3fd8c447f (worker bc-ad312479 for proofs bc-8416bc72)
---

# Train f38a: #730's `test_lean_registered_reads.py` never ran in a check, and its honest test fails

- In #730's check `r20261002-025522-7505`, the module wasn't run: none of its tests is among `suites/backends_flock.json`'s
  passed or failed tests (`verity-flock`: 435 passed, 15 skipped). It skips when `ci.fetch(art:bf70d8eb)` can't reach the
  store, and before #761 that skip passed.
- `test_an_honest_registered_statement_is_accepted_and_reports_its_roots` reads `line["partition"]["units"]`. But
  `flock-verify statement` puts META's `{rule, digest}` under `partition` and the finding under `partition_check`, so the
  test raises `KeyError: 'units'`.
- Train f38a (`597e355d5`) sits on #761, so a recorded check either runs the module (custody key: the KeyError) or fails
  the skip. Either way that test should fail f38a's `verity-flock` suite.
- Fix: `line["partition_check"]["units"]`. #757's merge of f38a (`3fd8c447f`) has the fix, with the module converted to
  hidden-output statements. All 10 of its tests pass locally, and check `r20261002-063333-9f82` runs them.
