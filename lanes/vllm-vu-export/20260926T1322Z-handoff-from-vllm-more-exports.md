---
lane: vllm-vu-export
kind: handoff
from: vllm-more-exports (agent bc-8ed3d15c-dd08-54c3-b30b-a6cbf5f20df4)
created: 2026-09-26T13:22Z
---

# vllm-more-exports: no #74 or #67 export to fold in. #67's export drew 0 VUs because vu_store's time budget includes the population build (>18 min on a B32 row)

- **#67 (olmoe b32 TP1, run `r20260926-082002-43e0`)** passed Build and Match. Its Commit ran through the sampled replay: coverage 406220 missing 0, C2 16120/16120 equal, replay "not retained 0, failed 0".
  - `export_vus` started at 12:58:01. By 13:16 it had stored no VU and written no `export.json`, so I stopped the run there, at the $30 and the deadline.
  - The cause: `t0` is taken at the top of `export_vus`, and `_run_draw` measures `max_seconds` from it. On #67 the `ProgramIndex` + `population` build over 33 request Programs alone took more than 18 minutes, so a 600 s budget (your default; I'd lowered this run's 1200 to 600 to hold the budget) expires before the first draw.
  - **Suggestion:** start the time budget after `select`, or scale it with the population. Otherwise every large default-on row (#67, #68, #23, ...) exports nothing.
- **#74 (qwen3-4b-fp8 H100)** passed Build and Match; the Match needed the 32 MiB snapshot cap. Its Commit can't fit a 251 GB pod: 197 GiB of pinned staging plus 69 GiB of C2 Programs objects. The bounded/exclude path crashes in finalize (`vllm_v1.fold`: "leaf must be a 32-byte digest"). No export.
- **Programs, if you want main-tree graphs:** both rows' request Programs are preserved in run custody (`research data fetch <run_record> --path 'programs/*'`).
  - #74: `r20260926-081920-036d` `programs/`, 9 request dirs, request digest `55fd66b6…`.
  - #67: `r20260926-082002-43e0` `programs/`, 33 dirs, `e9092446…`.
  - Both differ from the records' digests.
- **PR [#63](https://github.com/danielreuter/verity/pull/63)** (the `DECOMPOSE` / `TEMPLATE_OF` / `WEIGHT_ROWS_OF` additions) passes the unit and pod tests, but no served row has exercised it yet.
