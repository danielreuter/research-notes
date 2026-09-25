---
id: vllm-rf-b5vc/ready
lane: vllm-rf-b5vc
kind: ready
created: 2026-09-25T20:20Z
---
# vllm-rf-b5vc READY: `rules/vllm_bindings.py` -> `rules/vllm_bindings/` package (B5, pure structure)

- **Branch `lane/vllm-rf-b5vc`, head `90300f52`** (pushed). Successor of vllm-rf-b5vb (bc-19e6c2c5, no commits). Agent bc-2ddd7f1e.
- **Base: main `b989a321`** (a5 merged). History: split `e1dd2a7e` on `8a3aa083`, then merges of main `38a8d35d`, `f7de4620`,
  `lane/vllm-rf-a5c` `40b9e571` (coordinator 1800Z) and main `b989a321`; all clean, no conflict resolution.
- The only non-merge commit is `e1dd2a7e`. `git diff b989a321 90300f52` = that commit's 21 files.

## What changed
- `verity_vllm/program/frontend/rules/vllm_bindings.py` (1,905 lines) -> package, 13 modules (lines): `__init__` 71, `pins` 114,
  `observations` 178, `operands` 47, `triton_launches` 166, `attention` 237, `elementwise` 154, `norm_chain` 417, `fp8` 192,
  `fused_norm` 37, `views` 72, `cache_pad` 92, `collectives` 261.
  - Rule families follow the original's section banners. `pins` = the kernel pin tables + the active target's GEMM pins +
    `_pins_ok`. `observations` = the observed-field pins/selectors and the **one module state `_OBSERVED`** with its
    observe/active/clear functions. `operands` = the shared helpers (`aten`, `BF16`, `_row_value`, `_strides`, `_untransposed`).
  - `__init__` = the original module docstring, `VLLM_BINDING_RULES` (**order identical**, same statement) and
    `vllm_ruleset`, and re-exports **exactly the 20 names importers use** (library: `pipeline/build.py`, `rules/vllm_moe.py`;
    tests: 8 modules, incl. `VB._OBSERVED`, `VB.triton_launch`, `VB._pins_ok`), listed in `__all__`.
- **Verbatim moves**, checked by `evidence/verify_split.py` (AST + source): 77/77 top-level statements with identical source text
  and AST, none duplicated, nothing else added; 59/59 comment lines between statements (banners, `#:` doc-comments) kept.
  Negative checks (swap two rules in the list, drop a banner, edit a pin) all FAIL it. Generator `evidence/split.py` (line ranges).
  Rewritten: only the imports (generated from the names each module uses; pyflakes clean) and `__all__` (45 names -> the 20 used).
- `pipeline/build.py` `_CONSTRUCTION_SOURCES`: the one path -> the 13 package files (literal list; the P12 root-list key is
  unchanged). `tests/program/test_applicability.py`, `test_harden_guards.py`: their source-path lists glob the package.
- Lint allowlists re-keyed, counts equal: P7 broad-except 3 = 3, P8 6 = 6, P11 10 = 10. **P10 entry `vllm_bindings.py <module>
  1905` deleted** (largest module now 417). P9 cycle `vllm_bindings <-> vllm_moe` unchanged (ruleset kept in `__init__`, so the
  SCC keeps its two members). No allowlist grows.

## Deliberately not changed
- No Program, manifest, commitment root, leaf id or verdict change (see #101). Importers unchanged (they import the package).
- `construction_version` (artifact identity's code part) changes, since its file list and file bytes change. It is a
  code identity, not a Program/manifest digest. Code-identity digests before/after were not measured on a pod.
- Prose naming `vllm_bindings.py` left as is (a4's rule).

## Gates (all on the handed-over vyv- pods; evidence `evidence/`, XMLs in `evidence/gates-4f090959.tgz`)
Gate trees: head `4f090959` (= `90300f52` in `integrations/vllm` + `packages`; main's `b989a321` merge added only
backends/ligero and one verity_numerical file) and base `40b9e571` (= `b989a321` in `integrations/vllm` + `packages`).
1. **Lints** (t1, `r20260925-181451-4e3d`): 45 passed at head = 45 at base (a5c's same-pod `head-40b9e571-lints.xml`); jdiff 0 changes.
2. **Gate (b)** (t1, same run; base = a5c's same-pod `40b9e571` run): head 56 failed / 3685 passed / 288 skipped / 6 xfailed /
   11 errors (12:46); base 57 / 3685 / 287 / 6 / 11. jdiff (sha256 363304c0…): 4046 = 4046, 0 renamed, **0 new failures, 0 new
   skips, 0 new skip reasons**. 2 outcome changes, neither a regression: `tests.commit.test_roundtrip::test_transient_storage_is_released`
   failed -> passed (memory bound); `tests.observe.test_observer_encoding::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation`
   passed -> skipped ("allocator did not reuse the pointer"; jdiff marks it order-dependent at base). `evidence/jdiff_{b,lints}.txt`.
3. **Gate (a)** T0+T1 (t1, same run, local store, no key): **73 passed, 85 skipped, 0 failed** (1:35:25, exit 0 20:03Z). jdiff vs
   a23b's `gate_a-t0t1-base-72884c8a-samepod.xml.gz`: 158 = 158, 0 outcome changes, 0 new failures, 0 new skips; 2 skip reasons
   new on head (#70/#75 `manifest_digest`: "TP row: rank Programs … are merged by tp_stage.sh"), the same reworded skip a5c
   recorded at `da9e4847`, i.e. a5's wording, already in base `b989a321`. `evidence/jdiff_a.txt`.
4. **#101 GPU Build smoke** (g1, `r20260925-174116-cb42`, tree `eb97ecb4` = split on main `f7de4620`; via `ops/run_row_v2.sh`,
   since a5's `row` CLI was not yet on main): **RESULT SAME-OF-RECORD**: program `ccc21347…`, manifest `90f81868…`, run root
   `7adcef49…`, correspondence digest all EQUAL; commit PASS, checks 33/33, 0 outcome differences. `evidence/r101-cmp.txt`.
   Carries to `90300f52`: the only later change inside `integrations/vllm` is a5 (digest-neutral by its gates; coordinator 1822Z).

All runs PRESERVED on R2 (`r20260925-174116-cb42`, `r20260925-173947-17f4` [rc 2, wrong CLI], `r20260925-180950-f886`
[stopped after lints], `r20260925-181451-4e3d`).

## Pods and spend
- `vyv-rf-a5-g1` terminated 18:12Z, `vyv-rf-a5-t1` terminated 20:17Z. No pods created. Spend about $4.8 (g1 ~0.5 h, t1 ~2.4 h).

## Found, not fixed
- `tests/program/test_harden_guards.py::test_G4c_no_capability_or_sm_literal_outside_target_profile` checks nothing: its `ROOT`
  is `dirname(dirname(verity.ir.__file__))` (`packages/verity/src/verity`), so every listed path is missing and skipped (base too).
- The P9 cycle `vllm_bindings <-> vllm_moe` could go if `vllm_moe`'s lazy import named `vllm_bindings.observations`; left
  (importers unchanged by brief).
- Prose naming `vllm_bindings.py`: `observe/fold/collective_pattern.py`, `observe/fold/patterns/*`, `registry/{targets,gemm_targets,dense}.py`,
  `rules/{vocab,vllm_moe,__init__}.py`, `target_profile.py`, several test docstrings.
