---
id: r21-b-sweep/b-sweep/20260922T2330Z-report-b-sweep
campaign: r21-b-sweep
lane: b-sweep
kind: report
status: closed
repo: verity-main@e905529
branch: lane/b-sweep (off main 4987a47; commits 832050f, 5f11140, 01eb59b, c135a9c, e905529; not pushed, not merged)
machine: vy-h100c (RunPod bfg8ge5zmwavuq, H100 80GB HBM3, Xeon Platinum 8470 208 threads, driver 580.126.09; venv312 torch 2.6.0+cu124 / Triton 3.2.0 / numpy 2.5.3; ligero-verify sha256 9a59faa2…, rustup stable)
pod: created 2026-09-22 21:19:53Z, terminated 23:30:16Z -> 2h10m = 2.17 pod-hours at $3.49/h = $7.59 (budget 2.5 h); CEILING file read 50 $/h at every gate check
decision: drill-down curves behind the canonical Table 2 B-Ligero cell (B=4096, K=1536, 2^-128) + one 2^20-VU milestone proof
snapshot: b-sweep-h100-v1
---

# b-sweep: B-Ligero prover overhead vs batch, per-proof size, soundness, sub-batching on one H100; a 2^20-VU ZK milestone

Everything below is one H100 (not the Ampere target device: every artifact is labelled `same_device=false`,
`hardware=h100`); the relation is the campaign's Ampere BF16 `PROFILE` (K = 1536 = 96 m16n8k16 transitions) on the frozen
`bench-instances/v1` tier `vu-k1536` (4096 ids; the tier data files x/w/acc/y/index have the sha256s the committed
`fixtures/bench-instances/v1/manifest.json` lists -- `ebef04e9…`, `da301f94…`, `6d1c5ad6…`, `16dcf48c…`, `00759b8e…` -- the
manifest sha differs (`f7916d9d…` vs `9128d2b6…`/`059103cf…`) only through the `generated` block: build time, host, run id,
procs).  Timing = median of 3 recorded reps after one warm-up sub-batch (min-max given), `t.total` from the bench's own
`rate_measurements` (`rate.proved_flop_per_second` = 2·1536·B / t.total, `overhead.vs_native_peak` = 312e12 / that).  Every
run: `research run --on vy-h100c --exclusive --scratch triton --require-result --tool bench_vu -- python
backends/direct/ligero/bench_result.py bench-vu … --verifier /workspace/bin/ligero-verify --threads 16`; the wrapper dumps the
sub-batch proofs of the first `--dump-reps` reps and runs the independent Rust verifier on every one of them (interactive
mode: with the runner's step-0 coins, DISCREPANCIES D7), then `--keep-proofs 1` deletes all but the first proof of each rep
(manifest keeps every sha256/size; `verify/independent.json` every verdict).  Results are `bench-result/v1` artifacts whose
`run_files` tree carries `bench_vu.json` (the raw contract result with `split.*` and `rate.*`), `proofs/manifest.json` and
`verify/independent.json`.

## 0. Headline

* **The canonical cell reproduces**: B = 4096, l = 16384 (25 sub-batch proofs of 170 VUs), non-ZK interactive 2^-128:
  **1.017 s** (h100-bestvsbest on vy-h100: 1.034 s); ZK interactive 1.062 s (1.117), ZK Fiat-Shamir 1.180 s (1.194).
* **Per-proof size**: l = 32768 columns (341 VUs/proof) is the best point on this card at every B: 0.943 s at B = 4096
  (-7% vs l = 16384).  l >= 65536 leaves the SIMT encoder (shared memory: the l = 65536 tile needs 256 KB, the H100 has
  227 KB) for the torch fallback and is 2.3-2.7x slower with 30-59 GiB of device memory; l = 262144 is a CUDA OOM (asked
  for 27.5 GiB on top of 65 GiB).  So "the saturating B" is really "the saturating l"; B only amortises the fixed costs.
* **Batch scaling at l = 32768** (non-ZK): R_proved rises 1.06e7 (B = 1024) -> 1.33e7 (4096) -> 1.44e7 (16384) -> **1.46e7
  flop/s at B = 65536** and is flat/slightly down after that (1.34e7 at 262144 and 1048576).  **Saturating B = 65536**
  (overhead 2.14e7 vs the A100 BF16 peak); the canonical B = 4096 sits at 2.34e7 (l = 32768) / 2.52e7 (l = 16384), i.e.
  within 10-18% of saturation.  1M VUs non-ZK: 239.6 s, 3076 proofs, 18.9 GB of proofs, all 3076 Rust-accepted (591.9 s).
* **ZK at the saturating B (65536, l = 32768)**: interactive-ZK 14.64 s (+6% over non-ZK, R = 1.38e7), Fiat-Shamir HVZK
  17.35 s (+26%; t = 291 opened columns instead of 200, D = 7, R = 1.16e7).
* **Milestone (`milestone=1M-vu`)**: **2^20 = 1,048,576 exact BF16 tensor-core K=1536 dot products (1.61e9 BF16 MACs, 3.22e9 flop)
  proved Fiat-Shamir zero-knowledge (`COMPLETE_HVZK_BACKEND`, transferable) at 2^-128.46 in 323.4 s on one H100**, as 3076
  sub-batch proofs of 341 VUs (l = 32768, t = 297, D = 8), 29.9 GB of proofs (9.72 MB each), **all 3076 accepted by the
  Rust `ligero-verify`** on the pod (811.7 s total, 264 ms/proof at 16 threads, sequential); the retained proof
  `rep1/sub_00` (VUs 0-340) re-verifies on the laptop from bytes in 0.15 s.  Interactive-ZK at the same B: 250.5 s, 3076/3076 Rust-accepted with the runner's coins (591.1 s), 21.6 GB.
* **Bench limits found**: K is fixed at 1536 (no sweep); no `--rtt-ms` (no RTT sweep); the frozen tier has 4096 ids, so
  B > 4096 recycles them (`B_real = 4096`, recorded in the fingerprint -- the bench has no synthetic VU generator); the
  `bench_result.py` wrapper ran `ligero-verify` at its default `--soundness-bits 128` (fixed, commit e905529); at l = 256
  the bench's parameter choice misses 2^-128 by 0.46 bit under the union bound and the Rust verifier rightly rejects.

## 1. Batch scaling (sweep=batch)

### 1a. Per-proof size l at B = 4096 (axis=l), non-ZK interactive, 2^-128

| B (VUs) | l | N_sub | VUs/proof | t | t.total s (med/3) | min-max | R_proved flop/s | overhead vs 312e12 | peak dev GiB | proof MB | Rust verify s | Rust | run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4096 | 4096 | 98 | 42 | 199 | 2.310 | 2.295-2.316 | 5.45e+06 | 5.73e+07 | 0.7 | 322 | 6.4 | 294/294 | `r20260922-213247-f7b4` |
| 4096 (canonical) | 16384 | 25 | 170 | 196 | 1.017 | 1.015-1.018 | 1.24e+07 | 2.52e+07 | 2.6 | 111 | 3.0 | 75/75 | `r20260922-214319-c226` |
| 4096 | 32768 | 13 | 341 | 195 | **0.943** | 0.928-0.980 | **1.33e+07** | **2.34e+07** | 5.2 | 78 | 2.4 | 39/39 | `r20260922-214252-b33c` |
| 4096 | 65536 | 7 | 682 | 193 | 2.320 | 2.317-2.347 | 5.42e+06 | 5.75e+07 | 29.5 | 64 | 2.3 | 21/21 | `r20260922-213734-86df` |
| 4096 | 131072 | 4 | 1365 | 192 | 2.574 | 2.573-2.667 | 4.89e+06 | 6.38e+07 | 58.9 | 62 | 2.4 | 12/12 | `r20260922-213812-eae9` |
| 4096 | 262144 | 2 | 2730 | 191 | CUDA OOM | | | | >79 | | | | `r20260922-213900-fd64` (failed) |

`split.encode_seconds` tells the story: 0.09 s (l = 16384), 0.16 (32768), **1.42 (65536)**, 1.70 (131072) -- the
`encode_simt` kernel needs 4·l bytes of shared memory per tile and stops at l = 32768 on the H100's 227 KB; above it the
prover uses the torch NTT path.  Duplicate/noisy runs kept in the store and labelled `superseded_by`: `r20260922-213354-0e56`
(l = 16384 duplicate, 1.015 s), `r20260922-214058-42e6` (l = 32768, reps 1.97/5.19/8.33 s right after the l = 131072 run;
re-run `-b33c` is 0.93-0.98 s).

### 1b. Total VUs at l = 32768 (axis=B), non-ZK interactive, 2^-128

| B (VUs) | l | N_sub | VUs/proof | t | t.total s (med/3) | min-max | R_proved flop/s | overhead vs 312e12 | peak dev GiB | proof MB | Rust verify s | Rust | run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1024 | 32768 | 4 | 341 | 192 | 0.296 | 0.295-0.299 | 1.06e+07 | 2.94e+07 | 5.2 | 24 | 0.8 | 12/12 | `r20260922-214421-6be7` |
| 4096 | 32768 | 13 | 341 | 195 | 0.943 | 0.928-0.980 | 1.33e+07 | 2.34e+07 | 5.2 | 78 | 2.4 | 39/39 | `r20260922-214252-b33c` |
| 16384 | 32768 | 49 | 341 | 198 | 3.498 | 3.477-3.575 | 1.44e+07 | 2.17e+07 | 5.2 | 296 | 9.2 | 147/147 | `r20260922-231034-0693` |
| **65536** | 32768 | 193 | 341 | 200 | 13.789 | 13.782-29.119 | **1.46e+07** | **2.14e+07** | 5.2 | 1171 | 36.5 | 193/193 | `r20260922-214610-4de4` |
| 262144 | 32768 | 769 | 341 | 203 | 60.162 | 54.613-75.088 | 1.34e+07 | 2.33e+07 | 5.2 | 4700 | 146.4 | 769/769 | `r20260922-214847-0a45` |
| 1048576 | 32768 | 3076 | 341 | 206 | 239.626 | 205.913-246.413 | 1.34e+07 | 2.32e+07 | 5.2 | 18936 | 591.9 | 3076/3076 | `r20260922-215700-5bc1` |

Device memory is flat at 5.2 GiB (one sub-batch at a time; B costs host memory and time only).  **Saturating B = 65536**:
R_proved improves 1.38x from B = 1024 to 65536 and does not improve after (1.34e7 at 262144 and 2^20 -- within the
run-to-run noise, but not above 1.46e7).  The rep-to-rep spread grows with B (B = 65536: one rep 29.1 s vs 13.8 s; B = 2^20:
205.9-246.4 s): the prover is host-bound between GPU kernels (Python driver, hint generation, per-sub-batch Merkle/openings
serialisation; `split.witness_torch` + `split.tests` are 64% of t.total at B = 262144) and the pod's host (208-thread Xeon,
load average 15-20 from other tenants) is noisy; `--exclusive` only serialises our own runs.  First B = 16384 run
`r20260922-214449-6fea` (5.12/5.46/6.69 s) is labelled `superseded_by` the re-run above.  B > 4096 recycles the 4096 tier ids
(VU i = tier instance i mod 4096, `B_real = 4096` in the fingerprint and `instances.range = [0, 4096]`): the bench has no
seeded synthetic VU generator, and I did not add one.

### 1c. ZK at B = 4096 and at the saturating B = 65536 (axis=zk), 2^-128

| B (VUs) / mode | l | N_sub | VUs/proof | t | t.total s (med/3) | min-max | R_proved flop/s | overhead vs 312e12 | peak dev GiB | proof MB | Rust verify s | Rust | run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4096 FS-ZK (HVZK) | 16384 | 25 | 170 | 288 (D=7) | 1.180 | 1.153-1.192 | 1.07e+07 | 2.93e+07 | 3.3 | 165 | 3.8 | 75/75 | `r20260922-222741-f7ea` |
| 4096 int-ZK | 16384 | 25 | 170 | 197 | 1.062 | 1.061-1.067 | 1.18e+07 | 2.63e+07 | 3.3 | 122 | 3.0 | 75/75 | `r20260922-222822-2f22` |
| 4096 FS-ZK (HVZK) | 32768 | 13 | 341 | 285 (D=7) | 1.159 | 1.147-1.173 | 1.09e+07 | 2.87e+07 | 6.5 | 115 | 3.1 | 39/39 | `r20260922-222900-192f` |
| 4096 int-ZK | 32768 | 13 | 341 | 195 | 1.037 | 1.035-1.052 | 1.21e+07 | 2.57e+07 | 6.5 | 89 | 2.5 | 39/39 | `r20260922-222938-936a` |
| 65536 FS-ZK (HVZK) | 32768 | 193 | 341 | 291 (D=7) | 17.347 | 17.347-17.402 | 1.16e+07 | 2.69e+07 | 6.5 | 1729 | 46.6 | 193/193 | `r20260922-223005-ebe2` |
| 65536 int-ZK | 32768 | 193 | 341 | 201 | 14.635 | 14.597-15.051 | 1.38e+07 | 2.27e+07 | 6.5 | 1337 | 37.2 | 193/193 | `r20260922-223242-d449` |

ZK cost over the non-ZK control on this card: interactive +4% (l = 16384) / +10% (l = 32768, B = 4096) / +6% (B = 65536);
Fiat-Shamir +16% / +23% / +26% -- the FS reparameterisation (2^60 hash queries: t ~ 288-291 instead of ~196-200, D = 7,
t_pad = 512) costs more than the masking.  Interactive-ZK transcripts are labelled `not-transferable` by the verify lane
(D7); the FS proofs are `accepted` from bytes.

## 2. Soundness (sweep=soundness): B = 4096, l = 16384 (canonical), non-ZK interactive

| target | achieved log2 (union over 25) | per-proof log2 | rate k/n | opened columns t | D | t.total s | R_proved | overhead | proof MB | Rust verify s | Rust (--soundness-bits) | run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2^-80 | -80.11 | -84.75 | 16384/65536 = 0.25 | 125 | 4 (BabyBear^4) | 0.885 | 1.42e+07 | 2.19e+07 | 71.8 | 2.10 | 75/75 (80) | `r20260922-230654-9512` |
| 2^-100 | -100.45 | -105.10 | 16384/65536 = 0.25 | 155 | 6 | 0.989 | 1.27e+07 | 2.45e+07 | 95.8 | 2.75 | 75/75 (100) | `r20260922-230741-8ea0` |
| 2^-128 | -128.25 | -132.90 | 16384/65536 = 0.25 | 196 | 6 | 1.017 | 1.24e+07 | 2.52e+07 | 110.8 | 2.98 | 75/75 (128) | `r20260922-214319-c226` |

The code rate is fixed by `--rate-log2 2` (n = 4l) at every target; the target only moves the opened-column count t
(Appendix C with the per-proof target -128 - log2 25 = -132.64, etc.) and the extension degree (D = 4 at 2^-80).  Prover
time barely moves (-13% from 2^-128 to 2^-80): t only enters the openings/Merkle-path serialisation; proof size scales with
t (72 -> 111 MB).  First attempts `r20260922-223447-90bc` / `-57dd` are in the store as `verified=rejected`,
`superseded_by` the rows above: the wrapper called `ligero-verify` without `--soundness-bits`, so the verifier (default
128) refused "parameters give 2^-80.11 over 25 sub-batches; requested 2^-128" -- correct behaviour, wrong request; fixed in
commit e905529 (the target is now passed and recorded as `verifier.soundness_bits_requested`).  The verify lane
independently reached the same conclusion (its `verify_note` on `-90bc`) and re-verified those proofs at 80 bits.

## 3. K (sweep=K): not run

`bench_vu` proves the frozen tier's relation only: `K = STEP * STEPS = instances.STEP * instances.STEPS = 16 * 96 = 1536`
is a module constant of `backends/direct/ligero/vu.py` / `run.py`, the constraint system is compiled for 96 transitions,
and the instance set has one VU tier (`vu-k1536`).  There is no K knob; adding one would mean a new instance tier and a
new compiled system, which the spec said not to hack.  No K artifacts.

## 4. Sub-batching (sweep=subbatch): B = 4096, non-ZK interactive, 2^-128

The bench has no `N_subbatches` knob: the number of proofs is `ceil(B / per_proof_vus)` with `per_proof_vus = floor(l·16 /
1536)` -- `--batch` (= l, columns per proof) is the knob, so the sweep is over l (the 1a rows are the same axis).  Smallest
l the SIMT encoder accepts: 256 (`l >= 256`, power of two; 2 VUs per proof, 2048 proofs); largest that fits: 131072 (4 proofs).

| l | N_sub (split.subbatches) | VUs/proof | t | per-proof log2 | union log2 (achieved) | t.total s | split.hints / witness / encode / merkle / tests / openings s | R_proved | overhead | proof MB | Rust verify s | Rust | run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 256 (most) | 2048 | 2 | 205 | -138.54 | **-127.54** | 37.286 | 2.87 / 19.35 / 0.35 / 0.63 / 10.02 / 3.88 | 3.37e+05 | 9.25e+08 | 6091 | 6.8 | **0/2048** | `r20260922-223541-8985` (failed) |
| 512 | 820 | 5 | 204 | -138.10 | -128.42 | 15.301 | 1.18 / 7.94 / 0.16 / 0.25 / 4.06 / 1.62 | 8.22e+05 | 3.79e+08 | 2453 | 39.4 | 820/820 | `r20260922-230808-6267` |
| 1024 | 410 | 10 | 202 | -136.86 | -128.18 | 8.204 | 0.64 / 4.07 / 0.11 / 0.13 / 2.25 / 0.95 | 1.53e+06 | 2.03e+08 | 1237 | 20.6 | 1230/1230 | `r20260922-223948-6358` |
| 4096 | 98 | 42 | 199 | -134.91 | -128.29 | 2.310 | 0.17 / 1.01 / 0.07 / 0.06 / 0.70 / 0.25 | 5.45e+06 | 5.73e+07 | 322 | 6.4 | 294/294 | `r20260922-213247-f7b4` |
| 16384 (default) | 25 | 170 | 196 | -132.90 | -128.25 | 1.017 | 0.06 / 0.29 / 0.09 / 0.05 / 0.40 / 0.09 | 1.24e+07 | 2.52e+07 | 111 | 3.0 | 75/75 | `r20260922-214319-c226` |
| 32768 | 13 | 341 | 195 | -132.22 | -128.52 | 0.943 | 0.04 / 0.18 / 0.16 / 0.05 / 0.40 / 0.08 | 1.33e+07 | 2.34e+07 | 78 | 2.4 | 39/39 | `r20260922-214252-b33c` |
| 65536 | 7 | 682 | 193 | -130.87 | -128.06 | 2.320 | 0.04 / 0.13 / 1.42 / 0.05 / 0.53 / 0.06 | 5.42e+06 | 5.75e+07 | 64 | 2.3 | 21/21 | `r20260922-213734-86df` |
| 131072 (fewest) | 4 | 1365 | 192 | -130.19 | -128.19 | 2.574 | 0.03 / 0.11 / 1.70 / 0.06 / 0.55 / 0.04 | 4.89e+06 | 6.38e+07 | 62 | 2.4 | 12/12 | `r20260922-213812-eae9` |

Security union bound: each proof is sized to `per_proof_target = -128 - log2 N_sub` (t grows ~1-2 columns per doubling of
N_sub: 192 at N = 4 -> 205 at N = 2048) and the reported `achieved_log2` is the union over N_sub; proof bytes grow with
N_sub because every proof pays its own t opened columns + Merkle paths (62 MB at N = 4, 6.1 GB at N = 2048).  **l = 256 does
not meet the target**: `config_for` sizes t with the Appendix-C terms at k = l, while `soundness()` (and `ligero-verify`)
book the non-ZK code with k = l + 1 (`validate` needs l < k); the gap is ~t/(2l)·log2 e bits -- 0.46 bit at l = 256, 0.23 at
l = 512 (absorbed by the integer-t slack), < 0.03 bit at l >= 4096 -- so at l = 256 the union lands at 2^-127.54 and the
independent verifier rejects all 2048 proofs ("parameters give 2^-127.54 over 2048 sub-batches; requested 2^-128").  The
Python live verifier reports "passed" because it checks the transcript, not the target.  Not fixed here (a prover
parameterisation change is out of this lane's scope); noted as a bench defect at small l.  The largest sub-batch count that
meets 2^-128 is 820 (l = 512).

## 5. RTT (sweep=rtt): not run

`bench_vu` has no `--rtt-ms` (its `bench-vu` parser: `--root --device --target --rate-log2 --batch --out --zk --mode
--hints --reps --run-id --total-vus --hvzk-label --dump-dir --dump-reps`) and the e2e/latency path
(`verity_numerical.bench.latency`, lane b-e2e-v2) is a different tool that was not part of this lane.  The only e2e number
here is `e2e_0ms` = prove_wall + Rust verify_wall in every `bench-result/v1`.

## 6. Milestone (sweep=milestone, milestone=1M-vu): 2^20 VUs, l = 32768, 2^-128

| run | mode | class | VUs | proofs | t / D | achieved | t.total s | R_proved | overhead | proof GB (MB/proof) | Rust verify s (ms/proof) | Rust | Python verify s | peak GiB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `r20260922-224216-f153` | Fiat-Shamir ZK | COMPLETE_HVZK_BACKEND (transferable) | 1,048,576 | 3076 x 341 | 297 / 8 | 2^-128.46 | **323.4** (1 rep) | 9.96e+06 | 3.13e+07 | 29.90 (9.72) | 811.7 (264) | **3076/3076** | 225.2 | 6.6 |
| `r20260922-231134-43fa` | interactive ZK | COMPLETE_ZK_BACKEND | 1,048,576 | 3076 x 341 | 207 / 6 | 2^-128.31 | **250.5** (1 rep) | 1.29e+07 | 2.43e+07 | 21.59 (7.02) | 591.1 (192) | 3076/3076 | 150.6 | 6.5 |
| `r20260922-215700-5bc1` (control) | interactive non-ZK | NON_ZK_PROOF_DIAGNOSTIC | 1,048,576 | 3076 x 341 | 206 / 6 | 2^-128.09 | 239.6 (med/3) | 1.34e+07 | 2.32e+07 | 18.94 (6.16) | 591.9 (192) | 3076/3076 | 166.0 | 5.2 |

The milestone runs use `--reps 1` (the ZK median-of-3 at the saturating B is §1c; a 2^20 FS-ZK rep is 5.4 min of proving
plus ~14 min of dumping 30 GB and Rust-verifying 3076 proofs, so three reps did not fit the budget).  The FS-ZK proof set
is 3076 independent statements/proofs against one `system.bin` (229,581 B, sys_id `44cb05b9…`); each proof commits its own
341 VUs (statement = the a/b/c_in/y_out of those VUs, `ligero-statement/v2`) and the batch's soundness is the union bound
2^-140.05 · 3076 = 2^-128.46.  Retained on the laptop and in the store (`ligero-proof-dump/v1`, §8): `system.bin`,
`rep1/sub_00.stmt` (2,162,746 B, VUs 0-340), `rep1/sub_00.proof` (9,721,600 B, sha256 `eb00b762…`) -- re-verified on the
laptop with a fresh `cargo build --release` of `backends/ligero-verify`: `accepted`, total 0.152 s, per-proof 2^-140.050,
union 2^-128.464.  The other 3075 proofs were deleted after verification (manifest keeps sha256 + bytes of each; the
verdicts are in `verify/independent.json`).  D = 8 at 2^20 (D = 7 at B <= 65536): the field terms (n + 3) / p^D must survive
the 2^60 FS factor and the 1/3076 per-proof share.

Cross-device caveat, once more: 312e12 is the Ampere target's (A100) BF16 peak and these are H100 prover times; the
canonical same-device cell is the A100 lane's.  R_proved here = 2·1536·B / t.total with B the *proved* VU count (the tier's
4096 instances recycled 256x; the prover does not know they repeat -- every sub-batch is committed and proved independently).

## 7. Bench limits / discrepancies from the spec

1. **Saturating B vs saturating l.**  The spec asked for the B where R_proved stops improving; on this prover R_proved is
   set mostly by l (columns per proof, the sub-batch size) -- l = 32768 is 1.07x better than the canonical 16384 and 2.5x
   better than 65536 (SIMT encoder shared-memory limit, then torch fallback) -- and B only amortises fixed cost, saturating
   at 65536 (1.46e7) with a slight *decline* to 1.34e7 at 2^18-2^20 that is inside the host-noise band.
2. **Instances beyond the tier**: `vu-k1536` has 4096 ids; B > 4096 recycles them (`B_real = 4096`; fingerprint
   `instances.range = [0, 4096]` plus a `note`).  There is no seeded synthetic VU generator in the bench; I did not add one.
3. **K = 1536 only** (§3).  **No `--rtt-ms`** (§5).
4. **No `N_subbatches` knob**: sub-batching is `--batch` = l (§4).  `split.*` measurements exist in the raw
   `bench_vu.json` (in the artifact's `run_files` tree), not in the `bench-result/v1` measurement list.
5. **`ligero-verify --soundness-bits`** defaults to 128; the wrapper did not pass the target -> the 2^-80 / 2^-100 first
   attempts were "rejected" (correctly, per the request).  Fixed (commit e905529, test in `bench_result_test.py`); the
   rejected artifacts stay in the store labelled `verified=rejected`, `superseded_by=<re-run>`.
6. **l = 256 misses 2^-128 by 0.46 bit** (k = l vs k = l + 1 between `config_for` and `soundness()`); the Rust verifier
   rejects; artifact kept, `verified=rejected`, `note=` explains.  Affects only l < ~1024.
7. **l >= 65536** leaves the SIMT encoder (227 KB shared memory on H100; the l = 65536 tile needs 256 KB) and uses 30-59 GiB;
   **l = 262144 OOMs** (`r20260922-213900-fd64`, no result artifact).
8. **Host noise**: rep spread up to 2x on the first rep of large runs (B = 65536: 29.1 s vs 13.8; l = 32768 B = 4096 first
   run 1.97-8.33 s).  Medians and min-max are reported; two noisy runs were re-run and the originals labelled
   `superseded_by`.  The pod's host showed load average 15-20 from other tenants throughout.
9. **Milestone reps = 1** (budget), and its `prove_wall_min == prove_wall_max == prove_wall`.
10. `research data push` has no `--preserve` flag (the spec's `push --preserve`): pushing an artifact *is* preserving it (PRESERVED
    = blobs + manifest read back from the remote); labels are local-store files by design and are not pushed.
11. The verify lane (`by=verify`) independently re-verified this lane's dumps as they landed and wrote its own
    `verified=accepted|rejected|not-transferable` + `verify_note` labels; on every artifact it had labelled by the time
    this note was written the two agree (including the two soundness first attempts, which it re-checked at 80 bits).

## 8. Store

Every `bench-result/v1` (28 results, 3 of them `status=failed` and kept) is labelled `candidate=B-Ligero`,
`sweep=batch|soundness|subbatch|milestone`, `axis=l|B|zk` (batch), `same_device=false`, `hardware=h100`,
`mode=interactive|fiat-shamir`, `zk=true|false`, `proof_class=…`, `independently_verified=true|false`,
`verified=ligero-verify|rejected`, `campaign=r21-b-sweep`, `stage=<launch stage>`; the milestone results also
`milestone=1M-vu`; superseded/noisy ones `superseded_by=<run>` and `note=…`.  Pushed with `research data push --pending`
(PRESERVED); snapshot **`b-sweep-h100-v1`** = `art:5b72a1447724d4ec9a29b88dac519180a41f128476405fc7c35f7bfe11b9cdb8` (dataset-snapshot/v1, 34 members, PRESERVED) (members: every result above + the proof-dump artifact), pushed
`--preserve`.  Milestone proof artifacts (each `--ref result=<the bench-result>`; the tree kinds are new names, the store accepted them as
unknown kinds):

* FS-ZK: dump `art:50368595a8db6c8463d83a5d8acfc66a93aa25a1ad98732d6252ca1bf841c876` (`ligero-proof-dump/v1` tree: `system.bin`, `manifest.json`,
  `rep1/sub_00.stmt`, `rep1/sub_00.proof`, `laptop_verdict.json`), proof `art:acddcbd7a67ccae068acac3bbd8fe9f36fc2bb7cb4cc2af0196d9812c418f6ad` (`proof/v1`, payload = the 9,721,600-byte proof,
  meta statement/system digests + params), laptop verdict `art:c6c5ea917ec940778cbdfc8267a3a91c21bb751f92d499dd14f142a284bb9283` (`verification-verdict/v1`, PASS, 0.135 s).
* interactive-ZK: dump `art:df284324f43bcd699c1d1cb73cb57220a410020b0780f70547a9b866eab493f5` (+ `rep1/sub_00.coins`), proof `art:00d6a99916c973b1033e0991b604e2a00cb740f8b13b2faffd39e4bfc882fa96`, laptop verdict `art:ee484e58cc49b45262b21bfe6cb3dd4ffb7b49bcb8f82658a95c6122d32ceadc` (PASS with the dumped coins, 0.097 s;
  D7: not transferable).

Result artifacts (run -> art):

- `r20260922-213247-f7b4` batch_l-axis sweep=batch passed -> `art:bae3fcc1f86869d7b09c6ccf41afe38eedf4b1105465b589a68ef97b5444c912`
- `r20260922-213354-0e56` batch_l-axis sweep=batch passed -> `art:4641e267ab6319942825eb9a29c2f7f169e531bede1ee735dd316203adaa541c`
- `r20260922-213734-86df` batch_l-axis sweep=batch passed -> `art:505294c96af6d4eda88548bdeeed0342022f2c1dbae83c95adc7ef1aaaae1914`
- `r20260922-213812-eae9` batch_l-axis sweep=batch passed -> `art:a43efa19d60ecb3f393925039a6e36146b7f598c6a4feb38fce78241e1a93976`
- `r20260922-214058-42e6` batch_l-axis sweep=batch passed -> `art:20f80d2fa4103751422f4825d1a091e0e7ce2e6283304a81b334bd0e9559f9a0`
- `r20260922-214252-b33c` batch_l-axis sweep=batch passed -> `art:992705772db9add2163eca5740913682a1ab73091bd72333227aa93069925df6`
- `r20260922-214319-c226` batch_l-axis sweep=batch passed -> `art:d9887391c2098c63c3490cca7e950d1e2409dc151aad397c2023ab3c85c45318`
- `r20260922-214421-6be7` batch_B-axis sweep=batch passed -> `art:74fb7e4045c2224db3ba7f91a9cfa2c19596aee4e12b3501e516ffb8ea163bea`
- `r20260922-214449-6fea` batch_B-axis sweep=batch passed -> `art:d746ccba0bd2c6183c7d3153d3e31b026190cc644f6280c107a15b0b4ef82986`
- `r20260922-214610-4de4` batch_B-axis sweep=batch passed -> `art:4a029a9a9fb4a215674a6eb2bfed2531cfb607f87794557519982afd697b75b7`
- `r20260922-214847-0a45` batch_B-axis sweep=batch passed -> `art:bde11a76222f0f1e3ee7645dd23bf39d4868c88ecbae1d821e0044ea661284ad`
- `r20260922-215700-5bc1` batch_B-axis sweep=batch passed -> `art:566b388e98a64e70088d03c87c6c05b1a5556346d8ac58e5401b001bc9a8b54c`
- `r20260922-222741-f7ea` zk_fs_l16384_B4096 sweep=batch passed -> `art:0db4c28569d82455d5078b19e64a21a5ac5a43e2ea84f376ed08330fb9be4f74`
- `r20260922-222822-2f22` zk_int_l16384_B4096 sweep=batch passed -> `art:da1168f4f09f14eebad17e7c956412944e11fe5399fa0eb19db45bcdf1d29af6`
- `r20260922-222900-192f` zk_fs_l32768_B4096 sweep=batch passed -> `art:b0eb9f5fa41dde2ad04dc4397fb2d9681ccebf664fb1a034e9ab0c0445f906c7`
- `r20260922-222938-936a` zk_int_l32768_B4096 sweep=batch passed -> `art:d33ee4c2652d0fe6f918d7e4f79f17569fe40437a9c2b1f74f6e3b0ab66287b9`
- `r20260922-223005-ebe2` zk_fs_l32768_B65536 sweep=batch passed -> `art:b3888b8bf1ae45772774b2a7d534060bcebbb6ff285b272a7e9b5ce978f7f1cf`
- `r20260922-223242-d449` zk_int_l32768_B65536 sweep=batch passed -> `art:b5440e7db3964f541cf97734da5bf3aa8d46bea0ba7d3cd44c9ff5dfe3fb9580`
- `r20260922-223447-90bc` snd_t80_l16384_B4096 sweep=soundness failed -> `art:6e80c1ff82cd5651e6308e5bf9b4efb8e89124aec5e7cfc0c620b8273b1ff3b4`
- `r20260922-223514-57dd` snd_t100_l16384_B4096 sweep=soundness failed -> `art:2c02d4d4c0d35614f1b01211ae0d14529ac562af5bd5413776f7d3465bf114fd`
- `r20260922-223541-8985` sub_l256_B4096 sweep=subbatch failed -> `art:80961c3170534d59adcb8b513841813ef7eb9683b29453ccaa87478999cd9fe1`
- `r20260922-223948-6358` sub_l1024_B4096 sweep=subbatch passed -> `art:373d523200e38ca96c5ad2e2a9629f4ddeb9b7e1ae02b7138520f7ee4ae0a332`
- `r20260922-224216-f153` milestone_zk_fs_l32768_B1048576 sweep=milestone passed -> `art:2d46e6b1026a4f36d90215b426670ffcc58497f81a330a0387782b9bf01e4faa`
- `r20260922-230654-9512` snd_t80_l16384_B4096_v2 sweep=soundness passed -> `art:7f9260bd9eeb5ccb717dd1efdb0dd30c5642eff7761ef2cc4734f0a69fe72d63`
- `r20260922-230741-8ea0` snd_t100_l16384_B4096_v2 sweep=soundness passed -> `art:9418e28097585dcef6a5d8bc20b1b29d807aa25f1587f35805a5238eba2f1c11`
- `r20260922-230808-6267` sub_l512_B4096 sweep=subbatch passed -> `art:076adaa95e9526a71e3b92ac1f9eca540e998a791d080e3168439b855b130520`
- `r20260922-231034-0693` batch_l32768_B16384_nonzk_v2 sweep=batch passed -> `art:5494ea3cfd95f995986102c50b90d832633b98f431a6cc5f09a525d4d7ce79ce`
- `r20260922-231134-43fa` milestone_zk_int_l32768_B1048576 sweep=milestone passed -> `art:6f6e1b52a34b372b38463dd93467aeaa7cd3ee40198b3a115e175cf0a9e4b6aa`

## 9. How it was run

~~~
# laptop: worktree lane/b-sweep off 4987a47; store creds sourced locally only
python -m research.pods.runpod create --name vy-h100c --gpu "NVIDIA H100 80GB HBM3" --disk 100   # 21:19:53Z, $3.49/h
research run --on vy-h100c --project verity --campaign r21-b-sweep --source . --stage bootstrap -- bash bootstrap.sh
#   (uv python 3.12 venv, torch 2.6.0+cu124, cupy, blake3; rustup + cargo build --release backends/ligero-verify;
#    verity_numerical.bench.instances build -> /workspace/bench-instances/v1; pytest bench_vu_test.py)
# one point (all points are this with different flags; --exclusive, --scratch triton, --require-result):
research run --on vy-h100c --project verity --campaign r21-b-sweep --source . --exclusive --scratch triton --require-result \
  --tool bench_vu --stage batch_l32768_B65536_nonzk --env PYTHONPATH=packages/verity/src:backends/numerical/python:. -- \
  /workspace/venv312/bin/python backends/direct/ligero/bench_result.py bench-vu --mode interactive --batch 32768 \
  --total-vus 65536 --reps 3 --dump-reps 1 --keep-proofs 1 --root /workspace/bench-instances/v1 --device cuda \
  --verifier /workspace/bin/ligero-verify --threads 16
# ZK: add --zk [--mode fiat-shamir]; soundness: --target -80|-100; milestone: --total-vus 1048576 --reps 1 --dump-reps 1 --keep-proofs 1
research data pull RUN --from vy-h100c --project verity; research data label ART k v --by b-sweep --ref RUN; research data push --pending
research data snapshot --name b-sweep-h100-v1 --members art:...,art:... --note ...; research data push art:<snapshot>   # push has no --preserve flag; it preserves (blobs + manifest read back) by default
python -m research.pods.runpod terminate bfg8ge5zmwavuq
~~~

Code on the lane branch (not merged): `backends/direct/ligero/vu.py` (vectorised `marshal_ids` loader so 2^20 VUs marshal in
seconds, `--dump-reps`, honest `instances`/`B_real` when ids recycle), `run.py`/`tool.py` (`--dump-reps`, `--keep-proofs`
plumbing), `bench_result.py` (`--keep-proofs` pruning after verification; `--soundness-bits` = the bench's target),
`bench_vu_test.py` / `bench_result_test.py` (CPU-only, `importorskip`).  The prover itself is untouched.
