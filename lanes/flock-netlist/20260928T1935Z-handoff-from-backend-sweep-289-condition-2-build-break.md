---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T1935Z-handoff-from-backend-sweep-289-condition-2-build-break
campaign: backend-sweep
lane: flock-netlist
kind: handoff
status: final
repo: verity
origin: backend-sweep (bc-ea1c2c4f), via the coordinator
---

# #289 condition 2: the merged head `9728be8d` doesn't build the proving binary; run A didn't run

This answers condition 2 of `internal/lanes/coordinator/20260928T1824Z-merge-request-refinement-train-flock-gemm-witness-289.md`.

**Result: blocked by a compile error, which is on `main` too.** On `9728be8d`, the proving build of `flock-circuit` fails:

~~~text
cargo build --release -p flock-live --features sha512 --features glue --features gpu --bin flock-circuit
error[E0425]: cannot find type `View` in this scope
    --> crates/flock-live/src/bin/flock-circuit.rs:1400:22
1400 | fn view_hello(view: &View) -> Result<String, String> {
note: found an item that was configured out: flock-circuit.rs:1354  #[cfg(feature = "seed-injection")]  type View = ...
~~~

- **The cause:** `view_hello` is compiled in every build, but `View` exists only under `seed-injection`. Its callers (1505 and 1694 on `ac412eb8`) appear to be seed-injection code.
- **The origin:** coin-tree v2 (`1053c0c9`), which came in with `main` `ac412eb8`. `ac412eb8` has the same ungated `fn view_hello` at line 1394, against a gated `type View` at 1348. So `main`'s proving build is broken too, not only #289's.
- **Why a local build can pass:** the selftest build has `--features seed-injection` and compiles. I expect the local sm_89 build that passed was that one.
- **The likely fix:** `#[cfg(feature = "seed-injection")]` on `view_hello`, on `main` and on #289. That moves #289's head, so condition 2 runs again on the new head.

## The run

- **Source:** `9728be8d7e8118e2615aebf3095f42e0df94a310`, fetched from the coordinator's bundle `artifacts/pr289-9728be8d-on-adcf38bf.bundle` (sha256 `b0afd0b7…`) onto `adcf38bf`.
  - Both GEMM Definition ids bind at that commit.
  - The harness has #299 and the compat fix.
- **Run:** `r20260928-191552-269a` (campaign `backend-sweep`), on a fresh 1× L40S (`tqmp9ttlw6m48o`, secure, driver 580.159.03).
  - Settings: `DEFS=` the two GEMM coordinates, `SELECT=table-free BATCH=16 SELFTEST=1 SELFTEST_GPU=1 SELFTEST_CASES=gpu_paths_agree,gpu_proofs_match_cpu WARM=0 RUNS=1`.
  - It failed in the build after 2.5 minutes, with 0 records.
- **Custody:** preserved (run record `art:f5cdcbfc…`, with `out/build.log` and `out/build-circuit.txt`).
- **Labels:** `build_failure=flock-circuit-view_hello-ungated-without-seed-injection`, `defect_origin=1053c0c9-on-main-ac412eb8`.
- **Pods:** the pod was terminated at 19:19:08Z. Two earlier L40S pods were dropped before any run, because their ssh links stalled (20 MB didn't cross in 60 s).
- **Spend:** $0.50 of the $3 cap.

**To rerun:** send the fixed head, the same way as the bundle. The poll, the ssh check and run A are scripted. It needs a 1× L40S with a working link: between 18:40Z and 19:16Z, 3 of 7 create attempts found stock, and 1 of those 3 pods was usable.
