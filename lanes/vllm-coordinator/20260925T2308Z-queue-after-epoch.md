---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Queue after the epoch (low priority), 23:08Z

## PENDING DANIEL'S BUDGET DECISION (top of queue; root 15:52Z)
- **Switch the query of record to `Q_word_v1{X}`** (`docs/fine-query-plan.md` beyond steps 1–3). Not approved.
- **The re-baseline epoch** that switch implies: about $150–250, beyond the $770 vLLM cap ($716.74 spent). Not approved. Fold in
  what's still open from this epoch: the whole-epoch re-record at right-sized pods (`docs/vllm-epoch-review.md`), deferred items 2c/3/4,
  and #4's reclassification.
- Approved and running now: steps 1–3 (build `Q_word_v1{X}` + `query/word.py` width check; diff manifests on 13 rows; one #101 L40S
  run, about $5), by vllm-vu-export.

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
5. **VU export out of the pre-verdict window** (from PR #81): read the drawn units' committed words during the window (O(MB)),
   then evaluate, decompose and write them after `verdict.json`. Also arm `driver.keep_population` only when `--vu-export-dir` is set
   (it's set at `vu_store` import today, so it's on in every Commit).
