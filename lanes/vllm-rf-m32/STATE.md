# vllm-rf-m32 STATE

New lane (no predecessor). Agent bc-7039be6c-2a9f-5501-af51-ee96bf96b428, branch `lane/vllm-rf-m32` from origin/main `78b8935b`
(contains fee32f05). Brief: `$STORE/internal/lane-briefs/vllm-m32.md`.

## Done
- `271a0952` scheme.chunk_header passes `M & 0xFFFFFFFF` (kernels write u32 M; length bound by the step root's n). Tests in
  `tests/commit/test_production_vectors.py`: `test_chunk_header_matches_the_pre_c1_u32_header` (M in {0, 8, 2^32-1, 2^32, 2^32+7,
  5036944512, 2^40+3}; equals the pre-c1 `pack_words` header; equals core's unmasked header for M < 2^32) and
  `test_chunk_header_of_a_step_past_2_32_words` (#4's M = 5036944512 no longer raises; word 6 = M mod 2^32).
- Header-word audit (only M needs the mask):
  - chunk header, all three kernel paths (`native_tree.cu` via `native_collect.cpp` `static_cast<uint32_t>`, `hidden_gpu_tree.cu`
    `(uint32_t)`): launch_tag = step, HB = step, chunk_index = `(uint32_t)(ci+ci_base)` < M*4/chunk_bytes <= 2^27 for any real
    step, chunk_words in {32,64,128}, NB in {0,1} (committer) or the key-block cap (hidden stream), src_mask `& 0xFF` in-kernel
    and < 2^8 in core. None reaches 2^32 on a real row: unchanged.
  - thread header (`verity_tap.h` 487-489, all `(uint32_t)`): slab, m_block, n_block, tidx, seqlen_q/k, tag, nbmax -- all bounded
    by sequence lengths and head counts, far below 2^32: unchanged.
  - No CPU reference of the kernel's header exists (the CUDA copies are pinned only on GPU pods by `test_scheme_cuda.py`).

- Fix READY (`READY.md`): gate (b) run r20260925-214510-4478 PRESERVED, jdiff clean; vyv-rf-m32-cpu terminated 22:39Z;
  merge-ready handoff to vllm-coordinator and sha handoff to vllm-rf-epoch sent 22:40Z.

## Task 2: confirming gate (a) T0+T1 on main (coordinator handoff 20260925T2155Z)
- Tree origin/main `5f8d8789` (b1 dca6a867 in; 271a0952 not yet merged). Worktree ~/wt/main-5f8d8789.
- Mint 22:40:00Z on the VM: TTL 3h, object-read-only, prefixes manifests/ + objects/sha256/, piped to vyv-rf-m32-reg
  /root/r2ro.env (0600). Prefetch 26 ok / 0 fail; key deleted 22:47:08Z (prefetch trap).

- Gate (a) on main 5f8d8789 CONFIRMED: r20260925-224745-e739 rc 0, 73 passed / 85 skipped (158), = a23b's base; only the #70/#75
  skip rewordings. PRESERVED (both runs). CONFIRM handoff 20260926T0315Z sent.

## Task 3: admission fix 89cd9d1a -> main (coordinator handoff 20260926T0315Z, $3, deadline 08:00Z)
- Branch `lane/vllm-rf-admit` = origin/main `7289e3ad` + `git cherry-pick -x 89cd9d1a` -> `7b9558b7` (pushed). Conflict only in
  p10_size.json: commit.py `main` cap set to the merged size 1770 (main had 1776; the fix shrinks main by 6); module stays 2939.
  The cherry-picked message still says "1913 -> 1907" (epoch-branch numbers; no amend).
- vyv-rf-m32-reg was already terminated; every cpu3g/cpu3m/cpu3c/cpu5* shape returned "no instances available", so the gate pod is
  vyv-rf-m32-admit = RunPod lq6wt0cak7uhxx, 1x RTX A4000 host ($0.25/h, 128 cpus, 503 GB), GPU hidden (CUDA_VISIBLE_DEVICES=-1).

- Base r20260926-031830-2411 (7289e3ad) done: lints rc 1 (pre-existing on main: test_no_by_name_rules, vu_export.py:478/481
  path predicates), gate (b) 30 failed / 3801 passed / 286 skipped / 6 xfailed in 1981 s. sampled_proofs importable.
- Head 7b9558b7 lints added 2 failures from the cherry-pick: P7 stale broad-except entry (commit.py main) and P11 doc-round
  (`[moe R17-1]` in admission_lag's docstring). Fixed in `02b3be03` (docstring tag dropped, P7 entry deleted; no allowlist grows).

## Running
- vyv-rf-m32-admit: head r20260926-031940-f369 (7b9558b7) done 04:30Z (32 failed = base 30 + the 2 lint tests). head2 r20260926-041141-1cd3
  (02b3be03): lints done 04:31Z = base (only the pre-existing by-name failure); gate (b) since 04:31Z, ETA ~05:05Z.

## Next
- jdiff base vs head2 (+ f369), test_admission_commit passes, lints = base's single pre-existing failure, preserved (3 runs),
  terminate, merge-ready handoff, FINAL.

## Open questions
- none

## Found-not-fixed
- `test_native_jit_keying::test_pod_release_fails_closed_...` needs `tests/sweep/pod_release.sh`, which is absent (fails at base and head).
- Gate scripts that set their own PYTHONPATH miss `protocols/sampled_proofs` on post-#29 trees (gate (a) fails at collection).
