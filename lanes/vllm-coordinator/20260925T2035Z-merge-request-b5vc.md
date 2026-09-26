---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: b5vc, split `vllm_bindings.py` into a package (B5, pure structure), from vLLM coordinator bc-ecac3029, 20:35Z

- **Merge:** `lane/vllm-rf-b5vc` @ **`90300f52`**, `--no-ff`: one real commit `e1dd2a7e`, plus clean merges of main and a5c.
- **Recheck against main `7da00370`** (includes PR #29, b4, c4ir, gc): **no conflict, the allowlists included.** On the
  merged tree, every ratchet lint runnable without pytest passes (39/39).
  - Since its base `b989a321`, main shares with it only the p07/p10/p11 allowlists, `pipeline/build.py` (b4) and
    `tests/program/test_applicability.py` (gc). All auto-merge.
  - In the merged `build.py`, `_CONSTRUCTION_SOURCES` lists b5vc's 13 `rules/vllm_bindings/*` files alongside b4's
    entries: 27 sources, and all exist in the tree.
  - PR #29 touched none of b5vc's files.
- **Change:** `program/frontend/rules/vllm_bindings.py` (1,905 lines) becomes `rules/vllm_bindings/`, 13 modules of at
  most 417 lines. 77/77 statements are verbatim (AST and source, `evidence/verify_split.py`). `VLLM_BINDING_RULES` order is
  identical, `_OBSERVED` state is in one module, and `__init__` re-exports the 20 imported names. The allowlist entries
  are re-keyed at equal counts (P7 3, P8 6, P11 10); the P10 1,905 entry is deleted. `construction_version` moves (code
  identity, allowed).
- **Gates** (t1 `r20260925-181451-4e3d`, g1 `r20260925-174116-cb42`, preserved):
  - lints 45 = 45;
  - gate (b), head against same-pod base `40b9e571` (the `b989a321` tree): 4046 = 4046, 0 new failures, skips or skip
    reasons. There are 2 flaky outcome changes, one of them a fix;
  - gate (a) T0+T1: 73 passed / 85 skipped, 158 = 158 with a23b's base, 0 outcome changes.
- **Acceptance:** #101 SAME-OF-RECORD (program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`, commit PASS 33/33).
- **Found, not fixed:** `tests/program/test_harden_guards.py::test_G4c` checks nothing (its `ROOT` points at the wrong
  directory). It's routed to gc2 as a test-side fix. Also: a removable P9 cycle, and prose file names.
- **Evidence:** `lanes/vllm-rf-b5vc/READY.md`; handoff `lanes/vllm-coordinator/20260925T2020Z-handoff-from-vllm-rf-b5vc.md`.
  Pods terminated; about $4.8.

