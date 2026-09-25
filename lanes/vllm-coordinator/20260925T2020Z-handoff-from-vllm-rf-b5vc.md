---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-b5vc (bc-2ddd7f1e)
created: 2026-09-25T20:20Z
---
# MERGE-READY vllm-rf-b5vc: `lane/vllm-rf-b5vc` `90300f52` on main `b989a321` (vllm_bindings package split, pure structure)

- Branch/head: `lane/vllm-rf-b5vc` **`90300f52`** (pushed); base main **`b989a321`**; one real commit `e1dd2a7e` + clean merges
  (main x3, a5c `40b9e571`). `git diff b989a321 90300f52`: 21 files.
- Change: `rules/vllm_bindings.py` (1,905) -> `rules/vllm_bindings/` (13 modules, max 417). 77/77 statements verbatim (AST +
  source; `evidence/verify_split.py`), `VLLM_BINDING_RULES` order identical, `_OBSERVED` in one module (`observations`),
  `__init__` re-exports the 20 names importers use. Allowlists: P7 3=3, P8 6=6, P11 10=10 re-keyed; P10 1905 entry deleted; P9/P12
  unchanged. `build.py` `_CONSTRUCTION_SOURCES` lists the 13 files (construction_version moves; no Program/manifest effect).
- Gates (t1 `r20260925-181451-4e3d`, g1 `r20260925-174116-cb42`, all PRESERVED):
  - lints 45 = 45; gate (b) head vs same-pod `40b9e571` (= `b989a321` tree): 0 new failures/skips/skip reasons (4046 = 4046;
    2 flaky outcome changes, one fixed, one order-dependent skip).
  - gate (a) T0+T1: 73 passed / 85 skipped / 0 failed; = a23b's base 158 = 158, 0 outcome changes; 2 reworded #70/#75 skip
    reasons (a5's, already on main).
  - #101: SAME-OF-RECORD (program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…` EQUAL; commit PASS 33/33).
- Behaviour changes: none. Found-not-fixed: `test_harden_guards::test_G4c` is vacuous (wrong ROOT), P9 cycle removable, prose
  file names. Details: `lanes/vllm-rf-b5vc/READY.md`.
- Pods g1, t1 terminated; spend about $4.8.
