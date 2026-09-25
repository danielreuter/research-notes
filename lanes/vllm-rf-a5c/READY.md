---
id: vllm-rf-a5c/ready
lane: vllm-rf-a5c
kind: ready
updated: 2026-09-25T17:55Z
---
# a5c READY: one `verity-vllm` CLI, typed config (`config.option`), `verity_vllm.LLM`

- **Branch** `lane/vllm-rf-a5c`, **head `40b9e571`** (pushed) = a5b's `da9e4847` rebased onto main (`ce6d69d4`, on `239c0e28`),
  then `git merge origin/main` at **`f7de4620`** (per coordinator 1655Z; main had moved past `38a8d35d` to b5patb's merge).
- **Base** `f7de4620`. a5/a5b/a5c history: a5 bc-95dc5f40 -> a5b bc-a9b686f7 -> a5c bc-ac8c8a30.

## Gates
| Gate | Head | Base | Result | Runs / evidence |
|---|---|---|---|---|
| 1. Lints (lint/, no_by_name, imports_resolve) | 40b9e571 | f7de4620 | 45/45 both; jdiff 0 changes | t1 `r20260925-170857-a861` / `r20260925-173534-b495`; `evidence/jdiff-lints-40b9e571-vs-f7de4620.txt` |
| 2. Gate (b) `-n 12 --dist loadfile`, same pod (t1) | 4046: 57F/3685P/287S/6xF/11E | 4023: 57F/3662P/287S/6xF/11E | **0 new failures, 0 new skips, 0 new skip reasons**, 0 outcome changes; 40 only-in-base, 63 only-in-head (all pass) | same runs; `evidence/jdiff-gate_b-40b9e571-vs-f7de4620.txt`; XMLs `/workspace/a5c/logs/{head-40b9e571,base-f7de4620}-{lints,gate_b}.xml` on t1 |
| 3. Gate (a) T0+T1 | da9e4847 | a23b's same-pod base XML | 73P/85S both, 0 changes; 2 reworded skip reasons (#70/#75 manifest_digest: tp_stage.sh -> CLI) | t1 `r20260925-142613-7113`; `/workspace/a5/logs/jdiff-gate_a-head-da9e4847.txt` |
| 4. #101 via `verity-vllm row` (g1) | 40b9e571 | row of record | SAME-OF-RECORD: program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`, 33/33 checks, commit PASS | `r20260925-170927-4a2d` (also `r20260925-164441-db55` at ce6d69d4, `r20260925-145116-81b6` at da9e4847) |
| 4. #70 TP2 via `verity-vllm row` (tp2d) | da9e4847 | f1's base Commit of record | commit FAIL = record (class FAIL); cmp70 **32/32 equal**, CMP70_RC=0 | `r20260925-144310-53e5`; `evidence/cmp70.txt` |
| 4. `LLM(...)` example (g1) | da9e4847 | vllm.LLM same kwargs | EQUAL greedy + sampled (a5b) | `r20260925-142335-a597` |

All runs PRESERVED on R2 (`research data preserved <run>`).

**Gate (a) scope:** run at `da9e4847` (on a4). It carries to `40b9e571` only for files main didn't change since a4: c1 (`commit/`
scheme), b2vb (`properties/`, verdict), b5gmb (`check/match/*` split), c2b, b5patb touched regression-relevant code, and gate (a)
was not re-run on the merged tree (coordinator asked for lints + gate (b) + #101 only). Gate (b)'s regression-adjacent unit tests
and the #101 smoke cover the merged tree.

**Only-in-base 40:** deleted `tests/ops/test_row_pod_*` (row_pod.sh is gone; its logic is `verity-vllm row`) and renamed tests in
test_weights_pin_acceptance, test_admission_hook, test_release_json, test_source_identity, program/test_lint, test_target_family
(these now run through the CLI; the 63 only-in-head are their successors plus new CLI tests, all pass).

## What changed (a5's scope)
- `pipeline/cli.py` is the only parser: a lazy registry of subcommands; each library module declares an `Options` dataclass with
  `config.option()` and a `main(opts)`. No argparse or `__main__` elsewhere in `verity_vllm`. P6/P7/P10/P11 allowlists shrink.
- row_pod.sh / tp_stage.sh / run_row_v2.sh replaced by `verity-vllm row [stage]`; `verity_vllm.LLM` (pinned engine via
  `build_engine`, called like `vllm.LLM`); README.
- Merge resolutions: `check/match/global_match.py` (a5's Options/main re-applied onto b5gmb's 416-line module),
  `properties/{census,golden,holdout,noninterference,protected,quarantine_lint}.py` and two tests (both sides' imports),
  `commit/padding_steps.py` + `hidden_gpu.py` (c1's `scheme` + `config.option`), `p10_size.json` (all caps recomputed from the
  merged tree; nothing grew, 19 caps lowered, `pipeline/match.py main` deleted).

## Deliberately not changed
- No Program, manifest, commitment root, leaf id or verdict input changes; no allowlist grows. Flags, defaults and env fallbacks
  of every command are the same.

## Found, not fixed
- TP Commit (`pipeline/tp/commit.py`) writes no `commit/verdict.json`, so `check.verdict.from_record` gives INSUFFICIENT_EVIDENCE on
  TP rows (base and head alike). Folding it into `vllm-verdict/v1` is a verdict-semantics change, not small.
- b2vb's deferred `row_pod.sh:686-800` heredoc verdict now lives as `pipeline/row_records.match_summary` (a straight port).
  Folding it into `check/verdict.py` changes the Match decision's plumbing; not small, left for a verdict lane.
- `tests.observe.test_observer_encoding::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation` flips pass/skip by
  test order (seen at base too).
- Store FS (Project store) returns EAGAIN on overwriting a recently written file; `research notes checkpoint` fails intermittently.
