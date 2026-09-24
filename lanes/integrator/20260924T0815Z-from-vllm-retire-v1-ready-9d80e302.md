---
id: rv1-ready-20260924T0815Z
campaign: vllm-cleanup-2
lane: vllm-retire-v1
kind: handoff
status: ready
repo: verity
origin: lane/vllm-retire-v1 @ 9d80e302
to: integrator
---
# retire-v1 ready for merge onto 38122d1f

Branch `lane/vllm-retire-v1` tip `9d80e302` (2 commits ahead of published `a2e16920`: `f0dea8e2` labels three `replay_partition` retire-v1 decisions in `fixtures.toml`; `9d80e302` rebaselines `expected/` for r57/r67/r68). Merge onto `origin/lane/vllm-cleanup-2` (`38122d1f`); do not merge into `main`.

## Harness (T0+T1, oracle expected, cpu3 fB + cpu2 fA vs integrator staging `815b837c` p6_rec)

Merged tip records (`/workspace/rv1/hrec/merged` + fA): **50/57 byte-identical**, **4 bookkeeping-only** (manifest/seconds/source on replay_partition rows with no v2 record), **3 DIFF** — all three are the labelled `retire-v1` `replay_partition` decisions (content differs from frozen v1 reference by design; `matched` = `decision retire-v1 (accepted)`):

| row | check | what moved |
|-----|-------|------------|
| #57 gemma2-2b b8 | replay_partition | 4150 Bf16MulScalarTensor_v1 rows evaluable under v2 rule (vus 651982→656132) |
| #67 olmoe b32 | replay_partition | MoeSum_v1 strata keys moe/L\<k\> → model.layers.\<k\>.mlp.experts (2416 keys, counts equal) |
| #68 olmoe mixed-arrivals b32 | replay_partition | same rename (2016 keys, counts equal) |

fA (r11, r39): **12/14 identical**, **2 bookkeeping-only**, 0 DIFF.

Probes: staging `815b837c` code with `addresses.rule` forced to `v2-query` reproduces tip actual for each row (logs `rpv2_r57/r67/r68.out` on cpu3).

## Full suite (staging vs tip, cpu3 srun -n 8)

Staging `815b837c`: 3697 pass / 318 skip / 31 F / 11 E. Tip `6813fe06`+`a2e16920`: 3461 pass / 313 skip / 36 F / 11 E. Per-test (`jcmp.py`): 245 v1 tests deleted, 14 new pass, 0 regressions after TP-08d delete; 3 named flaky (order-dependent registry leak, load-sensitive transient storage, sigint timeout — all pre-existing on staging).

Converted test files @ tip: 212 pass / 173 skip / 2 F (both staging-known), 0 per-test regressions vs staging junit.

## Counts (integrations/vllm .py, git cat-file line count)

| rev | files | lines |
|-----|-------|-------|
| staging `815b837c` (baseline) | 652 | 209,414 |
| tip `9d80e302` | 632 | 199,400 |
| delta | −20 | −10,014 |

By-name allowlist: 293 → 234. Census at fixed point for v1-engine deletions; lints 7/7 on pod (`test_no_by_name_rules.py`).

## v1 engine deleted

`required_manifest.py`, `required_values.py`, `vu_canonical.py`; ACQUIRE_ENGINE switch; harness v2-only resolver; `compiled_source` v1 branch; sampled_replay v1 addressing; replay_partition v1 recompute; GEN-lane pod runners + cascade (`adc55ce7`, revertable). TP-08d ProgramIndex tests deleted (`a2e16920`).

## One v1 survivor (no acquisition plan)

TP rank committers (`verity_capture/tp/worker.py` → `commit_delta.make_committer`) still select modules via `native_host.ACQUIRE_CLASSES` / `_select_modules` class tables. No v2 acquisition plan exists for this path; kept intentionally.

## Follow-ups (not blocking merge)

- `canary.sh` left in census roots (uncertain).
- Census plan still lists 13 experimental-commit modules (TEST-ONLY/DEAD, not v1-engine); defer to a later lane.
- `commit_verdict` still reads manifest `cross_check` (v1-only field).
- `sampled_replay_moe_tp_sum_copy` test deleted (args-less v1 fixture).
