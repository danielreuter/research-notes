---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T15:15Z
---

# Re your 14:16Z decisions: #546 is ready at `51318a6e`; the `rows.py` split isn't needed; #557 is #535's rework, and its B1/B8 acceptance is Kueue jobs 215/216

A correction first: my 14:01Z handoff did reach you. My 14:28Z one duplicates it and adds the main-only CPU check. It was not a replacement.

- **4. The `rows.py` split: not needed any more, so I haven't opened it.**
  - Main's `7604eb59` (the sm_120 kernels lane's MoE change) moved `moe_router_topk` to `kernels/moe_router_rows.py`. Main's `rows.py` is now 756 lines.
  - With #546 it's 761, with #557 769, and with both about 774. #516 and #524 add no rows.
  - If you still want the split, say so and I'll send it.
- **5. #546 is ready for review**, head `51318a6e` (main `8a4e1147` merged in; one import-line conflict in `rows.py`).
  - circuit-check: 5 targets, 0 failures. Its tests, the kernel self-check, lint and the gates pass (`r20260930-150522-4f2c`).
  - The DeepGEMM GEMM stays held.
- **2. #535's rework is [#557](https://github.com/danielreuter/verity/pull/557)** (draft), a new branch on main at `9c390086`. #535's branch carries the #483/#501 merges, and I can't force-push it. #535 can be closed as superseded (your call or Daniel's).
  - **Acceptance:** managed jobs 215 (B1) and 216 (B8), both `ROLE=QWEN05`, on #557 + `infra/nebius` + the two workloads.
  - **Job 212 was a bad submission.** It used `ROLE=B1`, which is Qwen2.5-1.5B's checkpoint role, and its tree lacked the workload. It failed at the Build in 44 s.
  - **The B8 workload** (`qwen25-05b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager`) isn't on any branch. I generated it with `verity-vllm workload` (`r20260930-150147-3448`); the same command reproduces the coverage lane's B1 file byte for byte. It's in my scratch job tree only. The coverage lane may want to add it.
  - **cc 8.x:** the cc 8.9 Qwen2.5-0.5B Program digest is `92554796` on both main and #557. Its manifest names `GemmBias_v1` as `qkv_proj/0` instead of `qkv_proj/out`, which is the fix.
  - **cc 9.0:** the Program digest is `5fbb6fee` on both, still `Gemm_v2` + `BiasAdd_v1`. That Build declares FA2 (`r20260930-150743-0c7e`, `-150748-2d71`): on main, FA3 refuses both Qwen2.5-0.5B and 1.5B at `fa3_masked_from` (7 or 6 query heads per KV head don't divide the tile).
- **Needs your decision: Hopper Qwen2 has sm_120's gap on main.** Its cc 9.0 manifest requires 96 call boundaries at `qkv_proj`'s pre-bias `Gemm_v2`, and it names the post-bias value `bias`. So an H100 Qwen2 Commit fails identity coverage on main.
  - #557 fixes it with one line (`gemm_bias_dot: True` on `hopper`), but that moves the H100 Qwen2 Program digests. It's off until you say.
- **6. The linears without a bias:** I'll add the line to #557's body with the acceptance verdict.
