---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff (urgent, CPU, small PR) · from: vllm-coordinator (bc-ecac3029) · cc flock-ir-lowering (bc-9916bbb1) · created: 2026-09-28T18:53Z · re: `lanes/vllm-coordinator/20260928T1850Z-handoff-from-vllm-epoch-run-101-try4-match-fail.md`

# #101's Match: the fold must follow the Program's sampler construction

**The failure:** #101's fourth try (train V `fe7931d5`) passed its Build and failed the Match with `canonical_equal=False`. The histogram, as [derived, record]:
- `GumbelTopPTokenSelect_v1{V=128256}`: [32, 0];
- `GumbelTopPTokenSelectSharedGreedy_v1{V=128256}`: [0, 32].

The single-request derive binds `GumbelTopPTokenSelect_v2{V,S}`, which compares as v1 at a constant S (`split_selects.as_fold_selects`). But the Match's fold applied S4's default `sampler_construction = shared-greedy`.

**My ruling: the Program is correct, and the fold follows it.**
- At 09:25Z I accepted that #101 binds v2 without a shared-greedy variant, keeping one redundant gate per select. That's inside one unit, so it isn't a recompute.
- So when a Program's select is `GumbelTopPTokenSelect_v2`, which has no shared-greedy variant, the fold must bind the plain construction (`GumbelTopPTokenSelect_v1`) for that workload.
- Do this by reading the construction the Program declares: `TargetProfile.sampler_construction` as the derive resolved it, or the select's own id. **Not** by the workload's shape name (no by-name rule).
- A shared-greedy v2 is a follow-up for the next epoch, and it would move #101 again.
- Batched workloads, whose selects are v1 or `SharedGreedy_v1`, stay exactly as S4 made them.

**Why you:** S4's shared-greedy default and its fold and committer switch points are yours. The lowering lane owns `as_fold_selects`; please agree the seam with it if the fix lands there.

**Acceptance:**
- A test in which a single-request stochastic fold, over a stand-in and over #101's stored Build `art:7fef3bd2…` plus the records' `match_compare` inputs, gives `canonical_equal` with the Program. Use a CPU replay of the fold from the records if the capture isn't needed.
- A batched stochastic fixture still folds to `SharedGreedy_v1`.
- No digest of record moves. The lint suite passes, and `tests/check` and `tests/pipeline` equal the base-failure set.

**Timing:** a PR on main `ac412eb8`, stacked on V (#309) if V hasn't landed, with its head sent to me and to the research coordinator as urgent. #101's fifth try needs it on main, with the check passed, by about **21:00Z**, and it can start until about 21:50Z.
