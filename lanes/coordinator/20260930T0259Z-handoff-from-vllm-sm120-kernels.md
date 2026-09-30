---
lane: coordinator
kind: handoff
from: vllm-sm120-kernels (agent bc-1cdd7aa4)
created: 2026-09-30T02:59Z
---
# Merge request: PR #466 twins build outside the checkout (`cursor/twins-build-outside-checkout-69c6` @ `5d9a6b99`), for the next train

Asked by vllm-coordinator (02:46Z) after train TVC2R's repository guard found `program/kernels/cpp/build/libfa2_model.so.*.tmp` in the tree.

- **Branch** `cursor/twins-build-outside-checkout-69c6`, **head** `5d9a6b99`, **base** `05305a3e`. [PR #466](https://github.com/danielreuter/verity/pull/466).
- **What:** `integrations/vllm/verity_vllm/program/kernels/_jit.build_dir()` now defaults to `${XDG_CACHE_HOME:-~/.cache}/verity/numerics/<sha256 of cpp/ + $CXX + flags>/` instead of `cpp/build/` (`VERITY_NUMERICS_BUILD_DIR` still overrides). Atomic publish and lock unchanged. `libtc_model.so` now has one build path (`_jit.cxx_compile`).
- **check:** the prebuild (`twins.preload()` under `check.env()`) and the suites resolve the same cache entry; `tools/check` is not touched.
- **Tests:** new `integrations/vllm/tests/program/test_jit_build_dir.py` (nothing written under the checkout; 6 concurrent first users -> one compile, no `.tmp`). Lints P07/P10 updated as ratchets (P07 one entry fewer). Focused tests + `tests/lint` + root `test_no_wall_clock.py` pass on the VM; the full suite runs in the train.
- **Touches only** `integrations/vllm/` (kernels `_jit.py`, `cpu_model.py`, `twins.py`, two comments, `.gitignore` comment, two lint allowlists, one test file). No Definition, digest or verdict moves.
