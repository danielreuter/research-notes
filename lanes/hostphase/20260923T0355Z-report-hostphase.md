# Lane hostphase — B-Ligero prover: host-bound phases moved to the device (protocol-, format- and Rust-identical)

Written 2026-09-23 03:55Z. Worktree `~/projects/verity-main-wt/hostphase`, branch `lane/hostphase`, based on main `5a8a744`;
commits `7336524`, `270ae85`, `d8f896c` (HEAD). `git status --short` empty; `git diff main -- backends/ligero-verify` empty
(Rust untouched); no `.md` in the repo. All changes are under `backends/direct/ligero/` (11 files, +379/-50):
`witness_device.py` (new), `witness_device_test.py` (new), `witness.py`, `hints_torch.py`, `protocol.py`, `tests_fused.py`,
`chain.py`, `merkle.py`, `relchain.py`, `run.py`, `serialize.py`.

Pod: `vy-hostphase` = RunPod `ms2c0dq167fl0f`, `NVIDIA H100 80GB HBM3` (SXM, SECURE, US-NE-1), driver 580.126.09 / CUDA 13.0, host
Intel Xeon Platinum 8470 (26 vCPU visible / 208-thread host), 172 GB RAM, 100 GB disk, $3.49/h. Created 02:30:12Z,
terminated 03:39:59Z (confirmed absent from `research pods list`): **69.8 pod-minutes ≈ $4.06** of the 2.5 h / $9 budget.
`machines.toml` entry marked TERMINATED.

TL;DR: bf16-hopper int-ZK 4096 VUs on the same pod, same seed/target, median of 3: **main 1.589 s → lane 0.727 s (2.19×)**;
overhead vs 989.4e12 native FLOP/s **1.25e8 → 5.72e7**, R_proved 7.92e6 → 1.73e7 FLOP/s. Witness 0.744 → 0.027 s
(one fused CUDA kernel instead of ~4 000 eager torch launches), hints 0.107 → 0.064 s (the CUDA graph now actually captures),
tests 0.440 → 0.342 s, openings 0.083 → 0.074 s. Everything else (encode, Merkle, ZK masks, serialization) unchanged.
Transcripts are byte-identical to main's: 64/64 `.stmt/.proof/.coins` files identical over 7 (relation, mode, zk) pairs with
replayed coins and mask keys, `ligero-verify` binary identical, pytest 43 passed / 1 skipped (+2 v2), 6/6 gates green,
Rust batch ACCEPT with `python_agree` = n on every dump tree. Not reached in the 3 h: the remaining ~0.35 s of tests
(SHAKE-256 challenge expansion on the CPU + torch NTT launch chains), ~0.07 s hints marshalling, 0.11 s Python serialization.

## 0. Runs (campaign `r21-hostphase`, all on vy-hostphase)

| run | stage | tree | state |
|---|---|---|---|
| r20260923-023702-98f2 | profile main: one 170-VU sub-batch + full 4096-VU pass, `torch.profiler` | main 5a8a744 (`src-main`, git archive) | done |
| r20260923-025922-b0cc | bitexact v1 (harness debugging: the NVRTC `%` bug surfaced here) | both | done (superseded) |
| r20260923-030235-4817 | **baseline** bf16-hopper int-ZK 4096 VUs seed 20260922 target 2^-128 reps 3 | main 5a8a744 | done |
| r20260923-030340-bf77 / -030442-7aed / -030529-ab1d | fused-kernel unit test + exactness debugging | lane | done |
| r20260923-030652-a174 | profile lane: same two profiles as 98f2 | lane d8f896c | done |
| r20260923-031046-9e90 | **bit-exactness**: 7 pairs, 64 files, + Rust digest/batch on the lane dumps | main + lane | done |
| r20260923-031323-9951, -031348-bc72, -031413-e31b, -031438-12a9, -031503-2862, -031528-8b78 | six failed launches (my driver passed `"stage rel flags"` as `--relation`; argparse rc=2 after ~20 s each, no result) | lane | failed (ignore) |
| r20260923-031611-55f1 | **lane bf16-hopper int-ZK** | lane d8f896c | done |
| r20260923-031657-a769 | lane bf16-hopper FS-ZK | lane | done |
| r20260923-031744-b10b | lane bf16-hopper interactive non-ZK | lane | done |
| r20260923-031830-65d9 | lane fp8-hopper int-ZK | lane | done |
| r20260923-031855-bef9 | lane fp8-hopper FS-ZK | lane | done |
| r20260923-031920-d2ae | lane fp8-hopper interactive non-ZK | lane | done |
| r20260923-032053-03b5 | pytest `backends/direct/ligero` + 6 relation gates | lane | done |

Bench command (b-merge-h100's exact line; `bench.sh` in the evidence dir): `python -m backends.direct.ligero.run --relation REL
bench-vu [--zk] --mode interactive|fiat-shamir --batch 16384 --total-vus 4096 --reps 3 --target -128 --device cuda
--instance-procs 16 --instances-cache /workspace/instances-cache --run-id ID --out $RD/result.json --dump-dir $RD/proofs
--dump-reps 1` (seed default 20260922; `--impl device` is the lane default, `--impl legacy` = main's torch program).

## 1. Attribution BEFORE (main 5a8a744 on the pod, run r20260923-023702-98f2)

`torch.profiler` (CPU + CUDA, `record_shapes`, `with_stack`), `protocol._Clock` laps wrapped in `record_function` ranges, one
170-VU bf16-hopper int-ZK sub-batch (l=16384, n=65536, D=6, t=197, t_pad=256; m=3292 rows, 97 hints, 552 program ops).
Un-profiled wall of the same sub-batch: 60.0 ms prove + 4.3 ms hints; under the profiler 105 ms (the profiler roughly doubles
launch cost, so read `wall` as an upper bound and `gpu` as the truth).

| phase | wall ms (profiled) | GPU kernel ms | kernel launches | graph launches | syncs (`.item/.cpu/.tolist`) | D2H MB | torch ops | verdict |
|---|---|---|---|---|---|---|---|---|
| hints (+ public-row marshalling, pre-prove) | 314.1 (4.3 un-profiled × 25 = 0.107 s/pass) | 0.66 | 377 | **0** | 22 | 0 | 2117 | **launch/CPU-bound**: the CUDA-graph capture fails silently (indexing a tensor with a Python list inside the capture) and falls back to eager; the rest is numpy→torch marshalling |
| statement (blake2b) | 1.70 | 0 | 0 | 0 | 1 | 0 | 6 | CPU hash, protocol-mandated |
| witness_torch | **62.4** (29.1 un-profiled = 0.744 s/pass) | **8.8** | **4158** | **0** | 553 | 0 | 12870 | **launch-bound**: ~4 000 eager torch kernels (~7 µs each) + 553 host syncs from Python-int constant handling; the CUDA graph never captured (poisoned by the hint capture failure: `captures_underway.empty()` assert) |
| zk_masks | 1.29 | 0.09 | 21 | 0 | 11 | 0 | 118 | sync-bound (os.urandom keys, tiny tensors), 16 ms/pass |
| encode (SIMT NTT) | 4.70 | 4.55 | 20 | 0 | 5 | 0 | 239 | **GPU-bound** (0.115 s/pass) |
| merkle (GPU BLAKE3) | 2.03 | 1.74 | 0 (cupy) | 0 | 3 | 0 | 0 | **GPU-bound** (0.048 s/pass) |
| tests_w (linear) | 15.5 | 0.89 | 138 | 0 | 7 | 0.8 | 475 | **CPU-compute-bound**: `hashlib.shake_256` expansion of the challenge rows (`_expand`) ≈ 8 ms, + `batch_modinv`/`Z_H` recomputation, + per-VU public-column index building |
| tests_quad | 5.2 | 3.30 | 151 | 0 | 1 | 0 | 410 | launch-bound + an `index_select` copy of the boolean rows (1.2 ms GPU of pure copy) |
| tests_chain | 6.0 | 0.55 | 140 | 0 | 7 | 1.6 | 731 | **launch-bound**: one kernel per (row, family, kappa) term of `chain_coefs` + the torch NTT chain for q(X) |
| openings | 6.2 | 0.03 | 2 | 0 | **41** | **8.4** | 47 | **sync/D2H-bound**: 197 Merkle paths gathered on the host, one `.cpu()` per tree level |
| serialization | — (0.119 s/pass, not inside prove) | 0 | 0 | 0 | — | 118 MB | — | CPU: Python `struct`/`bytes` packing of the v4 statement / v1 proof (~1 GB/s) |

Full 4096-VU pass under the profiler (main): total 1.744 s = witness 0.978 + tests 0.452 (w 0.280 / quad 0.090 / chain 0.083)
+ hints 0.129 + encode 0.116 + openings 0.087 + merkle 0.048 + statement 0.038 + zk_masks 0.020. Un-profiled (the baseline
row below): 1.589 s.

Conclusion before touching anything: witness (launch-bound, 47 %) and hints (launch/CPU, 7 %) are pure overhead; the tests
are ¼ launch overhead, ¼ redundant copies/inverses and ½ CPU SHAKE-256; openings are D2H syncs; encode and Merkle are the only
genuinely GPU-bound phases (0.16 s/pass together). Serialization is CPU byte packing.

## 2. What was changed (all under `backends/direct/ligero/`, protocol/format untouched)

1. **Fused witness kernel** (`witness_device.py`, `witness.IMPL = "device"`): `System.program` is compiled once per system to
   straight-line CUDA C (NVRTC via cupy `RawKernel`), one thread per column, every derived row computed and stored in program
   order with the same integer / mod-p arithmetic the torch program performs (per-term 64-bit reduction, Python-int constants
   reduced at code-generation time, `bits` on the residue, `sels` on the signed representative, `inv` by Fermat with 0→0).
   Output `W` is int32 (values < p < 2^31); the SIMT encoder, the fused tests and the mutation hooks accept it. 1 launch instead
   of 4 158; 0.744 → 0.027 s/pass. `--impl legacy` keeps main's torch program.
2. **Hint graph capture fixed** (`hints_torch._wide_index`): the wide-add index tensors are built outside the capture region, so
   the CUDA-graph capture of the vectorised hint generator succeeds (asserted by `witness_device_test.test_hints_graph_captures`).
   0.107 → 0.064 s/pass; the rest is marshalling (see §6).
3. **Tests**: `_expand` reduces the SHAKE output mod p on the device (uint32 → torch) instead of numpy; `_zh_inv_on_coset`
   caches the `Z_H` inverses per (l, n, coset) instead of a `batch_modinv` per sub-batch; `_lin_pub_index` caches the public-
   column index tensors; `tests_fused.lincomb(..., rows=...)` gains `boolcomb_rows_*` kernels that index the boolean rows
   directly (no `index_select` copy); `chain.chain_coefs` becomes one `index_add_` over a cached (row, family, kappa) term table
   (`_chain_tables`) instead of one kernel per term — same residues (exact integer sums of < 2^31 residues, reduced once).
   0.440 → 0.342 s/pass.
4. **Openings**: `merkle.open_device` gathers all 197 paths' siblings on the device (cupy take), stacks them, ONE D2H copy.
   41 → 13 syncs, 8.4 → 4.3 MB D2H; 0.083 → 0.074 s/pass.
5. Plumbing: `run.py --impl {device,legacy}` (default device), `relchain`/`serialize._manifest` record `impl` in the dump manifest
   and in `software.backend.impl` of the result.

Not changed: field, encoder, Merkle, coin handling, ZK masks (keys still `os.urandom`), statement/proof/coins formats,
`system.bin`. `ligero-verify system-digest` prints the pinned digests: bf16-hopper `sys_id 9dcc7cdc…0df4 / table 74ce68a2…469c`,
fp8-hopper `c7cbebe3…4bc3 / d5b77463…58e7` for both trees' `system.bin`.

## 3. Bit-exactness (run r20260923-031046-9e90) and correctness gates (r20260923-032053-03b5)

Harness `bitexact.py` (evidence/scripts): proves 3 sub-batches × 170 VUs of a relation from ONE source tree with
`os.urandom` replaced by a seeded SHAKE stream (seed 7), so the runner's interactive step-0 coins AND the prover's ZK mask
keys are replayed identically into both trees; writes `system.bin` + `sub_NN.{stmt,proof[,coins]}` exactly as
`relchain.bench_vu_rel` dumps them; then `sha256sum` of every file main vs lane.

| pair | relation | mode | zk | lane impl | files compared | identical |
|---|---|---|---|---|---|---|
| bf16h-int-nonzk | bf16-hopper | interactive | no | device | 10 (system + 3×stmt/proof/coins) | **10** |
| bf16h-fs-zk | bf16-hopper | fiat-shamir | yes | device | 7 (system + 3×stmt/proof) | **7** |
| bf16h-int-zk | bf16-hopper | interactive | yes | device | 10 | **10** |
| bf16h-int-zk-legacy | bf16-hopper | interactive | yes | legacy | 10 | **10** |
| fp8h-int-nonzk | fp8-hopper | interactive | no | device | 10 | **10** |
| fp8h-fs-zk | fp8-hopper | fiat-shamir | yes | device | 7 | **7** |
| fp8h-int-zk | fp8-hopper | interactive | yes | device | 10 | **10** |
| **total** | | | | | **64** | **64** |

Also in that run: the Rust `ligero-verify` built from the lane tree is byte-identical to main's (`cmp`), and Rust `batch
--target-bits 128 [--coins]` on each lane dump tree: 3/3 accepted, batch ACCEPT, system pinned (bf16-hopper / fp8-hopper).

`pytest backends/direct/ligero` (lane tree, pod): **43 passed, 1 skipped, 2 deselected** (v2 tests, run separately: 2 passed);
includes the new `witness_device_test.py` (fused kernel == torch program on bf16-hopper and fp8-hopper; hint graph captures).
Gates (`gate-vu --vus 64 --device cuda`): bf16-ampere rc=0; bf16-hopper rc=0 (2 honest sub-batches, 87 negatives, 0 failures);
bf16-hopper `--zk` rc=0; bf16-hopper `--impl legacy` rc=0; fp8-hopper rc=0 (1 honest, 92 negatives, 0 failures); fp8-ada rc=0
(1 honest, 92 negatives, 0 failures). (The laptop venv has no torch, so the suite was run on the pod only.)

## 4. Like-for-like benchmark on the same pod (4096 VUs, seed 20260922, target 2^-128, median of 3 reps)

| run | tree | relation | mode | zk | t.total s | witness | hints | tests | encode | merkle | openings | zk_masks | serialization | R_proved FLOP/s | overhead vs 989.4e12 | achieved log2 | proof MB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 030235-4817 | **main 5a8a744** | bf16-hopper | interactive | ZK | **1.589** | 0.744 | 0.107 | 0.440 | 0.115 | 0.048 | 0.083 | 0.016 | 0.119 | 7.92e6 | **1.250e8** | −128.05 | 118.0 |
| 031611-55f1 | **lane d8f896c** | bf16-hopper | interactive | ZK | **0.727** | 0.027 | 0.064 | 0.342 | 0.111 | 0.048 | 0.074 | 0.016 | 0.110 | 1.73e7 | **5.717e7** | −128.05 | 118.0 |
| 031657-a769 | lane | bf16-hopper | fiat-shamir | ZK | 0.823 | 0.029 | 0.067 | 0.383 | 0.114 | 0.049 | 0.117 | 0.017 | 0.157 | 1.53e7 | 6.475e7 | −128.04 | 158.9 |
| 031744-b10b | lane | bf16-hopper | interactive | non-ZK | 0.603 | 0.027 | 0.064 | 0.275 | 0.085 | 0.046 | 0.069 | 0 | 0.106 | 2.09e7 | 4.744e7 | −128.25 | 106.4 |
| 031830-65d9 | lane | fp8-hopper | interactive | ZK | 0.397 | 0.017 | 0.065 | 0.162 | 0.059 | 0.025 | 0.035 | 0.008 | 0.057 | 3.17e7 | 6.244e7 | −128.32 | 62.3 |
| 031855-bef9 | lane | fp8-hopper | fiat-shamir | ZK | 0.422 | 0.017 | 0.063 | 0.172 | 0.060 | 0.025 | 0.057 | 0.008 | 0.078 | 2.98e7 | 6.644e7 | −128.32 | 84.0 |
| 031920-d2ae | lane | fp8-hopper | interactive | non-ZK | 0.366 | 0.017 | 0.068 | 0.150 | 0.046 | 0.024 | 0.037 | 0 | 0.059 | 3.44e7 | 5.751e7 | −128.52 | 56.2 |

(`witness` = `split.witness_torch_seconds`; `t.witness` = witness + hints. The coordinator-verified EPYC-9554 row was 1.638 s;
this Xeon-8470 pod gives 1.589 s for the same main tree — the host-CPU dependence the spec describes.)

Every row: `contract.validate(result) == []`. `tables.reject_reasons`: int-ZK rows → only `not independently verified`;
the FS-ZK and non-ZK rows additionally list `proof_class 'COMPLETE_HVZK_BACKEND' / 'NON_ZK_PROOF_DIAGNOSTIC' is not B-Ligero's
declared class COMPLETE_ZK_BACKEND` (as b-merge-h100's did — inherent to those modes, not a defect).
Self-checks on the pod (per dump tree, rep1): runner cold Python verify n/n; `serialize verify-batch --target-bits 128` ACCEPT
(batch_log2 as in the table); Rust `ligero-verify batch --jobs 16 --threads 1 --target-bits 128 [--coins]`: 25/25 (bf16-hopper)
or 13/13 (fp8-hopper) accepted, batch ACCEPT, system pinned, **`python_agree` 25/25 resp. 13/13, 0 disagree**
(`evidence/<run>/{python_verify_batch_rep1,rust_batch_rep1}.json`).

## 5. Artifacts (all pushed to R2; `research data push --pending` reported nothing missing afterwards)

| run | result | run-files (blobs) |
|---|---|---|
| 030235-4817 baseline main | `art:4c56b1409ad0b90ea141ad61a8ed768aebf12a9874eeef43a78931ed7ed401fa` | `art:ee6a60dc3577a84353a001d6d2814e3095b56187308eb4d23bf177e4d03b9e3f` (78) |
| 031611-55f1 lane bf16h int-ZK | `art:5807c8b91188af7451aea0a7d6885d49c249662eba18d3214c43e4b4a5364deb` | `art:d6b593943f7d7741f0def4ac734fff4bd0dca27ed83ef8e1d8db0de5c9bc71ed` (78) |
| 031657-a769 lane bf16h FS-ZK | `art:ae030d7262d035a5c6a3e92208ba97fae89594aef509b8c1ea5d7d59b6c5de31` | `art:8f1b17f6549bc2124fa451a4a411bd8e9642adaf4836dd69991a9b02652e8647` (53) |
| 031744-b10b lane bf16h non-ZK | `art:da1f777e1b05c93323e7dc76a216ce86d87516048d8ec32f22d0b1390fb7fb30` | `art:2c069337a18e7629814c207aba7cee7b930fe5df60c05c83cf8f6f849dbc7047` (78) |
| 031830-65d9 lane fp8h int-ZK | `art:4729f223d0110510ff62c7ec297980083cb4fd7b800e8ccbb1d517d8ca763da1` | `art:306b3962c0e97e87cdf04cbc55e14940457dafe38368c80b7f758d349f57d1d0` (42) |
| 031855-bef9 lane fp8h FS-ZK | `art:617b2cf7ec6ec6127c6faf6a148bf818dae6902236f4645212b9ef99dbad2cd2` | `art:90fe6f049bd044f6974b583ad80d97d2e0267c436c770e103af690d4eabb5edc` (29) |
| 031920-d2ae lane fp8h non-ZK | `art:3f4bea27a3125d0d1ba870151ce5acc742e867c50cc3b668ec24773263de5904` | `art:3d48145dcee4d03a5d0fa460cf7134f50f7da7d8822b59f90dd464a3337d8174` (42) |

Snapshot **`hostphase-v1` = `art:89c953806a6a23243c4d4d63a35be6b19f3a8d94ced3f6dac5fe5f8d2a30db8f`** (14 members: the 7 results
+ 7 run-files). Run-files contain `proofs/system.bin`, `manifest.json`, `rep1/sub_NN.{stmt,proof[,coins]}` (`--dump-reps 1`, as
b-merge-h100), result.json, stdout/stderr, the two verify JSONs. Profile / bit-exactness / gate runs were pulled too
(98f2, a174, 9e90, 03b5 …) — their result/run-files ids are in `evidence/pull.log`. Labels on each result, `--by hostphase --ref
<run>`: `campaign=r21-hostphase candidate=B-Ligero track=B scope=vu hardware=… relation mode zk proof_class authentication=excluded
B K soundness instances_dataset instances_tier seconds_per_vu overhead label note=…` (note carries host CPU / VRAM / peak device
/ load, the self-check numbers and the bit-exactness reference). **No `verified=` labels written.** Local store stayed at
> 4 GB free throughout (checked before each pull); no dump trees were fetched with `research fetch --all`.

## 6. What is still host-bound (lane tree, profile r20260923-030652-a174, per 170-VU sub-batch; ×25 per pass)

| phase | wall ms | GPU ms | launches | syncs | D2H MB | why it is still on the host / what would fix it |
|---|---|---|---|---|---|---|
| tests_w | 10.5 (0.21 s/pass) | 0.74 | 47 | 5 | 0.8 | **`hashlib.shake_256` expansion of the linear-test challenge rows** (≈8 ms CPU, sequential, protocol-mandated: coins → coefficients must match the verifier byte for byte). Fix: a GPU Keccak-f[1600] SHAKE-256 kernel reproducing hashlib's stream (deterministic, trivially testable). Same cost recurs in tests_quad/chain. |
| tests_chain | 5.9 (0.10 s/pass) | 0.55 | 140 | 7 | 1.6 | the torch NTT chain for q(X) (launch-bound: 140 small kernels); a CUDA graph over `chain_test` or the SIMT encoder's NTT would remove it |
| tests_quad | 4.0 (0.06 s/pass) | 1.92 | 26 | 1 | 0 | half real work (`boolcomb_rows`, `quad`), half SHAKE |
| hints + marshalling (pre-prove) | 33.7 (0.07 s/pass) | 0.64 | 34 | 21 | 0 | the graph runs in 0.6 ms; the rest is `relchain` marshalling numpy public rows → torch, H2D, per-VU bookkeeping, `hints_tensor` re-stacking. Fix: keep the instance tensors resident on the device for the whole run (they are re-uploaded per sub-batch). |
| openings | 3.6 (0.08 s/pass) | 0.10 | 2 | 13 | 4.3 | now one D2H per sub-batch for the Merkle paths, but the opened columns (`U[:, cols]`) and the per-tree roots are still separate `.cpu()`s; fold into the same staging buffer |
| statement (blake2b) | 1.6 (0.04 s/pass) | 0 | 0 | 1 | 0 | CPU hash of the statement bytes — protocol-mandated; could overlap with encode on a side thread |
| zk_masks | 1.0 (0.02 s/pass) | 0.09 | 21 | 11 | 0 | os.urandom + 11 tiny syncs; batch the mask key derivation |
| serialization | — (0.11 s/pass) | 0 | 0 | — | 118 MB | Python `struct` packing of v4 statement / v1 proof at ~1 GB/s; a device-side packer into the exact byte layout + one `cudaMemcpy` per sub-batch would make it a memcpy (~0.01 s) |
| witness | 1.3 | 0.75 | 3 | 1 | 0 | done (the one sync is the fused kernel's completion) |
| encode / merkle | 4.5 / 2.0 | 4.3 / 1.75 | 19 / — | 5 / 3 | 0 | genuinely GPU-bound (0.16 s/pass) |

Full-pass profile of the lane tree: 0.693 s = tests 0.364 + encode 0.112 + openings 0.079 + hints 0.073 + merkle 0.049 +
statement 0.039 + witness 0.029 + zk_masks 0.019 (+ serialization 0.11 outside prove). Realistic next floor with the items
above: ≈ 0.16 (encode+Merkle) + 0.05 (device tests incl. GPU SHAKE) + 0.03 (openings/serialization memcpy) + 0.03 (witness/hints)
≈ 0.27–0.30 s, i.e. the spec's 0.25–0.4 s ceiling is reachable but needs the GPU SHAKE-256 and the device serializer; both are
transcript-neutral and can be A/B'd with the same `bitexact.py` harness.

## 7. Wrong / surprising in the spec, and merge notes for the coordinator

- **main's witness "CUDA graph" never ran.** On main the hint generator's graph capture fails (Python-list indexing inside the
  capture), which leaves CUDA's capture state poisoned so the witness graph capture also fails (`captures_underway.empty()`
  INTERNAL ASSERT) and both fall back to eager — silently. Main's 0.84 s witness figure is 4 158 eager launches, not a graph.
  `test_hints_graph_captures` now guards this.
- **`witness_device.py` first shipped without compiling**: `%`-formatting the CUDA source (which is full of `%` modulo operators)
  raised at import and the module fell back to legacy — the bitexact v1 run passed for the wrong reason (both trees ran the same
  code). Fixed in `270ae85` (`@THREADS@` placeholder); the fused-kernel unit test now asserts `fused_for(...) is not None`.
- **Bit-exactness needs replayed randomness**: FS-ZK / int-ZK dumps differ between runs by construction (`os.urandom` mask keys
  and the runner's interactive coins). The spec's "same seeds/coins" is only achievable by seeding `os.urandom` in-process
  (`bitexact.py`) — the CLI has no seed for the mask keys. Consider a `--mask-seed`/`--coins-file` for A/B use (non-production).
- **`software.backend.commit` is null in every result** (main's and mine, also b-merge-h100's): the shipped tree is a git
  archive, so `research run`'s `--source-identity` knows the commit but the result does not. The `note=` label carries it.
- `research data push --preserve` does not exist (`--pending --jobs` only); `--pending` alone was used and re-checked.
- `tables.reject_reasons` is not "only not independently verified" for HVZK / non-ZK rows (proof-class mismatch is also listed);
  that holds for the int-ZK rows only.
- Pod host is a Xeon Platinum 8470, not the EPYC 9554 of the verified row (same GPU SKU); the baseline reproduces at 1.589 vs 1.638 s.
- SSH ingress to this pod was fine (source shipped in seconds); no R2-scratch detour was needed.
- **Merge conflict ahead**: main has moved 14 commits (`24bd337`, FP4 relation) and rewrote `chain.chain_coefs` for multi-
  component chain ends (`end_terms`/`end_values`, `END_FAMILIES = (6, 0, 1)`); my `chain_coefs` rewrite conflicts textually.
  Resolution that keeps my vectorisation: in `_chain_tables` replace the `ch["y16"]` loop by `for Y, fam, _, _ in end_terms(ch)`,
  and because components 1, 2 reuse families 0, 1 under the END mask (not the link mask), make the mask matrix 9 rows —
  `maskmat = stack([link×3, start×3, end, end, end])`, `rm = (rc.index_select(1, tensor([0,1,2,3,4,5,6,0,1])) * maskmat) % P`
  — and point the end terms of component x at virtual family `6 + x` (i.e. 6, 7, 8); `rhs` then adds
  `(rm[:, 6+x, :] * ((yv - Y.c) % P)).sum(1)` per `(Y, yv) in zip(end_terms, end_values(ch, y16_pub))`. For single-`y16`
  systems this is exactly the current code (transcripts unchanged); the FP4 tests on main cover the rest. `protocol.py`,
  `run.py`, `serialize.py` auto-merge.

## 8. Merge of main into lane/hostphase + validation (coordinator request, 2026-09-23 03:55–04:25Z)

Merge commit **`ef17cc5`** = `git merge main` at main `24bd337` (FP4 relation `backends/direct/ligero/fp4/`, NVFP4_SM120, tables),
then `c9cc381`, `f11e618`, and **`78c2dc2`** = a second `git merge main` after main advanced to `4163acd` (Rust-only:
`ligero-verify` reads `ligero-system/v2` and pins fp4-nvf4; no conflicts, no Python touched). HEAD `78c2dc2`;
`git status --short` empty, `rg -l '^<<<<<<< '` empty, `git diff main -- backends/ligero-verify` empty, no `.md` added.

Conflicts: **one file, `backends/direct/ligero/chain.py`** (`chain_coefs`). Both sides rewrote it: main for multi-component
chain ends (`end_terms` / `end_values`, `END_FAMILIES = (6, 0, 1)`), the lane for the one-`index_add_` term table. Resolution
(as planned in §7): keep the vectorised `chain_coefs`; `_chain_tables` loops over `end_terms(ch)`; the mask matrix has
`6 + len(ends)` rows (link×3, start×3, END×len(ends)) and a `famsel` selector maps virtual family `6 + x` to `rc[:,
END_FAMILIES[x]]` under the END mask; `rhs` adds `(rm[:, 6+x] · ((yv − Y.c) mod p)).sum` per `(Y, yv) in zip(end_terms,
end_values)`. For single-`y16` systems this is exactly the previous code (7-row mask matrix; bf16/fp8 transcripts unchanged —
re-checked below). New `chain_test.py` compares it residue-for-residue against main's per-term loop (kept verbatim as the
reference) on bf16-hopper (single end) and fp4 (three components, two layouts). `protocol.py`, `run.py`, `serialize.py`
auto-merged (system_id / system v2 / `_runner` fp4 dispatch / `--relation fp4-nvf4`; `set_impl` runs before the fp4 dispatch).
`vu.py`, `relchain.py` were not touched by main.

`--impl device` and the FP4 runner: `FP4ChainRunner.prove_vus` calls the shared `protocol.prove` → `witness.build_witness`,
so the fused kernel covers the FP4 witness (1583 rows/unit; `test_fused_witness_equals_torch_program_fp4` added to
`witness_device_test.py`: fused == torch program on all edge families). Its **hints are its own path** — `fp4/witness.hints_fp4`,
numpy on the host — unaffected by `--impl` either way; the fp4 result's `software.backend` now records
`impl` and `hints: "numpy (host)"` (`f11e618`). On the 4090: fp4 witness 7.9 ms (legacy) → 0.63 ms (device) per 170-VU sub-batch.

Two small fixes on top of main's code: `fp4/relation_test.py::test_chain_two_vus_cpu` had a stray `del torch` inside its
`(zk, mode)` loop → `UnboundLocalError` on the second iteration (all assertions had passed) — removed (`c9cc381`); and the
`impl`/`hints` fields above.

Laptop: `uv run pytest backends/numerical/tests tools/research/tests tools/native_peak/tests packages -q` → **1230 passed,
10 skipped** (155 s). `cargo test` in `backends/ligero-verify`: **36 passed** (19 + 7 + 10) at `78c2dc2` (30 at `ef17cc5`).

Pod `vy-hp-val` = RunPod `8xubf0u8uo4109`, RTX 4090 24564 MiB (`check-part`: reference), host AMD EPYC 75F3 (128 threads,
shared, load ~19–23), $0.74/h, created 03:55:48Z, terminated 04:22Z (confirmed absent from `pods list`): **~26 pod-minutes ≈
$0.33**. Bootstrap r20260923-040553-4611 (57 s; torch 2.6.0+cu124, cupy 14.2, blake3, rustc 1.98.1, ligero-verify built from
the tree). Runs on the merged tree (`ef17cc5`, then `c9cc381`/`f11e618`):
- r20260923-040725-74cd `validate.sh`: `pytest backends/direct/ligero` (minus v2) **54 passed, 1 skipped, 1 failed** — the
  failure is main's `del torch` above; v2: 2 passed. Gates rc=0 ×6: bf16-ampere (38 s), bf16-hopper `--impl device`,
  bf16-hopper `--impl legacy`, fp8-hopper, fp8-ada, **fp4-nvf4** (`--vus 64 --batch 1024`: vu-k1536 64/64, vu-k1536-neg 114/114,
  tu-k64-neg 3015/3015; needs no sm_120 — the relation's oracle is the Python model). Bit-exactness `--impl device` vs `--impl
  legacy` (seeded coins + mask keys, 3 sub-batches each): bf16-hopper int-ZK **10/10**, fp8-hopper int-ZK **10/10** files identical
  (system.bin + stmt/proof/coins); Rust batch on those dumps 3/3 accepted, pinned. Bench trees: bf16-hopper int-ZK 340 VUs
  (2 sub-batches) and fp8-hopper int-ZK 682 VUs (2 sub-batches): Python `verify-batch --target-bits 128` ACCEPT 2/2, Rust
  `ligero-verify batch --target-bits 128` 2/2 accepted, batch ACCEPT, **python_agree 2/2**, pinned, union 2^-128.33 each.
  fp4-nvf4 `bench-vu --zk --mode interactive --batch 4096 --total-vus 170 --reps 1`: proves, runner cold verify 1/1, Python
  `verify-batch` ACCEPT (2^-128.07); the pod's Rust (built from `ef17cc5`, i.e. main 24bd337) refused the v2 system as expected
  (`not a ligero-system/v1 file`) — main `4163acd` now reads v2; its fixture `fixtures/fp4-nvf4/system.bin` has the same sha256
  `6bb9d77f…` as the system.bin my fp4 benches wrote.
- r20260923-041818-ac51: after `c9cc381`, `pytest fp4/relation_test.py chain_test.py witness_device_test.py` → **15 passed**.
- r20260923-042009-b442: fp4-nvf4 bench-vu under `--impl device` AND `--impl legacy`: both prove, cold verify 1/1, Python
  verify-batch ACCEPT, identical `system.bin`; result records `impl`.
No Table 2 rows, no labels, no `verified=`. Evidence: `evidence/merge-val/` (run logs + JSONs, scripts, laptop pytest/cargo logs).

Surprises: (a) main moved twice during the task (24bd337 → 4163acd, Rust fp4 support) — merged both; (b) `research pods create`
launched from a backgrounded shell created the pod but died before registering it (no `machines.toml` entry) — registered by hand
after `check-part` said reference; the second `create` I started was killed before it could make a duplicate; (c) `research run`
ships files with `--send`, not `--input` (one failed launch, rc 127); (d) `--impl` is a subcommand flag (`bench-vu --impl`), one
failed fp4 launch; (e) main's own fp4 test fails on a second loop iteration (`del torch`), fixed here.

Evidence: `~/.research/notes/lanes/hostphase/evidence/` — per-run stdout logs, `<run>/prof/attribution.json` (98f2 main,
a174 lane), `9e90/bitexact/summary.txt` + per-pair sha256 lists, `03b5/stdout.log` (pytest + gates), per-row
`python_verify_batch_rep1.json` / `rust_batch_rep1.json`, `scripts/` (bootstrap.sh, profile_phases.py, bitexact.py,
bitexact_all.sh, bench.sh, gates.sh, validate_results.py, label.py, launch.sh, ssh.sh), `pull.log`, `drive.log`.
