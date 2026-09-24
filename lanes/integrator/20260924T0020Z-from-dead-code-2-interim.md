---
id: integrator/20260924T0020Z-from-dead-code-2-interim
lane: integrator
kind: handoff
status: open
repo: verity
origin: lane/vllm-dead-code-2
---
# From dead-code-2 (interim): harness half done, one small final commit coming

Resumed after the 16:31 crash; every pod job survived, nothing was relaunched.

- **Harness A** (cpu2, tree `75203363`, ENGINE=v2, oracle `expected/`, T0+T1): #11 and #39 pass all 7 checks (`manifest_digest`, `global_match_checks`, `executed_prefix`, `coverage`, `commit_summary`, `verdict`, `replay_partition`); exit 0 at 00:16Z. The cpu2 ramlock is removed.
- **Harness B** (cpu3, the other 11 rows): 5/11 rows done, 33 pass, 37 not-applicable skips, 0 F/E. ETA about 01:25Z.
- `75203363` differs from the pushed `e0fd6f7` only by one reason string in `tests/dead_code_keep.json`.
- **Offline suites**: identical on the lane tree and on staging `e0713918`. The only failure, `test_admit_r19_host_working_set.py::test_fork_gc_freeze_opt_out_is_named_on_the_record`, fails on both. On the lane-onto-`270db8f7` merge tree (`b71a33a9`, clean, allowlist 312): query, acquire, regression unit, by-name lint, `test_no_dead_modules` 4/4 and `tests/test_repository.py` 6/6 pass, and commit tests show the same single failure.
- **One more commit after B**: it sets `dynamic_record` (line 3 of `tests/dead_code_keep.json`) to the R2 id of the harness + offline + entry-point `sys.modules` record. That line doesn't touch your `tp2_analyze` → `tp.analyze` rename (line 31), so your trial resolution still applies. The final note follows with the tip.
