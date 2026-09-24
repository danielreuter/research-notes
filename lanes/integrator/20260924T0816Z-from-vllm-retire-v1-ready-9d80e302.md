---
lane: vllm-retire-v1
to: integrator
kind: ready
branch: lane/vllm-retire-v1
commit: 9d80e302
baseline: 815b837c
---
# retire-v1 ready @ 9d80e302

Merge `lane/vllm-retire-v1` onto your staging tip (`38122d1f`). The v1 manifest engine and non-product entry points are deleted; census is at a fixed point.

## Counts (integrations/vllm .py files, git cat-file)

| | files | lines |
|---|---:|---:|
| baseline `815b837c` | 652 | 209,414 |
| tip `9d80e302` | 632 | 199,400 |
| delta | −20 | −10,014 |

By-name allowlist: 293 → 234. Census `plan: delete {}`. Lints 7/7 (by-name uncovered 0, stale 0).

## Regression harness (T0+T1, oracle expected)

Staging records: cpu3 `/workspace/p6_rec/fB`, cpu2 `/workspace/p6_rec/fA` @ `815b837c`.
Tip records: cpu3 `/workspace/rv1/hrec/{fB1..fB5,fB3r,fB4r,fB5r}` + cpu2 `/workspace/rv1/hrec/fA` @ `9d80e302`.

`hcmp.py` (skip `program_digest`): **fA** 12 identical + 2 bookkeeping-only / 14 common; **fB** 50 identical + 4 bookkeeping-only / 57 common. Three `DIFF` lines, all `replay_partition` on rows #57/#67/#68 with `matched expected → decision retire-v1 (accepted)` — the only sanctioned differences.

### retire-v1 decisions (fixtures.toml)

1. **r57** gemma2-2b b8 `replay_partition`: 4150 `Bf16MulScalarTensor_v1` rows evaluable under v2 rule (vus 651982→656132).
2. **r67** olmoe b32 mixed `replay_partition`: MoeSum strata keys `moe/L<k>` → `model.layers.<k>.mlp.experts` (2416 keys renamed, counts equal).
3. **r68** olmoe b32 mixed-arrivals `replay_partition`: same rename (2016 keys).

Probed: staging code with `addresses.rule` forced to `v2-query` == tip actual for each row.

Rebaseline write: `expected/{gemma2-2b,olmoe-r67,olmoe-r68}.json` `replay_partition` contracts updated (`release: retire-v1`).

## Full suite (staging vs tip, -n 8)

Staging `815b837c`: 3697 pass / 318 skip / 31 F / 11 E.
Tip `a2e16920` (pre-decisions tree, suite code unchanged): 3461 pass / 313 skip / 36 F / 11 E.
Per-test (`jcmp.py`): 245 v1 tests deleted, 14 new pass, 0 fixed regressions. Named flakes (pre-existing, not on acceptance path): `test_lifted_tiny::test_specified_list_is_closed`, `fa2_commit::test_transient_storage_is_released`, `test_row_pod_cancel_forwarding::test_sigint_is_forwarded_the_same_way`.

Converted test files @ tip: 212 pass / 173 skip / 2 F (both staging-known).

## v1 survivor (no acquisition plan)

**TP rank committers** (`verity_capture/tp/worker.py` → `commit_delta.make_committer`): select modules by `native_host.ACQUIRE_CLASSES` class tables. Kept intentionally; report to coordinator.

Also left without v2 replacement (documented in state): `commit_verdict` reads manifest `cross_check` (v1-only field); `test_sampled_replay_moe_tp_sum_copy.py` deleted (args-less v1-vocabulary fixture).

## Commits since `815b837c` (high level)

v1 engine deletion (`required_manifest`, `required_values`, ACQUIRE_ENGINE switch, v1 addressing paths), harness v2-only, replay test conversion, GEN-lane pod runner cascade, TP-08d ProgramIndex test deletion, three `retire-v1` decision labels + rebaseline.
