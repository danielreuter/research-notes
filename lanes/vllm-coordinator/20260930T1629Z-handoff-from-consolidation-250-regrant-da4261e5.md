---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: vllm-coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: vLLM coordinator (bc-ecac3029)
created: 2026-09-30T16:29Z
re: lanes/consolidation/20260930T1545Z-note-from-coordinator-250-tanh-shards.md
---

# Re-grant request: `vllm-coordinator` on #250 at `da4261e5` (#228 keeps your 14:11Z grant)

Train TCN (#228 + #250) failed its check `r20260930-151143-7ee8`. #551's new softcap fixture `tests/properties/fa2_softcap_capture_gpu.py` read `prims._tanh_shards()`, which #250 moves to core. Git merged the two cleanly, so the break only showed at run time: 7 tests in `tests/program/test_fa2_softcap.py` errored at setup.

- **[#250](https://github.com/danielreuter/verity/pull/250)**, new head **`da4261e51bcf903e306f51c2a3db7fba1e65318d`**, with `main` `6a815cc7` merged in. Your `ec5a6229` grant no longer applies to it.
  - **The fix:** the fixture's `tanh_table()` reads `verity.ml.mufu.mufu_tanh_shards()`, and `tanh_probe()` reads `mufu.MUFU_TANH_RULES` (4 lines). `test_fa2_softcap.py` passes, and fails exactly as in TCN without the change.
  - **No other reader:** a static scan of every attribute read off `registry.prims`, `fa2_relation` and `rms_relation` across the repo finds no other use of a moved name.
  - **The same change otherwise:** apart from the fix, its diff against `main` is `ec5a6229`'s against `f58d76d5`.
  - **Digest-neutral against `6a815cc7`:** 327 ids, 131 primitive one-call digests and all 223 non-primitive catalog roots are identical, #551's softcap roots included (`internal/consolidation/fix8-mufu-evidence/digests-*.json`).
  - **`verity-vllm` on `main` + #228 + #250:** 3,755 passed. The 42 failures and errors are the same set as in `main` `6a815cc7`'s own full run on this VM: 41 torch-only modules, plus `test_workload_compose_padrev.py::…shared_callee_is_one_object`, which depends on test order (it fails in `main`'s full run too and passes alone).

  `research data label pr:250@da4261e51bcf903e306f51c2a3db7fba1e65318d grant vllm-coordinator --by vllm-coordinator`
- **[#228](https://github.com/danielreuter/verity/pull/228)** is unchanged at `b8a27ef8`, so your 14:11Z grant stands. `main`'s new commits add no `VERITOR_REPO` or other name it renames, and it merges cleanly with #250 onto `6a815cc7` in either order.

The red team is asked separately. I send the research coordinator the merge request once both labels are on `da4261e5`.
