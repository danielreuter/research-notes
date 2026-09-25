---
id: vllm-rf-a4/state
lane: vllm-rf-a4
kind: state
updated: 2026-09-25T08:23Z
---
# a4 (re-home into the §5.1 tree): state

> **Coordinator, 06:35Z: owner-approved naming. The evaluator implementations are "kernels": use `program/kernels/`, not `program/backends/`,** wherever SYNTHESIS 5.1/5.2 say `program/backends/`. That is where `numerics/` goes, with its `tables/` package data and `cpp/` sources, and where twins and derived rows go if a whole module moves. Put it in your move map now, and use "kernels" in `INTERIM_LAYER` / layer names. Details: `20260925T0635Z-handoff-from-vllm-coordinator.md`.
> **a4, 07:12Z: done** in `22f5bc58` (a follow-up commit renaming the PROGRAM commit's `program/backends/`). There is no backends layer in the P9 order (backends sat inside `program`), so `program/kernels/` stays in the `program` layer.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-a4`, branch
`lane/vllm-rf-a4`. **f1 merged; rebased onto origin/main `00ffe398` at 06:55Z** (force-with-lease). origin/main has since
moved to `5631e667` (backends/numerical only; merges #19, #20); not rebased yet.

## Done
- All moves committed and pushed; head **`10996616`** (test-file moves). Library commits: pipeline `2b8836c7`, engine
  `f2f1bf0a`, program `c397545b`, query `dd83b50b`, observe `ad847624`, kernels rename `22f5bc58`, commit/committer
  `9b755a43`, acquire/sources `32f783c5`, fixture `c95d3199`, check/match+replay `2bdfd9ce`, properties `e6f19e42`,
  collectives `6a0097f6`, lint LAYER `34400229`, README `14b0cf9f`, P11 stale entry `756d04d2`, tests `10996616`.
- Early head run (head1 = `14b0cf9f`) on vyv-rf-a4-cpu vs basemain `00ffe398`: 8 new failures, all fixed in `756d04d2` /
  `10996616` except two state-dependent ones: test_twins 'openmp' (reproduced at base on a fresh tree with no
  numerics JIT build: `/workspace/basefresh`), test_roundtrip transient storage (+152 B over the bound under xdist;
  passes alone at base and at head).
- Code identities (basemain -> head2, cpu pod `ident-*.json`): code_identity = hot-commit key = research_tools closure
  `248d6621…` (1170 files) -> `a2cf5fc7…` (1178); construction_version `9738a467…` -> `53cfbe1c…`; registry_version
  `a2204fa7…` -> `beb5d5f7…` (prims.py import lines).

## Running (tree `/workspace/head2` = basemain + `git diff 00ffe398 10996616` on every pod)
- `vyv-rf-a4-cpu` (4q60rifwx2r1bp): head2 lints + gate (b) xdist (started ~08:14Z) -> logs/head2*.
- `vyv-rf-a4-reg` (04fijzazbf1yj6, A100-SXM4 host, 250 GB cgroup, $1.59/h; no cpu3m/cpu5m 256-512 GB was available):
  bootstrap from head2 + pins (xdist 3.8.0, xgrammar 0.2.7), then prefetch (laptop-minted RO key) and gate (a) T0+T1.
- `vyv-rf-a4-g1` (7pmzr4ccgcomqa, 1x L40S, $1.09/h): `row101.sh` bootstrap --gpu LLAMA32_1B, row #101 build,match,commit at
  head2 then basemain.
- Pods registered via `research pods create --register` (machines.d, guard 90). Pod-to-pod tree copy via an ephemeral
  key (`/root/.ssh/a4pull` on reg/g1, pubkeys appended to the cpu pod's authorized_keys).

## Next
1. Fixture key for reg pod once bootstrap is done; gate (a); compare with a23b's base xml.
2. jdiff (tools/jdiff_moved.py) head2 vs basemain; GPU results; `python -m` resolution in ops/*.sh.
3. READY.md, terminate pods, final message.

## Found, not fixed
- `engine/engine_profile.py:130` `TP_WORKER_EXTENSION` names `verity_vllm.tp.poc_tp_worker`, which does not exist.
- `pipeline/commit.py` imports `workload_target` (absent; inside try/except).
- `engine_profile.py:102` comment names `verity_vllm/input_provenance/add_checkpoint.py` (never existed).
- `check/match/global_match_fast.py:24` names mfast's `verity_vllm/harness/match_diff.py`.
- `commit/__init__.py` docstring describes native_collect.
