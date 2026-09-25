---
id: vllm-rf-c1/state
lane: vllm-rf-c1
kind: state
agent: bc-9eae5bc7 (Cursor), coordinator bc-ba6cec03
created: 2026-09-25T06:52Z
updated: 2026-09-25T09:02Z
---
# vllm-rf-c1: C1, commitment scheme vllm-v1 (named-scheme form)

Deadline for vyv- pods: 2026-09-25T09:00Z (coordinator extends). Budget: $35 pod spend; spent about $0.40 before phase 2 pods (phase 2 pods: $4.61/h from 08:36Z).

## Status
- Phase 1 (evidence only, no repo commits): DONE 07:29Z. No mismatch anywhere (both results below).
  - Source for pod runs: clean detached worktree `~/projects/verity-wt/rf-c1-p1` at `origin/main` `00ffe398` ("Merge #15").
- Phase 2: A4 not yet in `origin/main` (checked 08:12Z: main `5631e667`; A4 head moved to `10996616`, linear over `14b0cf9f`,
  test-file moves only). `origin/main` past the A4 fork (`00ffe398`) touches only `backends/numerical` (#19, #20), so gates run on the
  A4-based head carry to the rebase onto main as long as A4 lands unchanged.
  - Branch `lane/vllm-rf-c1` (worktree `~/projects/verity-wt/rf-c1`, local, not pushed yet), on A4 head `10996616`:
    1. `af8d9711` scheme.py + rerouting (hidden_engine.py deleted; p10 caps native_host 2587->2579, padding_steps 930->914)
    2. `09ed0361` pod-marked `tests/commit/test_scheme_cuda.py` + PROTOCOL.md section 6
    3. `472207c3` per-scheme throughput in Spans / the Commit row (`spans_throughput`) + `tests/pipeline/test_spans.py`
    Laptop ast checks (syntax, p10 sizes, imported names): 0 errors, 0 unresolved.
  - When A4 lands: `git rebase --onto origin/main 10996616`, push `lane/vllm-rf-c1`.
  - Host layout label (`chunk-leaf-v1` on host committers): NOT fixed. It flows `pipeline/commit.py` `collector["layout"]` into
    `binding.build_binding_map` entries and so into `map_digest`; fixing it changes a digest. Listed for READY.md.
  - Next: pod gates (lints; gate (b) head+base same pod; gate (a) T0+T1 cpu3m; GPU row #101 + throughput + test_scheme_cuda).

## Pods
- Phase 2 (08:36Z): `vyv-rf-c1-big` = RunPod `rg1phl3ogbwgy2` (cpu3m 64 vCPU / 512 GB, 200 GB disk, $3.52/h) and `vyv-rf-c1-g2` =
  RunPod `pbsu9tvac48iqr` (1x L40S, driver 580.178.04, CUDA 13.0, $1.09/h), both `research pods register ... --guard 90`
  (`~/.research/notes/machines.d/vyv-rf-c1-{big,g2}.toml`). A first `pods create` pair whose shell died also created pods
  (`p3nyo6vv74j7at` big, `49jvnr6ll3vu7u` L40S): both terminated at 08:39Z, a few minutes after creation, never used.
  - Trees: head `472207c3` -> `/workspace/head`, base `10996616` (worktree `rf-c1-p1`, detached) -> `/workspace/basetree` (g2) and
    `/workspace/base` (big), shipped with `research pods sync`.
  - g2 run `r20260925-084508-e7c3` (`evidence/pod-scripts/g2.sh`): bootstrap --gpu LLAMA32_1B, CUDA tests at head, #101 head then base,
    ab_compare, throughput. 08:51Z BOOTSTRAP-OK. CUDA tests at head (test_scheme_cuda + test_production_vectors + test_leafhash_device +
    test_spans): **98 passed, 0 skipped** (FA2 tap tree present). #101 head: build PASS (step `03ace66f`, manifest `90f81868` 7043 = f3's),
    match PASS; commit running 09:02Z.
  - big runs: boot `r20260925-085137-18b5` (BOOTSTRAP-OK from the base tree, ops/ identical; xdist 3.8.0, xgrammar 0.2.7; freeze vs a1's
    baseline differs only in googleapis-common-protos 1.75.3->1.75.4, uvicorn 0.53.0->0.54.0); gate (a) `r20260925-085456-de22`
    (`big_gate_a.sh`: prefetch.sh then gate_a.sh T0+T1 at head); lints + gate (b) `r20260925-085512-8c77` (`big_gate_b.sh`).
    **Lints: 45/45 pass at head and at base**; allowlists at head vs base: only p10_size caps shrink (2587->2579, 930->914).
    Gate (b) xdist head + base started 08:56Z.
  - Fixture key: minted on the laptop 08:54:46Z (3 h, object-read-only), piped by ssh into `/root/r2ro.env` on vyv-rf-c1-big (786 B,
    mode 600, never printed); prefetch.sh deletes it when the fetch ends (trap on exit too).
- `vyv-rf-c1-g1` (runpod `zaazjzf44rc4wr`), 1x L40S, CUDA 12.9/13.0 allowed, guard 90. Created 07:07Z, TERMINATED 07:29Z
  after every run was fetched (`machines.toml` entry marked).
  - Runs: bootstrap `r20260925-070509-d288` (BOOTSTRAP-OK); `r20260925-071724-fd55` (failed: H1 harness bug); `r20260925-072312-94f5`
    (CUDA vectors); `r20260925-072432-1077` (weights root). All fetched with `--all`, all `preserved=yes`.
- Fixture key: own 3 h read-only key minted on the laptop 07:20Z, piped by ssh into `/root/r2ro.env` (786 bytes, never printed);
  fetched row #101 records (`art:a4ea1a18…`, 129 MB) with `evidence/pod-scripts/fetch_records.sh`, which deleted the key in the
  same ssh session right after the fetch, before 07:23Z ("key deleted").

## Results
### Phase 1.1: CUDA SHA-256 copies vs `vllm-v1` vectors: ALL EQUAL (run `r20260925-072312-94f5`)
Evidence: `evidence/cuda_vectors.r20260925-072312-94f5.json` (vectors.json sha256 `f63cd95d…`). L40S sm_89, torch 2.13.0+cu129,
vLLM 0.28.1rc1.dev472, nvcc 12.4. Driver `evidence/pod-scripts/cuda_vectors.py`. Result: `CUDA-VECTORS-OK`, 0 mismatches.

| copy | how it was run | equal | covered vectors |
|---|---|---|---|
| `native_tree.cu` (production .so) | ctypes on the extern "C" launchers of the JIT-built `verity_native_collect.so` (sha256 `bee47f00…`) | 33/33 | chunk_leaf 0–2 (whole step + ci_base window), trees N=1–17 (root + every path), node, lift, run-root fold ×2, weights-root fold |
| `native_tree.cu` (standalone) | `nvcc -O3 --use_fast_math -arch=sm_89` | 33/33 | same |
| `hidden_gpu_tree.cu` | production `hidden_gpu.ext()` | 30/30 | chunk_leaf 0–2, trees N=1–17 (root + paths), node, lift (via 3-leaf `tree_levels`), run-root fold ×2, weights-root fold |
| `native_leafhash.cu` | production `leafhash.ext()` | 45/45 | pos_leaf len 1–4096 (single + tail after 256/4096 leaves), trees N=1–17, node, weights-root fold |
| `verity_tap.h` (H1, VERITY_TAP=4) | harness TU per src_mask over the tap8 FA2 tree | 3/3 | thread_leaf 0–2 (src_mask 1, 27, 16) |

Not covered, by construction: chunk_leaf[3] (BN/D = 64/128; the chunk kernels hard-wire header words 8/9 to 0, as PROTOCOL §6 says);
the empty tree, `empty/v1`, `leaf/v1` and every root's binding (host code); pos_leaf len 0 (`pos_leaves` refuses it; the host skips numel 0).
The first attempt `r20260925-071724-fd55` failed only because the H1 harness lacked FA2's global `using namespace cute;` (harness bug,
fixed; A–C were already all equal there).

### Phase 1.2: weights root of a live model: ALL EQUAL (run `r20260925-072432-1077`)
Evidence: `evidence/weights_root.r20260925-072432-1077.json`; per-tensor roots and sha256 in the run's `weights_tensors.json`.
Driver `evidence/pod-scripts/weights_root.py --case LLAMA32_1B --execution bi-eager --records /workspace/c1/records-101`.
Engine: `vllm_adapter.build_engine` (unsloth/Llama-3.2-1B @ `9535bd9b`, eager), committer `NativeHostCommitter(gpu_tree=True)`, chunk 256.

| root | value | tensors / bytes | wall |
|---|---|---|---|
| production `register_weights()`, `VERITY_WEIGHTS_HASH=host` | `8baa442834d58dc7a6cc2555da33fac41ab2fa50419fa5a4bada45e1f8aa9b16` | 163 / 2 488 406 272 | 25.3 s |
| production, `device` (`native_leafhash.cu`) | same | same | 0.1 s |
| production, `device-checked` (163/163 tensors checked) | same | same | 15.5 s |
| core `verity.commitments.vllm_v1` (pos_leaf per 256 B, fold, weights_root) | same | same | 33.6 s |
| row #101 recorded Commit root (`commit/runs.jsonl#1/commit/weight_registration`, host, chunk 256) | same | same | – |

geo digest `222df080…` (recomputed independently: equal); names digest `75cfc105…`.
Weights of record (`build_request/weights_of_record.json`, root_of_record `120a8d6f…`) checked against the live parameters with
`weights_of_record.check`: result True, 163 compared, 0 mismatched, 0 missing, shards pinned and ok.

## Found, not fixed
- thread_leaf[1] (src_mask 27) carries ok0 = 1 where the kernel constructor derives 0 for its (m_block, seqlen_q). The digest still
  matches (the header encodes the bits given), but the vector is a field combination the tap never emits. Vector-generation note, not a
  CUDA defect.
- The pod's nvcc is 12.4 while torch is cu129; every JIT extension above (production path) was built by that nvcc.

## Phase 2 prep (read-only, from `00ffe398`; re-check after A4's file moves)
Python copies of `vllm-v1` rules in `integrations/vllm/verity_vllm`: `commit/hashing.py` (H, tags), `commit/merkle.py` (node, lift,
empty, levels), `commit/hidden_stream.py` (fa2h chunk header and leaves, stream and thread roots), `commit/hidden_engine.py` (step root),
`commit/semantic_layout.py` (pos_leaf, semantic root), `commit/padding_steps.py` (run root), `acquire/native_host.py` (run and weights roots).
