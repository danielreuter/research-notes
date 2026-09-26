---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Queue after the epoch (low priority), 23:08Z

1. **R10 guards G1a–G4b** (10 skips in `tests/program/test_harden_guards.py`): retire them in a small test-only follow-up (gc's successor or a tiny lane, about $1), unless their evidence files are small and recoverable **without veritor**. veritor is retired, and the repo must not depend on it. Record per guard which it was.
2. **G5** (`HARDEN_LIVE=1`): run at the next GPU pod opportunity, on a lane that already has an L40S up. Note the result in that lane's READY.md.
3. **`VERITY_REGRESSION_ROWS_ROOT` guard** (from `docs/process-robustness.md`, root 02:53Z): the name reads as "new rows", but it's
   the frozen reference input. The epoch's first rebase runs used it for new records and hit the v1 input pins. Add a check at
   regression session start (conftest or resolver, test-only): if the rows under that root don't match the v1 pins, stop with a
   message saying new records belong in `VERITY_REGRESSION_CANDIDATE`. Include a test for both directions. Small; it can share the lane
   with item 1.
4. **Dense planner calibration** (from PR #62; for the next epoch): the row planner'"'"'s dense coefficients overestimate (#4 Match: 122 GiB predicted, 80 GB
   used), so the new admission (`pool + committer_resident`) may refuse dense rows falsely. Capture #4'"'"'s per-term Match record
   (`footprint.jsonl` / the verdict'"'"'s predicted-vs-measured lines) on its next run, then recalibrate `telemetry.admission` coefficients.
