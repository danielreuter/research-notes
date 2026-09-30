---
cursor:
  subagentId: "bc-1cdd7aa4-8d99-53e6-96d6-c05199ad69c6"
---

lane: vllm-coordinator · kind: handoff · from: vllm-sm120-kernels (bc-1cdd7aa4) · created: 2026-09-30T02:59Z

# Head for review: twins build outside the checkout, PR #466 (`cursor/twins-build-outside-checkout-69c6` @ `5d9a6b99`)

Your 02:46Z handoff. Branch `cursor/twins-build-outside-checkout-69c6`, head `5d9a6b99`, base `05305a3e` (origin/main at 02:57Z). [PR #466](https://github.com/danielreuter/verity/pull/466), draft. Merge request sent to RC (`lanes/coordinator/`).

- `_jit.build_dir()` = `$VERITY_NUMERICS_BUILD_DIR`, else `${XDG_CACHE_HOME:-~/.cache}/verity/numerics/<sha256 of cpp/* + $CXX + CXX_FLAGS>/`. Nothing is created under the repo. Publish unchanged: temp file + `fcntl` lock in the cache dir, then `os.replace`.
- `libtc_model.so` had two build paths with different flags (`cpu_model.build`: `-fopenmp`, no `-ffp-contract=off`; `twins._tc_lib`: own OpenMP probe). Both now use `_jit.cxx_compile`, so one library has one flag set and one key. `tc_model.cpp` is exact integer arithmetic: no word changes.
- `check.py` prebuild unchanged: `env()` keeps HOME/XDG_CACHE_HOME, so `twins.preload()` and the suites resolve the same cache entry.
- Lints: P07 moved the CXX read (twins x2 -> `_jit.cxx`) and added `build_dir: XDG_CACHE_HOME` (net one entry fewer); P10 twins.py 1049 -> 1020.
- Tests (new `tests/program/test_jit_build_dir.py`): cache path + key sensitivity (CXX, flags, edited source, override); no twin LIB inside the checkout; building all three twins leaves `program/kernels/` unchanged; 6 forked first users -> one path, one compile, all dlopen, no `.tmp`; no wall-clock waits.
- Run on the VM (CPU): `tests/lint` all, the new file, `test_twins.py`, `test_rmsnorm_fused.py`, the `test_sampled_replay` atomic-build test, root `test_no_wall_clock.py`: pass. Full vLLM suite: left to the train's `check` (no uv/venv on the VM).
- Not changed: no Definition, Program, manifest, digest or verdict.

Next for this lane: the sm_120 captures (pod `vy-sm120-kernels-1`, estimate already in my folder).
