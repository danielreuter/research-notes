# vllm-rf-m32 READY

- Branch `lane/vllm-rf-m32`, head `271a0952`, base origin/main `78b8935b` (contains fee32f05). One commit, non-epoch, digest-neutral.
- Change: `integrations/vllm/verity_vllm/commit/scheme.py::chunk_header` passes `M & 0xFFFFFFFF` to core (the CUDA chunk kernels
  write u32 M; the length is bound by the step root's leaf count n). Core's u32 validation and the header format are untouched.
- Tests: `tests/commit/test_production_vectors.py` `test_chunk_header_matches_the_pre_c1_u32_header` (7 M values from 0 to 2^40+3:
  equals the pre-c1 `hidden_stream.pack_words` header; for M < 2^32 equals core's unmasked header, so bytes are unchanged) and
  `test_chunk_header_of_a_step_past_2_32_words` (#4's M = 5036944512 no longer raises; word 6 = M mod 2^32).

## Gates (vyv-rf-m32-cpu, cpu3g x16, one run r20260925-214510-4478, custody R2, PRESERVED sha256-readback)
- Lints: base and head green.
- New tests: 8 passed. Targeted `tests/commit` + `packages/verity/tests/commitments` at head: 498 passed, 32 skipped, 1 failed
  (`test_native_jit_keying::test_pod_release_fails_closed_on_a_stale_so_and_records_the_digest`; pre-existing, fails identically at
  base: `tests/sweep/pod_release.sh` absent from the tree).
- Gate (b), same pod, base then head: base 4072 (3718 passed, 50 failed, 11 error, 287 skipped, 6 xfailed); head 4080 (3726 passed,
  same 50/11/287/6). jdiff (baseline-jdiff.py 363304c0): outcome changed 0, new failures 0, new skips 0, new skip reasons 0; only in
  head: the 8 new tests (passed). Evidence: `evidence/jdiff-gate_b-base-vs-head.txt`, `evidence/m32_gates-stdout.txt`, script
  `evidence/m32_gates.sh`.

## Header-word audit
Only M can reach 2^32 on a real row; every kernel path casts all words to u32 (`native_collect.cpp` static_cast into
`native_tree.cu`, `hidden_gpu_tree.cu` (uint32_t), `verity_tap.h` 487-489). launch_tag = HB = step; chunk_index < 2^27;
chunk_words in {32,64,128}; NB small; src_mask `& 0xFF` in-kernel and < 2^8 in core; thread-header fields bounded by sequence
lengths / head counts. Unchanged. No CPU reference of the kernel header exists (GPU-only `test_scheme_cuda.py`).

## Deliberately not changed
Core `verity.commitments.vllm_v1` (validation, 64-bit M), thread_header, root bindings. No Program/manifest/root/leaf id change
for M < 2^32; the #101 path is untouched (small M). No GPU row run (the epoch lane re-runs #4 with this commit).

## Found-not-fixed
- `test_native_jit_keying::test_pod_release_fails_closed_...` opens `tests/sweep/pod_release.sh`, which isn't in the tree (fails
  at base and head).

## Pods / spend
vyv-rf-m32-cpu terminated 22:39Z. Spend about $0.35.
