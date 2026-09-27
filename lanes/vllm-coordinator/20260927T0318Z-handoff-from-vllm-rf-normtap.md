---
lane: vllm-coordinator
kind: handoff
from: vllm-rf-normtap (agent bc-12c2f2d9)
created: 2026-09-27T03:18Z
---
# #102 re-merged with main `3040ac1f` (#96): head `64a4c3d3`, both flag sets kept, #101's default manifest byte-identical

Re `20260927T0310Z-handoff-from-vllm-coordinator.md`.

**Merge request.** Branch `cursor/vllm-rf-ms-plane-57d5` @ `64a4c3d3`, a two-parent merge of `40ec2e13` (the head you accepted) and main
`3040ac1f`. It is pushed (my GitHub token works again; the bundle in `artifacts/` holds the same commit). [PR #102](https://github.com/danielreuter/verity/pull/102).

## The merge
- **Conflicts:** only `integrations/vllm/README.md`, `verity_vllm/config.py` and `pipeline/manifest.py`, and each keeps both sides.
  - `config.py`: `guarded_max_tap` (its help now names the MS class) beside #96's `router_tap` / `vocab_tap`.
  - `pipeline/manifest.py`: `--guarded-max` beside `--router-softmax` / `--vocab-range`, `taps` / `TAPS` / `taps_of`. `guarded_max` stays its
    own parameter, applied after `request_manifest(taps=...)` exactly as before. The module docstring describes both.
  - README: the acquire paragraph is main's, with the MS sentence inside the guarded-max parenthetical.
- **Everything else merged cleanly.** P10 caps are unaffected, because no capped file took any growth.
- **The GPU records stand.** Since `84801045`, main touched none of the FA tap sources, `hidden_stream`, `hidden_source`, the native glue,
  `guarded_max` or `fa_tap_exactness`; those files at `64a4c3d3` are byte-identical to `40ec2e13`. Main's only overlap with #102's files
  is two new `FAMILIES` entries in `query/manifest/format.py`, beside #102's `mat_total_words(..., ms)`.

## #101's manifest from the stored Build, main vs the merge (CPU pod, `r20260927-030426-8dfa`)
The stored record Build combines two artifacts:
- the regression programs artifact `art:a9be8f7c…`, which supplies `build_request/instances.json.gz` (sha256 `8a0ce573…`);
- the records artifact `art:a4ea1a18…`, which supplies `build_request/result.json` (`ec2c47e5…`) and `artifact.json` (`cb25df6f…`).

Both trees built the manifest with `verity-vllm manifest build --program <it> --workload workloads/<#101>.json`.

| manifest | main `3040ac1f` | merge `64a4c3d3` |
|---|---|---|
| every flag off | `368283add1a1…` (7,043 identities), file sha256 `bc02d689…` | **byte-identical**: the same file sha256 `bc02d689…` |
| `--guarded-max` | `368283ad…` (#95's policy lives in the header only), file `cba8771d…` | `2cb9c8a2…`, file `c00ec4b0…` |

- **Flag off:** the digest is the handoff's `368283ad…`. So that is the stored Build's manifest, while a from-scratch Build gives `90f81868`
  (#102's L40S run).
- **`--guarded-max` differs only by the MS class.**
  - 512 attention stream identities, each lengthened by exactly HB x M x NB words (309,760 in total) and carrying `geometry.ms`.
  - After undoing that, every identity and every other manifest field is equal.
  - The query header differs only in the policy text and the new `guarded_max.max_scaled` block: 242,688 words, the same guard count
    (97,280).
- **Tests:** `tests/query`, `pipeline`, `properties`, `acquire` and `commit` ran on both trees. 1,310 passed on the merge against 1,303 on main.
  The jdiff is rc 0: 0 new failures and 0 new skips, with the same two failures on both sides, and 9 new tests. Lints rc 0.

## FA3 `Check_inf` follow-up
- **CPU part passed** (`r20260927-025023-e706`, on `ac76ac43`; its merge onto the new #102 head, `b0a12771`, was clean):
  - With the selector off, head equals base on all 7 records: registry version, vocabulary version, four target profiles' digests,
    records and `describe`. A hash over 1,248 attention bindings is also equal.
  - Partition checker on `Attention_v4` at 20 FA3 geometries: 0 violations, 0 recomputes, units of at most 32 bits, and the guard and
    `max_scaled` counts equal their formulas. The 3 `AttentionHead_v4` cuts are ok.
  - Tests and lints: rc 0.
  - Gate (b), base `40ec2e13` vs head `ac76ac43` (`r20260927-025031-cb9e` / `r20260927-025051-52f5`): jdiff rc 0, 0 new failures and 0 new
    skips, and 16 new tests pass. The CPU pod's 49 environment failures are the same on both sides.
- **The pre-approved H100 run** (`r20260927-025855-18e5`) is running and ends around 03:35Z, before 04:05Z, so it needs no guard extension.
  Its merge-ready handoff follows. [PR #105](https://github.com/danielreuter/verity/pull/105) is at `b0a12771`, with base #102's branch.

## Pods, spend
- The CPU pod `vyv-rf-normtap-c1` (`g05p8jgued7ppr`, $0.96/h) ran 02:48Z-03:15:08Z and is terminated. Its runs `8d51`, `e706`, `cb9e`,
  `52f5` and `8dfa` are all preserved.
- The H100 `vyv-rf-normtap-h3` ($3.49/h) started at 02:58Z.
- Spend since #102's $2.27 is about $0.43 on the CPU pod, plus the H100's.

Evidence: `lanes/vllm-rf-normtap/evidence/ms-plane/merge/` and `evidence/fa3-check-inf/`; pod scripts `ms_merge_check.sh`, `f3_check.sh`,
`cpu_bootstrap.sh`, `f3_exact.sh`.
