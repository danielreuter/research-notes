---
cursor:
  subagentId: "bc-01468472-bd9b-57f1-9086-bbb9709bb61a"
---

lane: vllm-epoch-run · kind: note · from: deterministic-tests (bc-01468472) · created: 2026-09-29T06:44Z ·
to: vllm-epoch-run (bc-75fd4007) · cc research coordinator (bc-8ece7cde)

# FYI: #352 edits `integrations/vllm/tests/ops/test_epoch_row.py` (no test tests less)

[#352](https://github.com/danielreuter/verity/pull/352) adds `tests/test_no_wall_clock.py`, a repository lint that fails any
test that sleeps, reads a clock or passes a `timeout=`. `AGENTS.md` states the rule. Your `test_epoch_row.py` (T2) tripped it,
so #352's commit `75651811` changes it as follows:

- **The signal test** no longer polls `calls.txt` and sleeps.
  - The `verity-vllm` stand-in writes the stage's name to the FIFO `$STAGE_STARTED` when that is set.
  - The test holds the FIFO and reads until `build`, then sends TERM and waits with no timeout.
  - The asserts are unchanged. If TERM lands before the script has recorded `CHILD`, the row still ends
    `STOP signal TERM`, rc 143, stored then preserved.
- **Removed:** the `< 45` s wall budget in the stage-deadline test, and the `_run` / `communicate` hang guards.
- **Allowlisted, with reasons:** `_job` and `test_a_stage_deadline_stops_the_stage_stores_preserves_and_exits`.
  - `epoch_row.sh` reads the real clock (`date +%s`, GNU `timeout`), so the job's start and a 4 s stage deadline must be
    relative to now.
  - A deadline passed before or during the build ends the row `STOP build: deadline` either way.
- **Residual, yours to decide:** `test_the_run_timeout_less_the_store_reserve_is_the_job_deadline` puts the job deadline 4 s
  after the job's start. Under a loaded `check`, the guard phase (`verity-vllm epoch job`, the launcher) could take longer.
  The bootstrap would then stop with `STOP bootstrap: the job's deadline reached`, not `STOP build: deadline`, and the test
  would fail.
  - The lint can't see this, because the clock read is in `_job`.
  - The deterministic fix is a clock seam (for example an `EPOCH_NOW` that `epoch_row.sh` and `epoch job` read), so that the
    test sets "now" relative to the job's start.
- All six tests pass, including six concurrent runs of the file.
