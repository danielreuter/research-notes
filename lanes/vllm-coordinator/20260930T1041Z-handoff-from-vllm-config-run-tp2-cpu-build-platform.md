---
id: 20260930T1041Z-handoff-from-vllm-config-run-tp2-cpu-build-platform
campaign: overnight-sep30
lane: vllm-config-run-tp2
kind: handoff
status: ready-for-review
repo: danielreuter/verity
origin: cursor/build-cuda-platform-3847@3f195ad3
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

# The CPU-only Build for declared GPU targets: the digests are equal

**Branch `cursor/build-cuda-platform-3847`, head `3f195ad3`, based on main `f0da69ad`.** No PR is open yet (the environment opens it). Five commits, no force-push, the vLLM frontend only.

## Result

On vy-nebius-1, the SmolLM2-135M rtxpro6000 row (`smollm2-135m__bf16__rtxpro6000__tp1__b1__i256__o32__mixed__greedy__bi-eager`) was built with `row stage build --config-run 1` and no GPU. I compared it with the same row's GPU-visible Build in coverage cell `r20260930-083205-087a` (the sweep lane's, on pre-merge `2847317c`). Both CPU runs used the same tree: `2847317c` plus this branch, and the host's copy of the tree hashes identically to `2847317c`.

| run | GPU visibility | vLLM platform | step | request | workload | manifest |
|---|---|---|---|---|---|---|
| r20260930-083205-087a (reference) | GPU visible | NVML probe | 53aa6ed2… | 6ea7c413… | 393e9228… | b8e18695… |
| r20260930-095004-9211 | `CUDA_VISIBLE_DEVICES=` | NvmlCudaPlatform | equal | equal | equal | equal |
| r20260930-095004-bd5b | also NVML and nvidia-smi hidden | NonNvmlCudaPlatform | equal | equal | equal | equal |

- The full digests are 53aa6ed20e8dd0c1e74a0a332f359bda5dc36c40da38383d3a2e0a54a9c2a9c4 (step), 6ea7c413566473925be36c355ee9c3d84fa3db87d7d7e13e52c87bb6f50ac786 (request), 393e9228260663df610abdd41960ee1c861d2e9cec50d9184494b939a489e4e1 (workload) and b8e1869546c05b0a994f01a5381d135482f6137c2f3128ae6bfc09d2fc43c551 (manifest). The correspondence digests are also equal. Both CPU runs pass word-check with the same numbers (86,738 calls, 125,015,377 units).
- The second run is the realistic one. `CUDA_VISIBLE_DEVICES=` alone leaves NVML visible, and NVML is what the CPU pod lacks. So a harness outside the tree made every `libnvidia-ml.so.1` load fail and replaced nvidia-smi with a stub that logs calls. The Build made 0 nvidia-smi calls and resolved `NonNvmlCudaPlatform`.
- Negative control `r20260930-095531-b55e`: the unpatched `2847317c` under the same harness resolves `UnspecifiedPlatform`, and the Build crashes with `RuntimeError: Device string must not be empty`. That is the GPU-less pod's failure.
- `research status` shows rc 1 for every run, including the passing ones. The cause is the `bash -l` login shell's logout step; the Build printed rc=0 and the row checker's validation is `passed`.
- Labels (`--by vllm-config-run-tp2`, synced): the two equality runs are `ov.gate pass` and the control is `ov.gate fail`. Six earlier development runs of mine in the campaign are `ov.gate fail` with a note that they are superseded: r20260930-093317-6d2b/-00d0, -093422-ed8d/-968a and -094037-8837/-6e06. All carry `ov.ws build-cpu-platform`.

## What changed

- **Platform (`export_compat.select_cuda_platform`, called from `build.run` only when `--target` is declared, just before construction).**
  - `import vllm` itself resolves `current_platform`, because `torch_utils.PIN_MEMORY` reads it at import. So a one-shot `sys.meta_path` finder patches `vllm.platforms.resolve_current_platform_cls_qualname` (through `engine.hooks`) to return `vllm.platforms.cuda.CudaPlatform` as soon as `vllm.platforms` has executed.
  - vLLM then imports and instantiates the same class, at the same point, as its CUDA plugin does on a GPU host.
  - It first pins `engine_env.EXPORT`. The first version missed this, and `VLLM_USE_LAYERNAME=0` came too late, so the Build exported opaque `LayerName` arguments; the equality run caught it.
  - It refuses if a non-CUDA platform is already resolved. Serving and the Commit path are untouched: nothing runs without a declared Build target.
- **Declared target by row id.** `config.TARGET_NUM_SMS = {"rtxpro6000": 188}` and `target_family.declared_profile` give an rtxpro6000 row with no workload target the whole target (cc 12.0, 188 SMs). This is a no-op for the coverage workloads, which already declare both. h100 is left out because SXM has 132 SMs and PCIe 114.
- **Nothing in `row stage build` reads the device when the target is declared.**
  - The Build-only preflight uses the declared cc; commit and match still check the real device.
  - `row fa-version --target` is new.
  - `device_id`, the Program-cache key, uses the declared target and treats a missing nvidia-smi as no device. The sweep lane fixed this function too, in `b27ab8a0` on `cursor/coverage-v0-2622`. Mine conflicts textually with theirs; in the equality tree I kept mine.

## Tests and lints

- `tests/pipeline/test_declared_build_target.py` has 6 tests.
  - A fake `vllm` package on disk reproduces the real import order.
  - A declared GPU target gives the CUDA platform with NVML absent, and the export env is in force at vLLM import.
  - No declared target gives `UnspecifiedPlatform`, as before.
  - The selection also handles vLLM already imported, CUDA already resolved, and non-CUDA already resolved.
  - The preflight, `fa-version` and cache key read no device.
  - The old implementation fails this test file with the host's exact error.
- The full `-m "not pod"` suite on 3f195ad3: 4,269 passed, 13 failed. The 13 are the known missing-fixture failures, also present on main: test_kernel_dump ×1, test_sampling_rows ×1, test_topp_split_geometry ×7, test_topp_splits_operand ×4. The lints pass, and the root `tests/` pass (30).

## For you

- **Artifact identity moves; the Program digests do not.** The step and request `identity` fields change (24a21bd6 to 2a04b264, and 6b198395 to 2f5dbbf1) because the builder's sources changed, as with any builder PR. No record digest moves. A row with no declared target (sm_89 by default) builds exactly as before, and `TARGET_NUM_SMS` adds a declaration only for rtxpro6000.
- One behaviour change for rows that already declare a CUDA target (h100 and the coverage workloads): their Build now selects `CudaPlatform` through the declared target instead of NVML. On a GPU host that is the same class, as the equality run shows.

Copied to `lanes/nebius-infra/` so the config-run-split template's build task can drop its GPU once this is on main.
