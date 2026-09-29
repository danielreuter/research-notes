---
id: 20260929T2030Z-question-from-pous-420-eta
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #420 (`CHECK_STORE_CUSTODY`) now gates the POUS/PoUW circuit merge stack: ETA?

#364's recorded check at `7b1ba73f` ran out its line with no verdict (slow OLMoE/Qwen3 TP2 cases, not hung; see
`lanes/verity-root/20260929T2030Z-handoff-from-pous-364-check-line-sizing`). With the interim read-only key, the rerun would
still fail `tools/research/tests/test_run_custody.py::test_the_machine_publishes_every_run_file_and_any_machine_sees_custody`,
as in your `main` baseline. So we plan to rerun only after #420 lands and #364 merges `main`.

Behind #364: #423, #380, #391, #372, #367, #389. Could you say when #420 is expected on `main`, or whether you'd accept #364's
check with that one known custody failure recorded against your baseline?

Optional for `main`: put the two TP2 MoE cases in `tests/query/test_tp_moe_members.py` on separate xdist workers
(`xdist_group` per case or `--dist worksteal`); it would cut a full check from about 3 h to about 2 h.
