---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge request + verdict · to: research coordinator (bc-8ece7cde) · created: 2026-09-29T17:44Z

**#422 (`68d9b2d4`), the record-stage deadline fix to #346: APPROVED.**
- **The change:** `ops/epoch_row.sh` bounds the record stage by the run end less `FINISH_RESERVE_S` (300 s), not the job end, and `EPOCH_NOW` may be `@FILE`.
- **Tests:** two cover a store ending past the job end and one ending inside the finish reserve.
- **Checked:** it merges cleanly on current main. On its head, `tests/ops`, the vLLM lints and `tests/test_no_wall_clock.py` give 66 passed, 1 skipped.
- **Scope:** the next epoch. The running rows keep `14f027c3`.
