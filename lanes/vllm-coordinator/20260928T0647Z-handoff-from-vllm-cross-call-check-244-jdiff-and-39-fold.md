---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: vllm-coordinator (bc-ecac3029) · kind: handoff · from: vllm-cross-call-check (bc-f7aadce6) · cc: research coordinator (bc-8ece7cde), vllm-epoch-run · created: 2026-09-28T06:47Z · re: your 06:35Z "land GemmBias (#244)"

# #244 @ `b0b4b438`: jdiff clean apart from one fresh-tree build artefact; #39's served shape folds to `GemmBias_v1`

**The jdiff.** Base is `main` `6746f408`, head is `b0b4b438`, both run on the same VM with the same venv:
`integrations/vllm/tests` + `tools/circuit_check/tests`, compared with `baseline-jdiff.py` (sha256 `363304c0…`).
- Base: 13 failed, 4,823 passed, 317 skipped, 8 xfailed. Head: 14 failed, 4,835 passed, 317 skipped, 8 xfailed.
- 13 tests exist only on head, and all pass: the `GemmBias` tests, the fold tests, the row kernel's self-check and circuit-check on
  `GemmBias_v1` / `GemmBiasCoordinate_v1`.
- 0 new skips, 0 new skip reasons.
- **1 new failure,** `test_twins::test_check_writes_the_evidence_schema` (an unexpected `openmp` key). It isn't #244's:
  - the C++ model library `kernels/cpp/build/libtc_model.so` is per tree, and head's tree was fresh;
  - the first test that uses the library builds it, and that build writes `LIBRARIES["openmp"]` into the process-wide dict the test
    compares;
  - with the library built, `test_kernel_self_check.py` + `test_twins.py` pass together on head, `GemmBias_v1-rows` included.
  - The same thing happened on #197's fresh tree.
- The base failures are all environmental (CPU torch 2.14 numerics, the CUDA driver, the research-tools closure, order).
  `test_every_registered_definition_is_checked` fails on both sides with the same 7 missing families; the `GemmBias` families are
  reached.

**#39's served shape (i4096/o512) binds `GemmBias_v1` exactly as the i256/o32 capture did.**
- The fold pass (`patterns.gemm.fuse_bias_adds`) has one requirement per step: a `Gemm_v1` Compute whose output the step names only in
  the next Compute, a `BiasAdd_v1` over that output. Allocations are ignored, so `matmul_persistent`'s `aten.empty` of `c` doesn't
  count. Shape, tiling and chunking don't enter it; the GEMM pins are checked before it runs.
- **#39's record fold** (`art:38586a21…`, `match/resolution.json`, the served run under the Qwen2.5-1.5B profile):
  - all 512 steps (step 0 is the whole 4,096-row prefill in one step, no chunking) have exactly 28 `Gemm_v1{K=1536,N=2048}` and 28
    `BiasAdd_v1{N=2048}` Computes, with equal rows: 128,996 each;
  - no step has an unsupported event or an error;
  - every `aten.add.Tensor` of the run is one of those bias adds (14,336 = 512 × 28);
  - every `aten.empty` is an `alloc`.
- **The i256/o32 capture with #244's code** (the pod run that passed Match and GM-01): all 32 steps bind 28
  `GemmBias_v1{K=1536,N=2048}` Computes (8,036 rows: prefill M = 256, decode M = 1), leaving no qkv `Gemm_v1` and no `BiasAdd_v1`.
- The event sequence (`c = torch.empty`, the launch, then `output + bias`) is the same vLLM Python path at every shape.
- So #39's fold should carry 128,996 `GemmBias_v1{K=1536,N=2048}` rows, 28 per step, matching its Build.
- **For the run lane at #39's Match:**
  - `match_compare.json` should show `histogram_diff_T_normalised` empty and canonical equality;
  - the fold's `op_histogram` should show `aten.add.Tensor → Compute GemmBias_v1{K=1536,N=2048}` × 14,336, and the qkv launches as
    `Transparent noop` (pattern `gemm_bias.launch`) × 14,336.

**Unchanged:** the head is still `b0b4b438`. The pod was terminated at 06:21Z (32 minutes on an L40S, about $0.60), and future vLLM pods
will use the `vyv-` prefix. The tap stays unbuilt.
