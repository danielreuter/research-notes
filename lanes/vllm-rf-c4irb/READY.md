---
id: vllm-rf-c4irb/ready
lane: vllm-rf-c4irb
kind: ready
status: DRAFT (gate (a) pending)
created: 2026-09-25T14:30Z
---
# vllm-rf-c4irb READY: boundary, partition and liveness in core `verity.ir`, integration switched (phases 1 + 2)

c4irb succeeds c4ir (agent bc-fbcf78e2, hung about 12:30Z). Start commit `7313e799` (`lane/vllm-rf-c4ir-p2-on-a4`).
Phase 1 and phase 2 descriptions, the core API, the design questions and "Found, not fixed" are c4ir's
(`../vllm-rf-c4ir/READY.md`, still accurate); this file adds the phase 2 gates and the branch after a4's merge.

## Branch

| Branch | Head | Tree | Base |
|---|---|---|---|
| `lane/vllm-rf-c4ir` (for merge) | `793f14af` | `03f38c29` | `origin/main` `33e4d8d1` (a4 merged, 14:13:54Z) |
| `lane/vllm-rf-c4irb` (working) | `793f14af` | same | same |

- `lane/vllm-rf-c4ir` was force-pushed with lease from `cfe0ae63` (phase 1 only) to `793f14af`: 13 commits, phase 1's
  11 (rebased; their combined diff has the same patch-id as `00ffe398..cfe0ae63`, `8545f5da`) then phase 2's `ee9be814` (core names `family_tiling` / `CheckedTiling` publicly) and
  `793f14af` (integration importers to `verity.ir`, integration copies deleted, allowlists shrink). Phase 1's pending
  merge request at `cfe0ae63` is superseded by this head.
- `git rebase --onto origin/main 10996616` was clean. The phase 2 diff has the same patch-id before and after (`5f5e9fc2`).
- **Why the gates at `7313e799` stand for `793f14af`:** the `integrations/vllm` (`1796cb6b`) and `packages/verity`
  (`cc5d4794`) subtrees of `793f14af` equal those of the gated `7313e799`, and the base's subtrees at a4 `10996616` equal
  main `33e4d8d1`'s (`ae743c95`, `bde581db`). Main's other changes since a4 are in `backends/`, `benchmarks/`,
  `tests/test_commit_cost_benchmark.py` and `tools/research` only, and apply to both sides of every comparison.
- The importer check finds nothing:
  `rg "verity_vllm\.query\.(boundary|partition)\b|query import (boundary|partition)|frontend\.liveness|frontend import liveness"`.

## Gates

All on RunPod pods, launched with `research run --on ... --source <clean worktree at 7313e799> --cwd source`.
Head = `7313e799`; base = a4 `10996616` (on the cpu pod: the head tree plus `tools/to_base.patch`, the reverse diff, in c4ir's notes).

| Gate | Run | Pod | Result |
|---|---|---|---|
| Lints (`tests/lint`, `test_no_by_name_rules`, `test_imports_resolve`) | r20260925-121359-3a93 | cpu3g 32 vCPU | head 45 passed, base 45 passed. Allowlists only shrink (p07 -3, p10 -2, p11 -1; `LAYER` -3) |
| Core (`packages/verity/tests`) | same | same | head 661 passed, 1 skipped |
| Gate (b) (`-n 12 --dist loadfile`, `OMP_NUM_THREADS=3`), head and base concurrently on one pod | same | same | head 51 failed / 3640 passed / 287 skipped / 6 xfailed / 11 errors; base 51 / 3647 / 286 / 6 / 11. `baseline-jdiff.py` rc 0: **0 new failures, 0 new skips, 0 new skip reasons** |
| Gate (a) T0+T1 | r20260925-120631-fb6b | cpu3m 32 vCPU / 1 TB host, 256 GB cgroup | PENDING |
| GPU Build smoke #101 (`row_pod.sh build,match,commit`, `PAIRS=1`) | r20260925-122601-35bc | 1x L40S | build, match, commit PASS; run_roots `7adcef49…` = record; program `ccc213475e7c4eed04b3b0d3717e2144012be65f41d900a018dbd09d1e400c6b` = record; manifest `90f8186879d5035af027259151b4ac465bf6c3dcf08c1e6d62dab9b680bfeaac` = record; `commit_pass` True, every commit check PASS |

Gate (b) detail (`gate_b-jdiff-base10996616-head7313e799.txt`):
- 6 tests are only in base, not renamed: `tests.program.test_lint::test_no_{model_names,startswith,v1_membership_tables}`
  parametrized over `[boundary.py]` and `[partition.py]`, the deleted `query/` modules. That accounts for the 6 missing
  passes.
- 1 outcome change, on jdiff's UNSTABLE list: `test_observer_encoding::test_weakref_death_is_a_direct_free_and_reuse_bumps_generation`
  passed -> skipped ("allocator did not reuse the pointer"). That accounts for the 7th pass and the extra skip.
- The #101 record values are a4's (`../vllm-rf-a4/evidence/gpu_r101/`: run root from the frozen record; program and
  manifest from f3's base rebuild).

## Evidence and custody

- Beside this note: `lints-{head-7313e799,base-10996616}.xml.gz`, `core-head-7313e799.xml.gz`,
  `gate_b-{head-7313e799,base-10996616}.xml.gz`, `gate_b-jdiff-base10996616-head7313e799.txt`, `gpu-r101-7313e799.txt`.
- The three gate runs were launched before the `--custody-r2` rule. Their full run dirs are on R2 as copies inside
  custody runs launched on the same pods (`tools/custody_copy.sh`, which also writes a sha256 list per copied dir):
  - r20260925-141336-a832 holds r20260925-122601-35bc (106 files, 30 MB), run record `art:964ada3009abb1edbdaaea5aa38b18db53ecf6fc0b0455d0c0f83cedb7f649af`;
  - r20260925-141353-7997 holds r20260925-121359-3a93 (27 files, 48 MB), run record `art:58597aaa6120ac8fe2572e5291cfaad1ec97208116a14c8660653c511a89bda5`;
  - gate (a): PENDING.

## Invariants

- No Program digest, manifest digest, run root or verdict changed: #101 equals the record, and gate (a) PENDING.
- No digest-moving commit; nothing for the re-baseline epoch.
- Lints green; allowlists only shrink.

## Found, not fixed

c4ir's list stands (`../vllm-rf-c4ir/READY.md`). New:
- Gate (a) on `vyv-rf-c4ir-reg` ran about 2.7 times slower than a23b's same-pod reference (6391 s): the single-threaded
  `build-global` at 100% of one core, the host 64% idle, no cgroup CPU cap. So the per-core speed was lower; the
  results are unaffected.

## Pods and spend (phase 2, c4ir + c4irb)

- `vyv-rf-c4ir-g1` (L40S, $1.09/h) 12:17–14:18Z, about $2.2; `vyv-rf-c4ir-cpu` (cpu3g 32, $1.28/h) 12:10–14:19Z, about $2.75;
  `vyv-rf-c4ir-reg` (cpu3m 32, $1.76/h) from 12:06Z: PENDING. Both terminated pods were unregistered.
