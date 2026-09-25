---
id: vllm-rf-c1/ready
lane: vllm-rf-c1
kind: ready
agent: bc-9eae5bc7 (Cursor), coordinator bc-ba6cec03
created: 2026-09-25T09:50Z
---
# vllm-rf-c1 READY: C1, commitment scheme `vllm-v1` (named-scheme form), no digest change

## Branch
- `lane/vllm-rf-c1` (pushed to origin; worktree `~/projects/verity-wt/rf-c1`), head **`53314d1c`**, on A4 head `10996616`
  (`lane/vllm-rf-a4`). **A4 is not in `origin/main` yet** (last checked GATE_A_CHECK). When it lands: `git rebase --onto origin/main
  10996616` and push (fast-forward is impossible after a rebase: the coordinator decides; I did not force-push). `origin/main` past
  the A4 fork touches neither `packages/verity` nor `integrations/vllm`, so the gates below carry over if A4 lands unchanged.
- Commits (39 files, +726 / -501):
  1. `af8d9711` one `commit/scheme.py` routes every `vllm-v1` leaf and root rule over `verity.commitments.vllm_v1`: `pos_leaf` /
     `fold` / `fold_levels` stay local (prefix-once, pluggable `new`) over core's tags; headers and roots delegate to core through
     coercing adapters. `hidden_engine.py` deleted; `hashing` / `merkle` re-export core; p10 caps shrink (native_host 2587->2579,
     padding_steps 930->914).
  2. `09ed0361` pod-marked `tests/commit/test_scheme_cuda.py`: every CUDA SHA-256 copy (`native_tree.cu` production .so and
     standalone, `hidden_gpu_tree.cu`, `native_leafhash.cu`, `verity_tap.h` H1) against the vectors; PROTOCOL.md section 6 names it.
  3. `472207c3` per-scheme commit throughput: `Spans(scheme)` counts leaves beside bytes; `throughput()` gives per stage wall_s,
     bytes, leaves, bytes/s, leaves/s, labelled with the scheme; the Commit row carries it as `commit.spans_throughput`. No digest
     reads it. New `tests/pipeline/test_spans.py`.
  4. `7218ffbb` `commit/fasttree.py` and `commit/semantic_layout.py` move to `tests/commit/` (only their tests use them once the
     rules route through scheme; the dead-module lint required it; the keep-list is shrink-only). Their 4 P07 / P11 allowlist entries go.
  5. `53314d1c` p09 allowlist: the `commit <-> program` package-cycle entry goes (the cycle went with semantic_layout).
- Allowlists: only shrink (p10 caps x2, p07 x1, p11 x3, p09 x1). No new Markdown file; no board ids, lane names or dates in code.

## Phase 1 (evidence only): no mismatch
| copy | run | result |
|---|---|---|
| `native_tree.cu`, production .so (ctypes) | `r20260925-072312-94f5` | 33/33 |
| `native_tree.cu`, standalone nvcc | same | 33/33 |
| `hidden_gpu_tree.cu` (production `hidden_gpu.ext()`) | same | 30/30 |
| `native_leafhash.cu` (production `leafhash.ext()`) | same | 45/45 |
| `verity_tap.h` H1 (FA2 tap tree) | same | 3/3 |

Weights root of live Llama-3.2-1B (`r20260925-072432-1077`): `8baa442834d58dc7a6cc2555da33fac41ab2fa50419fa5a4bada45e1f8aa9b16`,
equal for production host / device / device-checked, the core reference, and row #101's recorded root.
Detail: STATE.md "Results", `evidence/cuda_vectors.*.json`, `evidence/weights_root.*.json`.

## Phase 2 gates
- **Lints** (`tests/lint` + `test_no_by_name_rules.py` + `test_imports_resolve.py`, 45 tests, `evidence/pod-scripts/lints.sh`): 45/45 at `53314d1c` (`r20260925-093225-daa0`), 45/45 at `472207c3` and at
  base (`r20260925-085512-8c77`). At `7218ffbb` the only failure was the stale p09 entry that `53314d1c` removes.
- **Gate (b)** (xdist `-n 12 --dist loadfile`, OMP 3, same pod `vyv-rf-c1-big`, base `10996616` run once 08:56-09:11Z):
  at **`53314d1c`** (`r20260925-094310-c681`, 09:43-09:58Z): **0 new failures**. base 4001 tests (58 F / 11 E / 3640 P / 286 S /
  6 xf), head 4006 (56 F / 11 E / 3646 P / 287 S / 6 xf). 4 new tests pass (test_spans x2, test_production_vectors x2); 1 new skip =
  `tests.commit.test_scheme_cuda` (collection skip without a GPU, by design); 2 base failures pass on head:
  `test_roundtrip::test_transient_storage_is_released` (passes on every head run) and `test_row_pod_cancel_forwarding` (a 15 s
  subprocess timeout on base: timing). `evidence/gates/jdiff_b_head3_vs_base.txt` (a1's `baseline-jdiff.py`).
  Earlier heads, same base: `472207c3` 1 new failure (dead modules -> commit 4); `7218ffbb` 1 new failure (stale p09 entry ->
  commit 5). Diffs: `evidence/gates/jdiff_b_*`.
- **Gate (a)** T0+T1 (cpu3m 512 GB): GATE_A
- **GPU Commit row #101** (L40S, head and base on the same pod; `r20260925-084508-e7c3` at `472207c3`, `r20260925-092150-e650` at
  `7218ffbb`; `53314d1c` differs by one allowlist line no runtime path reads):
  - run root `7adcef49184525329814d62364be7cb2b2c45003cad96dbca1434b11f5b1dec5` == the regression record, head and base;
    commit_pass true, every check PASS.
  - Program `ccc213475e7c4eed…` / manifest `90f8186879d5035a…` (7043 identities): head == base (== f3's). The record's
    `079ee0a8…` / `368283ad…` predate the relayout; a from-scratch Build cannot give them (f3's finding).
  - ab_compare: 61 row files identical; the rest differ only in volatile facts (timings, RSS, tmp paths, request-id suffixes, the
    file shas of those) and hidden_gpu.py's source sha (the two trees' files). Snapshot diffs: 96 entries, all device pointers
    (`block_table_ptrs`), metadata equal.
  - CUDA tests on the pod: 98 passed at `472207c3`; 163 passed at `7218ffbb` (adds the moved test_semantic_layout / test_stream_merkle).
- **Throughput** (`commit.spans_throughput`, scheme `vllm-v1`, #101 at `7218ffbb`): hashing 0.490 s over 907,708,156 B and
  3,545,764 leaves = **1.85 GB/s, 7.24 M leaves/s**; movement 0.0056 s; root_finalisation 0.0109 s (at `472207c3`: 1.62 GB/s,
  6.33 M leaves/s). Leaves and bytes equal the row's `leaves` / `bytes_bound`. frame-v3 is not a production committer, so it has
  no Commit row; its cost is `benchmarks/commitments/commit_cost.py`'s.

## Added task: agkr-bound's vllm-v1 operand-domain mapping: **replace**
`~/.research/notes/lanes/coordinator/20260925T0945Z-handoff-from-vllm-rf-c1.md` (copied to `lanes/agkr-bound/`). The framing
(`pos_leaf`, node / lift / empty, step-root preimage, `domain_digest`) is production's; the four digests are not: production has
no per-port operand tree. Its step domain is program = the committer's `root_program_digest` (by default
`sha256("cmt-integ/no-program-digest/" + run_id)`, not the Program; the Program of record is bound by the binding map), ctx =
`sha256(run_id/step=s)`, geo = the model-config JSON, layout = the step's tensor list; serving committers use GPU-tree chunk leaves.

## Found, not fixed
- Host layout label: host committers label their binding map `chunk-leaf-v1` over position leaves. Digest-bearing
  (`collector["layout"]` -> `binding.build_binding_map` -> `map_digest`), so not fixed (PROTOCOL section 7 finding 1).
- The step / run roots' `program` field is the committer's run_id-derived stand-in on every non-compiled row (see the mapping
  handoff); changing it changes every root.
- thread_leaf[1] vector (src_mask 27) has ok0 = 1, a combination the tap never emits (vector note, digest still matches).
- The pod's nvcc is 12.4 while torch is cu129; every JIT extension here was built by that nvcc.
- Strictness: where the rules now go through core, a malformed input raises `InvalidArtifact` (a `ValueError` subclass) instead of
  a bare `ValueError`; core's per-leaf `chunk_header` validation makes host verify paths slower (not the serving path).
- `tests/commit/fasttree.py` (now a test helper of `stream_merkle`) keeps a prefix-once id-leaf form (`leaf_header` /
  `leaf_digest`, pluggable hash); no test pins it to the `id_leaf` vectors (none did at base either; `hashing.leaf_hash`, which
  production uses, is pinned). `tests/commit/semantic_layout.py` holds no rule copy (it calls `scheme`).
- Pre-existing unused `hs` imports in native_host `_commit_step_gpu` / `_gpu_layout`; kept `native_host`'s coverage evidence string
  "per-step bind_root" and `hidden_stream.VERSION` on purpose (recorded strings).

## Pods, spend, keys
- `vyv-rf-c1-g1` (L40S, phase 1) 07:07-07:29Z; `vyv-rf-c1-g2` (L40S, $1.09/h) 08:36-09:44Z; `vyv-rf-c1-big` (cpu3m 64 vCPU /
  512 GB, $3.52/h) 08:36Z-POD_END; two duplicate creates terminated within ~3 min, unused. All registered `guard = 90`
  (`machines.d/vyv-rf-c1-*.toml`, marked TERMINATED). Spend: SPEND (cap $35).
- Fixture keys: minted on the laptop (3 h, object-read-only), piped by ssh into `/root/r2ro.env` on my own pod, never printed; deleted
  right after each fetch (07:23Z on g1; 09:02:43Z on big, confirmed absent). No other lane's key used.
