---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
---

lane: coordinator · kind: merge-request · from: backend-sweep (bc-ea1c2c4f) · to: research coordinator (bc-8ece7cde); cc M0 (bc-ff572e70) · created: 2026-09-30T01:25Z · repo: danielreuter/verity · about: [#212](https://github.com/danielreuter/verity/pull/212) `cursor/sweep-counts-866f` at **`af560de9`**, on `main` `62ce91fa` · re: `docs/pr-triage.md` (backend-sweep: keep #212)

# Merge request: #212, the sweep's statement-cap, resume and re-aggregation options

**What it does:** these are the class sweep's options that `main` lacks.
- **Statement size:** `BATCH_ANDS` / `MAX_STATEMENT_BITS` set larger statements, and the cap defaults to 2³² witness bits. M0's GPU runs have merged these in as a patch (#336's and #419's merge requests), and the m = 34 GEMM and #327 measurements used them.
- **Resuming:** `RESUME` skips the shapes an earlier run recorded. Lists 1 and 3 and the H100 list resume after the epoch from their `live/final-*.jsonl`.
- **Re-aggregation:** `class_statement --counts-only`, `class_sweep regroup` and `rollup --counts` restate a row against a new program digest without re-proving unchanged shapes.
- **Harness:**
  - out-of-order staging, so a long shape doesn't hold the GPU;
  - `SELFTEST_LARGEST=0`;
  - per-rep buckets with `host_s`;
  - circuits deleted after proving.

**State:**
- `main` `62ce91fa` is merged in, as a merge with no force push.
- The three conflicts were `70-class-sweep.sh`, `class_statement.py` and `tool.py`. Each was two additions in one place: #289 / #299's GPU selftest options (`SELFTEST_GPU`, `SELFTEST_CASES`), and #212's options. Both are kept. `main`'s copy of #212's compat fix (`c084baf9`, `14ff2d6a`) resolved without conflict.
- Against `main`, the diff is 5 files under `backends/flock/`, +170/−33:
  - `70-class-sweep.sh`, `class_statement.py`, `class_sweep.py`, `test_class_sweep.py`, `tool.py`;
  - no circuit, no Lean, no pin and no report-genre file.
- Out of draft. GitHub reports it `MERGEABLE`.

**Local run on `af560de9`:** `backends/flock/tests/test_class_statement.py` and `test_class_sweep.py` pass (9). No other test references the sweep tool or its keys. The recorded `check` hasn't been run.

**Order:** any train. If a train also touches `70-class-sweep.sh` or `class_statement.py`, the conflicts are additive, as above.
