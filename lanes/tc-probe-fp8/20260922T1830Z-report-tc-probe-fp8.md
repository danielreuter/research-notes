---
id: r21-silicon/tc-probe-fp8/20260922T1830Z-report-tc-probe-fp8
campaign: r21-silicon
lane: tc-probe-fp8
kind: report
status: closed
repo: verity-main@e028f9efbc5dcfff1768426b6bcb12ef95ab8ce2
branch: lane/tc-probe-fp8
worktree: /Users/danielreuter/projects/verity-main-wt/tc-probe-fp8
machine: vy-sp1 (RunPod RTX 4090, sm_89, driver 580.159.04, nvcc 12.4.131)
---

# tc-probe-fp8 — instruction-parametrized tensor-core probe, first FP8 captures (Ada)

Branch `lane/tc-probe-fp8`, final SHA `e028f9e` (5 commits on `main` = a0f0eb9; not pushed). Files owned and changed:
`tools/tc_probe/tc_probe.py`, `tools/tc_probe/mma_tiles.cu`, new `tools/tc_probe/wgmma_tiles.cu`, new `tools/tc_probe/tiles_common.cuh`.
Nothing under `packages/verity/**`, `tools/research/**`, `backends/**` touched; only the listed `verity.ml.tc.silicon` names are imported.

## Instruction table (as implemented; `--arch` derived, overridable)

| id | nvcc arch | TU / kernel (`extern "C"`; device kernel `<kernel>_kernel`) | K (M) | SASS per tile kernel | model(s) compared |
|---|---|---|---|---|---|
| `sm80.mma.m16n8k16.bf16` | sm_80 | mma_tiles.cu / `mma_bf16_m16n8k16_tiles` | 16 (16) | 1× HMMA.16816.F32.BF16 | `ampere_bf16_m16n8k16` (pinned) |
| `sm89.mma.m16n8k16.bf16` | sm_89 | mma_tiles.cu / `mma_bf16_m16n8k16_tiles` | 16 (16) | 1× HMMA.16816.F32.BF16 | `ada_bf16_m16n8k16` (pinned) |
| `sm90.mma.m16n8k16.bf16` | sm_90a | mma_tiles.cu / `mma_bf16_m16n8k16_tiles` | 16 (16) | 1× HMMA.16816.F32.BF16 | `hopper_bf16_m16n8k16` (pinned) |
| `sm89.mma.m16n8k32.e4m3` | sm_89 | mma_tiles.cu / `mma_e4m3_m16n8k32_tiles` | 32 (16) | 1× QMMA.16832.F32.E4M3.E4M3 | `ada_e4m3_m16n8k32` (pinned) |
| `sm89.mma.m16n8k32.e5m2` | sm_89 | mma_tiles.cu / `mma_e5m2_m16n8k32_tiles` | 32 (16) | 1× QMMA.16832.F32.E5M2.E5M2 | HYPOTHESIS `ada_e4m3_m16n8k32` + local `_e5m2_product` |
| `sm90.mma.m16n8k32.e4m3` | sm_90a | mma_tiles.cu / `mma_e4m3_m16n8k32_tiles` | 32 (16) | **2× HMMA.16816.F32** (+ F2FP, FADD) | HYPOTHESES `hopper_e4m3_wgmma_k32`, `ada_e4m3_m16n8k32`, `hopper_bf16_m16n8k16/2xHMMA.16816.F32+FADD` |
| `sm90.mma.m16n8k32.e5m2` | sm_90a | mma_tiles.cu / `mma_e5m2_m16n8k32_tiles` | 32 (16) | **2× HMMA.16816.F32** (+ F2FP, FADD) | the same three with `_e5m2_product` |
| `sm90.wgmma.m64n8k32.e4m3` | sm_90a | wgmma_tiles.cu / `wgmma_e4m3_m64n8k32_tiles` | 32 (64) | 1× QGMMA.64x8x32.F32.E4M3.E4M3 | `hopper_e4m3_wgmma_k32` (pinned) |
| `sm90.wgmma.m64n8k32.e5m2` | sm_90a | wgmma_tiles.cu / `wgmma_e5m2_m64n8k32_tiles` | 32 (64) | 1× QGMMA.64x8x32.F32.E5M2.E5M2 | HYPOTHESIS `hopper_e4m3_wgmma_k32` + `_e5m2_product` |

Pipelines (from `silicon.py`, unchanged): `ada_bf16_m16n8k16` groups (8,8) width 25 zero_exp −132; `hopper_bf16_m16n8k16` (16,) 26 −133;
`ada_e4m3_m16n8k32` (16,16) 14 −139; `hopper_e4m3_wgmma_k32` (32,) 14 −139. `_e5m2_product` is a local HYPOTHESIS (3×3-bit
significands, exponent bias 15, subnormals at exponent −14; non-finite exponent field raises). wgmma path: one warpgroup per tile, A
from registers (PTX m64nNk32 8-bit A fragment), B through a K-major no-swizzle shared-memory descriptor (LBO/SBO 128/256 bytes; the
layout check tries the swapped pair and records which passed), `wgmma.fence` / `commit_group` / `wait_group 0`, scale-d predicate.

## Runs on vy-sp1 (all fetched with `research fetch RUN --all`)

Every run: `research run --on vy-sp1 --project verity --source <worktree> --stage <stage> --require-result -- bash -c '<cmd>'`, the
command being the WP1 one (`PYTHONPATH=packages/verity/src:backends/numerical/python`, `/usr/local/cuda/bin` on PATH,
`/root/.local/bin/uv run --no-project --with numpy --python 3.12 python tools/tc_probe/tc_probe.py ...`). Seed 20260902 everywhere.

| step | run id | source SHA | `research inspect` one-liner | headline |
|---|---|---|---|---|
| (a) BF16 golden regression | `r20260922-174939-affc` | 9d53f10 | done rc=0 SUCCESS, validated **passed**, wall 2.3 s, $0.0005 | `sm89.mma.m16n8k16.bf16` `--replay-golden ada_bf16_m16n8k16.json --sass-check`: 360/360 records, **0 mismatches**, other_positions_nonzero 0; layout check 8192 elements passed; SASS 1× HMMA.16816.F32.BF16 |
| (b) sm89 e4m3 sweep | `r20260922-175246-0477` | 9d53f10 | done rc=0 SUCCESS, validated **passed**, wall 130.6 s, $0.0268 | `--sweep --n-random 100000 --replay-golden ada_e4m3_m16n8k32.json --sass-check`: **25,040,128 elements, 0 mismatches** vs `ada_e4m3_m16n8k32` (13 families, 12 asserted); e4m3 golden 360/360, 0 mismatches; SASS 1× QMMA.16832.F32.E4M3.E4M3 |
| (c) sm89 e5m2 sweep | `r20260922-175732-172a` | 9d53f10 | done rc=0 SUCCESS, validated **not_run** (hypothesis only), wall 132.2 s, $0.0272 | `--sweep --n-random 100000 --sass-check`: **25,040,128 elements, 0 mismatches** vs HYPOTHESIS `ada_e4m3_m16n8k32+e5m2_product` (model_agrees true); SASS 1× QMMA.16832.F32.E5M2.E5M2 |
| (d) FP8-specific families, e4m3 | `r20260922-182539-ea37` (supersedes `r20260922-180139-bccf`) | e028f9e | done rc=0 SUCCESS, validated **passed**, wall 12.7 s, $0.0026 | `--families zero_products_nonzero_acc,acc_only_lsb_walk,specials,adder_width_cancellation`: 141,824 elements, **0 mismatches** on the 3 asserted families (135,680 elements); specials recorded (4,128 words outside the finite model's domain) |
| (d) FP8-specific families, e5m2 | `r20260922-182641-e27d` (supersedes `r20260922-180323-3273`) | e028f9e | done rc=0 SUCCESS, validated **not_run**, wall 12.5 s, $0.0026 | same families: 141,824 elements, **0 mismatches** vs the e5m2 HYPOTHESIS on the asserted 135,680; specials recorded (4,824 outside the model's domain) |
| (e) sm90 compile + SASS check | `r20260922-182748-cff5` (earlier: `r20260922-180506-a006`, `r20260922-181825-a926`) | e028f9e | done rc=0 SUCCESS, validated **passed**, wall 14.0 s, $0.0029 | `--compile-only --sass-check` for the 4 sm90 FP8 ids + sm90/sm80 bf16: all compile with `nvcc -arch=sm_90a` (12.4); counts below |
| (a2) BF16 regression on the final SHA | `r20260922-182206-f46a` | e028f9e | done rc=0 SUCCESS, validated **passed**, wall 2.4 s, $0.0005 | 360/360 records, 0 mismatches, SASS 1× HMMA.16816.F32.BF16 |

Per-family counts, run (b) `sm89.mma.m16n8k32.e4m3` (elements / mismatches vs `ada_e4m3_m16n8k32`): randn_zero_acc 12,800,000 / 0;
randn_random_acc 3,200,000 / 0; uniform_bits 3,200,000 / 0; subnormal 1,600,000 / 0; cancellation 1,600,000 / 0; mixed_magnitude
1,600,000 / 0; near_overflow 800,000 / 0; signed_zero 32,768 / 0; tiny_acc_zero_products 65,536 / 0; zero_products_nonzero_acc 65,536 / 0;
acc_only_lsb_walk 65,536 / 0; adder_width_cancellation 4,608 / 0; specials 6,144 / not asserted (4,128 model domain errors = NaN codes).
Run (c) `sm89.mma.m16n8k32.e5m2` has the identical family sizes and 0 mismatches everywhere against the hypothesis (specials: 4,824 domain
errors = inf/NaN codes). Note: in runs (b)/(c) the `adder_width_cancellation` tiles had the residual's A exponent overwritten across the
eight columns (fixed in 0a8676d; the captured words still matched the model 4,608/4,608, but the intended per-ratio probe is the one in
the (d) runs). With c105f41, `--families` no longer changes the other families' random draws: the (d) tiles are bit-identical to the
corresponding families of (b)/(c) (verified from the npz artifacts).

## Findings (evidence, RTX 4090 sm_89, driver 580.159.04, nvcc 12.4)

1. **E4M3 `mma.sync.m16n8k32`: 25,040,128 + 360 + 141,824 hardware words reproduced bit-exactly by `ada_e4m3_m16n8k32`** (groups (16,16),
   width 14, zero exponent −139). No mismatch; the model was not touched.
2. **E5M2 `mma.sync.m16n8k32`: the HYPOTHESIS "Ada E4M3 pipeline with exact E5M2 products" reproduced all 25,040,128 + 141,824 finite
   words** (0 mismatches). Recorded as agreement counts, validation `not_run`; the raw capture (tiles_*.npz) is in both run dirs.
3. **Adder width and grouping (adder_width_cancellation, both formats, `+P −P + 2^ratio·P`, P = 2^0, 2^8, 2^16 for E4M3 / 2^0, 2^16, 2^30 for
   E5M2, ratios −26..−3):** with the residual in k slots 2..15 the hardware word is 2^(pe+ratio) for every ratio ≥ −13 and exactly 0 for every
   ratio ≤ −14, whether P is carried by product 0 or by the accumulator; with the residual in slots 16..31 the word is 2^(pe+ratio) down to
   ratio −26 (no truncation observed). No other word appeared in the 4,608 elements. (Consistent with the pinned (16,16)/14-bit model; stated
   here as the measured table.)
4. **Zero products, nonzero accumulator (65,536 elements each format, random finite FP32 accumulators over the whole exponent range, half the
   tiles with random finite B so products are ±0·x):** D == C in 60 elements, D != C in 65,476; D == (C & 0xFFFFFC00) in 65,535 of 65,536.
   The one exception (E4M3 and E5M2 alike, same tiles): C = 0x800001a9 (negative FP32 subnormal), random finite B → D = 0x00000000 (+0; the
   masked value would be −0). `acc_only_lsb_walk` (64 base words × all 1,024 low-10-bit patterns, zero products): bits 10..31 of D equal
   those of C in 65,536/65,536 elements; each of bits 0..9 equals C's bit in exactly 32,768 (i.e. is 0 whenever C's bit is 1 — the low 10
   bits come back zero, no rounding carry into bit 10 anywhere). D == C only for the 64 base words themselves.
5. **Specials (recorded, never asserted).** E4M3: any 0x7f/0xff (NaN) operand anywhere in the row/column → 0x7fffffff, including NaN×0 and
   with ±inf/NaN accumulators; accumulator +qNaN (payload or not) and +sNaN → 0x7fffffff regardless of operands; ±inf accumulators stay ±inf
   with finite products; accumulator +max (0x7f7fffff) with 31 products 1·1 → 0x7f7ffc00 (the 14-bit-truncated accumulator, no overflow);
   accumulator 0x00000001 with zero products → 0x00000000, with product 1·1 → 0x3f800000. E5M2: 0x7c/0xfc (±inf) operands produce ±inf
   words with the IEEE sign rules, inf·0 → 0x7fffffff, +inf + −inf → 0x7fffffff, inf·subnormal → inf; NaN codes 0x7d/0x7e/0x7f/0xfd →
   0x7fffffff. The canonical NaN word is always 0x7fffffff. Full per-tile tables in `probe_results.json` → `sweep.families.specials.summary`.
6. **sm_90a `mma.sync.aligned.m16n8k32.row.col.f32.{e4m3,e5m2}.{e4m3,e5m2}.f32` is not a single tensor-core instruction.** ptxas 12.4 emits
   12× `F2FP.F16.<fmt>.UNPACK_B` (FP8→FP16, low and high halves of each operand word separately), `HMMA.16816.F32 R8, R8, R18, RZ` and
   `HMMA.16816.F32 R4, R4, R2, RZ` (the FP16 K=16 tensor-core instruction, both with a ZERO accumulator: low halves = k mod 4 ∈ {0,1}, high
   halves = k mod 4 ∈ {2,3}), then `FADD` of the two partials and `FADD` with the accumulator (SASS excerpts: `sass_mma_e4m3_m16n8k32_tiles_sm_90a.txt`,
   `sass_mma_e5m2_m16n8k32_tiles_sm_90a.txt` in run `r20260922-182748-cff5`). So on Hopper the answer to "wgmma model or Ada model?" is
   expected to be neither; the table records `sass_mma = 2` for these two ids (the SASS check compares with it and flags
   `single_instruction: false`; the run's `hypothesis_findings` says so), and a third HYPOTHESIS model reproduces exactly that lowering around
   the pinned `hopper_bf16_m16n8k16` pipeline (the one assumption: FP16-input HMMA.16816.F32 has the same (16,)/26/−133 pipeline as BF16).
   Whether any of the three agrees is for the H100 run to say.

## Compile / SASS check for the sm90 paths (run `r20260922-182748-cff5`, nvcc 12.4.131 on vy-sp1, `kind: tc-compile-check/v1`, validation passed)

| id | compiled (`-arch=sm_90a`) | MMA-class SASS in the tile kernel | single instruction |
|---|---|---|---|
| `sm90.wgmma.m64n8k32.e4m3` | yes | 1 — `QGMMA.64x8x32.F32.E4M3.E4M3 R24, R28, gdesc[UR4], R24, gsb0` (with `WARPGROUP.ARRIVE`, `WARPGROUP.DEPBAR.LE gsb0`, `FENCE.VIEW.ASYNC.S`) | yes |
| `sm90.wgmma.m64n8k32.e5m2` | yes | 1 — `QGMMA.64x8x32.F32.E5M2.E5M2` | yes |
| `sm90.mma.m16n8k32.e4m3` | yes | 2 — `HMMA.16816.F32` ×2 (see finding 6) | **no** (recorded as `sass_mma = 2`) |
| `sm90.mma.m16n8k32.e5m2` | yes | 2 — `HMMA.16816.F32` ×2 | **no** |
| `sm90.mma.m16n8k16.bf16` | yes | 1 — `HMMA.16816.F32.BF16` | yes |
| `sm80.mma.m16n8k16.bf16` (sm_80) | yes | 1 — `HMMA.16816.F32.BF16` | yes |

The tile-kernel SASS of every id is kept as `sass_<kernel>_<arch>.txt` in the run dir (listed in `artifacts`). Nothing was executed on sm_90.

## H100 commands (replace `<H100>`; each is its own run; fetch with `research fetch RUN --all`)

The `--n-random 25000` for the wgmma ids keeps the element count at the Ada level (M = 64 rows per tile → 25.6M elements in randn_zero_acc
alone at 25,000 tiles); `--procs` defaults to cpu_count − 4. The wgmma layout check tries the descriptor (LBO, SBO) = (128, 256) and then
(256, 128) on exact-integer tiles before any capture and records the pair that passed; if neither passes the run stops with
`fragment layout check failed` and no capture is made (that would be the next thing to fix, not a numerics finding).

~~~
research run --on <H100> --project verity --source /Users/danielreuter/projects/verity-main-wt/tc-probe-fp8 --stage tc-probe-fp8.h100.wgmma-e4m3 --require-result -- bash -c 'export PYTHONPATH=packages/verity/src:backends/numerical/python PATH=/usr/local/cuda/bin:$PATH; nvidia-smi -L; nproc; /root/.local/bin/uv run --no-project --with numpy --python 3.12 python tools/tc_probe/tc_probe.py --instruction sm90.wgmma.m64n8k32.e4m3 --out "$RESEARCH_RUN_DIR" --sass-check --sweep --n-random 25000'

research run --on <H100> --project verity --source /Users/danielreuter/projects/verity-main-wt/tc-probe-fp8 --stage tc-probe-fp8.h100.wgmma-e5m2 --require-result -- bash -c 'export PYTHONPATH=packages/verity/src:backends/numerical/python PATH=/usr/local/cuda/bin:$PATH; nvidia-smi -L; nproc; /root/.local/bin/uv run --no-project --with numpy --python 3.12 python tools/tc_probe/tc_probe.py --instruction sm90.wgmma.m64n8k32.e5m2 --out "$RESEARCH_RUN_DIR" --sass-check --sweep --n-random 25000'

research run --on <H100> --project verity --source /Users/danielreuter/projects/verity-main-wt/tc-probe-fp8 --stage tc-probe-fp8.h100.mma-e4m3 --require-result -- bash -c 'export PYTHONPATH=packages/verity/src:backends/numerical/python PATH=/usr/local/cuda/bin:$PATH; nvidia-smi -L; nproc; /root/.local/bin/uv run --no-project --with numpy --python 3.12 python tools/tc_probe/tc_probe.py --instruction sm90.mma.m16n8k32.e4m3 --out "$RESEARCH_RUN_DIR" --sass-check --sweep --n-random 100000'

research run --on <H100> --project verity --source /Users/danielreuter/projects/verity-main-wt/tc-probe-fp8 --stage tc-probe-fp8.h100.mma-e5m2 --require-result -- bash -c 'export PYTHONPATH=packages/verity/src:backends/numerical/python PATH=/usr/local/cuda/bin:$PATH; nvidia-smi -L; nproc; /root/.local/bin/uv run --no-project --with numpy --python 3.12 python tools/tc_probe/tc_probe.py --instruction sm90.mma.m16n8k32.e5m2 --out "$RESEARCH_RUN_DIR" --sass-check --sweep --n-random 100000'
~~~

Optional regression on the same H100 (pinned BF16 Hopper model, seconds): the same prefix with
`--instruction sm90.mma.m16n8k16.bf16 --out "$RESEARCH_RUN_DIR" --sass-check --sweep --n-random 100000`.

Reading the results: `research inspect RUN` shows `mismatches[<model>]` per model; `result.json` → `tc_evidence.model_agrees` is the per-model
verdict; `validation.status` is `passed` only for `sm90.wgmma.m64n8k32.e4m3` (pinned `hopper_e4m3_wgmma_k32`), `not_run` for the three
hypothesis-only ids; for the two `sm90.mma.*` ids `tc_evidence.hypothesis_findings` also carries the `not single-instruction` note.

## Output contract (as delivered)

`result.json`: `schema research/result/v0.1`, `kind: tc-evidence/v1` (`tc-compile-check/v1` for `--compile-only`); `workload_fingerprint` =
probe, instruction, ptx, arch, sku/device, compute_capability, driver, nvcc, seed, n/n_random, families, models (name, pipeline, groups, width,
zero_exponent, product, lowering, declared); `measurements` = wall, elements, `mismatches[<model>]` totals and `<family>.elements` /
`<family>.mismatches[<model>]`, `tile_kernel_mma_count`, golden replay counts; `tc_evidence` = instruction, arch, sku, driver, nvcc, seed, n,
layout_check, models, per-family {elements, asserted, mismatches per model, domain_errors per model, first_mismatches (≤ 20, with acc/a/b/d
hex words and every model's word)}, model_agrees per model, total_mismatches_by_model, golden_replay, sass, hypothesis_findings.
`validation.status` = passed iff every replay and every asserted-family mismatch count against a declared (pinned) model is 0; `not_run` when
only hypothesis models are compared; `failed` otherwise (sweep mismatches vs a pinned model, replay mismatches, SASS count ≠ the table's).
Files under `--out`, listed in `artifacts`: `probe_results.json` (measurement_files), `capture_sample.json` (60 golden-format records per
family), `tiles_<family>.npz` (A, Bt, C, D per tile — the complete capture), `sass_<kernel>_<arch>.txt`.

## Merge note

`main` moved from a0f0eb9 to b070724 while this lane ran; none of the four files this lane changed were touched there (`git diff a0f0eb9..HEAD`
= exactly `tools/tc_probe/{tc_probe.py,mma_tiles.cu,wgmma_tiles.cu,tiles_common.cuh}`), so the branch merges cleanly. `main` added
`tools/tc_probe/tool.py` (the store declaration) whose `parse` already accepts `--instruction`; the new `--sass-check` / `--compile-only` flags
fall into its `_unknown` bucket (still hashed) — the store lane may want to add them and `kind: tc-compile-check/v1` to `produces`.

## Pod time

Run wall on vy-sp1 (from `research inspect` cost lines, $0.74/h): (a) 2.3 s + (b) 130.6 s + (c) 132.2 s + (d, superseded) 12.8 s + 11.5 s + (e, first)
13.8 s + (e2) 14.0 s + (a2) 2.4 s + (d final) 12.7 s + 12.5 s + (e3) 14.0 s = **358.8 s ≈ 6.0 min, ≈ $0.074** run occupancy (one launch,
`r20260922-181215-00d7`, was refused while another lane held the pod exclusively; no cost). No pod created, deleted or otherwise touched.

## Hopper (vy-h100, RunPod pod 4cp9bexmjfrpum; H100 80GB HBM3 SXM, cc 9.0, sm_90a, driver 570.211.01, nvcc 12.4.131; 2026-09-22 18:34–18:59Z)

Worktree `/Users/danielreuter/projects/verity-main-wt/tc-probe-h100` (branch `lane/tc-probe-h100` at `main` = c67a120, no source
changes). Every run: `research run --on vy-h100 --project verity --campaign r21-silicon --tool tc_probe --source <worktree> --require-result`
with R2 creds sourced; the run command checks `nvidia-smi -L` / `nvcc --version` / `nproc` (224), installs `uv` if absent (it was) and runs
`uv run --no-project --with numpy --python 3.12 python tools/tc_probe/tc_probe.py --instruction <id> --out "$RESEARCH_RUN_DIR" --sass-check --sweep ...`.
No launch was refused; the pod was not created, deleted or otherwise touched. All five runs `done rc=0`, `result=valid`, run dirs preserved.

### Runs and headline counts (asserted families; `specials` is never asserted, see below)

| # | run | instruction | n_random | elements | model | mismatches | validation | SASS (tile kernel) |
|---|-----|-------------|---------:|---------:|-------|-----------:|------------|--------------------|
| 1 | `r20260922-183435-fd5d` | `sm90.wgmma.m64n8k32.e4m3` | 25 000 | 25 554 432 | `hopper_e4m3_wgmma_k32` (pinned, (32,)/14/−139) | **0** | passed | 1 × `QGMMA.64x8x32.F32.E4M3.E4M3` |
| 2 | `r20260922-183837-940b` | `sm90.wgmma.m64n8k32.e5m2` | 25 000 | 25 554 432 | `hopper_e4m3_wgmma_k32+e5m2_product` [HYPOTHESIS] | **0** | not_run (hypothesis only) | 1 × `QGMMA.64x8x32.F32.E5M2.E5M2` |
| 3 | `r20260922-184111-671e` | `sm90.mma.m16n8k32.e4m3` | 100 000 | 25 040 128 | `hopper_bf16_m16n8k16+e4m3_product/2xHMMA.16816.F32+FADD` [HYP] | **0** | not_run | **2 × `HMMA.16816.F32`** (+ `F2FP.F16.E4M3.UNPACK_B`, `FADD`) |
|   |                        |                            |         |            | `hopper_e4m3_wgmma_k32` [HYP] | 18 613 610 (74.3 %) | | |
|   |                        |                            |         |            | `ada_e4m3_m16n8k32` [HYP] | 19 037 512 (76.0 %) | | |
| 4 | `r20260922-184835-4b95` | `sm90.mma.m16n8k32.e5m2` | 100 000 | 25 040 128 | `hopper_bf16_m16n8k16+e5m2_product/2xHMMA.16816.F32+FADD` [HYP] | **0** | not_run | **2 × `HMMA.16816.F32`** |
|   |                        |                            |         |            | `hopper_e4m3_wgmma_k32+e5m2_product` [HYP] | 15 528 222 | | |
|   |                        |                            |         |            | `ada_e4m3_m16n8k32+e5m2_product` [HYP] | 15 762 006 | | |
| 5 | `r20260922-185339-e337` | `sm90.mma.m16n8k16.bf16` | 100 000 | 25 698 304 | `hopper_bf16_m16n8k16` (pinned, (16,)/26/−133) | **0** | passed | 1 × `HMMA.16816.F32.BF16` |

Per-family element counts for the wgmma ids (M = 64): randn_zero_acc 12 800 000, randn_random_acc 3 200 000, uniform_bits 3 200 000,
subnormal / cancellation / mixed_magnitude 1 600 000 each, near_overflow 799 744, signed_zero 131 072, tiny_acc_zero_products 262 144,
zero_products_nonzero_acc 262 144, acc_only_lsb_walk 65 536, specials 24 576 (not asserted), adder_width_cancellation 9 216 — every asserted
family 0 mismatches for both wgmma ids.  For the mma ids the family sizes are the Ada ones (`## Runs on vy-sp1`).

### wgmma descriptor

The B-operand `wgmma` descriptor that passed `layout_check` (32 768 elements, `status: passed`) on the H100 is
**(LBO, SBO) = (128 B, 256 B)**, K-major, no swizzle (`LayoutType::INTERLEAVE`), i.e. exactly the pair the harness shipped with — no
descriptor fix was needed; both wgmma runs went through on the first launch.

### D14: what does Hopper `mma.sync.m16n8k32.{e4m3,e5m2}` compute?

**Answer: the 2 × HMMA.16816.F32 + FADD lowering, i.e. Hopper's BF16 K = 16 pipeline `hopper_bf16_m16n8k16` ((16,), width 26, zero
exponent −133) applied twice — over k ≡ 0,1 (mod 4) and over k ≡ 2,3 (mod 4), each with a zero accumulator — with the two partial
words and then the accumulator added by IEEE FP32 `FADD` (RNE, no FTZ).**  0 mismatches over 25 040 128 elements for each of e4m3 and
e5m2 (with e5m2 exact products).  The other two hypotheses are rejected: the wgmma K = 32 pipeline `hopper_e4m3_wgmma_k32` disagrees on
74 % / 62 % of the elements and Ada's `ada_e4m3_m16n8k32` ((16,16)/14) on 76 % / 63 %.  Consistent evidence from the finite families:

- `zero_products_nonzero_acc`: D == C for **65 536 / 65 536** elements (the accumulator passes through the FP32 `FADD` untouched; only 60
  survive the 14-bit mask).  Ada gives D == C&mask on all but the −subnormal case; the H100 wgmma path (below) gives D == C&mask on
  262 144 / 262 144.  So the "FP8 accumulator truncation to 14 bits" of Ada and of Hopper `wgmma` does **not** happen on Hopper `mma.sync` FP8.
- `acc_only_lsb_walk` for mma ids: all 32 accumulator bits survive (BF16-pipeline behaviour), vs. bits 0–9 not preserved on the wgmma path.
- `adder_width_cancellation` for mma ids: residual survives at ratio 2^−24…2^−26 relative to the pair exponent (the BF16 pipeline's 26-bit
  adder), not 2^−13/2^−14.
- SASS: `tile_kernel_mma_count = 2` `HMMA.16816.F32` per `mma.sync.m16n8k32` (matches the sm_90a compile check from this morning;
  `sass_mma_e4m3_m16n8k32_tiles_sm_90a.txt` / `..._e5m2_...` in the run dirs).  So these two PTX ids are **not single hardware
  instructions on Hopper** and should be modelled as the lowering, not as a pipeline.

Not-asserted `specials` family (48 tiles): the only elements where the 2×HMMA+FADD model disagrees are the **NaN-accumulator tiles**
(`+qnan`, `+qnan_payload`, `-qnan`, `+snan`: 1 344 elements for e4m3, 880 for e5m2): the hardware returns the canonical NaN `0x7fffffff`
where the model's `fp32_add_bits` (numpy) propagates the payload (`7fc00000` / `7fc12345` / `ffc00000` / `7fc00001`).  That is the GPU
`FADD` canonicalising NaN outputs; a one-line fix in `tc_probe.fp32_add_bits` (return `0x7fffffff` for any NaN result) would close it.
FP8-NaN operands → `0x7fffffff` for every model (`domain_errors`); `±inf` accumulators propagate (`7f800000` / `ff800000`) exactly as in
the model.  Unchanged from Ada: E4M3 `+max` accumulator saturates (`7f7fffff`) rather than overflowing.

### Hopper `mma.sync.m16n8k16.bf16` (run 5)

Matches the wgmma-pinned `hopper_bf16_m16n8k16` ((16,)/26/−133): **0 mismatches / 25 698 304** elements, 10 asserted families, 1 ×
`HMMA.16816.F32.BF16` per PTX instruction.  `ampere_bf16_m16n8k16` ((8,8)/25/−132) was evaluated on the laptop against the captured
`tiles_*.npz` (first 150 tiles of every family, 192 000 elements): **30 927 mismatches** (cancellation 8 299, zero_acc_tiny_cancellation
7 075, randn_random_acc 5 749, near_overflow 4 671, mixed_magnitude 2 274, uniform_bits 2 213, randn_zero_acc 646; 0 in signed_zero /
subnormal / tiny_acc_zero_products), while `hopper_bf16_m16n8k16` gives 0 on the same subset.  silicon-p0's hypothesis is settled: Hopper
`mma.sync` BF16 = `hopper_bf16_m16n8k16`, not Ampere's two-group pipeline.

### wgmma e4m3 finite probes (item 6 — supported on the wgmma path, ran as part of run 1; identical words in run 2)

- `adder_width_cancellation` (M = 64, 9 216 elements, `prod` and `acc` variants): in **all 30 slots (k = 2…31)** the residual survives at
  ratio 2^−13 and is truncated at 2^−14 relative to the pair exponent — one group of 32 with a 14-bit adder, i.e. `(32,)/14`, and nothing
  like Ada's two-group `(16,16)` boundary at k = 16.  This is the direct measurement behind the pinned `hopper_e4m3_wgmma_k32` shape.
- `zero_products_nonzero_acc`: D == C & mask14 for **262 144 / 262 144** elements (D == C only for the 244 elements whose C already has
  no low bits); no −subnormal exception as on Ada.
- `acc_only_lsb_walk`: bits 0–9 of C are not preserved (32 768 / 65 536 = chance), bits 10–31 preserved (65 536 / 65 536); D == C for 64.
- `specials`: FP8 NaN operands → `0x7fffffff`; `+max` accumulator saturates to `7f7ffc00` (the 14-bit-truncated max, vs `7f7fffff` on the
  mma.sync path); `+inf`/`-inf` accumulators propagate; NaN accumulators → `0x7fffffff`.

### Store

Attempts pulled with `research data pull RUN --from vy-h100` (the Ada runs `r20260922-182539-ea37` / `-182641-e27d` were missing from the
back-fill and were published with `research data attempt publish <run dir>`); every run pushed with `research data push RUN` (5/5 preserved
each).  Labels (`--by tc-probe-fp8 --ref <run>`) on every `tc-evidence/v1` result artifact: `instruction`, `model_agrees=true`, `model`,
`hardware=h100|rtx4090`, `evidence`, plus `model_status=hypothesis` and `model_rejected=…` where applicable.

| run | result artifact (`tc-evidence/v1`) | instruction | model (agrees) |
|-----|------------------------------------|-------------|----------------|
| `r20260922-174939-affc` | `art:d9c58b5770039bc7cc053dc0df98ed0687b2ce39ec8ce722acf22ca00f995b8c` | sm89.mma.m16n8k16.bf16 | ada_bf16_m16n8k16 (golden replay 360/360) |
| `r20260922-175246-0477` | `art:2f0c57374016f25b0cbf3984cec16768d62989f05d02629f59764e3c1bc54e62` | sm89.mma.m16n8k32.e4m3 | ada_e4m3_m16n8k32 |
| `r20260922-175732-172a` | `art:244c244903f65a9587f465a95d5ebcdfa8ac70c211ab3425cc1b313731fadf20` | sm89.mma.m16n8k32.e5m2 | ada_e4m3_m16n8k32+e5m2_product (hyp) |
| `r20260922-182539-ea37` | `art:773d6f2f3ffb2ce2241395953502a4de49e63cf9f770bf3956fe9c9e917f4a3c` | sm89.mma.m16n8k32.e4m3 (FP8 families) | ada_e4m3_m16n8k32 |
| `r20260922-182641-e27d` | `art:80f3365050a1a7974b53dd9d98fa22cfcc111bab455a7e36ac7600a07d8ff1c6` | sm89.mma.m16n8k32.e5m2 (FP8 families) | ada_e4m3_m16n8k32+e5m2_product (hyp) |
| `r20260922-183435-fd5d` | `art:8dbc2814cc551847d7aabaae0615dce567eb87d0f14693cfb3e7e6103fb0507c` | sm90.wgmma.m64n8k32.e4m3 | hopper_e4m3_wgmma_k32 |
| `r20260922-183837-940b` | `art:82649fd02351ab9fd2c15c129e18d18cb992e6b3b1c0431463ef69fbeb2cbdb4` | sm90.wgmma.m64n8k32.e5m2 | hopper_e4m3_wgmma_k32+e5m2_product (hyp) |
| `r20260922-184111-671e` | `art:eec89e1ebb4c7fa2da085a92777fd1809a14eb13d4ce65e789a62b7e655fa929` | sm90.mma.m16n8k32.e4m3 | hopper_bf16_m16n8k16+e4m3_product/2xHMMA.16816.F32+FADD (hyp) |
| `r20260922-184835-4b95` | `art:c5bb2231b9e9f5615d81ec60ea3077a78e38abe0353c2c2bf81efe439a35a948` | sm90.mma.m16n8k32.e5m2 | hopper_bf16_m16n8k16+e5m2_product/2xHMMA.16816.F32+FADD (hyp) |
| `r20260922-185339-e337` | `art:9e2a4c42138b275871861e7799f5cb1ae3d378bfe479fbcdbd33a3003b203a35` | sm90.mma.m16n8k16.bf16 | hopper_bf16_m16n8k16 |

Snapshot **`fp8-evidence-v1` = `art:9167b3db6a9dbd01433f8216f4c1626f6877caf73110e80f462738d80ca763ca`** (`dataset-snapshot/v1`, the ten
members above), `research data push` → **PRESERVED** on `s3://verity-dev` (verified 2026-09-22T19:12:10Z).

### For silicon-p0's registry (no `packages/verity/**` change made here)

- `hopper_e4m3_wgmma_k32` — confirmed on H100 silicon (pinned model holds, 0 / 25.5 M); with e5m2 products it also describes
  `wgmma.m64n8k32.e5m2` (0 / 25.5 M) → candidate to pin as `hopper_e5m2_wgmma_k32` (same pipeline, e5m2 product).
- `hopper_bf16_m16n8k16` — confirmed for `mma.sync.m16n8k16.bf16` on H100 (0 / 25.7 M); `ampere_bf16_m16n8k16` rejected for Hopper.
- `mma.sync.m16n8k32.{e4m3,e5m2}` on sm_90a — **not a pipeline**: model as `fadd(C, fadd(hopper_bf16_m16n8k16(k≡0,1 mod 4), hopper_bf16_m16n8k16(k≡2,3 mod 4)))`
  with FP8 products; `FADD` canonicalises NaN to `0x7fffffff`.  Anyone using PTX `mma.sync` FP8 on Hopper gets BF16-pipeline numerics
  (26-bit adder, no 14-bit accumulator truncation), not the Ada FP8 numerics and not the wgmma numerics.

### Pod time (vy-h100, $3.49/h; run occupancy only)

104.6 s + 76.5 s + 228.6 s + 197.2 s + 51.5 s = **658.4 s ≈ 11.0 min ≈ $0.64**.  No launch refused, nothing killed; the pod (shared with
h100-bestvsbest) was left running as found.
