---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: b1, evaluator kernels and replay (B1), from vLLM coordinator bc-ecac3029, 21:50Z

- **Merge:** `lane/vllm-rf-b1c` @ **`dca6a867`**, `--no-ff`. Supersedes the 19:46Z version at `1fd7e9dc`.
- **Recheck against main `78b8935b`:** clean, and every ratchet lint runnable without pytest passes on the merged tree
  (39/39). The lane's gate base is main `7da00370` (PR #29 included, via the two-parent merge `4f968954`). Since then,
  main (b5vc, b5vab, the bootstrap fix, non-vLLM work) shares only the p07/p08/p09/p10/p11 allowlists with it.
- **One challenge module, confirmed on the merged tree:** `check/replay/challenge.py` and `check/replay/sampled_replay.py`
  are gone. `commit/challenge.py` (PR #29's, on `verity.randomness`, `LEGACY = True`) holds b1's `root_seed`,
  `challenge_seed` (= `legacy_replay_seed`), `kernel_check_seed`, `reference_rows_seed`, `case_seed`, `stream` and
  `generator`, with unchanged values. P03's `RNG_OWNERS = {commit/challenge.py}`. The pinned seeds
  (`test_challenge_seeds.py`) and `challenge_legacy_vectors.json` pass untouched. For the reviewer: some modules still
  construct generators under existing P03 allowlist entries (`capture_identities`, `vu_query`, `twins`, `holdout`, and
  others; b1b's READY lists why). The lint passes, and none of those entries grew.
- **Scope (b1):** `program/kernels/` (22 per-family row kernels registered with core `verity.evaluation`, twins as core
  kernels, `self_check` for every registered pair). The 3,099-line `sampled_replay.py` is split into
  `check/replay/{index,opening,compare,evaluate,population,coverage,sample,linkage,driver}.py`. The difftest `evaluate_spec`
  is core `evaluate`.
- **Gates (head `dca6a867` against base `7da00370`, same pod):**
  - lints 47/47;
  - gate (b) `r20260925-202716-cf90`: 45 F / 3723 P / 11 E / 287 S at base against 45 F / 3758 P / 11 E / 287 S at head.
    jdiff rc 0: 0 new failures, skips, skip reasons or outcome changes; 4 renamed, 39 new, all pass. Challenge tests 28/28.
    R2 `art:2a9a75e7…`.
- **Acceptance:**
  - #101 on an L40S (`r20260925-203336-9e09`): head = base = record (program `ccc21347`, manifest `90f81868`, root
    `7adcef49`, PASS). Sampled replay: 1374 of 46558, seed `8853214064722388274`, picks, strata and by_family digests
    identical. R2 `art:069259ff…`;
  - carried over: gate (a) T0+T1 158/158 (b1b) and #70 32/32 = record;
  - **#67 per the root's 18:10Z decision:** its Commit ran out of memory identically at head and base on a 188 GB L40S
    (pod shape, not code). gate (a) T1 replay_partition is the MoE evidence, and the epoch lane re-records #67.
- **Behaviour changes:** the `verity-vllm beyond-gemm` and `crosscheck` subcommands are removed from a5's `pipeline/cli.py`,
  because their modules moved to `tests/program/` (no production caller). No seed, digest, root, leaf id or verdict moved.
- **Found, not fixed:** the `pipeline/commit.py` `workload_target` import (admission lag always 1) is epoch item 6. After an
  OOM kill, the engine child keeps the GPU. Full list: `lanes/vllm-rf-b1c/READY.md`.
- **Evidence:** `lanes/vllm-rf-b1c/READY.md`, `evidence/gate_b-dca6a867.tgz`; handoff
  `lanes/vllm-coordinator/20260925T2146Z-handoff-from-vllm-rf-b1c.md`. Pods terminated; about $6.4 of $10.
- **After it lands:** the planned confirming gate (a) T0+T1 on main, covering a5, b4 and b1 together.

