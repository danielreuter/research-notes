---
id: 20260929T1552Z-finding-from-pous-vllm-skip-guard
campaign: verity
lane: coordinator
kind: finding
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator: `verity-vllm` in the gate fails on check pods with no evidence-store remote (cc verity-root)

- **What we saw:** in POUS's recorded check of #364 at `08a7b3f6` (r20260929-152329-2242), everything passed except
  8 `verity-vllm` tests: 4,198 passed, 8 failed, 334 skipped. The Lean audit, circuit-check and the other 17 pytest suites
  all passed. #364 touches no `integrations/vllm` file.
- **Cause:**
  - `dedcb565` (train TW2) put the vLLM suite in the gate. The tests' skip guard, `store_io.reachable()`, only checks
    that the store CLI answers and that a local store root exists.
  - A pod that has a local root but no remote gets "no manifest locally (no remote configured)" and fails instead of
    skipping.
- **Tests:** the two in `tests/check`, the three `test_101s_*` in `test_single_request_build_path.py`,
  `test_the_v2_logs_are_the_gpus_words_on_every_probed_input`, and the two TP2 MoE cases in `test_tp_moe_members.py`.
- **Ask:** either tighten the guard, so it skips when the artifact isn't local and no remote is configured, or document
  how a lane's check pod gets read access to the store remote. We're trying the second for #364's relaunch. Any lane's
  recorded check will hit this until one of them is in.
