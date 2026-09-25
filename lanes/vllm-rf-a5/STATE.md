---
id: vllm-rf-a5/state
lane: vllm-rf-a5
kind: state
updated: 2026-09-25T10:02Z
---
# a5 (one CLI, typed config, decision-8 `verity_vllm.LLM`): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T14:00Z (7 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

Coordinator: vLLM coordinator bc-ba6cec03. Agent bc-95dc5f40. Worktree `~/projects/verity-wt/rf-a5`,
branch `lane/vllm-rf-a5`. **a4 base: 10996616.** Budget $35 of pod spend. Spent: $0.

## Commits (pushed to origin/lane/vllm-rf-a5)
- `f1a63699` config: typed configuration (RowId grammar, DTYPES, TARGETS, EnginePin, Build/Match/Commit configs,
  RunEnv, option()/group()/UsageError); target_family.DEVICE_FAMILY = config.TARGETS; P8 gpu entries move.
- `38bf7043` one `verity-vllm` CLI: every library argparse/`__main__` block → `Options` dataclass (or `COMMANDS`) +
  `main(opts)`; `pipeline/cli.py` is the only parser and env reader; old pipeline/cli.py → `pipeline/manifest.py`;
  check/verdict's CLI → `pipeline/verdict_record.py` (P4); telemetry admission commands →
  `pipeline/telemetry/admission_commands.py` (P10); pod_bootstrap writes a `verity-vllm` launcher.
  Lints: P6/P7 owners = pipeline/cli.py; P11 now checks option() flag/env names. Allowlists: P6 −~130, P7/P10 shrink,
  P8/P9/P11 moves. Static: pyflakes no new messages; all 12 ratchet lints 0 new / 0 stale (relint, pure ast).
  Tests not yet run (pods).

## Design (settled)
- Entry point: `Options` (or `COMMANDS = {"sub": SubOptions}`) + `main(opts)`; cli returns main's int unchanged,
  UsageError → exit 2. Spawns use `python -m verity_vllm.pipeline.cli <cmd>`; shells use the venv launcher.
- Row driver: `verity-vllm row run|stage|chain|shed` in `pipeline/row.py`; row_pod heredoc verdict moved intact.
- `verity_vllm.LLM(model, revision=..., ...)` → `EnginePin.resolve` → `engine.vllm_adapter.build_engine(...)`.

## Running
- nothing (no pods yet).

## Next
1. Census (dead_code_keep entries now live; `verity-vllm <cmd>` shell edges); ops shells → launcher.
2. Row driver port (row_pod.sh, tp_stage.sh, run_row_v2.sh) + research Tools → CLI; shell-regex tests → unit tests.
3. `verity_vllm.LLM` + README section; pyproject `[project.scripts]`; cli unit test.
4. Pods: CPU (lints + gate b head/base), cpu3m (gate a), 1x L40S (#101, olmoe tp1, LLM example), 2x L40S (#70).

## Open questions
- b4: `verity_vllm.LLM` calls `engine.vllm_adapter.build_engine(checkpoints, *, max_num_seqs, engine_args, target,
  execution)`; if b4 relocates it, please keep the signature (brief says so) — the call site is `pipeline/llm.py`.
- b2v: `verity-vllm verdict from-record|mapping` now lives in `pipeline/verdict_record.py` (check/verdict.py keeps
  from_record/mapping_markdown, loses only its argparse main).

## Found, not fixed
- none yet
