---
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T08:18Z
---

# Follow-up to 07:29Z: the full quick vLLM suite is clean on #483 and #501; #483 needs your grant at 7cea7a99

- **Suite results:** CPU only, CUDA hidden, on vy-nebius-1 check slots (after root's 07:55Z note), `-m "not regression and not slow and not pod"`.
  - **#483 head `7cea7a99`:** run `r20260930-075229-cb5f`.
  - **#501 head `1005435c`:** run `r20260930-075224-1fc7`.
  - **Base `29f691be`:** run `r20260930-075234-32cf`.
  - **No failure is new on either head:** all three trees fail the same 38 tests. Those are environmental: fixtures not fetched in a `--source` tree, and CUDA-dependent cases on a host whose GPUs are hidden.
  - `test_no_by_name_rules` passes on both heads.
  - `test_the_stored_tp2_moe_builds_merge_with_every_peer_bound` was deselected, per your 05:33Z note. It's unverified in this gate and left to the train check.
  - Both PR bodies record this.
- **#483:** please grant at **`7cea7a99`**. 720/720 still stands, since the lint fix leaves the bindings unchanged.
- **The earlier suite runs were stopped.** The 07:01Z and 07:32Z runs opened CUDA on a Kueue-owned GPU (nebius-infra 07:32Z). I stopped them at 07:51Z; they're `CANCELLED_MANUAL`, and nebius-infra has been told.
- **(4) is scoped, not started.**
  - `observe/fold/patterns/gemm.py` matches only the Triton `matmul_kernel_persistent` launch.
  - An sm_120 linear is a cuBLASLt `aten.linear`/`aten.addmm` node with no Triton launch, so today it folds as Unsupported ("without exactly one batch-invariant launch").
  - The fix is a pattern that binds `Gemm_v2` / `GemmBiasF32Epilogue_v1` / `GemvBiasF32_v1` on a cuBLASLt target. Writing it needs a recorded sm_120 fold tree (a full row with Match). Point me at one, or it waits.
- **Still yours from 07:29Z:** #502's census line (1,000 TFLOPS dense FP8, which adds an empty Table 2 draft row), and whether to pin e5m2.

**Nothing of mine is running. My PRs:**
- #465, #476 and #483: yours to merge in order;
- #487: ready;
- #501 and #502: drafts, stacked.
