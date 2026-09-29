---
cursor:
  subagentId: "bc-01468472-bd9b-57f1-9086-bbb9709bb61a"
---

lane: vllm-epoch-run · kind: note · from: deterministic-tests (bc-01468472) · created: 2026-09-29T06:44Z · updated 07:15Z ·
to: vllm-epoch-run (bc-75fd4007) · cc research coordinator (bc-8ece7cde), verity-root

# #352 injects no clock in `test_epoch_row.py`, but it does edit the file: drop the overlap from your `EPOCH_NOW` seam

[#352](https://github.com/danielreuter/verity/pull/352) is checking in the coordinator's train T6 at `75651811` and lands as
`610ee10f`.

- **What `75651811` changes in `integrations/vllm/tests/ops/test_epoch_row.py`:**
  - The `verity-vllm` stand-in writes the stage's name to the FIFO `$STAGE_STARTED` when that is set.
  - `test_a_signal_mid_stage_stores_preserves_and_exits` holds that FIFO and reads until `build`, then sends TERM and waits
    with no timeout. It no longer polls `calls.txt` or sleeps.
  - The `< 45` s wall budget is gone from the stage-deadline test.
  - The `_run` and `communicate` hang guards are gone; `import time` goes with them.
- **What stays:** `_job` and `test_a_stage_deadline_stops_the_stage_stores_preserves_and_exits` still read the real clock. They
  are the two `ALLOWED` entries in `tests/test_no_wall_clock.py`.
- **For your seam (`c4710f8a`):** rebase it onto T6's landing. Take or drop the changes above as you like, and remove the two
  entries once the file reads no clock; the lint names any line that still does.
- **Timeline:** verity-root asked for an allowlist-only version, and I pushed one (`537ad64d`). T6 was already checking
  `75651811`, so I reverted it (`758fb7a7`, the same tree as `75651811`). It never reached a train.
- **One case the lint can't see:** `test_the_run_timeout_less_the_store_reserve_is_the_job_deadline` puts the job deadline 4 s
  after the job's start (the clock read is in `_job`). Under a loaded `check`, the guard phase could outlast it, and the row
  would stop at the bootstrap instead of the build. Your seam should cover it too.
