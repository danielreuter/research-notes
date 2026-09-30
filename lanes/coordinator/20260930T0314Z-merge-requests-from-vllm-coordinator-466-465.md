---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-coordinator · kind: merge requests · to: research coordinator (bc-8ece7cde) · created: 2026-09-30T03:14Z

# #466 first (it fixes the TVC2R flake), then #465

**1. #466 (`5d9a6b99`), the C++ twins built outside the checkout: APPROVED, high priority.** It fixes TVC2R's stray `cpp/build/*.tmp` flake.
- **The change:**
  - `_jit.build_dir()` becomes `$VERITY_NUMERICS_BUILD_DIR`, else `${XDG_CACHE_HOME:-~/.cache}/verity/numerics/<sha256 of sources + CXX + flags>/`;
  - the lock and atomic publish are kept;
  - `libtc_model.so`'s two build paths are unified onto one flag set;
  - `check.py`'s prebuild resolves the same cache entry.
- **Tests,** on current main: the new `test_jit_build_dir.py` (concurrency, and nothing written under the checkout), `test_twins.py`, `test_sampled_replay.py` and the vLLM lints give rc 0. After the run, the checkout's `program/kernels/` has no build products.
- No Definition, Program or digest changes.

**2. #465 (`f740c1d5`), the sm_120 target registration: APPROVED.**
- **The change:** `config.TARGETS["rtxpro6000"] = (12, 0)`, and a `blackwell_consumer` GEMM target. Linears are cuBLASLt with split-K off (vLLM's Triton overrides are major-8 only), with the dot `HopperBF16WgmmaDot16_v1`, since core pins sm_120's `mma.sync` step to the Hopper model. Attention is refused by name until FA2 is registered.
- **Checks:** cc 8.0/8.9/9.0 registry dumps are byte-identical, per the lane. On current main, `test_gemm_targets.py`, `test_target_family.py`, `test_golden.py`, `test_profiles_generic.py` and the lints pass.
- **Still to run:** its torch test on sm_120 runs on the lane's first pod. The GEMM record says it's registered before the correspondence.
