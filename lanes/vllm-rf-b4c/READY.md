---
id: vllm-rf-b4c/ready
lane: vllm-rf-b4c
kind: ready
updated: 2026-09-25T18:55Z
---
# b4c (engine and hooks): READY

**Branch** `lane/vllm-rf-b4c`, **head `9689a1ef`**, **base `lane/vllm-rf-a5c` `40b9e571`** (a5's merge request, which
contains main `f7de4620`). Agent bc-3b287dbf (cloud), successor of b4b (bc-892f86c5) and b4 (bc-95aa165d); coordinator
bc-ecac3029. Pushed; not merged anywhere.

## History of the head
| commit | what |
|---|---|
| `5c05ff6d` | b4b's head: b4's four commits (`engine/hooks.py`, `engine/env.py`, P11, test fix) rebased onto main `8b3537d5` (c1) |
| `5494e29f` | `git merge 38a8d35d` (main with b2vb, b5gmb, c2b): clean |
| **`9689a1ef`** | `git merge origin/lane/vllm-rf-a5c` (`40b9e571`), four conflicts resolved (below) |

The lane's own change is b4b's, unchanged: see `../vllm-rf-b4b/READY.md` ("What changed", "What deliberately didn't",
"Open questions", "Found, not fixed"; code identity before and after). The b4/b4b gate evidence at `0f71b5b4` / `2908cca1`
(gate (a) T0+T1 = a23b's base 158/158, #70 TP2 32/32 fields, FA3 on H100 PCIe head == base) is on the pre-c1 tree; what
carries over is stated per gate below.

## Conflict resolution at `9689a1ef`
- `pipeline/build.py`: import block only; keeps a5's `from verity_vllm.config import option` and b4's
  `from verity_vllm.engine import env as engine_env, hooks`. a5 moved the argparse/`__main__` block to the CLI; b4's two edits
  (`engine_env.apply_target`, `hooks.Hooks()` for the vocab-parallel binding) are outside it and auto-merged.
- `tests/lint/test_p07_declared_inputs.py`: `ENV_OWNERS = {engine/env.py, pipeline/cli.py}` (both may read the environment and
  name machine paths). **Small behaviour choice:** `pin_writes` now exempts only `PIN_OWNER = engine/env.py`, not all of
  `ENV_OWNERS`, so "engine/env.py is the one writer of vLLM's pins" still holds (`pipeline/cli.py` only reads). Docstring merged.
- `allowlists/p09_layering.json`: b4's deletion of every `runtime-patch` entry (including the four `evaluate_lazy` ones,
  cleared by b4's `_constructs` refinement) plus a5's `query.manifest.verify -> pipeline.manifest` edge.
- `allowlists/p10_size.json`: caps at the merged sizes, computed with the lint's own `file_sizes`: native_collect 1924,
  native_host 2572, rank_worker 1553, vllm_adapter 1913 (all at or below both sides); the rest take a5c's values, which equal
  the merged sizes. No allowlist grew.

## Gates at `9689a1ef`
### Lints
`python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q`
(inside `tools/gate_b.sh`): **47 passed** at head, 45 at base `40b9e571` (the two new: `test_only_engine_env_writes_vllm_pins`,
`test_leaf_modules_import_nothing`).

### Gate (b)
`OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile` (`tools/gate_b.sh`), head and base
on the same pod `vyv-rf-b4c-cpu` (cpu3g, 32 vCPU, AMD EPYC 9655P).

| run | tree | tests | failed | error | passed | skipped | xfailed |
|---|---|---|---|---|---|---|---|
| `r20260925-180449-ed37` | base `40b9e571` | 4046 | 56 | 11 | 3685 | 288 | 6 |
| `r20260925-180555-f321` | **head `9689a1ef`** | 4063 | 56 | 11 | 3703 | 287 | 6 |

`baseline-jdiff.py base head` (exit 0): **0 new failures, 0 new skips, 0 new skip reasons, 0 deleted or renamed**; 17 new
tests, all pass (5 `engine/test_env`, 10 `engine/test_hooks`, 2 lint). One outcome change, not counted:
`observe/test_observer_encoding::test_weakref_death...` skipped -> passed (allocator-dependent). Evidence
`evidence/gate_b2/` (XMLs gz, lints XMLs, env, jdiff).

Also at `5494e29f` vs main `38a8d35d` (same result shape, `r20260925-165436-ee4e` / `r20260925-165256-8dfd`, pod
`vyv-rf-b4b-cpu`): `evidence/gate_b/`.

### #101 (GPU row) at `9689a1ef`
`llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, 1x L40S `vyv-rf-b4b-g1`, FA2 matReq tap,
PAIRS=1, `verity-vllm row run ... --stages build,match,commit` (a5 removed `ops/row_pod.sh`; `tools/g1_cli.sh`), run
`r20260925-180228-0dda`:

| | record | head `9689a1ef` | `5494e29f` (`r20260925-172753-d0b2`, row_pod.sh) |
|---|---|---|---|
| Program | `ccc213475e7c4eed…` | = | = |
| manifest | `90f8186879d5035a…` (7043) | = | = |
| run root | `7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5` | = | = |
| Build / Match / Commit | PASS | PASS (step `03ace66f1c80b04a`, workload `a2b43bde001d335a`; global PASS, tokens equal, fold; every Commit check PASS, manifest_verify True) | same |

Non-interference (`verity-vllm noninterference --workload workloads/workload_32x16_1req.json`, `tools/nonint_cli.sh`,
`r20260925-184105-e73e`): **PASS 992/992 hashes, tokens a_observer / b_hooks / c_bare all True, problems 0** (also at
`5494e29f`). Evidence `evidence/r101/`.

### Gate (a), #70, FA3
Not re-run (the brief asks for lints, gate (b) and #101). b4b's gate (a) at `2908cca1` matched a23b's base 158/158; the
lane touches nothing under `tests/regression`, and the merges bring in other lanes' changes, which those lanes gated.

## Found, not fixed (new; b4b's list carries over)
- After a5, `python -m verity_vllm.properties.noninterference` exits 0 without doing anything (the module has an `Options`
  dataclass for the CLI and no `__main__` run); use `verity-vllm noninterference`. A silent exit 0 on the old entry point is easy to
  mistake for a pass. The same probably holds for other modules a5 moved onto the CLI.
- On `vyv-rf-b4b-g1` (image nvcc 12.4, 128 CPUs), `pod_bootstrap.sh`'s FA2 tap build fails with MAX_JOBS=nproc=128 (35 min, then
  CalledProcessError; the log is overwritten by a retry) and builds in 7 min with `MAX_JOBS=12`. The bootstrap could cap MAX_JOBS.
- The Project-store mount returns EAGAIN intermittently; the research CLI (checkpoint, machines.d reads) needs retries.
- `machines.d` again lists `vyv-rf-b4-{g1,h100,tp2}` (b4b unregistered them at 14:19Z; those pods are terminated).

## Pods and spend
| pod | part | used by b4c (Z) | $/h | about |
|---|---|---|---|---|
| `vyv-rf-b4b-cpu` cjzaq3ploo8kok | cpu 32 vCPU | 16:21-17:20 | 1.28 | $1.3 | **handed to vllm-rf-b5vab** 17:20Z |
| `vyv-rf-b4b-g1` nplcyinf9r2si8 | 1x L40S | 16:21-18:50 | 1.09 | $2.7 | **handed to vllm-rf-b5vab** 18:50Z |
| `vyv-rf-b4c-cpu` o7ow729nl1v0kw | cpu3g 32 vCPU | 18:02-18:48 | 1.28 | $1.0 | terminated, unregistered |

About **$5 of the $8** lane budget. Every run is PRESERVED on R2 (`research data preserved`), including the stopped ones
(`r20260925-164820-0072`, `r20260925-172034-f1de`, `r20260925-172357-4478`). No keys minted.
