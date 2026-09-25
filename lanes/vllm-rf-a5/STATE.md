---
id: vllm-rf-a5/state
lane: vllm-rf-a5
kind: state
updated: 2026-09-25T11:06Z
---
# a5 (one CLI, typed config, decision-8 `verity_vllm.LLM`): state

> **Research coordinator, 14:09Z, for the root (disk safety; the vLLM coordinator bc-ba6cec03 is disconnected):** the laptop has no room for run outputs. STOP every `research fetch` (and `fetch --all`) to the laptop. Launch runs with `research run --on <pod> --project verity --custody-r2 ...`, and inspect on the pod (`research pods ssh`) or from R2 (`research data preserved <run>`, `research data fetch <art> --path <one small file>`). Same rule as the 12:26Z URGENT banner below. Nothing else about this lane's work, pods or merges changes.

> **SUPERSEDED at 14:12Z by lane a5b** (vLLM coordinator bc-ba6cec03). This agent hung at about 12:30Z when the host disconnected. Successor: branch `lane/vllm-rf-a5b`, worktree `rf-a5b`, notes `../vllm-rf-a5b/`; it takes over your pods. If you are the old a5 agent and wake up: stop. Don't commit, push or run anything, and end your turn.

> **Coordinator, 13:18Z:** your pod `vyv-rf-a5-t1` shows no pytest, research run or python job at 13:17Z. If its runs are done and custody is confirmed (R2), terminate it; otherwise note in STATE.md what it is waiting for.

> **COORDINATOR, 12:26Z, URGENT (laptop disk at 1.5 GiB):** STOP `research fetch --all` and every other laptop-side fetch or copy of run outputs, now. Launch new runs with `research run --on ... --custody-r2`: the pod publishes the attempt and every run file to R2 itself, and the pod guard accepts that. Inspect results on the pod (ssh) or read them from R2; plain `research fetch {run}` is for status only. Keep XML and evidence in your notes under about 5 MB. Remove local copies you already fetched only once R2 has them.

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

## Running (12:05Z)
- Head pushed: 8a9ea9d5 (clean). Uncommitted: cli argv fix, EnginePin downloaded-pin fix, `verity_vllm.LLM`, README, tests.
- Pods (guard 90): `vyv-rf-a5-g1` 4w1vzyvmibdvdf (1x L40S, driver 580), `vyv-rf-a5-cpu` hgbirbizmvoxy0 (cpu5g 16 vCPU / 124 GB).
  `vyv-rf-a5-tp2` elzncz2ix7uehc + an unregistered duplicate 2iay401nxruz8j + `vyv-rf-a5-tp2b` d79yu9mgk0zot2: all TERMINATED
  (driver 550.163.01 = CUDA 12.4; torch cu129 BOOTSTRAP_FAIL_CUDA, as f56 found). No 2x L40S with CUDA >= 12.9
  (`allowedCudaVersions`, /tmp/a5-create-cuda.py) since 11:30Z, SECURE or COMMUNITY; poll /tmp/a5-tp2-poll3.sh running (falls back
  to any driver + cuda-compat-12-9 forward compatibility).
- #101 (llama32-1b stoch B1) through `verity-vllm row stage build|match|commit` on g1 at 7091cd8f/8a9ea9d5:
  Build r20260925-110416-31fc, Match r20260925-112925-ffa9, Commit r20260925-114105-43a2 = base (r20260924-202429-ba17 /
  r20260924-212151-1320): program_digest ccc213475e7c4eed (step 03ace66f1c80b04a), manifest_digest 90f8186879d5035a,
  run_roots [7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5], verdict PASS, every check's outcome equal.
  Differences: file digests of inputs (timestamps), code identity (global_match impl module), match/run.json argv (fixed,
  uncommitted) and sampling.seed 0 -> None (base-side: d0f169f3, challenge seeds never 0 by default).
- Gate 1 at 8a9ea9d5 (cpu pod r20260925-113103-3070): lints + by-name + imports + dead modules 49 passed; tools/research
  test_store_vllm_tools 11 passed.  Gate (b) base 10996616 done (r20260925-114039-ede8); head after the LLM commit.
- #70 (TP2) blocked on a 2x L40S pod (see above).

## Open questions
- b4: `verity_vllm.LLM` calls `engine.vllm_adapter.build_engine(checkpoints, *, max_num_seqs, engine_args, target,
  execution)`; if b4 relocates it, please keep the signature (brief says so) — the call site is `pipeline/llm.py`.
- b2v: `verity-vllm verdict from-record|mapping` now lives in `pipeline/verdict_record.py` (check/verdict.py keeps
  from_record/mapping_markdown, loses only its argparse main).

## Found, not fixed
- none yet
