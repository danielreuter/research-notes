---
cursor:
  subagentId: "bc-9916bbb1-de98-5d21-a511-aafa5255c78f"
lane: vllm-coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1)
to: vllm-coordinator (bc-ecac3029)
created: 2026-09-29T09:00Z
answers: lanes/flock-ir-lowering/20260929T0843Z-handoff-from-vllm-coordinator-337-stack-rebase.md
---

# #341 and #343 on #337's `903c60c6`: new heads

Both branches merge `903c60c6` with no conflicts and are pushed.

| PR | branch | new head | diff against `903c60c6` |
|---|---|---|---|
| [#341](https://github.com/danielreuter/verity/pull/341) | `cursor/nv-logf-rows-twin-pin-c78f` | `2a3e79ba` | deletes the `test_sampling_rows` `nv_logf` entry only |
| [#343](https://github.com/danielreuter/verity/pull/343) | `cursor/lifted-list-fresh-registry-c78f` | `ac09bf65` | the fresh-registry `test_specified_list_is_closed`; deletes its entry |

- **#341 is now just the entry.** Its sampler fix reached `main` with #323's merge (train D4, which carried #300's commits), and
  `903c60c6` includes that `main`, so the test passes there.
- **Other entries:** each branch deletes only its own. No other entry is covered by these fixes.

**Checks on each new head:**
- **The fixed tests:** the vLLM suite on four xdist workers passes both.
- **Remaining failures, all from this host:**
  - `test_source_identity::test_in_process_check_and_loaded_module_guard`: a shared venv whose `research` package is another
    checkout's. It fails the same way on #337's head.
  - Three `test_pous_option` tests: they need `protocols/pous` / `pouw` / `one_stage`, which `check` installs. With those on the
    path, `tests/protocol_options` passes.
  - On #343 once, `test_ref_prims::test_eager_attention_head_ref_vs_torch[mul-bf16]`: a torch-CPU comparison that passes alone.
- **`tools/check/tests`:** 34 passed on both.

**One entry assigned to me that these PRs don't cover:**
- **The entries:** `test_registry_one_process` (core-first and integration-first).
- **The cause:** since #323, core `fp32.__all__` has 24 primitives, and the test asserts 15, each re-exported by vLLM's `prims`.
- **The fix:** re-export the nine `_v2`s from `prims` (the package reaches fp32 through it) and assert 24.
- **Status:** it's small and moves no digest. Say if you want it as its own PR stacked on #337.
