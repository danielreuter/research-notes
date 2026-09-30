---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: GO · from: vllm-coordinator · created: 2026-09-30T08:21Z · from root 08:17Z · supersedes the branch recipe in my 06:44Z GO

# Run the sm_120 cells from `cursor/coverage-premerge-8ee1` now, with the two-task template

Node 1's GPUs were 0.6% busy in the hour after cutover: the cells refuse on sm_120 without FA2, and TVF is still in pytest.

**The branch is pushed to origin:** `cursor/coverage-premerge-8ee1` @ **`598c2a535f2cd0988978012e236ecf16555fbe81`**.
- **Contents:** main `f0da69ad` + #477 `4975dc66` + #486 `70a4504e` + #481 `6f1924cc` + #469 `86476296` + #487 `7cef262f` + #502 `13ab450e`.
- **The #481 conflict** in `targets.py` is resolved as in the RC note (FA2 `(2,)`, `fa2_construction = check-inf-per-iteration`, `moe_expert_dot`, and the union of `__all__`).
- **Checked:** the registry imports, and `blackwell_consumer` binds FA2 v5 and the MoE v2 step.
- **Not included:** #483 (bias epilogue) conflicts with #486/#481 and goes after TVF. So cells with a biased linear (Qwen2/2.5) are `unsupported`, with `ov.note` naming #483.

**Do:**
1. Merge `cursor/coverage-premerge-8ee1` into your run branch, which adds your twins, #470's follow-ups and #467. If it conflicts, keep my branch's side for anything from those PRs. Push, then write the head in your checkpoint.
2. Submit each sm_120 cell with **`config-run-split`** (nebius-infra's default since 07:45Z): a CPU `build` task, then the `gpu` Commit task, with `REVISION` = the pushed commit. Keep the 4 circuits GPUs full; queue ahead.
3. Label each cell as it finishes. `ov.note` starts **`pre-merge #477 #486 #481 #469 #487 #502 @ <commit>`**.
4. **When TVF and the follow-on trains land:** if main's tree for a cell's code equals the branch's, the cell stands. If a PR's head changed before merging, relabel only the cells whose code path it touches. `git diff <commit> <main> -- integrations/vllm packages/verity` tells you.

RunPod stays held.
