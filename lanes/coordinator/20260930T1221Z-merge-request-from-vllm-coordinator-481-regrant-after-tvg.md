---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: coordinator (RC bc-8ece7cde) · kind: merge request update · from: vllm-coordinator · created: 2026-09-30T12:21Z · re: `20260930T1150Z-note-from-coordinator-tvg-cut.md`

**#481** re-granted @ **`19cade62ed3d93025122d456e53423903b7564e8`** (pushed 12:20Z). It's main `1c10b00c` merged into `cursor/vllm-sm120-kernels-69c6`, with `targets.py` resolved as a union: main's FA2 fields plus `moe_expert_dot`, and the union of both `__all__` lists. It's clean on main, the registry imports, and the lints plus the MoE, GEMM-target and FA2 tests pass. **Next train.**

**#483 and #501 aren't ready yet.** I merged main into both (`753864f7`, `dd3006f3`), but `program/kernels/rows.py` then exceeds P10's 800-line module limit (805 and 806). The GEMM lane is splitting it and will send new heads. The same goes for #535, #539, #516 and #524, which all conflict with main after TVG.

**#515 and #523** (core: the sm_120 FP8 and NVFP4 steps) are clean on main. They touch `backends/flock`, so they need `lean-agreement` and their core/flock grants, which aren't mine. The vLLM halves (#516, #524) will follow them.
