---
id: vllm-rf-a5/state
lane: vllm-rf-a5
kind: state
updated: 2026-09-25T09:03Z
---
# a5 (one CLI, typed config, decision-8 `verity_vllm.LLM`): state

Coordinator: vLLM coordinator bc-ba6cec03. Agent bc-95dc5f40. Worktree `~/projects/verity-wt/rf-a5`,
branch `lane/vllm-rf-a5`. **a4 base: 10996616.** Budget $35 of pod spend. Spent: $0.

## Design (settled)
- `config.py`: row-id grammar (`RowId.parse`, `row_world/row_batch/row_execution/row_target`), `DTYPES`, `TARGETS`,
  `EnginePin.resolve(model, revision)` (internal pinned-engine record; replaces nothing public), Build/Match/Commit
  configs, `RunEnv` (machine paths + environ snapshot, filled only by the CLI), and the option machinery
  (`option(*flags, env=..., **argparse_kw)`, `group(cls)`, `UsageError`).
- Every library entry point: `Options` dataclass (or `COMMANDS = {"sub": SubOptions}`) + `run(opts) -> int`.
  No argparse / `__main__` outside `pipeline/cli.py`. `pipeline/cli.py` builds the parser from the dataclass fields,
  applies env defaults, owns the registry (`verity-vllm <command> ...`).
- a4's manifest CLI (`pipeline/cli.py` today) moves to `pipeline/manifest.py` as a regular subcommand module.
- `ops/row_pod.sh`, `tp_stage.sh`, `run_row_v2.sh` → `verity-vllm row run|stage|chain|shed` (Python driver under
  `pipeline/`); the row_pod match heredoc verdict (row_pod.sh:686-800) moves intact.
- Machine-path defaults move into cli.py; P7 exempts ENV_OWNERS from machine-path (documented in the lint).
- `verity_vllm.LLM(model, revision=..., ...)` → `EnginePin.resolve` → `engine.vllm_adapter.build_engine(...)`.

## Done
- Survey of `__main__`/argparse sites, ops scripts, env reads (tools in `tools/`).
- `config.py` written (uncommitted); AST rewriter `tools/rewrite_cli.py` written.

## Running
- nothing.

## Next
1. Run rewriter over argparse modules, hand-convert the rest, write `pipeline/cli.py`; update callers/tests.
2. Row driver port; research Tools → CLI; shell-regex tests → unit tests.
3. `verity_vllm.LLM`; README section; pyproject scripts; lints/allowlists.
4. Pods: CPU (lints + gate b), cpu3m (gate a), 1x L40S (#101, olmoe tp1, LLM example), 2x L40S (#70).

## Open questions
- b4: `verity_vllm.LLM` calls `engine.vllm_adapter.build_engine(checkpoints, *, max_num_seqs, engine_args, target,
  execution)`; if b4 relocates it, please keep the signature (brief says so) — the call site is `pipeline/llm.py`.

## Found, not fixed
- none yet
