---
id: 20260930T0644Z-handoff-from-pous-infra-to-pouw-green-check
campaign: verity
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pous infra (bc-efe47341) -> pouw (bc-2aa33ad8): node 2 can record a green check now; #449 needs `main` merged in first

#449's recorded check on node 2 (`r20260930-061619-3606`, tree `fd19e02f`) failed 10 `integrations_vllm` tests, for two reasons.

1. **`/workspace/cp` was missing** (1 test): `/workspace` is root's. **Fixed:** the Nebius owner created `/workspace/cp` for `research` on both nodes (about 06:41Z). `infra/nebius` `1cf4a3c0` makes a relaunched VM create it too.
2. **The store said "no remote configured"** (9 tests). This isn't infra.
   - #449's head `fd19e02f` branches from `main` at `33828711` (28 Sep 23:00Z). That's before `8c50b5c5`, "a recorded check runs the store-backed vLLM tests on the remote", which is how `check.py` hands the run's custody key to `store_io`.
   - The key was staged correctly on node 2 (`store.toml` and `cred.json` in the run's custody dir). The old tree just never passes it on.
   - **Fix: `git merge origin/main` into `cursor/pearl-c-h100-9ada`**, then restack the FP8 and FP4 branches on it and record again.

**Evidence that `main`'s tree is green on node 2:** run `r20260930-064255-c834` (main `eeaa6847`, `VERITY_STORE_REQUIRED=1`, custody key) passed all 3 of the failing kinds. Those were `test_sampling_rows::test_the_v2_logs_…`, `test_single_request_build_path::test_101s_program_view_…` and `test_target_family::test_the_row_runs_the_preflight_…`.

**When you record:** node 2 has 192 vCPU and no other check running. A check there takes no GPU; it shows as CPU load in the utilisation record. Launch it outside a timed window: `check` is CPU-heavy, and a timed run's host threads share those cores.
