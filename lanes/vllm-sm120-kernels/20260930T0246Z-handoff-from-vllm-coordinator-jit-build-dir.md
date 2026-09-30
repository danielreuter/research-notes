---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-sm120-kernels · kind: handoff (**high priority, before the sm_120 work**; CPU only) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-30T02:46Z

# Build the C++ twins outside the checkout (one small PR, through RC's trains)

**What broke:** train TVC2R failed with every suite passing. The Lean-suite step's repository guard found a stray `integrations/vllm/…/program/kernels/cpp/build/libfa2_model.so.*.tmp`: a concurrent vLLM test had JIT-compiled the FA2 twin **into the source tree**.

**The cause:** `program/kernels/_jit.py` `build_dir()` defaults to `cpp/build/` beside the sources (gitignored) unless `VERITY_NUMERICS_BUILD_DIR` is set. The same applies to `libtc_model.so`, `libfa2_model.so` and `librms_triton_model.so`.

**The fix:**
- **`build_dir()`:** `$VERITY_NUMERICS_BUILD_DIR` if set; otherwise a per-user cache **outside the checkout**, `${XDG_CACHE_HOME:-~/.cache}/verity/numerics/<sha256 of the sources + compiler flags>/`. Never create anything under the repo.
- **Keep the publish atomic:** a tmp file in the same cache dir, then `os.replace`, under a file lock (`fcntl.flock`) around the compile, so concurrent tests build each library once and never see a partial `.so`.
- **Keep `check`'s pre-build step working:** `check.py` builds the twins once before its groups start (#a13124d7). Point it at the same cache, or set `VERITY_NUMERICS_BUILD_DIR` for the run.
- **Tests:**
  - a test that fails if any build writes under the checkout;
  - a concurrency test with N processes resolving one library at once: one compile, all load it, no `.tmp` left behind;
  - no wall-clock waits (#352's lint).

**Priority:** Daniel wants anything that speeds up or stabilises checks landed first. Do this **before** your sm_120 captures. Send the head to `lanes/vllm-coordinator/` and a merge request to the research coordinator (`lanes/coordinator/`) for the next train.
