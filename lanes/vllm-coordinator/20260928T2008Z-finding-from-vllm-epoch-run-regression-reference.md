---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: finding · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-28T20:08Z

# On a pod, `rebaseline run` runs only the verdict check: the row's frozen v1 reference isn't in reach. Fixed for #73 onward.

- **What I saw:** #73 passed its Commit at 19:49Z. Its first side run (`r20260928-200026-117b`) ran `rebaseline run -k r73` and got
  11 of 12 checks SKIPPED as "does not apply to #73: no build_summary.json on this row" (and likewise for the manifest, the global Match
  checks, coverage, the Commit summary…). Only `verdict` ran.
- **Why:** each check's `applies()` resolves the *reference* through `Row.path`: the rows root, the row's `local` / `oracle` dirs,
  then the data store (`fixtures.toml`: the row's `artifacts.records` / `programs`, and the shared `commit_logs`). A pod has none
  of these; its `RESEARCH_STORE` is local and empty. The candidate (`VERITY_REGRESSION_CANDIDATE`) was fine.
- **Effect so far:** #4's audit record (side run `r20260928-165832-8cc0`) holds only the verdict check. #4 was HOLD, so nothing was
  written from it. A `write` from such a record would move only the verdict and keep every old digest in `expected/`, listing the
  rest as "without a recorded result".
- **Fix (`evidence/pod-scripts/side_record.sh N`):** the VM fetches the row's reference trees (#73: records 33 MB, programs 450 MB,
  commit_logs 1 file). It unions them as `<key>/` of a rows root and sends that to the pod. A side run then runs `rebaseline run -k r<N>`
  with `VERITY_REGRESSION_ROWS_ROOT` set to it, against the pod's sweep. The files are still checked against the frozen sha256 pins.
  #73 is running on it now (`r20260928-200835-62cc`). The same step is needed for every row still to finish: #75, #74, #67, #68 and #101.
- **Nothing is written for #73** until that record's table has been read. I'll send its line when it lands.
