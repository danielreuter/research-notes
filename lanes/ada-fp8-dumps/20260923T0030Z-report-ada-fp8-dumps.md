---
id: r21-ada-fp8-dumps/ada-fp8-dumps/20260923T0030Z-report-ada-fp8-dumps
campaign: r21-ada-fp8-dumps
lane: ada-fp8-dumps
kind: report
status: closed
repo: verity-main@a4b0ac7 (merged into main as aecc298)
---

# ada-fp8-dumps: contract-valid FP8 Ada B-Ligero results with their proof bytes preserved

Branch `lane/ada-fp8-dumps` (worktree `verity-main-wt/ada-fp8-dumps`), base `main` a6df54d, head **a4b0ac7** (7bb0ffa +
merge of main 707b67c), clean tree, no conflict markers. The coordinator merged it into `main` as aecc298 ("in progress;
code as of a4b0ac7"); `main` is now 1dcba68 (b-batch-bound) and the store writes below were all made from `main`.
Producer lane only: no `verified*` label was written. Pod `vy-ada8` (RTX 4090 24 GB, RunPod SECURE, $0.74/h) via
`research run --on`; no GPU work on the laptop.

## Result (Table 2 row RTX 4090 / E4M3, target `fp8-ada-mma-draft/2026-09-22`, native peak 330.3e12 FLOP/s)

Frozen set `bench-instances-fp8-ada/v1` / `vu-k1536-fp8-ada`, range [0, 4096], seed 20260922, manifest
`e66ff0f21c8e67d13b4b2d4cee2afa35b8345656b314da80e6b342ba051f078d`; target 2^-128; median of 3 reps; 4096 VUs proved as
49 sub-batches of <= 85 VUs (l = 4096 rows, 48 K=32 units per VU, 3769 rows per unit); prove-then-verify per rep
(f28c13d structure), so no verifier host work sits between timed prover sub-batches.

| run | mode | proof_class | t.total (s, median) | s/VU | R_proved (FLOP/s) | overhead vs 330.3e12 | achieved (union over 49) | proof bytes / rep |
|---|---|---|---|---|---|---|---|---|
| r20260922-235542-295b | non-ZK, interactive (control) | NON_ZK_PROOF_DIAGNOSTIC | **1.917** | 4.68e-4 | 6.56e6 | **5.03e7** | 2^-128.62 (t=198) | 169.9 MB |
| r20260922-235643-98f7 | ZK Fiat-Shamir | COMPLETE_HVZK_BACKEND | **2.463** | 6.01e-4 | 5.11e6 | **6.47e7** | 2^-128.40 (t=302, 2^60 FS queries) | 263.9 MB |
| r20260922-235746-0929 | ZK interactive (+coins) | COMPLETE_ZK_BACKEND | **2.340** | 5.71e-4 | 5.38e6 | **6.14e7** | 2^-128.40 (t=203) | 181.5 MB |

Per-phase medians (non-ZK / ZK-FS / ZK-int): witness 1.015 / 1.067 / 1.064 s (torch hints 0.35-0.39 s + witness
0.67-0.68 s), encoding+commitment 0.100 / 0.182 / 0.181, arithmetic tests 0.574 / 0.796 / 0.780, ZK masks 0 / 0.042 /
0.042, serialization (openings) 0.232 / 0.364 / 0.261; verifier (Python, on the pod) 1.63 / 1.84 / 1.79 s per rep of 49.
Peak device memory 0.98 GB. Versus lane fp8-proof's 1.643 s / 2.055 s (non-ZK / FS-ZK, B=4096, same SKU, same 49 x 85
split, same union-bound accounting, identical proof bytes 169.9 / 263.9 MB so identical t): **+17-20% here**. The
GPU-bound phases match to the millisecond (encode 0.048 vs 0.046 s, Merkle 0.051 vs 0.048: cupy GPU Merkle was active),
the host-touching ones do not (tests 0.574 vs 0.435, openings 0.204 vs 0.144, torch hints 0.345 vs 0.29): the gap is
the pod's host CPU (RunPod SECURE EU-CZ-1 box behind pod #2 vs vy-sp1), not the code (the prover loop is unchanged; dumps
and the cold self-check run after the timed reps). Same-SKU holds (GPU = RTX 4090); the host is not part of the row's
invariant, so the numbers stand as this host's measurement, and a re-run on a faster host would likely reproduce 1.64 / 2.06.

`contract.validate(result) == []` for all three (main 1dcba68). `tables.reject_reasons(result, labels, attempt,
FP8_ADA_MMA, B-Ligero)`: 0929 (COMPLETE_ZK_BACKEND) has exactly one reason, "not independently verified: no label
independently_verified=True|true or verified=accepted by a non-producer"; 295b / 98f7 have that reason plus the expected
"proof_class ... is not B-Ligero's declared class COMPLETE_ZK_BACKEND" (drill-down rows).

## Store (R2 `s3://verity-dev`, all PRESERVED / `where` = remote present, verified)

| run | bench-result/v1 | run-files/v1 (dump tree) | dump size | telemetry |
|---|---|---|---|---|
| r20260922-235542-295b | art:df1f9963…ef68e5 | art:c5dff3c6…1ad30ca (445 objects, 551.2 MB) | 551.1 MB, 147 stmt + 147 proof + 147 coins | art:f97a6cf0… art:7d8a9cd7… |
| r20260922-235643-98f7 | art:f247cd15…49d7ad | art:66c0ac67…f960f8b1 (298 objects, 833.0 MB) | 832.9 MB, 147 stmt + 147 proof (no coins: FS) | art:b32d9c12… art:37b6fd25… |
| r20260922-235746-0929 | art:8d03e01e…89ca823 | art:4a37603f…5f875884 (445 objects, 585.8 MB) | 585.8 MB, 147 stmt + 147 proof + 147 coins | art:8906ca8e… art:8a767bfc… |

Full ids: df1f99631dddee3bc543065bd19f95b012a17ae65c2b7e5469f80034aaef68e5, c5dff3c62eba6a1f29ae50a86eb5763300978e1af97af64809fe0632e1ad30ca,
f247cd1550880e407f28516c91f67ded99e5f4b9099dc9690d81a87049a7d9ad, 66c0ac67f57259e4d8d71e8955ccc43036a04e5028187344a021b720f960f8b1,
8d03e01e219071065364e2793dd4682a54cc5debf4ce68d86176f1ed389ca823, 4a37603fb9304cb697dda441af4e6da4d4c7dd0e0405c740d5d4f78e5f875884.

Snapshot **ada-fp8-dumps-v1** = art:4ea0c002f6fa15c2a121a7df32fba02c43748deb3d799dfb767b87bcb8112f8c (6 members: the three
results + their run-files). Labels (17 per result, `--by ada-fp8-dumps --ref <run>`): candidate=B-Ligero, proof_class,
mode, zk, K=1536, B=4096, soundness (text: target + achieved + bound model), hardware=rtx4090, same_device=true (not in
the vocabulary; stored with a warning), relation=fp8-ada, target=fp8-ada-mma-draft/2026-09-22, campaign=r21-ada-fp8-dumps,
instances_dataset, instances_tier, authentication=excluded, overhead, seconds_per_vu. No verified* labels. Labels are
local-store assertions (`~/.research/store/labels/`, append-only files; the store design keeps them off R2), so they are
visible to every lane reading this laptop's catalog, including `verify`. The `push --pending` at 00:15Z also carried 7
pending attempts of other lanes (r21-bestvsbest x6, r21-verify x1), as the shared-catalog command implies.

Dump layout (in the run dir, listed under `artifacts`, so `research fetch --all` / `data pull` carry it whole):

~~~
proofs/
  system.bin            ligero-system/v1 of the fp8-ada system (sys_id 6b570eef…, table_digest 443e4fc7…; m=3769 L=589 Q=3532 pins=192)
  manifest.json         commit, device, relation, zk, mode, set (total_vus/batch/per_proof/n_proofs), files[] with sha256 + sizes
  rep{1,2,3}/sub_{00..48}.stmt     ligero-statement/v4 (LIGSTM04: word_bytes=1, y_bytes=4, relation "fp8-ada", n_proofs=49, no auth block)
  rep{1,2,3}/sub_{00..48}.proof    ligero-proof/v1
  rep{1,2,3}/sub_{00..48}.coins    interactive runs only: the verifier's step-0 coins (r1||s1||r2||s2)
  verify_python.json    cold self-check from the bytes: 147/147 accepted per run (independent: false -- shares code with the prover)
~~~

## The Rust verifier does NOT accept FP8-relation proofs (measured, main 1dcba68 build)

`ligero-verify` is BF16-relation-only, at three layers, each demonstrated on rep1/sub_00 of 0929:

1. `verify --system proofs/system.bin ...` -> `reject: system file is not the pinned REAL chain system`.
   `verify.rs:25-26` pins `PINNED_SYS_ID 44cb05b9…` / `PINNED_TABLE_DIGEST c147cc4c…` (the BF16 chain); the fp8-ada
   system is `6b570eef…` / `443e4fc7…` (`ligero-verify system-digest` on our system.bin parses it fine: the
   ligero-system/v1 container is relation-agnostic).
2. `--allow-any-system` -> `reject: statement file: not a ligero-statement/v2 or /v3 file`. `format.rs:275-277`
   accepts LIGSTM02 / LIGSTM03 only; relation-named statements (1-byte E4M3 operand words, 4-byte FP32 public words)
   are LIGSTM04 (`serialize.py`, this lane; main's v3 is the auth-block statement). `batch --dir rep1` -> 0/49.
3. Behind parsing, the chain check decodes u16 operand words with the BF16 `OP_FRAC` / `OP_EXP_BITS` split and the BF16
   accumulator semantics; the fp8-ada relation needs the E4M3 decode + FP32-accumulator rescale of
   `backends/direct/ligero/fp8/relation.py` (3769 rows/unit: 2474 bit, 640 selector, 161 hint, 192 pin, 301 product, 1
   inverse; 589 linear + 3532 quadratic constraints).

So the FP8 row cannot be independently verified until `ligero-verify` learns (a) LIGSTM04 with word_bytes / y_bytes /
relation, (b) the fp8-ada pinned digests (or a per-relation pin table), (c) the fp8-ada chain semantics. The dumps are
complete for that lane: system.bin + statements + proofs (+ coins), 147 per run, all accepted cold by the Python file
verifier. Until then the `verify` lane will (correctly) not write `verified=accepted` on these.

## Code (commits 7bb0ffa, a4b0ac7; merged to main as aecc298)

* `backends/direct/ligero/serialize.py`: `Statement` gains `relation` / `word_bytes` / `y_bytes`; relation-named
  statements are **ligero-statement/v4** (`LIGSTM04`: u8 word_bytes, u8 y_bytes, str relation, arrays in those widths,
  u8 has_auth + optional auth block); v2 (BF16, no auth) and v3 (BF16 + auth, main 707b67c) unchanged byte-for-byte.
  `read_statement` accepts v2/v3/v4; `verify_files` / `_runner` / `_statement_of` / `_manifest` / `cmd_verify` are
  relation-aware (`RelationHooks`, `FP8ChainRunner` for `fp8-ada`).
* `backends/direct/ligero/fp8/chain.py`: `bench_vu_fp8 --dump-dir` writes the layout above, then cold-verifies every
  file from bytes (`verify_python.json`), and lists `proofs/` under `artifacts`; reps are prove-all-then-verify (f28c13d).
  `fp8/tool.py`, `run.py`: `--dump-dir` plumbing. Test `fp8/relation_test.py::test_dump_round_trip_v4_cpu`
  (importorskip torch): v4 round trip incl. word widths / relation, and v2 backward compatibility.
* Laptop suites green at a4b0ac7: `uv run -q pytest backends/numerical/tests/bench tests -q` and the ligero suite.

## Pod accounting

* vy-ada8 #1 `c7h4zbihk69e2h` (US-NC-1) 23:12Z-23:42Z, ~30 min, ~$0.37: bootstrap, smoke, and the first three runs
  (7fb9 / 4316 / 6b9f) with the pre-merge LIGSTM03 relation-statement layout -- superseded once main's v3 (auth block)
  collided; their local `proofs/` were deleted to make room, their results are not in the snapshot.
* vy-ada8 #2 `plds13nsy0rpfs` (EU-CZ-1) 23:47Z-~00:05Z, ~18 min, ~$0.22: bootstrap (venv312, torch 2.6 cu124 +
  cupy-cuda12x for GPU Merkle -- without cupy the first pod's Merkle fell back to CPU and dominated), the three v4 runs,
  `data pull`. Total ~48 pod-minutes, ~$0.59 (budget 1.5 pod-hours). Both pods terminated; `runpod list` shows none.

## Things wrong / worth knowing in the spec

* The BF16 dump layout writes `system.bin` (ligero-system/v1), not `system.json`; the FP8 layout mirrors that.
* `same_device` is not a vocabulary key (stored with a warning). `relation=fp8-ada` was written as asked; the vocabulary's
  example spelling is `fp8-ada-k1536`.
* The row's prover time depends on the pod's host CPU by ~20% at the same GPU SKU (see above): the same-SKU invariant
  does not pin the host. If the coordinator wants the best same-SKU number, re-run on a faster-host 4090 pod; the
  present numbers are the conservative ones. Statements carry n_proofs=49 per rep and the achieved bounds are union
  bounds, so they satisfy main 1dcba68's `verify-batch` (sum_i 2^-b_i <= 2^-128, N presented == n_proofs).
* `research data doctor` lists 10 `store_publish_error.json` from other lanes' runs earlier today (05:38Z-17:22Z,
  state=running); none are this lane's.
