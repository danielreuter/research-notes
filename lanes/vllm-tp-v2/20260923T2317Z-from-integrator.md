---
id: vllm-tp-v2/20260923T2317Z-from-integrator
lane: vllm-tp-v2
kind: handoff
status: open
repo: verity
origin: lane/vllm-cleanup-2
---
# From the integrator: tp-n × staging, two breakages with no textual conflict

Context: `lane/vllm-tp-n` @ `40f40a2` (based on main `22e10e0`) merged into staging `lane/vllm-cleanup-2` @ `e071391` (now `b773399` with sampler-literals). Beyond the 6 textual conflicts, the merge has two breakages git does not flag:
- allowlist
- `sweep/research_outputs.py`
- `sweep/row_pod_tp2.sh`
- `sweep/run_row_v2.sh`
- `tp/capture.py` and `tp/fold_match.py` (the `bench/tp2_*` → `tp/*` moves against profiles-generic / hygiene edits)

Line numbers below are at `origin/lane/vllm-tp-n` `40f40a2` unless marked staging.

## 1. `tp_stage.sh` points Qwen3 TP rows at a deleted profile

- `integrations/vllm/verity_capture/sweep/tp_stage.sh:112`:
  ~~~
  case "${FOLD_PROFILE-unset}" in unset) case "$ROLE" in QWEN3_30B_A3B) FOLD_PROFILE=gen_ov_moe_qwen3 ;; *) FOLD_PROFILE="" ;; esac ;; esac
  ~~~
  The profile is consumed at `:209` (`python -m verity_capture.tp.fold_match ... --profile "$FOLD_PROFILE"`) and `:261` (`--require-fold-match`).
- `verity_capture/profiles/gen_ov_moe_qwen3.py` does not exist on staging. `09589c73` ("vllm/profiles: retire the per-model hand modules; every role is generic.build_profile (P6, step 2)") deleted it, along with `gen_llama_llama32_1b_tp2rank.py` and `vllm_d9105ea80_sm89_eager_qwen15_tp2rank.py`. tp-n does not modify these files, so the merge deletes them silently, and a Qwen3 TP row's fold Match would fail on import.
- Staging's convention (staging `sweep/row_pod_tp2.sh:26,106-107`):
  ~~~
  case "${FOLD_PROFILE-unset}" in unset) FOLD_PROFILE="derived_${ROLE}_tp${WORLD}" ;; esac
  ~~~
  `derived_<ROLE>_tp<W>` is materialised on import by the `sys.meta_path` hook in `verity_capture/profiles/__init__.py:6-14` (→ `generic.make_module`). `profiles/expected/` pins `derived_B1_tp2`, `derived_LLAMA32_1B_tp2` and `derived_QWEN3_30B_A3B_tp2`.
- Behaviour choice for the lane: tp-n runs the fold Match for `QWEN3_30B_A3B` only, while staging's TP2 runner runs it for every role.
- Other references to retired modules:
  - `tp/fold_match.py:8` and `:150`, in a conflict hunk: `--profile gen_llama_llama32_1b_tp2rank` in the usage/help text. Staging says `derived_LLAMA32_1B_tp2 (profiles.generic, world = 2)`, and tp-n's own change on that hunk is `--build-rank0/1` `default=None`.
  - The tests that import the retired modules on main (`verity_capture/tests/test_tp2_rank_profiles.py`, `test_gen_ov_moe_qwen3.py`) are unmodified by tp-n, so the merge takes staging's retargeted versions. Nothing to do there.

## 2. The sweep-output code reads `commit_summary.json`, which staging no longer writes

- `integrations/vllm/verity_capture/sweep/research_outputs.py:60`:
  ~~~
  COMMIT_FILES = ["commit_summary.json", "weights_of_record.log", "manifest.log", "manifest_verify.log"]
  ~~~
- `research_outputs.py:201-205`, the commit stage:
  ~~~
  cs = _read_json(d / "commit_summary.json") or (_read_json(d / "commit" / "summary.json") if tp else None) or {}
  ... "tokens_equal": cs.get("tokens_equal"), "n_runs": cs.get("n_runs")
  ~~~
  The docstring `:18-19` lists `commit_summary.json` among the commit outputs.
- Staging deleted the writer in `9e080093` ("vllm P5: delete the finalize board and the commit_summary writer"). Staging's reader is the verdict of record:
  - staging `research_outputs.py:18-21` (docstring: "commit_summary.json and the finalize board are retired: F-r19-int-21 / P5").
  - staging `:51`: `COMMIT_FILES = ["verdict.json", ...]`.
  - staging `:172-179`: meta `outcome` / `n_runs` / `runs_failed` from `verdict.json`'s `outcome` and `runs`.
  - `commit/verdict.py:144-149` maps each retired `commit_summary.*` field to its `verdict.json` replacement, and `:1311` writes `commit_summary_deprecated`.
- Consequences:
  - On a TP1 row, tp-n's version lists `commit_summary.json` as missing and returns `tokens_equal` / `n_runs` = None.
  - On a TP row, it falls back to `commit/summary.json`, which `tp/commit.py:1168,1171` does write.
- Related: `tp_stage.sh` does not write `verdict.json`. Staging's `row_pod.sh:1112-1120` does (`python -m verity_capture.commit.verdict from-record "$D" --rc ...`). Under staging's verdict-based `research_outputs`, a TP row's commit entry therefore has `outcome` / `n_runs` = None unless `tp_stage.sh` gains the same step. The pass/fail decision (`tp_stage.sh:266-268`) reads `commit/summary.json`.
- Also: `tp_stage.sh:133` builds the N-rank manifest with `verity_capture.commit.required_manifest build-global` (v1). That is your v2-query move. p2p4 (`fd23744`, "required_manifest says what still keeps members_for (TP rank Programs, ...)") is changing the same module.

## Smaller items in the textual conflicts
- `sweep/run_row_v2.sh` (`cmd_stage`): the flip (`b353ed20`) removed the v1 `required_manifest build/build-global` fallback after the stage, because `row_pod.sh` builds the manifest at the end of a PASS Build via `verity_vllm.query.cli`. tp-n's only real change there is the runner selection (`row_world` → `tp_stage.sh`). The v1 block in the conflict is main's, not tp-n's.
- `tp/capture.py:4` usage: the module path is `verity_capture.tp.capture` (tp-n). The workload is `workloads/workload_qwen15_32x16_1req.json` on staging (tp-n: `verity_capture/profiles/...`).
- Allowlist: tp-n's entries for `profiles/gen_llama_llama32_1b_tp2rank.py` (`tests/by_name_allowlist.json:3035,3045` at tp-n) name a file staging deleted. The staging count is 316 and may not grow.
