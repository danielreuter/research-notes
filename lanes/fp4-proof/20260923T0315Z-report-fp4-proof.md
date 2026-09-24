---
id: r21-silicon/fp4-proof/20260923T0315Z-report-fp4-proof
campaign: r21-silicon
lane: fp4-proof
kind: report
status: closed
repo: verity-main@lane/fp4-proof f44cb5b
---

# fp4-proof: sm_120 FP4 instructions PINNED; first B-Ligero (ZK-capable) proof of the exact NVFP4 dot product (RTX 5090)

Branch `lane/fp4-proof` (worktree `verity-main-wt/fp4-proof`, base 1bd6573, main merged at e0e7d46, head **f44cb5b**, clean
tree, not merged). Diff vs main: 30 files, +6,391/-73 (`backends/direct/ligero/fp4/*` new, `chain.py` / `protocol.py` /
`serialize.py` component chain ends + `ligero-system/v2`, `target.py` NVFP4_SM120, `families.py` / `programs.py` NVFP4 gates,
`trust.py` contract instance sets, `contract.py` / `tables.py` NVFP4 instance set + native-dtype alias, `tools/native_peak`
`--dtype nvfp4` + `mma_peak_fp4.cu`, registry flip, tests). No `.md` in the repo. All GPU work on pod **vy-5090c**
(RunPod, RTX 5090 32 GB, `GPU-1257f022-5d0f-1ea9-7922-bc7bc7959672`, driver 570.195.03, CUDA 12.8, host AMD EPYC 7543);
the laptop edited code, ran tiny pytest, launched, fetched, published, labelled.

**Caveat (fp4-re's, verbatim):** this evidence is `mma.sync kind::mxf4nvf4` on a consumer die; B200 `tcgen05.mma` cannot be
assumed. (Lane tcgen05 has since pinned `sm100.tcgen05.mma.e2m1.{nvf4,mxf4}` separately on a B200 with the same model
parameters; this lane's evidence says nothing about sm_100 by itself.)

## 1. Trust: both sm_120 FP4 instructions HYPOTHESIS -> PINNED

| instruction | before (this morning) | after | dossier (published) |
|---|---|---|---|
| `sm120.mma.m16n8k64.e2m1.nvf4` | HYPOTHESIS (`art:9782e67b`, 23:34Z; P2 short by 3,364,480 elements) | **PINNED** (P1-P5 PASS; Ta, Tb, Tc PASS; S1 PASS) | `art:de42d6cad7c63a387d64535efc151310fd9632dd9c2dcd4502d35c3f5dcd6422` (00:15Z, P1-P5) then re-published **`art:3e02931df28cccd398de4219f9d977371a58cdc6e8addfb7ff0a6269e5481b0e`** (03:03Z, after the relation's Tc gate; the registry cites this one) |
| `sm120.mma.m16n8k64.e2m1.mxf4` | HYPOTHESIS (`art:44e46d6b`, 23:34Z; P2 short by 5,240,448) | **PINNED** (P1-P5 PASS; Tb PASS; S1 PASS; Ta/Tc/Td/Te FAIL = TRUSTED work) | **`art:d8d4d1b602c9fde61df218c315430535fe5181882ab6b26c2b95dd81dc1b5d92`** |

Fresh-seed sweeps (all 20 families, `--sweep --n-random 20480 --sass-check`, `--procs 48`; nvf4 also replays autoproof's
probe3 1601 records):

| run | instruction | seed | elements | mismatches | evidence | run-files |
|---|---|---|---|---|---|---|
| `r20260922-234714-0fc0` | nvf4 | 20260925 | **10,657,792** | **0** | `art:163e7bf580d944c570f3580bdef2303c5f927e6c5f46caa9801de3c16eb3e0cb` | `art:480d15b1eed86e51eaa9af875ca3bfdd9998d3461150a1f93646c6f0bc094e64` |
| `r20260922-235348-a405` | mxf4 | 20260926 | **9,658,368** | **0** | `art:05d4388398cac0969b3b6c723f522cac2e04bcea821548b826e58a0f680520c6` | `art:ed48e03e82785788518960109d097f8f9a57dcff03afdcf25175aa9a5516b97e` |

Labels as fp4-re's (`instruction`, `model`, `model_agrees=true`, `hardware=rtx5090`, `evidence=sweep`, `family`, `--by fp4-proof
--ref <run>`) plus **`device=GPU-1257f022-5d0f-1ea9-7922-bc7bc7959672`**. Cumulative 0-mismatch anchor evidence: nvf4
17.3M elements (this + fp4-re's 4.37M + 2.27M), mxf4 14.4M. No mismatch appeared, so no D-entry was opened; the model was not
touched. **S1 (>= 2 physical devices / environments) now PASSES for both**: fp4-re's pod was `GPU-506928f9` on driver
580.178.04, this pod `GPU-1257f022` on 570.195.03 -- the brief's "second physical device eventually" came for free.
P4: cuobjdump shows one `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X` per PTX `mma.sync` (nvcc 12.8.93).

Registry (`instructions.py`): both `status="pinned"` citing the dossiers above; `test_instructions.py` follows. Registry <=
computed level holds (the flip was made after `trust` computed PINNED from the labelled evidence).

## 2. Target and relation

**`NVFP4_SM120`** (`verity/verification/target.py`): profile `nvfp4-sm120-mma-draft/2026-09-22`, instruction
`sm120.mma.m16n8k64.e2m1.nvf4`, model `BLACKWELL_SM120_NVF4`, `GemmAccumulator<1536>` = 24 chained K=64 steps (96 UE4M3 scale
blocks of 16 on each of A and B), FP32 accumulate from c_0 = 0, the final FP32 word public; domain finite per D20 (an NVFP4
chain from 0 cannot leave binary32, so there is no overflow path). `native_peak`: **RTX 5090 dense FP4 with FP32 accumulate
= 1676 TFLOPS** (NVIDIA RTX Blackwell GPU Architecture whitepaper, Appendix A, **Table 3** "GeForce RTX 5090 vs GeForce RTX
4090 vs GeForce RTX 3090 Specs", row "Peak FP4 Tensor TFLOPS with FP32 Accumulate (FP4 AI TOPS)": **1676/3352²**; footnote 2
"Effective TOPS / TFLOPS using the Sparsity Feature", footnote 1 "Peak rates are based on GPU Boost Clock" = 2407 MHz. The
second number and the card's headline "3352 AI TOPS" are the 2:4-sparse figure; dense 1676 is used. It is the only FP4 row --
there is no FP16-accumulate FP4 rate on the sheet -- and it is 4x the FP8-with-FP32-accumulate 419, i.e. FP4 with FP32
accumulate is *not* half-rate on GeForce the way FP8/FP16 with FP32 accumulate are; the instruction measurement below confirms
the full rate.)
Reference vectors `fixtures/tc/vectors/nvfp4-sm120-mma-{k64,k1536}.json`; `families.py` handles `BlockScaledAlignAdd`
pipelines (68 words per operand per step: 64 codes + 4 scale bytes); `programs.gemm_accumulator_nvfp4`.

**Relation `fp4-nvf4`** (`backends/direct/ligero/fp4/relation.py`, one unit = one `Model.step`): the four 16-element group
dots are exact integers (numerators in halves, |gd| <= 2304), scaled losslessly by `ma*mb` (|mant| < 2^19) at unit weight
`2^X_g` (X in [-20, 8]); one five-way align-add on the grid `2^lsb`, `lsb = max(G, acc_cand)`, `G = max_participating X_g - 27`
(the leading-*participating*-group anchor of D17; -174 when none participates), `acc_cand = E_acc - 35` (the 36-bit window,
-174 for a zero accumulator); every addend truncated toward zero; RZ normalisation; every zero result +0 (D16). The one gadget
is a *truncating shifter*: shift `d = 12j + r - u`, the right part as a division with two `lt_pow` range lookups, the fine left
part in two lookup stages into 12-bit digits, the coarse part a one-hot placement -- so the adder sums signed non-canonical
digit vectors over six 12-bit positions (72 bits >= the 49-bit exact sum) and every constraint stays inside BabyBear. The
output is the shifter run backwards on the claimed 24-bit significand with the remainder checked digit-wise. Public inputs
decoded by the verifier: the 128 numerators, per group `ma*mb`, `X`, participation, `G`; UE4M3 NaN (0x7F) and bit-7 bytes
rejected in the decode. Chain ends are the three *components* of the FP32 word (sign / exponent field / fraction, each < p),
because a 32-bit word is not a BabyBear element: `chain.py` `y_end` component mode, `protocol.system_id` covers it,
**`ligero-system/v2`** carries it, statements are **`ligero-statement/v4`** (word_bytes 1, y_bytes 4, relation `fp4-nvf4`).

Census (`census_fp4`), next to FP8's (fp8-proof note) and BF16's:

| | **NVFP4 sm120 (this lane)** | FP8 Ada | BF16 |
|---|---|---|---|
| rows / unit | **1,583** | 3,769 | 3,516 |
| bit rows / unit | 972 | 2,474 | 2,401 |
| selector / hint / pin / product / inverse rows | 172 / 86 / 141 / 210 / 2 | 640 / 161 / 192 / 301 / 1 | 610 / 92 / - |
| linear / quadratic constraints | 306 / 1,389 | 589 / 3,532 | 347 / 3,387 |
| lookups (shifter stages) / unit | 18 (6 shifters) | - | - |
| K per unit; units / VU (K=1536) | 64; **24** | 32; 48 | 16; 96 |
| **rows / VU** | **37,992** | 180,912 | 337,536 |
| bit rows / VU | 23,328 | 118,752 | 230,496 |
| VUs per l=4096 proof (B_proof) | 170 (25 sub-batches at B=4096) | 85 | 42 |

4.8x fewer rows per VU than FP8 (5.1x fewer bits): the block-scaled instruction eats 64 codes per firing, its products are
tiny exact integers, and the digit representation replaces most of the per-bit alignment rows.

**Tests.** `fp4/relation_test.py` (numpy witness builder, torch-free): 21 honest edge families accepted; 14 wrong-rule
variants (`witness.VARIANTS`: frac26/frac28, window35/window37, nearest-align, floor-align, negzero, scale-sub-as-normal,
scale-exp+1, rne-norm, participate-zero-scale, acc-exp+1, wrong-sign-acc, drop-group3) rejected wherever they change a
word; reference vectors replay; system/statement round-trips; 2-VU chain (torch-gated). Local pytest passes on the touched
packages (`packages/verity`, `backends/numerical`, `tools/native_peak`).

**Tc gate on the 5090** `r20260923-021410-2142` (`gate-vu --batch 1024 --vus 2048 --row-negatives 60 --unit-negatives 48`),
`bench-result/v1` **`art:098c184a422eec0541c42bd1f7b26eb21ff138a409d41b8ca6873615c4a970a4`**, `validation.detail` =
**`vu-k1536 2048/2048 ok; vu-k1536-neg 116/116 ok; tu-k64-neg 3015/3015 ok`**. Chain negatives (through `verify`): 32
claimed-word bit flips, +-1 ulp, public-decode rejections (UE4M3 NaN, padding bit, E2M1 code, operand sign, scale exponent
bit), 6 link / c_0 mutations, an accumulator bit in a linked unit, 60 witness-row mutations, and 11 wrong-rule witnesses
proved with the wrong rule's *own* claim on a VU where its final word differs. Unit negatives (through the constraint tables):
1,008 units x 14 variants, 3,015 differing witnesses, 3,015 rejected (`window37` produced no differing unit in the sample --
the one variant not exercised at unit level; it is exercised at chain level). Trust reads Tc PASS from this artifact (the
`_INSTANCES_FAMILIES` composition satisfies the edge predicate for a contract-pinned recipe).

Earlier gate attempts, for the record: `r20260923-013752-d8bb` (pod's Python 3.11 lacks `verity_numerical`, which needs
>= 3.12 -> `/workspace/venv312`), `r20260923-014856-ca02` (no `blake3` in the venv: placeholder hash refused),
`r20260923-015229-168e` (64 VUs; **accepted two "negatives"**, floor-align and negzero, that coincided with the model on
the chosen base VU -- a defect of the negative *construction*, fixed in 6b76883/e6096a3: a wrong rule is a negative only
where it changes a word, and it must claim its own word).

## 3. Proofs at B=4096 on the RTX 5090 (K=1536, 25 proofs x 170 VUs, l=4096, 2^-128 union-bounded, 3 reps each)

Commit on the pod 3b03017; Python 3.12.14, torch 2.8.0+cu128, numpy 2.5.3; blake3 on GPU. Each `bench-result/v1` is contract
valid; rep 1 dumped (`ligero-system/v2` `system.bin` + 25 x `ligero-statement/v4` + `ligero-proof/v1` [+ coins for the
interactive modes]) into the run dir and listed under `artifacts` -> `run-files/v1`.

| mode (proof_class) | run / bench-result / run-files | t.total | witness / enc+commit / arithmetic / zk / serial. | verifier (live) | cold file re-verify (25 proofs) | proof bytes | achieved log2 | R_proved | **overhead vs spec 1676 T** | vs measured instruction peak 1880 T | vs measured cuBLASLt GEMM 1283 T |
|---|---|---|---|---|---|---|---|---|---|---|---|
| non-zk (NON_ZK_PROOF_DIAGNOSTIC) | `r20260923-024035-f3cf` / `art:5b5e9f3c0b8f878550f54636302320caaacd86ad9aef4524c69824e3c54e2822` / `art:d83225e73bb117d10ad6edac2ff3d72b476e971c4e025bfa2b1d39cb3daba871` | **1.465 s** (0.358 ms/VU) | 0.899 / 0.034 / 0.369 / 0 / 0.164 s (61/2/25/0/11 %) | 1.303 s | 25/25, 1.16 s | 43.08 MB (10.5 kB/VU) | -128.23 (t=196, BabyBear^6) | 8.59e6 FLOP/s | **1.95e8** | 2.19e8 | 1.49e8 |
| zk-interactive (COMPLETE_ZK_BACKEND, step-0 coin commitment; D7 live-verifier-only) | `r20260923-024119-8da9` / `art:8dd5c52487b1541263df7c674cfab79dc832da03b8d4150dc89f78714d2c9573` / `art:188ddc7572b78d6d4f8720e1eba4c887b968b57d07e8d60a0a499da1ec6495f2` | **1.636 s** (0.400 ms/VU) | 0.900 / 0.091 / 0.451 / 0.031 / 0.163 s (55/6/28/2/10 %) | 1.321 s | 25/25, 1.12 s (own coins replayed) | 47.87 MB (11.7 kB/VU) | -128.05 (t=201, t_pad=256) | 7.69e6 | **2.18e8** | 2.44e8 | 1.67e8 |
| zk-fiat-shamir (COMPLETE_HVZK_BACKEND, transferable) | `r20260923-024204-1f80` / `art:249785b87e09e61b8a50b45c963708a828b681d61cb55930aa49febc18a31a0a` / `art:9c5f7eeaa2921db3d7595c833fe809029482f1859c05dfd7edc3e5a860470e79` | **1.691 s** (0.413 ms/VU) | 0.884 / 0.094 / 0.472 / 0.031 / 0.211 s (52/6/28/2/12 %) | 1.422 s | 25/25, 1.33 s | 68.27 MB (16.7 kB/VU) | -128.09 (t=300, BabyBear^7, 2^60 FS loss) | 7.44e6 | **2.25e8** | 2.53e8 | 1.72e8 |

Other = t.total - sum(buckets) within 0.1 %. Peak device memory 0.74-0.93 GB. Witness is 52-61 % of the prover, and
0.63-0.64 s of it is the **numpy hint generator on the host** (`split.hints_seconds`; the torch witness is 0.26 s): the
obvious next optimisation is porting `unit_hints` to torch/CUDA. Against FP8 Ada's 4090 headline (zk-interactive 2.246 s,
181.5 MB) the NVFP4 proof is 1.37x faster and 3.8x smaller for the same K and B -- on a different host CPU, so only the
census comparison above is apples to apples.

**Native peak** `r20260923-024527-a82e`, `native-peak/v1` **`art:a0442c17dea5d644dfab8730d4fbc10630797a63112c1312c4609d7e2935ede8`**
(run-files `art:b3bd3f2066999688211dafa88df245955e6dbbffbce2ae1d2b28f748661909c6`), `tools/native_peak/measure.py --dtype nvfp4`:
*measured the instruction itself* -- `mma_peak_fp4.cu` issues
`mma.sync.aligned.kind::mxf4nvf4.block_scale.scale_vec::4X.m16n8k64.row.col.f32.e2m1.e2m1.f32.ue4m3` back to back with
register-resident operands from 2,720 warps (4/block x 680 blocks on 170 SMs), 8 independent accumulator chains x 4 operand
sets, 311,919 x 32 MMAs per launch, median of 5 event-timed launches, outputs finite and bit-identical across launches,
cuobjdump SASS check 32/32 `OMMA.SF.16864.F32.E2M1.E2M1.UE4M3.4X`. **1,879.9 TFLOP/s = 1.12 x the datasheet's dense 1676**,
at a sustained SM clock of 2,715 MHz (575 W). The datasheet figure is 4,096 FP4 FLOP/clk/SM at the 2,407 MHz boost clock;
at 2,715 MHz that is 1,890.5 T, so the instruction ran at **99.4 % of the architectural rate** -- the >1 ratio is the clock,
not a measurement error. Recorded beside it: a cuBLASLt block-scaled NVFP4 GEMM via `torch._scaled_mm` (blockwise UE4M3
scales, n=8192, kernel `cutlass3x_sm120_bstensorop_s16864gemm_block_scaled_ue4m3xe2m1_...`) at **1,282.9 T = 0.77 x spec**
-- the GEMM-methodology number comparable to the other rows' "cublas dense gemm". Table 2 prints the instruction peak as the
measured column (the artifact's `flop_per_second`); the GEMM is in `gemm_attempt`. First attempt `r20260923-024249-9a38`
FAILED its own SASS check (928 = 29 x 32 MMAs: nvcc unrolled the loop) -> `#pragma unroll 1` + the check accepts whole
unrolled copies (100e163).

**Rust `ligero-verify`: cannot verify this relation, precisely because** (a) it pins relations by `(sys_id, table digest)`
in `src/relation.rs` for `bf16-ampere`, `fp8-ada`, `bf16-hopper`, `fp8-hopper` only; (b) it parses `ligero-system/v1`
only, and this system is `/v2` (component chain ends for the FP32 word); (c) it has no E2M1 / UE4M3 public decode
(`format.rs`). All three are needed; `--allow-any-system` would not help past (b) and (c). So **nothing here is independently
verified**: every dump was re-verified cold from bytes by the Python file verifier (`serialize.verify_files`, shares code
with the prover; `dumps/verify_python.json`, `validation.evidence.dumps.independent=false`), and no `independently_verified`
or `verified=accepted` label was written by this lane. The Fiat-Shamir dumps (`art:9c5f7eea`, 79 MB) are the transferable
ones for whoever extends the Rust verifier (next lane: `ligero-system/v2` parsing, E2M1/UE4M3 decode, the `fp4-nvf4` pin).

**Labels** on the bench-results: `candidate=B-Ligero`, `target=nvfp4-sm120-mma-draft/2026-09-22`, `profile`, `proof_class`,
`relation=fp4-nvf4`, `hardware=rtx5090`, `device=GPU-1257f022-...`, `verifier=python-file-verifier` (self-check),
`--by fp4-proof --ref <run>`; vocabulary keys only.

**Tables** (`python -m verity_numerical.bench.tables --root ~/.research/store --format md`): the RTX 5090 row **is in Table 2**
-- `NVIDIA GeForce RTX 5090 | E2M1 sm120.mma.m16n8k64.e2m1.nvf4 · nvfp4-sm120-mma-draft/2026-09-22 | 1676 T | 1880 T (1.12) [6]
| — | — | —` -- with the B-Ligero cell empty. The rejecting predicate, exactly: for the COMPLETE_ZK_BACKEND result
`art:8dd5c524` -> **"not independently verified: no label independently_verified=True|true or verified=accepted by a
non-producer (producers: fp4-proof, r21-silicon)"**; the non-zk and FS results are rejected first as "proof_class ... is not
B-Ligero's declared class COMPLETE_ZK_BACKEND" (they become the drill-down lines once verified). The A100 / 4090 cells carry
"verified by coordinator against the runner's step-0 coins"; the same coordinator step (replaying `art:188ddc75`'s coins,
or verifying the FS dumps) fills this cell. Also Table 2 needed `NATIVE_DTYPE_ALIASES` (`nvfp4` -> `e2m1`) for the measured
column to match the target's operand dtype (c32d26d).

## 4. Snapshot

**`fp4-proof-v1` = `art:ae3ab50573b30527cf0164e1e40430b15c72af5599149414507634d2e52d0e28`** (`dataset-snapshot/v1`), 16 members:
the two sweeps + run-files, the three dossiers (`art:3e02931d`, `art:de42d6ca`, `art:d8d4d1b6`), the gate, the three
bench-results + run-files (dumps), the native peak + run-files. Pushed; `research data verify` -> **PRESERVED** on
`s3://verity-dev` (snapshot 1 object; spot-checked members 22 / 18 / 79 / 79 / 3 / 1 objects read back).

## What the brief got wrong / what moved

* The datasheet dense peak is not a ceiling: at the pod's sustained 2,715 MHz the instruction beats the 2,407 MHz-rated
  1676 T by 12 % (99.4 % of the per-clock rate). Ratios against "spec" for this row are therefore optimistic for the prover
  by 1.12x; the note reports overhead against all three denominators.
* The 5090's cuBLASLt block-scaled GEMM (`torch._scaled_mm`, sm_120 supported in torch 2.8.0+cu128) reaches only 0.77x spec
  at n=8192, versus the instruction's 1.12x: "measured peak" for FP4 depends strongly on which one you mean. The tables
  column footnote names the method.
* The Rust verifier is relation-specific (pinned digests) *and* format-bound (`system/v1`, no FP4 decode); the brief's "if
  its system supports this relation" resolves to no on three counts, listed above.
* Table 2's NVFP4 *row* appears (target + both peaks) but its B-Ligero *cell* cannot be filled by the producer lane by design
  (independent-verification predicate) -- the brief's "confirm a row appears" and "cell filled" are different events.
* S1 already passes: fp4-re and this lane landed on two different physical 5090s with two drivers.
* The FP32 chain end does not fit a BabyBear element (the FP8/BF16 22-bit trick does not apply): `y_end` components,
  `ligero-system/v2`. The Rust verifier's `/v1` pin is the casualty.
* The RunPod `pytorch:2.8.0-py3.11` image cannot import `verity_numerical` (`requires-python >= 3.12`): a `/workspace/venv312`
  (torch 2.8.0+cu128, numpy, blake3, cupy-cuda12x) is part of the bootstrap for any lane using this image.
* The first gate accepted two "negatives" because the wrong rule coincided with the model on the base VU; a negative must
  differ in a public word and be claimed by the wrong rule itself. The 116 + 3,015 counts above are of that kind.
* nvcc 12.8 unrolls a `for` over 32 MMAs 29x; a SASS-count check must count whole copies.
* `trust --publish` for nvf4 was run twice at 03:03Z (`art:6acbf422`, `art:3e02931d`, identical content); the registry and
  the snapshot cite `art:3e02931d`.

## Pod

`vy-5090c` (RunPod `0cq0wpoqbmb2p7`, RTX 5090 32 GB SECURE, $0.99/h, image `runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel`):
created 2026-09-22 ~23:25Z, terminated 2026-09-23 ~02:50Z after the native-peak fetch -- **~205 pod-minutes, ~$3.40** of the
5-hour budget; entry annotated TERMINATED in `~/.research/machines.toml`. 15 runs on it (2 sweeps; 6 gate attempts, of which
3 failed on environment / an `args.run_id` bug, one 64-VU gate exposed the negative-construction defect, one 64-VU and the
final 2048-VU gate passed; 5 bench runs, the first two superseded by the three published ones after the artifacts/commit fix
in 3b03017; 2 native-peak attempts). No other pod touched. Laptop `~/.research/runs` holds 55 + 60 + 79 MB of
dumps for the three benches (also preserved as run-files); nothing multi-GB.

## Next (for the coordinator)

1. Extend `ligero-verify`: `ligero-system/v2` (component chain ends), E2M1 / UE4M3 public decode, pin `fp4-nvf4` by
   `(sys_id, table digest)`; verify `art:9c5f7eea` (FS) and replay `art:188ddc75` (interactive) -> Te, and the Table 2 cell.
2. Td: `tc_probe --replay-instances` of the contract-pinned NVFP4 recipe (digest `d2d65f65...`) on a 5090, labelled
   `family=frozen-instances`.
3. mxf4 to TRUSTED needs its own relation (or the nvf4 relation with the UE8M0 = mantissa 8 at 2^(code-130) decode) and an
   independent reference.
4. Port `unit_hints` to torch (0.64 s of the 1.5-1.7 s prover is host numpy).
