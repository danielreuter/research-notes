---
id: r21-b-hopper/b-hopper/20260922T2320Z-report-b-hopper
campaign: r21-b-hopper
lane: b-hopper
kind: report
status: closed
repo: verity-main@a39de82
branch: lane/b-hopper (off main; merges lane/fill-a100 at aef1214; bench commits 11f4120 / bc039b1; not pushed, not merged)
machine: vy-h100b (RunPod 3xj2zz9xqigu10, H100 80GB HBM3 SXM, Xeon Platinum 8470 208 threads, driver 580.126.09 / CUDA 13.0 host, venv torch 2.6.0+cu124, cupy 14.2.0, rustc 1.98.1; $3.49/h, ~92 min, ~$5.4; terminated 23:16Z)
decision: Table 2 H100 rows -- B-Ligero proofs of the HOPPER relations, self-proved on an H100
snapshot: h100-self-proved-v1 = art:0768100291d7b69a40e498c6b86902ab300222767e044a36121cdf2624a99ba3 (8 members, PRESERVED on s3://verity-dev 23:43Z)
---

# b-hopper: B-Ligero proves the Hopper tensor-core relations (BF16 mma.m16n8k16, FP8 wgmma e4m3 K32) on an H100

## 1. Result (Table 2, H100 rows)

B = 4096 VUs, K = 1536, target 2^-128, median of 3 recorded reps after a warm-up, synthetic deterministic instances
(`bench-instances-bf16-hopper/v1` manifest `2a5babca16e8…`, `bench-instances-fp8-hopper/v1` manifest `0ff750026b8d…`, seed
20260922, range [0, 4096]), every dumped proof (3 reps x every sub-batch) re-checked from files on the same pod.

| relation | mode | prover s (median/3) [reps] | ms/VU | t.total | file verifier s (which) | Py live verifier s | proof MB | depth | e2e@0ms | soundness | class | run | art |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **bf16-hopper** | interactive non-ZK | **1.462** [1.461, 1.477] | 0.357 | 1.463 | 2.856 (`ligero-verify` Rust, 25 x ~0.115 s, 16 thr, **75/75**) | 0.692 | 106.38 | 3 | 4.318 | 2^-128.25 (t=196, D=6) | NON_ZK_PROOF_DIAGNOSTIC | r20260922-223827-8b4b | art:ea50b6d02931… |
| bf16-hopper | Fiat-Shamir `--zk` | **1.651** [1.636, 1.663] | 0.403 | 1.652 | 3.641 (Rust, **75/75**) | 0.778 | 158.87 | 1 | 5.291 | 2^-128.04 (t=288, D=7, t_pad=512) | COMPLETE_HVZK_BACKEND | r20260922-224340-8b34 | art:0ad68da7243f… |
| bf16-hopper | interactive `--zk` | **1.537** [1.533, 1.550] | 0.375 | 1.538 | 2.879 (Rust + `--coins`, **75/75**) | 0.673 | 118.03 | 3 | 4.417 | 2^-128.05 (t=197, D=6, t_pad=256) | COMPLETE_ZK_BACKEND | r20260922-224750-e360 | art:759fcf5830aa… |
| **fp8-hopper** | interactive non-ZK | **0.674** [0.671, 0.679] | 0.165 | 0.675 | 19.18 (Python file verifier, CPU, separate process, 13 x ~1.4 s + torch start-up, **39/39**) | 0.400 | 56.19 | 3 | (19.86) | 2^-128.52 (t=195, D=6) | NON_ZK_PROOF_DIAGNOSTIC | r20260922-230038-1f2a | art:ea8bd418bd8b… |
| fp8-hopper | Fiat-Shamir `--zk` | **0.753** [0.752, 0.797] | 0.184 | 0.754 | 18.21 (Python file, **39/39**) | 0.443 | 83.98 | 1 | (18.96) | 2^-128.32 (t=287, D=7, t_pad=512) | COMPLETE_HVZK_BACKEND | r20260922-230307-ee44 | art:0d0cd47914e6… |
| fp8-hopper | interactive `--zk` | **0.722** [0.718, 0.753] | 0.176 | 0.722 | 16.88 (Python file, **39/39**) | 0.400 | 62.25 | 3 | (17.60) | 2^-128.32 (t=196, D=6, t_pad=256) | COMPLETE_ZK_BACKEND | r20260922-230538-19a5 | art:0800188b4ab0… |

Full art ids: bf16 = `art:ea50b6d029316ac8d065aaee23b9fc07eedf39916a31972008b0aaaa20f880cd`, `art:0ad68da7243f8008995a32bc4a860c144e3876e75b4ddc3fa6a76a6a38785b67`,
`art:759fcf5830aa4addf893449a2a7d86fce482395f3cbea1d3ad26505556d09e1d`; fp8 = `art:ea8bd418bd8b785418a6818d499df4ed35eed0349c5c307bd7a65a9867427981`,
`art:0d0cd47914e6aa9e27a617fb2cc90922bf22bc968bf812eb2d8bdd40efe365fc`, `art:0800188b4ab0fc8cb38b223fe5406ca00d8e5b4d6514734a17a5736fdcdee36a`.

t.* medians (s, per pass over 4096 VUs): bf16 non-ZK witness 0.823 / encoding+commitment 0.136 / arithmetic 0.386 /
zk 0 / serialisation 0.119; bf16 FS-ZK 0.820 / 0.168 / 0.471 / 0.015 / 0.172; bf16 int-ZK 0.819 / 0.164 / 0.421 / 0.015 /
0.116; fp8 non-ZK 0.301 / 0.073 / 0.227 / 0 / 0.072; fp8 FS-ZK 0.306 / 0.089 / 0.257 / 0.009 / 0.096; fp8 int-ZK 0.303 /
0.087 / 0.254 / 0.009 / 0.070. Peak device memory 3.00 GB (bf16) / 3.54 GB (fp8). Witness (the torch hint generator +
program) is ~55% of the bf16 prover and ~45% of fp8.

Rows/unit: **bf16-hopper 3292** (bit 2391, sel 542, hint 97, pin 96, prod 166; 339 linear, 3164 quadratic), 96 units/VU
(K=1536 / 16), 170 VUs per l=16384 proof, 25 sub-batch proofs. **fp8-hopper 3396** (bit 2196, sel 577, hint 148, pin 192,
prod 282, inv 1; 554 linear, 3164 quadratic), 48 units/VU (K/32), 341 VUs per proof, 13 sub-batch proofs -- half the
units, so the FP8 prover is ~2.2x faster per VU than BF16 on the same card.

`rate.*`: bf16 proved 8.60e6 flop/s vs the H100 SXM datasheet bf16 peak 989.4e12 = overhead 1.15e8x; fp8 1.87e7 flop/s vs
1978.9e12 = 1.06e8x. The *measured* native peaks (§3) are 0.72x / 0.57x of datasheet, so against what the card actually
sustains the overheads are 8.2e7x (bf16) and 6.0e7x (fp8).

## 2. What was built (branch lane/b-hopper, code + tests only)

* **`BF16_HOPPER` target** (`target.py`): `bf16-hopper-mma-draft/2026-09-22`, pipeline `HOPPER_BF16_M16N8K16`, instruction
  `sm90.mma.m16n8k16.bf16`, status draft, `H100_BF16_PEAK` (989.4 TFLOPS dense bf16, fp32 acc). Transition unit: tc_dot16
  with any finite FP32 c joining ONE group of 16, the 26-bit adder, floor -133, exact BF16 products. **Epilogue: FIRST's
  `f32_to_bf16`** (RN-even, overflow -> +-inf, NaN -> 0x7FC0), bit-identical to `cvt.rn.bf16.f32` on the finite domain --
  nothing pipeline-specific is pinned. Frozen vectors `fixtures/tc/vectors/bf16-hopper-mma-k16.json`, `…-k1536.json`;
  `make_tc_bf16_gate_set` generalises the Ampere gate set (`families.py`). Tests: `test_bf16_hopper_target.py`,
  `test_hopper_bf16.py` (numerical checker at `Params.from_model(HOPPER_BF16_M16N8K16)`), `test_fp8_targets.py`.
* **Relation registry** `backends/direct/ligero/relations.py` (`bf16-hopper`, `fp8-hopper`, `fp8-ada`) + one generic chain
  runner `relchain.py` (`fp8/chain.py` is now a shim). `run.py --relation {bf16,bf16-hopper,fp8-hopper,fp8-ada}`.
  Parameters come from the models: bf16-hopper = `Params.from_model(HOPPER_BF16_M16N8K16)` (groups (16,), width 26, floor
  -133); fp8-hopper = `FP8Params.from_model(HOPPER_E4M3_K32)` (one group of 32, 14-bit truncating adder as
  `rescale=10`, floor -139). Grouping is a parameter; no gadget code was copied.
* **Wide group sums** (`wide.py`, wired in `unit.py`/`compile.py`/`hints_torch.py`): the Hopper BF16 sum of 16 26-bit
  terms leaves (-p, p) of BabyBear, so `SignedSum`/`LeadingBit`/`Normalise` are replaced for wide groups by a partition
  into partial sums that fit (7+7+3 terms), 16-bit low/high limbs with carries, and limb-level identities for the sum,
  leading bit and normalisation. The Ampere system is byte-for-byte unchanged (`needs_wide(p)` is false there).
* **`ligero-statement/v3`** (`serialize.py`): word widths + relation id for 8-bit operand / 22-bit claim relations
  (fp8); v2 stays the bf16 format. `bench_result.py --verifier python` runs the Python file verifier per proof in a
  separate process (used for fp8-hopper, see §4).
* **Gate pytest** `backends/direct/ligero/relations_test.py` (`importorskip("torch")`; parametrised over both Hopper
  relations): honest random + D-family cases accepted, other pipeline's words refused by the public decode, row mutations
  rejected by the Python verifier, chain VUs, statement round-trip. **On the pod: 21 passed** (r20260922-221834-d38e at
  11f4120). Also fixed: the `relchain` instance cache re-read the whole npz per VU (435 GB of reads, 194 s per bench) ->
  materialised once (bc039b1; 0.9 s).
* `tools/native_peak/measure.py` (merged from lane/fill-a100) gained the H100 SXM5 / PCIe datasheet peaks; contract test
  `PROFILES` updated for the new target (a39de82).
* Laptop suites (`packages/verity/tests backends/numerical/tests tools/native_peak/tests relations_test.py tools/research`):
  **1103 passed, 11 skipped**.

## 3. Native peaks on the same card (`native-peak/v1`, `tools/native_peak/measure.py`, sizes 8192/16384, 5 reps, 2 s sustain)

| dtype | measured flop/s (16384^3) | datasheet | fraction | kernel | clocks / power | run | art |
|---|---|---|---|---|---|---|---|
| bf16 (cuBLAS, fp32 acc) | **707.9 TFLOP/s** (sustained 708.4) | 989.4 | 0.715 | `sm90_xmma_gemm_bf16bf16_bf16f32_f32_nn_n_tilesize256x128x64…` | 1425 MHz median, 692 W (700 W cap; throttle 0x4 = SW power cap) | r20260922-230809-b5d5 | art:070b6df778f4facef35a39cb703746f864bfd1eb26eb2c66f55251c90410189c |
| e4m3 (`_scaled_mm`, fp32 acc) | **1125.1 TFLOP/s** (sustained 1175.0) | 1978.9 | 0.569 | `sm90_xmma_gemm_e4m3f32_e4m3f32_f32_tn_n_tilesize128x128x128…` | 1380 MHz, 693 W | r20260922-230834-a27d | art:4cb7ff00eda6ad0d7f20e2719694b4cf37a059bc3639ce3440c6a2df7b092f8d |

Both power-capped at 700 W (this is a HBM3 SXM at 1980 MHz max SM clock); sub-block checks vs fp32 reference passed
(max rel err 2.0e-3 bf16, 1.5e-4 e4m3). SASS not captured (no `ncu` on the pod).

## 4. Caveats

* **fp8-hopper is NOT independently verified.** `ligero-verify` (Rust) reads `ligero-statement/v2` only; the fp8-hopper
  statements are v3 (8-bit operand words, 22-bit claims), so the first two fp8 attempts with the Rust verifier failed
  cleanly at "statement file: not a ligero-statement/v2 file" (r20260922-225900-3c75, r20260922-225925-ff72; 0/39). The
  fp8 rows were re-run with `--verifier python` (`backends.direct.ligero.serialize verify` in a separate CPU process, relation-
  aware): 39/39 accepted in every mode, labelled `verifier=python file verifier…`, `independently_verified=false`,
  `verified_by_python_only=true`. Their `verify_wall` (~17-19 s) is 13 Python processes each importing torch and
  verifying on CPU -- not a verifier-cost measurement; the live in-process GPU verifier is 0.40-0.44 s. Teaching the Rust
  verifier v3 statements is the obvious next step for a proper H100 FP8 row.
* **bf16-hopper interactive proofs** are checked by the Rust verifier against the runner's step-0 coins (`--coins`), a
  faithful recomputation of the verifier's checks, not a live interaction (as in h100-bestvsbest); the FS proofs are
  verified cold from files.
* **Proof bytes were left on the pod** (11 proof dirs, ~0.1-0.5 GB each) and died with it: the laptop had 650 MB of disk
  free, so only `bench_vu.json`, `verify/independent.json` and `proofs/manifest.json` (per-proof sha256s + verdicts) are in
  the store as `run-files/v1`. Same situation as h100-bestvsbest; a pod-side `research data put --tree proofs` + push
  from the pod would need R2 credentials on the pod.
* Datasheet-vs-measured: `rate.native_peak_flop_per_second` in the fingerprints is the datasheet number (989.4 / 1978.9
  TFLOPS); §3 gives the measured anchors.
* Both targets are `status="draft"`; the BF16 Hopper vectors were generated from the model, not captured on silicon
  (the tc-probe lanes own that). The fp8-hopper unit proves `GemmAccumulator<1536>` (22-bit packed claim) as fp8-proof
  defined it.
* The first bf16 non-ZK attempt (r20260922-222231-b5f1, 126 s prover) ran with Merkle on the host because `cupy` was
  missing from the pod venv; superseded by r20260922-223827-8b4b after adding `cupy-cuda12x` to the bootstrap. Not labelled.

## 5. Store

Labels `--by b-hopper --ref <run>` on every artifact above: `campaign=r21-b-hopper`, `hardware=h100`, `candidate=B-Ligero`;
bench rows add `relation`, `mode`, `zk`, `proof_class`, `verifier`, `independently_verified` (true for bf16, false for
fp8), `self_proved=true`; native peaks add `kind=native-peak`, `dtype`. Snapshot `h100-self-proved-v1` =
`art:0768100291d7b69a40e498c6b86902ab300222767e044a36121cdf2624a99ba3` (the 8 artifacts). All 9 `research data verify` ->
PRESERVED on s3://verity-dev (23:43Z).

~~~
research data select --kind bench-result/v1 --label campaign=r21-b-hopper           # 6 rows
research data select --kind bench-result/v1 --where meta.relation_id=bf16-hopper --label hardware=h100
research data select --kind native-peak/v1 --label campaign=r21-b-hopper            # 2 rows
~~~

## 6. Runs (campaign r21-b-hopper, vy-h100b)

bootstrap r20260922-214449-213b; gate (21 passed) r20260922-221834-d38e (earlier gate attempts 220410/220559/220825/221401 at
pre-fix commits: 8 failed on the hooks signature, fixed in 11f4120); bench rows and native peaks as tabled; superseded
r20260922-222231-b5f1 (CPU Merkle); failed-by-design r20260922-225900-3c75, r20260922-225925-ff72 (Rust verifier vs v3).
Pod: created ~21:40Z, terminated 23:16Z (~92 min at $3.49/h ≈ $5.4). Ceiling check at launch: `~/.research/notes/CEILING` = 50.
