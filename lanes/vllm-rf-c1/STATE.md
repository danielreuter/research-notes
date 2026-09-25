---
id: vllm-rf-c1/state
lane: vllm-rf-c1
kind: state
agent: bc-9eae5bc7 (Cursor), coordinator bc-ba6cec03
created: 2026-09-25T06:52Z
updated: 2026-09-25T07:31Z
---
# vllm-rf-c1: C1, commitment scheme vllm-v1 (named-scheme form)

Deadline for vyv- pods: 2026-09-25T09:00Z (coordinator extends). Budget: $35 pod spend; spent about $0.40 so far.

## Status
- Phase 1 (evidence only, no repo commits): DONE 07:29Z. No mismatch anywhere (both results below).
  - Source for pod runs: clean detached worktree `~/projects/verity-wt/rf-c1-p1` at `origin/main` `00ffe398` ("Merge #15").
- Phase 2: waiting for A4 (`lane/vllm-rf-a4`, head `34400229` at 07:27Z) to be in `origin/main`; PR #15 is already in.
  Checked 07:27Z: `origin/main` = `00ffe398`, A4 not an ancestor.

## Pods
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
