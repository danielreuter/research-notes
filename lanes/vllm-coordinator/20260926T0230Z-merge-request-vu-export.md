---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: PR #42, the VU exporter, on by default in `verity-vllm row` (owner-approved), from vLLM coordinator bc-ecac3029, 02:30Z

- **Merge:** PR [#42](https://github.com/danielreuter/verity/pull/42), `cursor/vllm-vu-export-289b` @ **`8c4d381d`** (6 commits on
  `6c3568dc`, plus a main merge): `pipeline/vu_export.py` (530 lines), a tap in `check/replay/evaluate.py`, a hook in `pipeline/commit.py`,
  `CommitConfig.vu_export` (default `1`, `VU_EXPORT=0` opts out), `row_stages` wiring, tests, and two research store kinds.
- **Recheck against main `a57628fc`:** clean. Every ratchet lint runnable without pytest passes on the merged tree (39/39). The lane's
  tests passed on its pod (`r20260926-021658-3bcd`: `test_vu_export`, `tests/lint`, `test_sampled_replay*`, `test_cli`, `test_row*`).
- **Against the review criteria** (`20260926T0212Z-pending-vu-export-default.md`):
  1. **Record-neutral:** the export runs only after pair 0's replay PASSes and its value source is filed. It feeds no verdict, and
     `EVALUATION_TAPS` is empty on every record (the exporter installs its tap around its own evaluations and removes it). #101 with
     the export equals the record (`r20260925-233347-8515`: program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`). **Pass.**
  2. **Failure isolation:** `after_replay` catches every exception, names it, and never touches the verdict. **Pass for exceptions.**
     **Not for OOM:** the hook sits at `commit.py:2513`, *before* `summary.json` and `verdict.json` are written (from line 2754), and
     it may fork a pool of 8 workers. On a row already near its cgroup limit (#60, #67, #68, the B=8 rows), a kernel OOM kill here
     loses the Commit's record, and `except` can't catch it. **Required follow-up (small):** run the export after `verdict.json` and
     `summary.json` are written (or as a separate stage after the Commit exits), or default to serial when the admission headroom is
     under about 20%.
  3. **Cost:** bounded. 256 VUs per family and a 600 s budget; about 190 MB of data for #101; #101 took 823 s serially, projected under
     150 s with 8 workers.
  4. **Opt-out:** `VU_EXPORT=0`, resolved once in `CommitConfig`. **Pass.**
  5. **Custody:** the export goes to `$RESEARCH_RUN_DIR/vu-export/<row>` with `provenance.json`, so `--custody-r2` takes it with the run.
     **Pass.**
  6. **Not covered:** TP rows (`pipeline/tp/commit.py` has no hook yet), which is fine as a later step.
- **Recommendation: merge now.** Until the OOM follow-up lands, the lane rules tell runs of memory-tight rows to set `VU_EXPORT=0`.
- Not cherry-picked into tonight's epoch (per the root): it has already written.

