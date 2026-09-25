---
id: vllm-rf-a4/state
lane: vllm-rf-a4
kind: state
updated: 2026-09-25T10:08Z
---
# a4 (re-home into the §5.1 tree): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T14:00Z (7 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

> **Coordinator, 06:35Z: owner-approved naming. The evaluator implementations are "kernels": use `program/kernels/`, not `program/backends/`,** wherever SYNTHESIS 5.1/5.2 say `program/backends/`. That is where `numerics/` goes, with its `tables/` package data and `cpp/` sources, and where twins and derived rows go if a whole module moves. Put it in your move map now, and use "kernels" in `INTERIM_LAYER` / layer names. Details: `20260925T0635Z-handoff-from-vllm-coordinator.md`.
> **a4, 07:12Z: done** in `22f5bc58` (a follow-up commit renaming the PROGRAM commit's `program/backends/`). There is no backends layer in the P9 order (backends sat inside `program`), so `program/kernels/` stays in the `program` layer.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-a4`, branch
`lane/vllm-rf-a4`, head **`10996616`** (pushed), on origin/main `00ffe398`. origin/main has since moved to `5631e667`
(backends/numerical only); not rebased yet.

## Done (evidence under `evidence/`)
- All moves committed and pushed. Library commits: pipeline `2b8836c7`, engine `f2f1bf0a`, program `c397545b`, query
  `dd83b50b`, observe `ad847624`, kernels rename `22f5bc58`, commit/committer `9b755a43`, acquire/sources `32f783c5`,
  fixture `c95d3199`, check/match+replay `2bdfd9ce`, properties `e6f19e42`, collectives `6a0097f6`, lint LAYER
  `34400229`, README `14b0cf9f`, P11 stale entry `756d04d2`, tests `10996616`.
- Lints 45/45 at head and at base (cpu pod).
- Gate (b), xdist `-n 12 --dist loadfile`, same pod, head `10996616` vs base `00ffe398`: no new error, skip or skip
  reason. One new failure, `tests.program.test_twins::test_check_writes_the_evidence_schema`: it depends on state (the
  'openmp' flag is recorded by the first process to JIT-build tc_model), fails at base on a fresh tree, and passes at
  both once the library exists. 942 renamed test ids in 85 files (`evidence/gate_b/jdiff-head2.txt`).
- GPU smoke #101 (L40S), head and base: run_root `7adcef49…` equal to the record, program `ccc21347…`, manifest
  `90f81868…`, commit PASS. Only provenance differs (construction_version, registry digest, driver module names,
  paths). All 33 `python -m` targets in ops/*.sh resolve at head.
- Code identities: code_identity = hot key = research_tools closure `248d6621…` -> `a2cf5fc7…`; construction_version
  `9738a467…` -> `53cfbe1c…`; registry_version `a2204fa7…` -> `beb5d5f7…`.
- Pods `vyv-rf-a4-cpu` and `vyv-rf-a4-g1` are terminated.

## Running
- `vyv-rf-a4-reg` (04fijzazbf1yj6, A100-SXM4 host, 250 GB cgroup, $1.59/h): gate (a) T0+T1 on head since 08:30Z
  (fixtures prefetched with a laptop-minted RO key, deleted 08:30Z). At 10:07Z it was 72/158 (45%), about 1.9x
  slower than a23b's base, so the ETA is about 12:00Z (deadline 13:00Z). Memory: pytest RSS 101.6 GB, cgroup peak 130.8 GB of 250 GB.
- The twins failure at base is now reproduced on one pod with an empty build dir (base and head both 1 failed; both pass
  once built): `evidence/twins/`. READY.md is drafted apart from gate (a) and the reg pod's cost.

## Next
1. When gate (a) finishes, jdiff against `vllm-rf-a23b/gate_a-t0t1-base-72884c8a-samepod.xml.gz`; terminate reg.
2. Finalize READY.md (draft exists) and send the final message.

## Found, not fixed
- `engine/engine_profile.py:130` `TP_WORKER_EXTENSION` names `verity_vllm.tp.poc_tp_worker`, which does not exist.
- `pipeline/commit.py` imports `workload_target` (absent; inside try/except).
- `engine_profile.py:102` comment names `verity_vllm/input_provenance/add_checkpoint.py` (never existed).
- `check/match/global_match_fast.py:24` names mfast's `verity_vllm/harness/match_diff.py`.
- `commit/__init__.py` docstring describes native_collect.
