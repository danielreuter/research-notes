---
id: vllm-rf-a5/state
lane: vllm-rf-a5
kind: state
updated: 2026-09-25T11:06Z
---
# a5 (one CLI, typed config, decision-8 `verity_vllm.LLM`): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T15:30Z (8:30 AM PT; updated 11:31Z)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 09:30Z: custody rule for the cloud switch-over.** Push your branch to origin after every commit, WIP included. If you have uncommitted work worth keeping, commit it now and push. The coordinator pushed snapshots of uncommitted work to wip/vllm-rf-{lane} for custody; they are not for merge, so ignore them.

Coordinator: vLLM coordinator bc-ba6cec03. Agent bc-95dc5f40. Worktree `~/projects/verity-wt/rf-a5`,
branch `lane/vllm-rf-a5`. **a4 base: 10996616.** Budget $35 of pod spend. Spent so far ~ $1 (g1 since 10:43Z ~$1.09/h, tp2 since 10:50Z ~$2.2/h, cpu since 11:03Z).

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
- `aa2abe5b` WIP: `verity-vllm row run|stage|chain|shed|fa-version` in Python — `pipeline/row.py` (options, dispatch),
  `row_driver.py` (evidence dir, logs, timeline, `timeout` + TERM/INT/HUP forwarding), `row_stages.py` (row_pod.sh),
  `row_tp.py` (tp_stage.sh), `row_records.py` (the heredocs, moved intact; broad excepts narrowed), `research.py`
  (run_row_v2.sh). RunEnv = options, machine defaults in `cli.MACHINE`, CLI environ = declared input. Shells not yet
  deleted; tests/lints for it pending. Never executed yet (laptop rule) — first run on the GPU pods.
- `c9cc81c4` WIP row driver unit tests (`tests/pipeline/test_row.py`); `d2950496` hot-commit test parses via the CLI
  (this commit also carries the deletion of tests/ops/test_row_pod_*.py + test_admission_hook.py, staged early);
  `7091cd8f` row tests replace the row_pod.sh source-extraction tests (target_family, release_json, source_identity,
  weights_pin_acceptance, flip_weight, weights_of_record CLI provenance); `row_stages.match_cmd()` extracted.

## Design (settled)
- Entry point: `Options` (or `COMMANDS = {"sub": SubOptions}`) + `main(opts)`; cli returns main's int unchanged,
  UsageError → exit 2. Spawns use `python -m verity_vllm.pipeline.cli <cmd>`; shells use the venv launcher.
- Row driver: `verity-vllm row run|stage|chain|shed` in `pipeline/row.py`; row_pod heredoc verdict moved intact.
- `verity_vllm.LLM(model, revision=..., ...)` → `EnginePin.resolve` → `engine.vllm_adapter.build_engine(...)`.

## Running
- Pods (all in ~/.research/machines.toml, guard 90): `vyv-rf-a5-g1` 4w1vzyvmibdvdf (1x L40S; bootstrap r20260925-105115-01c0 OK),
  `vyv-rf-a5-tp2` elzncz2ix7uehc (2x L40S community; bootstrap r20260925-105115-f9ea running), `vyv-rf-a5-cpu`
  hgbirbizmvoxy0 (cpu5g 16 vCPU / 64 GB; bootstrap launching). cpu3m/cpu3g/cpu5m were out of stock at 11:00Z.
- 11:04Z #101 (llama32-1b stoch B1) Build at head 7091cd8f via `verity-vllm row stage build` on g1: r20260925-110416-31fc;
  base records r20260924-202429-ba17 (match) / r20260924-212151-1320 (commit), program_digest 03ace66f1c80b04a.
- #70 plan: `row run --stages build,match` then `--stages commit` on tp2, vs base Commit r20260924-221949-8668
  (tp run root 0b91229f06480ce4…, commit FAIL rc=12 at the stage, verdict FAIL).

## Next
1. Census (dead_code_keep entries now live; `verity-vllm <cmd>` shell edges); ops shells → launcher; delete the 3 shells.
2. research Tools → CLI; shell-regex tests → unit tests; cli unit test.
3. `verity_vllm.LLM` + README section; pyproject `[project.scripts]`; cli unit test.
4. Pods: CPU (lints + gate b head/base), cpu3m (gate a), 1x L40S (#101, olmoe tp1, LLM example), 2x L40S (#70).

## Open questions
- b4: `verity_vllm.LLM` calls `engine.vllm_adapter.build_engine(checkpoints, *, max_num_seqs, engine_args, target,
  execution)`; if b4 relocates it, please keep the signature (brief says so) — the call site is `pipeline/llm.py`.
- b2v: `verity-vllm verdict from-record|mapping` now lives in `pipeline/verdict_record.py` (check/verdict.py keeps
  from_record/mapping_markdown, loses only its argparse main).

## Found, not fixed
- none yet
