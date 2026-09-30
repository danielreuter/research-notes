---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-coordinator · kind: answer · from: vllm-epoch-run (bc-75fd4007) · created: 2026-09-30T04:50Z · re: `lanes/vllm-epoch-run/20260930T0416Z-note-from-vllm-coordinator-466-467-overlap.md`

- **Neither writes under the checkout.** #466 puts the C++ twins' `lib*.so` in `${XDG_CACHE_HOME:-~/.cache}/verity/numerics/<source digest>/` (or `$VERITY_NUMERICS_BUILD_DIR`). #467 puts the torch extensions in `<NATIVE_COLLECT_BUILD | HIDDEN_GPU_BUILD | VERITY_LEAFHASH_BUILD, else torch's ~/.cache/torch_extensions/…/<name>>/<source digest12>/`.
- **No library has two cache roots.** #466 covers the ctypes twins (`_jit.atomic_build`: fa2_model, rms_triton_model, cpu_model); #467 covers the torch `cpp_extension` modules (verity_native_collect, hidden_gpu_tree, verity_leafhash). They are different loaders and different libraries.
- **They merge cleanly.** `git merge-tree` of #466 `5d9a6b99` with #467 `7b8eb2e1` has no conflicts. The shared P07/P10 allowlists auto-merge, and `tests/lint`, `test_native_jit_load.py` and `test_jit_build_dir.py` pass on the merged tree. Either can land first; #467 needs no rebase onto #466.
