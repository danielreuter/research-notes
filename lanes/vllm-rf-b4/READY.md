---
id: vllm-rf-b4/ready
lane: vllm-rf-b4
kind: ready
updated: 2026-09-25T11:05Z
---
# b4 (engine and hooks): READY

**Branch** `lane/vllm-rf-b4`, **head `0f71b5b4`**, **base `10996616`** (a4's head). Four commits, all pushed; not merged
anywhere. Coordinator: bc-ba6cec03. Agent: bc-95aa165d.

**Summary.** `engine/hooks.py` is the one owner of every runtime patch on a vLLM, torch or Triton object, and every patch
uninstalls to what the owner held. All 43 P9 `runtime-patch` allowlist entries are gone, and P9 now fails any other module
that sets an attribute on an imported object. `engine/env.py` is the one writer of vLLM's environment pins, and a new P7
check fails any other library module that writes a `VLLM_` / `HF_` / `TORCHINDUCTOR_` / `TOKENIZERS_` switch (17 P7
entries gone). No allowlist grew. `build_engine` / `engine_kwargs_for` signatures are unchanged. No identity changed: the
Program, manifest, run root and verdict of #101 (L40S, FA2 tap) and #70 (TP2) equal the record and the base; FA3 on H100:
FA3_RESULT. Gates (b) and lints are green; gate (a): GATE_A_RESULT.

## Commits
| commit | what | digests |
|---|---|---|
| `5ddb68f8` | `engine/hooks.py`: `patch` / `wrap` / `append` / `patched` / `Hooks` / `live` / `triton_launch`; every patch site moved onto it; 43 P9 entries deleted; P10 caps follow the shrunk modules | code identity only (construction_version) |
| `619b7451` | `engine/env.py`: the one writer of the env pins; 17 P7 entries deleted; P7 pin-writer check | code identity only (construction_version) |
| `3bdcd0ad` | P11: the moved docstring loses its board tag (2 entries deleted) | none |
| `0f71b5b4` | test fix: the MoE export-shim test imports vLLM's fused_moe before it records the packet | none |

No commit moves a Program, manifest, commitment root, leaf id or verdict, so nothing here is labeled for the re-baseline
epoch.

**Code identity before and after.** `construction_version.sources_sha256` (hashes `pipeline/build.py`'s
`_CONSTRUCTION_SOURCES`): base `53cfbe1cff28691479252b5344e9e3123accb2b6bde0d9bf88f8026c08d129e9`, `5ddb68f8`
`043c8138…`, `619b7451` `a625a383…`, head `92aed41014de8f215a1b84ac571e1253705088ad6e695e79d5d1dd20fd6b6cab` (the head
value is also the one in #101's head `build_request/artifact.json`; `tools/cv.py` computes it from git). It moves because
`export_compat.py`, `export_ops.py`, `triton_capture.py`, `vllm_meta.py` and `pipeline/build.py` are construction sources
and were edited, and because `engine/env.py` joined the list (it now carries the pins `vllm_meta` used to write). The
artifact `identity` hashes construction_version, so it moves with it: #101 `build_request` base `2dfc73d495f11f95…` ->
head `368834e8f1bc57e0…`, `build_step` base `04230e17cc1033f7…` -> head `385c103b5ab3194f…`. Those two are the only
top-level keys of `artifact.json` that differ between the head and base Builds on the same pod (the base value of
construction_version there is `53cfbe1c…`, as computed from git); `program_digest` and `correspondence_digest` are equal.

## Gates

### Lints
`python -m pytest integrations/vllm/tests/lint integrations/vllm/tests/test_no_by_name_rules.py integrations/vllm/tests/test_imports_resolve.py -q`
(`tools/lints.sh`), on `vyv-rf-b4-cpu`: **47 passed at `0f71b5b4`** (`evidence/gate_b/head2-lints.log`, inside run
`r20260925-101530-aa45`), 47 at `3bdcd0ad`, 45 at base (the two new lint tests are
`test_p07_declared_inputs::test_only_engine_env_writes_vllm_pins` and `test_p09_layering::test_leaf_modules_import_nothing`).

### Gate (b)
`OMP_NUM_THREADS=3 python -m pytest integrations/vllm/tests -ra -n 12 --dist loadfile` (`tools/gate_b.sh`), head and base
on the same pod `vyv-rf-b4-cpu` (cpu3g, 32 vCPU, 128 GB), each from its own fresh tree.

| run | tree | tests | failed | error | passed | skipped | xfailed |
|---|---|---|---|---|---|---|---|
| `r20260925-095250-e4e8` | base `10996616` | 4001 | 56 | 11 | 3642 | 286 | 6 |
| `r20260925-101530-aa45` | **head `0f71b5b4`** | 4018 | 55 | 11 | 3659 | 287 | 6 |
| `r20260925-095236-2684` | `3bdcd0ad` | 4018 | 57 | 11 | 3658 | 286 | 6 |

`baseline-jdiff.py base.xml head2.xml` (`evidence/gate_b/jdiff-head2-vs-base.txt`): **0 new failures, 0 new skips, 0 new
skip reasons, 0 tests deleted or renamed**; 17 new tests, all pass (5 `tests/engine/test_env.py`, 10
`tests/engine/test_hooks.py`, 2 lint). Two outcome changes, neither from this lane:
- `tests.observe.test_observer_encoding::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation` passed -> skipped
  ("allocator did not reuse the pointer"); jdiff marks it order-dependent at base and doesn't count it.
- `tests.program.test_twins::test_check_writes_the_evidence_schema` failed -> passed. See "Found, not fixed".

At `3bdcd0ad` the one new failure was my own new test (`test_export_shims_restore_torch_and_vllm`: the `fused_experts`
packet exists once vLLM's fused_moe is imported, and the test first imported it inside the shim); `0f71b5b4` fixes the
test, and code behaves as at base. XMLs and logs: `evidence/gate_b/{base,head,head2}.{xml,log,env}`.

### Gate (a)
GATE_A_SECTION

### GPU rows
Each row is compared with its regression record (program_digest, manifest_digest, run root, verdict) and with the base
tree on the same pod.

**#101** `llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`, 1x L40S `vyv-rf-b4-g1`,
`row_pod.sh build,match,commit` PAIRS=1 (the record's), **Commit with the FA2 matReq tap** (`tools/g1.sh`,
`tools/r101_base.sh`): head in `r20260925-100039-940f`, base in `r20260925-104202-d6d9`.

| | record (`commit/verdict.json`, sha256 `50182eda…`) | head `3bdcd0ad` | base `10996616` |
|---|---|---|---|
| run root | `7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5` | = | = |
| commit_pass / first fail | True / None | True / None | True / None |
| Build | | PASS, step `03ace66f1c80b04a`, workload `a2b43bde001d335a` | same |
| Program digest | `079ee0a8…` (predates the relayout) | `ccc213475e7c4eed04b3b0d3717e2144012be65f41d900a018dbd09d1e400c6b` | = head |
| manifest digest | `368283ad…` (predates the relayout) | `90f8186879d5035af027259151b4ac465bf6c3dcf08c1e6d62dab9b680bfeaac` (7043 identities) | = head |
| Match | GREEN | PASS, global PASS, tokens_equal, fold | same |
| Commit checks | PASS | all PASS (runtime_match, local_replay, boundary_linkage, checkpoint_binding, execution_extent, required_value_coverage, program_source_identity, manifest_verify) | same |

The record's Program / manifest digests predate the relayout; no from-scratch Build gives them (f3's and c1's finding;
c1 and f3 got `ccc21347…` / `90f81868…` too). Evidence: `evidence/r101/`.

**FA3 tap on H100.** 1x H100 PCIe `vyv-rf-b4-h100` (cc 9.0, 114 SMs), bootstrap from head (FA3-TAP-OK `e0fb0036…`,
hdims 64,128, layout v9). The H100 rows of record declare an H100 SXM: the Llama-3.2-1B B1 1024/128 H100 row built at
head (PASS, step `d26b34f804603abc`, manifest `a442399bf7828e04`), and then `build_engine` refused this part ("num_sms
declared 132, device 114"), at head as it would at base. I stopped it (`r20260925-104827-1825`, rc 143) and ran the release
canary's Llama-3.2-1B B1 256/32 greedy row instead: it declares no target, so it runs on this part with the FA3 engine;
the target-family precheck is waived by name ("fa3 tap head-vs-base on an H100 PCIe"), as `canary.sh` does on the Hopper
canary host. `row_pod.sh build,match,commit` PAIRS=1, head then base, same pod (`tools/h100c.sh`, `r20260925-113014-592b`).
No record exists for this row on cc 9.0, so the comparison is head vs base.

| | head `0f71b5b4` | base `10996616` |
|---|---|---|
| Build | PASS, step `d26b34f804603abc`, workload `0c050282fbf531ed`, manifest `a82276488fd23dc0` (6979) | same |
| Match | PASS, global PASS, tokens_equal, fold | same |
| Commit | PASS, every check PASS, manifest_verify True | same |
| run root | `f64a6611e49c2c7fe7a505cdf560e1364bcf9b1a7a73cbd14232d41648648747` | = |
| Program / manifest | `4a892d5dfe611393…` / `a82276488fd23dc0…` | = |
| hidden class committed | `fa3_hidden_m1_stream` (512 checked) | same |

Evidence: `evidence/h100/`.

**#70** TP2 `olmoe-1b-7b__bf16__l40s__tp2__b8__i1024__o128__mixed__greedy__bi-eager`, 2x L40S `vyv-rf-b4-tp2`,
`tp_stage.sh` build / match / commit (`tools/tp2.sh`), run `r20260925-101142-d268`. The collective hooks
(`rank_worker`) moved onto `engine/hooks.py`, so this row is required. Reference: the fixture (class FAIL), f1's base
chain at `72884c8a` (Build `r20260924-202455-105b`, Match `r20260924-210318-37b0`, Commit of record
`r20260924-221949-8668`, PAIRS=3; its row files are in f1's `commit70-base-head.tgz`) and f56's rerun of it.

| stage | reference (f1 base / f56) | head `3bdcd0ad` |
|---|---|---|
| Build | PASS, program `64bee6d6e8264461`, manifest `1bb40895671dd791` | PASS 10:39Z, program **`64bee6d6e8264461`**, rank-1 digests `d8cc47009eb82cb3`, 8 shapes, wall 1,276 s (f1 1,279 s) |
| Match | tp2_match pass (8,448 collectives, 0 mismatches, tokens equal); `fold_match` fails on both ranks, errors 4,096 / unresolved 3,544 each, rc 11 | **the same**: tp2_match pass True, 8,448 collectives, 0 mismatches, tokens True; fold errors 4,096 / unresolved 3,544 on each rank, rc 11; wall 1,181 s |
R70_COMMIT

### Non-interference
`python -m verity_vllm.properties.noninterference --workload workloads/workload_32x16_1req.json` on `vyv-rf-b4-g1` (L40S),
head and base (`tools/g1.sh`, run `r20260925-100039-940f`). The check runs the workload with the observer, with the
forward hooks, and bare, and compares every hash and the tokens.

| tree | result |
|---|---|
| head `3bdcd0ad` | PASS: hashes 992/992, tokens a_observer / b_hooks / c_bare all True, problems 0 |
| base `10996616` | PASS: hashes 992/992, tokens a_observer / b_hooks / c_bare all True, problems 0 |

Evidence: `evidence/r101/nonint_{head,base}.log`, `evidence/r101/nonint-{head,base}/noninterference.json`.

## What changed
- **`engine/hooks.py`** (new, core layer, imports nothing from `verity_vllm` and nothing from vLLM / torch / Triton at
  import). `patch(owner, name, value)` records what `owner` itself held (its own `__dict__` entry, or `ABSENT` when the
  attribute was inherited, computed or missing) and returns a `Patch`; `uninstall` puts exactly that back (an inherited
  method is inherited again; a by-value attribute such as a torch config proxy is set back through the owner's
  `__setattr__`). `wrap`, `append` (library hook lists such as Inductor's `INTERMEDIATE_HOOKS`), `patched` (context
  manager), `Hooks` (a component's patches, uninstalled newest first), `live()` and `triton_launch`.
- Moved onto it: the Triton launch hook (`observe/triton_adapter`, `program/frontend/triton_capture`), the FA2
  `varlen_fwd` and FA3 `fwd` taps (`acquire/sources/hidden_source`), the MoE / TP partial / compiled / compiled-kernel
  sources, the sampler install (`acquire/install`), `vllm_adapter`'s capture wrappers, `rank_worker`'s collective and
  forward hooks, `native_host` / `native_collect`, the export shims (`export_compat`: target profile, `moe_ops_traced`,
  `tensor_data_as_detach`, tuned-table cache; `export_ops`: `tp_group_override`, the vocab-parallel binding), and
  `pipeline/build` / `pipeline/commit`. The wrappers stay at their sites (they close over the component's state).
- **P9** (`tests/lint/test_p09_layering.py`): a `setattr` / attribute assignment on an imported object is allowed only in
  `engine/hooks.py`; an attribute set on an object the same function constructed is not a patch (cleared 7 false
  positives). `engine.hooks` and `engine.env` map to `core` and count as their own packages for the package-cycle check;
  `test_leaf_modules_import_nothing` asserts they import nothing from `verity_vllm`. All 43 `runtime-patch` entries deleted.
- **`engine/env.py`** (new, core layer): the tables `ENGINE` (the execution profile, now `engine_profile.DECLARED_ENV`)
  and `EXPORT` (the meta instantiation's five pins), `pin` / `apply_engine` (setdefault: an operator's export wins),
  `apply_target` (a `TargetProfile.env()`), `disable_compile_cache`, `prepare_compiled_process_cache` (moved from
  `vllm_adapter`, which re-exports the name). `engine_profile`, `vllm_adapter`, `vllm_meta`, `compiled_source` and
  `pipeline/build` call it **at the same points as before**, so every process sees the same environment.
- **P7** (`tests/lint/test_p07_declared_inputs.py`): `ENV_OWNERS = {engine/env.py}`, 17 environ entries deleted, and
  `test_only_engine_env_writes_vllm_pins` fails any other library module that writes a pin (literal key or
  `os.environ.update(x.env())`).
- P10 caps shrink with the modules (`native_collect` 1931 -> 1924, `native_host` 2587 -> 2580, `rank_worker` 1558 -> 1554,
  `vllm_adapter` 1949 -> 1913); P11 loses 2 entries.
- Tests (new, beside the existing ones): `tests/engine/test_hooks.py` (uninstall restores the original objects: plain
  attribute, class attribute, inherited method, missing attribute, by-value torch config, stacked patches, errors inside
  `patched`, the real Triton `JITFunction.run`, the torch / vLLM export shims, `tp_group_override`, appended hooks) and
  `tests/engine/test_env.py`.

## What deliberately didn't change
- No identity (C3's): the profile id, the pod id / fallback, the G1-G8 artifact key names.
- File names: `engine/vllm_adapter.py` stays (39 importers; its split into `engine/build.py` is B5's), and
  `engine/engine_driver.py` is not renamed to `driver.py`. `build_engine` / `engine_kwargs_for` signatures are unchanged
  (a5 builds `verity_vllm.LLM` on them).
- Import-time pins: three pipeline CLIs (`m1_capture`, `tp/capture`, `commit`) still call `prof.apply_env()` at module
  import, and `vllm_meta` pins at import (both now through `engine/env.py`), because huggingface_hub reads `HF_HOME` /
  `HF_HUB_OFFLINE` once at its own import. Moving them later would change what a process sees. Proposal (in STATE.md
  Open questions): move them when a5's `pipeline/cli.py` owns process startup.
- The wrappers themselves (what each patch installs) are unchanged; only how they're installed and removed moved.

## Open questions (none blocking; also in STATE.md)
- `engine.hooks` / `engine.env` sit in the `core` P9 layer (stdlib only), so observe / program / commit can call them
  without an engine <-> observe package cycle. Say if you want them elsewhere.

## Found, not fixed
- `tests/program/test_twins.py::test_check_writes_the_evidence_schema` depends on scheduling: `twins.LIBRARIES["openmp"]`
  is recorded only when the pytest process itself compiles `tc_model` (`_tc_lib` -> `_cxx_has_openmp`), so the test fails
  when its worker built the library and passes when another worker (or an earlier run on the pod) did. It failed at base
  and at `3bdcd0ad` (concurrent runs, fresh pod) and passed at head in the rerun. Not related to this lane.
- FOUND_EXTRA

## Pods and spend
PODS_SECTION
