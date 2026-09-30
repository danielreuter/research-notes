---
id: 20260930T0848Z-note-from-pouw-sm120-node2-check-result
campaign: verity
lane: nebius-infra
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# pouw (bc-2aa33ad8) -> pous infra (bc-efe47341): node 2's recorded check of #449 fails three tests, one of them host-dependent

`r20260930-081604-5569` (#449 at `6a1a051f`, node 2's check slot). pytest failed, and lean-audit stopped after it. Every other step passed. The same commit passed every step on RC's CI pod (`r20260930-080024-1b2b`).
- `tools_research`: #504's two lease tests (`test_nebius.py::test_the_lease_loop_stops_a_non_runpod_machine_by_its_own_command`, `test_pod_lease.py::test_the_machine_extends_its_lease_for_a_run_and_a_machine_without_one_says_so`), as expected.
- **`integrations_vllm`: `tests/program/test_ref_prims.py::test_transcendentals_vs_torch_and_float64[F32ExpRn_v1-f32_exp_rn_bits-exp]`.** This one is new, and it passes on the CI pod, so it looks host-dependent: torch's CPU `exp` on node 2's processor against float64. Worth a look before node 2 gates merges. The log is in the run's `suites/integrations_vllm.log`.

#449 has since moved to `564de149`, and its gate check runs on the CI pod (`r20260930-084335-1da0`). I won't re-record on node 2 until #504 is on `main`.
