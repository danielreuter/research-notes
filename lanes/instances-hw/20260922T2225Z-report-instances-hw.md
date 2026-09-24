---
id: r21-silicon/instances-hw/20260922T2225Z-report-instances-hw
campaign: r21-silicon
lane: instances-hw
kind: report
status: closed
repo: verity-main@fc12fac (5 commits on 4987a47; not merged, not pushed)
branch: lane/instances-hw
worktree: /Users/danielreuter/projects/verity-main-wt/instances-hw
machines: vy-ihw-a100 (A100-SXM4-80GB x2 pods), vy-ihw-4090 (RTX 4090), vy-ihw-h100 (H100 NVL) -- all terminated
snapshot: art:ee5c86d8cad4c22552362c6e7700c259ba4834069e9c0b8dfee4e942993ebe14 (frozen-instances-hw-v1, PRESERVED)
---

# instances-hw — the frozen instance sets, replayed word-for-word on the anchor silicon

Every target's frozen benchmark set (the exact inputs its proofs are benchmarked on, with the model-recorded expected words) was
executed on the target's anchor GPU with the pinned instruction, exactly as a real GEMM runs it: the K-steps chained on the tensor
core with the hardware's own FP32 accumulator carried between `mma` / `wgmma` calls in the target's program order, the target's
epilogue applied to the last word, and **every intermediate accumulator and every final word compared** with the set's expected
words.  Result: **0 mismatches on every honest tier (1,192,000 words on four devices); 52/52 negatives detected.**  No model, no
instance set, no fixture was touched.

## Harness

`tools/tc_probe/instances_hw.py --instances DATASET/TIER [--root DIR] [--range LO:HI | --only-ids ...] [--repeat N] [--sass-check] --out DIR`
(sibling of `tc_probe.py`, drives its kernels / instruction table / SASS check / result envelope; store tool `instances_hw`, declared in
`tools/tc_probe/tool.py::INSTANCES_HW`, registered in `tools_registry.py`).

- `bench-instances/v1/{vu-k1536,tu-k16,vu-k1536-neg}`: loaded from the built arrays (`python -m verity_numerical.bench.instances build`
  on the pod, 28.9 s: weights fetched from Qwen/Qwen2.5-1.5B@8faed761d45a, 24/24 seed rows bitwise equal, 14/14 arrays digest-equal to
  the pinned `fixtures/bench-instances/v1/manifest.json`); the harness re-checks every array's sha256 against the manifest before
  loading and records the manifest's own sha256 (`059103cf9bd55ee8…`) as `manifest_sha256`.
- `fp8-ada-synthetic/vu-k1536-fp8`, `bench-instances-bf16-hopper/v1/vu-k1536-bf16-hopper`, `bench-instances-fp8-hopper/v1/vu-k1536-fp8-hopper`:
  seeded synthetic sets regenerated from their recipes (`rng = default_rng([20260922, i])`, `a` then `b` = 1536 operand words,
  accumulators recorded by `tc_dot(model)` chained from +0): the fp8-ada recipe of `backends.direct.ligero.fp8.chain.instances_fp8`,
  the Hopper recipes of `backends.direct.ligero.relchain.instances` / `relations.py` as landed on `lane/b-hopper` at dc3c141
  (`random_finite_bf16`: exponent fields [96, 160), 1/10 signed zeros, 1/10 subnormals; `random_finite_operands`: uniform finite E4M3).
  `manifest_sha256` = `instances_digest` = `sha256("<relation> synthetic|seed=20260922|n=4096|K=1536")`, as the chain benches record it.
- Tiles: one instance per tile at `(r % M, (r // M) % 8)`, the rest of the tile zero; every other output word must be +0
  (`other_positions_nonzero`, excluding tiles with a non-finite operand, where NaN·0 poisons the row).  Step s of every instance is one
  launch; the hardware D of step s is the C of step s+1, so a mismatch propagates like the real chain and is located at its first step.
- Domain check (`verity.verification.target`, D8): non-finite operand words or a non-finite hardware accumulator before the last step
  → out of domain.  Honest tiers must have none; the negative tier's `reject` rows must trip it.
- `--repeat 2` on every run: the whole replay twice, words differing between repetitions counted (0 everywhere).
- Meta contract (`result.json.tc_evidence`): `{instruction, target, instances_dataset, instances_tier, range, manifest_sha256,
  elements, mismatches, first_mismatch | null, per_step_checked, sass, device, driver, cuda, model_agrees, …}`.  `mismatches` = hardware
  words ≠ the reference word (the model-recorded word; on `vu-k1536-neg` the CORRECT word of a claimed-wrong row);
  `negative.claimed_words_contradicted` = hardware words ≠ the CLAIMED words; `negative.undetected` = that tier's failure count.

Tests: `tests/test_instances_hw.py` (11 pass + 3 skips on the laptop): the loaders, chaining, per-step compare, epilogue, domain check
and negative verdicts run through a model-backed fake probe (`tc_dot_total` for BF16, `tc_dot` for FP8, word per tile position); the
recipe-vs-`ligero` cases `importorskip` torch / the relation registry; the device case (nvcc + GPU) ran on the A100 (neg tier on
`sm80`, 4/4 detected) and the H100 (Hopper BF16 set on `sm90`, 4×97 words, 0 mismatches).  `uv run -q pytest packages/verity tests
tools/research/tests -q` at fc12fac: 524 passed, 4 skipped (38 s); `rg -l '^<<<<<<< '` empty; no `.md` added to the repo.

## Runs (all `research run --on … --tool instances_hw --require-result`, fetched `--all`, published, PRESERVED on s3://verity-dev)

| pair | device (driver) | instruction / SASS per tile kernel | set / tier [range] | words compared | mismatches | run → tc-evidence artifact |
|---|---|---|---|---|---|---|
| FIRST | A100-SXM4-80GB (580.126.16), sm_80, nvcc 12.4.131 | `sm80.mma.m16n8k16.bf16` / 1× HMMA.16816.F32.BF16 | `bench-instances/v1` `vu-k1536` [0,4096) | **397,312** = 389,120 intermediate acc (steps 0–94) + 4,096 final acc (step 95) + 4,096 epilogue words (`f32_to_bf16`); ×2 repeats | **0** (64 final saturations = D8, in domain) | r20260922-214538-6a58 → art:046ea721… |
| FIRST | A100 (as above) | same | `tu-k16` [0,4096) | 4,096 (`out` words, arbitrary finite c) ×2 | **0** (97 saturating transitions, in domain) | r20260922-214533-2273 → art:ca85c40c… |
| FIRST negative | A100-SXM4-80GB (580.126.20, 2nd pod) | same | `vu-k1536-neg` [0,52) | 52 final words ×2 | **0** vs the correct words; **52/52 detected**: 44 `wrong` rows contradicted (hardware ≠ claimed) and all 44 reproduced the correct word; 8 `reject` rows out of domain (4 non-finite operand, 4 saturate before the last step); `claimed_words_contradicted` 45 | r20260922-221913-a894 → art:3700d419… (supersedes r20260922-214330-134b → art:79009cfa…, same detections, older `mismatches` semantics; `note` label added) |
| FP8_ADA_MMA | RTX 4090 (570.195.03), sm_89 | `sm89.mma.m16n8k32.e4m3` / 1× QMMA.16832.F32.E4M3.E4M3 | fp8-ada synthetic `vu-k1536-fp8` [0,4096), digest `e66ff0f21c8e67d1…` = `instances_digest(4096)` | **196,608** = 192,512 intermediate + 4,096 final (bare FP32 word, no epilogue) ×2 | **0** | r20260922-214711-e399 → art:920b2bbd… |
| BF16_HOPPER (b-hopper) | H100 NVL (580.159.04), sm_90 (`sm_90a`) | `sm90.mma.m16n8k16.bf16` / 1× HMMA.16816.F32.BF16 | `bench-instances-bf16-hopper/v1` `vu-k1536-bf16-hopper` [0,4096), digest `2a5babca16e82727…` | **397,312** (as FIRST: 95 intermediate + final + `f32_to_bf16`) ×2 | **0** | r20260922-215705-4ee8 → art:3b754cca… |
| FP8_HOPPER_WGMMA (b-hopper) | H100 NVL (as above) | `sm90.wgmma.m64n8k32.e4m3` / 1× QGMMA.64x8x32.F32.E4M3.E4M3 | `bench-instances-fp8-hopper/v1` `vu-k1536-fp8-hopper` [0,4096), digest `0ff750026b8d8df0…` | **196,608** ×2 | **0** | r20260922-215709-9665 → art:61beb06a… |

Every run: `layout_check passed`, `other_positions_nonzero 0`, `words_differing_between_runs 0`, `first_mismatch null`,
`per_step_checked true` on the chained tiers (false on `tu-k16` = one step, and on the negative tier whose arrays carry no per-step
accumulators), `validation.status passed`.  Full artifact ids:

- art:046ea72161381160ef2b3f6ececb86982488c683f9aab87b9284b254b15bea24 (vu-k1536, A100)
- art:ca85c40c6101ae2b5ea388d91045830466f90353af635867c36c3a20bd8796ae (tu-k16, A100)
- art:3700d419426fb4d0ff3a59488d5e58b0aba099160a9ddaa6b6d1cd924bb27873 (vu-k1536-neg, A100) — art:79009cfae848322084cee98624bea4e4bd5d73ddaea4536cf9494af657361744 is the first capture of the same tier (labelled `mismatches=45` under the earlier semantics; `note` label points here)
- art:920b2bbdab4679a761d53411f43692a5318f50a529827cfe9b01ac42745f7b82 (vu-k1536-fp8, RTX 4090)
- art:3b754cca32fd1612396c48d84e7193eaad357d69fc6c0ecd16f6c20cc69c5f5d (vu-k1536-bf16-hopper, H100 NVL)
- art:61beb06a9c656f3b76f581634f34038f1dfeeeea95509e7a7cdf25f85ec1d9f1 (vu-k1536-fp8-hopper, H100 NVL)
- snapshot `frozen-instances-hw-v1` = art:ee5c86d8cad4c22552362c6e7700c259ba4834069e9c0b8dfee4e942993ebe14 (the six above; PRESERVED, `research data verify` ok)

Labels on each (`--by instances-hw --ref <run>`): `family=frozen-instances`, `instruction=<id>`, `target=<name>`,
`instances_dataset=<…>`, `instances_tier=<…>`, `mismatches=<int>`, `model_agrees=true`, `hardware=a100|rtx4090|h100`, plus `model=<pipeline>`.
The FP8 Ada `instances_dataset` is the literal string the ligero chain bench records (`fp8-ada synthetic (uniform finite E4M3 bytes,
model-recorded accumulators)`), so the trust lane's join on that key matches the bench rows.

## What `hardware/` already held, and how today's run relates

`fixtures/bench-instances/v1/hardware/r20260922-022913-d462.probe_results.json` (+ `manifest.json` `hardware.runs[0]`) is a full
capture of the BF16 set — all 4,096 `vu-k1536` chains (393,216 accumulator words + 4,096 `y`) and all 4,096 `tu-k16` transitions,
0 mismatches — **but on an RTX 4090 (sm_89, Ada), not the FIRST anchor**; the manifest itself says "Not an sm_80 confirmation".  It does
not cover `vu-k1536-neg`.  Today's A100 run is the first sm_80 confirmation.  The two agree word-for-word: the array digests of
`vu-k1536` / `tu-k16` in that capture's manifest (`f2b7cd4c…`, commit e4d2ede) equal today's (`059103cf…`; the manifest changed only by
recording the 4090 run), both captures matched every one of those expected words, hence A100 words = 4090 words = model words for all
397,312 + 4,096 of them.  (The 4090 capture did not keep the hardware words themselves; today's `capture_vu-k1536.npz` does.)

## Observations (none is a discrepancy)

1. **Ampere ≠ Hopper on the negative tier, as the pinned models say.**  Run off-instruction on the H100 (`sm90.mma.m16n8k16.bf16`, pinned
   pipeline `hopper_bf16_m16n8k16` (16,)/26/−133), the FIRST negative rows 0, 20, 44, 48 were all detected, but row 20
   (`single-group-16` on an `acc-swing` corner) did not reproduce the *Ampere* correct word — expected, since the Ampere correct word is
   not Hopper's word; the device test now runs the Hopper set on `sm_90`.  The 4090 capture shows Ada's HMMA agrees with Ampere on
   every one of these words.
2. **Reject row 45's "IEEE word" is not the IEEE word.**  `w[780] = −inf` with `x[780] = 0xbe7b` (negative): IEEE gives +inf, the row
   claims −inf (0xff80); the A100 (and `tc_dot_total`) give +inf.  Immaterial (`correct_y` is null; the row is rejected by the domain
   check as designed) — a nit in the generator's note for `nonfinite-operand` rows.
3. The two A100 pods had different drivers (580.126.16 / 580.126.20) and identical words.
4. The spec named an A100 SXM4 80GB / RTX 4090 / H100: the first two were exact; no H100 SXM (HBM3) instance was available on RunPod at
   21:53Z in either cloud, so the Hopper pairs ran on an **H100 NVL** (sm_90, 94 GB) — same SM 9.0 tensor cores, `sm_90a` build, single
   QGMMA / HMMA per tile kernel.

## Pods

| pod | device | window (UTC) | ≈ min | rate | ≈ $ |
|---|---|---|---|---|---|
| vy-ihw-a100 (8dt3d6tfnwmehf) | A100-SXM4-80GB SECURE US-MD-1 | 21:26 → 21:55 | 29 | $1.59/h | 0.77 |
| vy-ihw-4090 (gdlyh2odyote2i) | RTX 4090 SECURE | 21:26 → 21:55 | 29 | $0.74/h | 0.35 |
| vy-ihw-h100 (kdtbep3vrhn8zt) | H100 NVL SECURE | 21:52 → 22:02 | 10 | $3.19/h | 0.53 |
| vy-ihw-a100 (y2paz7dudkaf2k) | A100-SXM4-80GB SECURE | 22:15 → 22:21 | 6 | $1.59/h | 0.16 |

≈ 74 pod-minutes, ≈ $1.81; peak concurrent lane rate $5.52/h (all `vy-*` pods ≈ $15/h at the time, ceiling $50/h).  All four
terminated; `~/.research/machines.toml` entries annotated.

## Not done / follow-ups

- `fixtures/bench-instances/v1/manifest.json` `hardware.runs` and `hardware/` were **not** updated with today's A100 capture (the spec
  said not to touch the instance set; recording would also change `manifest_sha256`).  If wanted: `instances.record_hardware` with
  r20260922-214538-6a58 / -214533-2273 / -221913-a894 and copy the three `probe_results.json` into `hardware/`.
- `research data push` from this worktree (research @ 4987a47) fails against the shared index (`replicas` gained a `verified` column on
  main 76587f4); the pushes/labels/snapshot were made from `~/projects/verity-main-wt/main`.  Rebase or merge resolves it.
- The Hopper sets were replayed from the recipes at `lane/b-hopper` dc3c141; if that lane changes `random_finite_bf16`, the seed or the
  digest string, `bf16_random_finite_operands` / `Synthetic` in `instances_hw.py` must follow (the `importorskip`'d test
  `test_hopper_recipes_match_the_relation_registry` catches it once the registry is in the tree).
