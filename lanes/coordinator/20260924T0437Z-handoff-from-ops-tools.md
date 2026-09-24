# ops-tools part B ready after the device wave: lane/ops-tools @ aa01f247 (bootstrap quota threads, research pods health, bench timing guard, summary contended / --best / slow-vs-ref)

- Merge `lane/ops-tools @ aa01f247` (pushed; part A = 0b0768ed, which you may already have) **after the device wave**. It changes
  pod-side code that running lanes use: `pod_bootstrap.sh`, `run.py` (one decorator line on `main`), `bench_result.py` (carries
  `contention`), and `verity_numerical.bench.summary`. New files: `timing_guard.py`, `pod_health.py`, `pod_health_ref.json`,
  `research/pods/health.py`. Tests (all pass): ligero `timing_guard_test.py`, `pod_health_test.py`, `bench_result_test.py` (17),
  `backends/numerical/tests/bench/test_summary.py` (7), `tools/research/tests/test_pods_health.py` (2), and notes (40).
- Validated on a 4090 (chr1s1sfq2yeyf, US-TX-3, 04:26-04:35Z, about $0.11, terminated). Evidence is in
  `lanes/ops-tools/evidence/b-validation-4090/`.
  * B1: env.sh sets `OMP/MKL/OPENBLAS_NUM_THREADS = VY_CPU_THREADS = 13` (quota 13.6 of nproc 128). torch's intra-op pool was
    13, and `nproc` printed 13 too.
  * B2: health OK at 1.00x / 0.99x the recorded reference. Beside a GPU hog it printed DEGRADED (encode 7.6x, matmul 2.2x),
    exit 3.
  * B3: bench-vu clean took 0.0301 s (not contended). Beside a hog it took 0.0619 s, contended with "1 other GPU compute
    process" (NVML showed container pids, so our own process is excluded exactly). `summary --best` refused that row.
    `bench_result.py` carried `contention` into result.json.
- One decision for the owner of `verity_numerical/bench/tables.py` (not mine; its rules are frozen): Table 2 cell selection
  does not refuse contended results yet. The one-line proposal for `tables.reject_reasons` is
  `if _at(result, "contention.contended"): p.append("contended: " + "; ".join(result["contention"]["reasons"]))`.
  Only `summary --best` refuses them today.
- `slow-vs-ref` on the whole store: 406 of 662 results have a reference and 135 are flagged. Most flags are older runs
  measured against a newer, faster build. So the flag means "slower than the best on record"; check the `ref` art before
  calling it pod degradation.
- After the merge: run `research pods health <pod> --record` on one known-good pod per SKU in use (h100, 5090, a100, l40s) and
  commit `pod_health_ref.json`; only rtx-4090 has an entry. Until an SKU has an entry, health prints NO-REFERENCE, not DEGRADED.
- Known failure, older than this lane: `backends/numerical/tests/bench/test_tables.py::test_label_keys_are_the_store_vocabulary`
  fails on main b761c3a9 as well.
