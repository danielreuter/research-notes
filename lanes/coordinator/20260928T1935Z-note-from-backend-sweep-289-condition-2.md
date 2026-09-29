---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
id: 20260928T1935Z-note-from-backend-sweep-289-condition-2
campaign: backend-sweep
lane: coordinator
kind: handoff
status: superseded
repo: verity
origin: backend-sweep (bc-ea1c2c4f)
---

# #289 condition 2 is not met: `9728be8d` doesn't build the proving binary, and neither does `main` `ac412eb8`

**Superseded (20:25Z): condition 2 passes at `788bf662`, run `r20260928-200802-32fc`; see `20260928T2025Z-note-from-backend-sweep-289-condition-2-pass.md`.**

For the research coordinator's merge of [#289](https://github.com/danielreuter/verity/pull/289) (`internal/lanes/coordinator/20260928T1824Z-merge-request-refinement-train-flock-gemm-witness-289.md`, condition 2).

- **Verdict:** don't merge #289 at `9728be8d` on condition 2. Run A couldn't run, because the GPU proving build fails.
  - The failing build: `cargo build … --features sha512 --features glue --features gpu --bin flock-circuit`.
  - The error: `E0425: cannot find type View`. `fn view_hello(view: &View)` is compiled in every build, but `type View` exists only under `seed-injection`.
- **It's on `main`:** the defect is coin-tree v2's (`1053c0c9`), and `main` `ac412eb8` has it at lines 1394 / 1348 of `backends/flock/live/src/bin/flock-circuit.rs`. Any GPU run on current `main` that builds the prover fails the same way.
  - The selftest build, which has `seed-injection`, compiles.
  - As far as I can tell, `check` doesn't build this binary, so it wouldn't catch it.
- **The likely fix:** `#[cfg(feature = "seed-injection")]` on `view_hello`, on `main` and #289. Condition 2 then reruns on #289's new head.
- **Evidence:**
  - run `r20260928-191552-269a`, preserved (run record `art:f5cdcbfc…`), source `9728be8d` from your bundle (sha256 checked);
  - labels `build_failure=…` and `defect_origin=1053c0c9-on-main-ac412eb8`;
  - details in `internal/lanes/flock-netlist/20260928T1935Z-handoff-from-backend-sweep-289-condition-2-build-break.md`.
- **Spend and pods:**
  - $0.50 of the $3 cap, at most one 1× L40S at a time;
  - no `vyb289-` pod is left, and the guard is stopped;
  - the pods were `j1gimzf1xsysum` and `y07zz2vu7lx78i` (dropped, stalled ssh links) and `tqmp9ttlw6m48o` (terminated 19:19:08Z after the run).
- **The rerun** needs the fixed head, sent as a bundle as before, and 1× L40S stock. The scripts are ready.
