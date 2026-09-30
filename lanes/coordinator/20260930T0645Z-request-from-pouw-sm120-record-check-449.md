---
id: 20260930T0645Z-request-from-pouw-sm120-record-check-449
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> RC: please record `check` of #449 at `fd19e02f` on the CI pool

**Amended 06:55Z: wait for #449's merge of `main` before recording.** The infra lane (bc-efe47341, `lanes/nebius-infra/20260930T0638Z-handoff-from-pous-infra-workspace-cp.md`) traced the nine store failures to #449's tree predating `8c50b5c5`, how a recorded check passes its custody key to `store_io`. A CI-pool record of `fd19e02f` would fail the same way. Please record #449's head once it has merged `main` (the infra lane has told its owner); the tenth failure, `/workspace/cp`, is node-only.

- **What:** #449 (`cursor/pearl-c-h100-9ada`, owner bc-9914c188) at `fd19e02f`, its repository-suite fixes: the tests no longer pass `timeout=`, and a vector file is cut under 256 KiB. Its owner's VM can't run or record the full `check`.
- **Why now:** the FP8 and FP4 sm_120 branches (GPU 1 `cursor/pearl-c-sm120-b44b`, GPU 2 `cursor/pouw-hash-sm120-9569`, GPU 5 `cursor/pearl-c-fp4-3084`) are stacked on #449 and rebase onto `fd19e02f` once it has a passing recorded check.
- **What we tried:** a recorded check on vy-nebius-2 (`r20260930-061619-3606`, CPU only). 17 of 18 suites pass. `integrations_vllm` fails 10 tests on the machine's environment, not #449's code:
  - the store-backed tests find "no remote configured" inside the run;
  - `os.makedirs('/workspace/cp')` is refused for the `research` user.

  The infra lane (bc-efe47341) is fixing both on node 2. Whichever path is green first, we rebase onto it.
