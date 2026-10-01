---
id: 20261001T0200Z-handoff-from-bc-9914c188-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: kernel lane (bc-9914c188, Pearl-C H100 scheme and harness)
---

_Relayed verbatim from the Cursor store by old-accounting (bc-b729c175): the author's VM gets a 403 pushing to research-notes._

# Migration handoff from bc-9914c188 (kernel lane): #449 is in the train; one small follow-up is kept; nothing is in flight

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. Written 7:00 PM PDT.

## 1. Branches and PRs

- **#449**, `cursor/pearl-c-h100-9ada`: Pearl-C's FP8 scheme, verifier and H100 harness.
  - Origin head: `1b1895bc`. It's a draft, green, and in the merge train since 5:27 PM PDT.
  - Its recorded check passed at `5f6a31c7` (`r20260930-112836-2ecb`).
  - Other agents later merged `main` into it and added an MKL VML conftest fix, giving `1b1895bc`. The research coordinator
    re-checks it as part of the train.
  - What's left: it lands. Not in `main` as of 7:00 PM PDT (`main` is at `4860d817`).
- **#449's follow-up**, not pushed as a branch yet: the `fake_cuda.c` kernel-name limit.
  - It raises the stub's table from 64 to 128 names and its buffer to 8,192 bytes, and aborts past either. Before, the 65th
    name was dropped silently and its `cuModuleGetFunction` returned 500.
  - It's one commit, GPU 2's `ea17cefb`, which is on origin in `cursor/pearl-c-sm120-h1-b44b` and others. My cherry-pick of
    it is `efd776a5`.
  - Held until #449 lands, by the old coordinator's decision: #449 merges at its checked head without it.
  - #449's tests register 28 names, so the 64-name limit never bit #449's check.
- **#462**, `cursor/pearl-c-vllm-9ada` at `9eef1893`: Pearl-C's CPU executor half for the vLLM option.
  - It's a draft, stacked on #435 (`cursor/pouw-gpu-path-4f91`), and paused. The backlog says to drop it tonight.
- **#295**, `cursor/h100-fp8-pouw-scheme-9ada` at `f76cf2ab`: the older fp8-is-h100 scheme.
  - It's a draft, conflicts with `main` and was last touched on Sep 29. Pearl-C superseded it. The backlog says to close it
    or leave it; that's Daniel's call.

## 2. Runs and jobs in flight

None. I have no research runs, fill jobs or node 2 outputs; this lane ran CPU-only. Nothing needs custody or hand
preservation.

## 3. Half-done state

- **This VM holds nothing unique.**
  - `/workspace` (on #449's branch, ahead 1 with `efd776a5` and behind 303) and the `/tmp/wt-pcv` worktree for #462 are
    clean.
  - Everything else is pushed. The tmux sessions are idle shells.
- **`efd776a5`** is saved in the store as `code/pearl-c-h100/fake-cuda-kernel-limit.patch` (`git format-patch` output). It
  is the same change as `ea17cefb` on origin.
- **#462's fixture,** `integrations/vllm/tests/protocol_options/fixtures/qwen7b_layer2_down_split_rows.f32.gz`
  (4,558,837 bytes):
  - It's committed on the branch at `9eef1893`.
  - It isn't registered in `fixtures/artifacts.json`; registering needs `research data put --kind fixture/v1` from a machine
    with store access.
  - Its source scripts are in the store under `code/pearl-c-h100/qwen7b/`.
- **Store documents I own:** `internal/pouw/rtx-pro/blake3-tree-interface.md` (the frame-b3 / `-h1` tree interface) and my
  entries in `internal/pouw/coordinator-inbox.md`.
- **Code in the store:** `code/pearl-c-h100/{ship,bench-ship,capture}` hold earlier ship and capture material for #449,
  kept for reference. Nothing there is needed to land it.

## 4. Next step for each item

- **#449:** the research coordinator lands it in the next train. Nothing is needed from a successor unless the train's
  re-check fails.
  - If it fails on the test-order leak (see the traps), the pin test is `test_native_jit_isolation.py`.
  - If it fails on anything else, fix that, and fold the `fake_cuda.c` commit into the new head before re-recording.
- **The follow-up (keep):** once #449 is in `main`:
  - Make `cursor/<name>` off `origin/main` and apply the patch (`git am`) or cherry-pick `ea17cefb`.
  - Run the two CPU dry runs, then open a draft PR against `main`. Only those dry runs are needed (old coordinator's
    decision).

~~~text
uv run pytest benchmarks/pouw/tests/test_pearl_c_kernel.py::test_runner_dry_run benchmarks/pouw/tests/test_pearl_c_bench.py::test_bench_dry_run
~~~

- **#462 (I'd stop):** park or close it, as Daniel decides. If it's revived, it waits for #435 to land and needs its
  fixture registered.
- **#295 (I'd stop):** close it, or leave it parked.

## 5. Traps

- **Don't push this VM's `cursor/pearl-c-h100-9ada`.** It diverges from origin: origin carries `main` merges and the MKL
  fix, and the local branch carries `efd776a5`. A push would rewrite #449's train head. Take the fix from the patch or
  `ea17cefb` instead.
- **The `.FTZ` gate fails closed off its toolchain.**
  - `benchmarks/pouw/pearl_c/build.sh` and `ftz_gate.py` are keyed to `V12.9.86/sm_90a -O3 -std=c++17 -fmad=false`
    (`ftz_pins.json`).
  - Another nvcc version, or other flags, fails the build by design. Pin that toolchain with `ftz_gate.py --pin` on that
    machine.
  - The `--use_fast_math` negative control must still fail inside `ieee_ops` or `ieee_q`.
- **The test-order leak:** `test_ref_prims.py`'s `exp` test (`F32ExpRn_v1-f32_exp_rn_bits-exp`) failed when
  `test_native_jit_load.py` ran first in the same pytest process.
  - The fix runs the native JIT load in a subprocess (`_isolated`), which compiles the test file from source, because a
    stale `.pyc` once ran old code.
  - The mechanism was never found. It may be MKL VML threading, which `1b1895bc`'s conftest fix addresses.
- **`fake_cuda.c` drops kernel names silently** until the follow-up lands: a 65th `FAKE_KERNELS` name fails with
  `cuModuleGetFunction` 500, which looks like a missing kernel. #449 is at 28 names.
- **Bench keys differ from check keys:** `bench.py` runs with `unit=None`, using bench.json's line keys, because the CPU twin
  can't hash a whole A at bench shapes. `run.py`'s check derives seed_A on the device from A's `-h1` root (check.json v2). Don't
  compare their keys.
- **Prices are per device:** `PearlC` defaults to `H100_PRICES`, and v0 is H100-only.
  - The sm_120 record gives the name `@sm_120`, at FADD 8. That's the code's credit, the cheapest bit-exact form.
  - The "larger of 8.00 and 8.38" rule applies only to published γ figures.
- **Files reserved for the hashing-cut work on #435:** don't edit `pouw.py`, `pouw_device.py`, `pouw_native.py`, `pouw_cuda/*`
  or `vllm_bench.py`.
- **This VM can't push to research-notes:** it gets a 403 as cursor[bot]. Replies go through the store outbox
  `internal/pouw-fp8/accounting-outbox/`.

After this handoff I start no new work. I'll answer my replacement's questions in this lane until it confirms takeover.
