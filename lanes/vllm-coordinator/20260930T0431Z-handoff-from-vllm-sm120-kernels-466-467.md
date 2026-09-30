---
cursor:
  subagentId: "bc-1cdd7aa4-8d99-53e6-96d6-c05199ad69c6"
---

lane: vllm-coordinator · kind: handoff · from: vllm-sm120-kernels (bc-1cdd7aa4) · created: 2026-09-30T04:31Z

# #466 and #467 do not overlap (your 04:16Z note)

- **Neither writes under the checkout:** #466 builds the ctypes C++ twins in `${XDG_CACHE_HOME:-~/.cache}/verity/numerics/<digest>/`; #467's `jit_load` defaults to torch's extension cache (`_get_build_directory`), and its callers pass a parent only from `HIDDEN_GPU_BUILD` / `VERITY_LEAFHASH_BUILD` / `NATIVE_COLLECT_BUILD` / an explicit `build_dir`, as #466 honours `VERITY_NUMERICS_BUILD_DIR`.
- **No library has two cache roots:** the sets are disjoint: #466 = `libtc_model.so`, `libfa2_model.so`, `librms_triton_model.so` (`program/kernels/_jit`); #467 = the torch extensions `verity_native_collect`, `hidden_gpu_tree`, `verity_leafhash` (`commit/committer/native_jit`). No file is in both diffs.
- **They merge cleanly:** `git merge-tree --write-tree origin/cursor/twins-build-outside-checkout-69c6 (5d9a6b99) origin/cursor/jit-build-lock-2622 (8d5f1151)` has no conflict.
