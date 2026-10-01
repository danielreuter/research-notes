---
id: vllm-coverage-defs/20261001T0812Z-friction-source-identity-guard-fails-under-research-run
lane: vllm-coverage-defs
kind: friction
status: open
recurs: note:20260929T0924Z-handoff-from-flock-ir-lowering-399-registry-one-process
cursor:
  subagentId: "bc-272bd4a1-8f85-5153-b057-e86d89991046"
---

# `test_source_identity::test_in_process_check_and_loaded_module_guard` fails whenever the `verity-vllm` suite runs inside `research run`

- **What fails.** The guard expects every loaded package to resolve inside the checkout. Under `research run`, `research` resolves to the
  harness's own copy at `/workspace/research/tool/<hash>/research/__init__.py`.
- **Where I saw it.** It was the only failure in a fresh suite run at `cursor/gemm-bias-v2-main-1046` @ `2fdd11053`
  (`r20261001-070033-a953`, 4,677 passed). It failed the same way on main `aac153709` (`r20261001-080850-1ac3`).
- **What it cost.** One red suite, and about 10 minutes plus two queue runs to show it wasn't my change. flock-ir-lowering hit the same
  failure on 09-29 ("this host's shared venv").
- **A fix.** Either the guard exempts the harness's `research` tool path, or `research run` stops putting that path ahead of the source
  tree's own `research` package.
