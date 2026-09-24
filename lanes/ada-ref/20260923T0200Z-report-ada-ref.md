---
id: r21-ada-ref/ada-ref/20260923T0200Z-report-ada-ref
campaign: r21-ada-ref
lane: ada-ref
kind: report
status: closed
repo: verity-main@c93e1f6 (branch lane/ada-ref, base main 710e851; not merged)
---

# ada-ref: contract-valid FP8 Ada B-Ligero results on the REFERENCE-part RTX 4090 (24 GiB), proof bytes preserved

Branch `lane/ada-ref` (worktree `verity-main-wt/ada-ref`), base `main` 710e851, head **c93e1f6** (two commits: the reference-part
gate 381c045 -- the commit the pod ran -- and a 404-handling fix), clean tree, no conflict markers.  Producer lane only: no `verified*` label was written by this lane.  Pod `vy-ada-ref`
(`7ctvlc53czdxqt`, RunPod SECURE US, RTX 4090 **24564 MiB**, $0.74/h) via `research run --on`; no GPU work on the laptop.  All store
writes (pull / labels / snapshot / push) from `main` (710e851).

## Why: lane ada-fp8-dumps' row was measured on a *variant* board

`main` 710e851 rejects ada-fp8-dumps' art:8d03e01e (the only verified FP8 Ada run) with `device variant: 48.0 GiB ... the reference
'NVIDIA GeForce RTX 4090' has 24 GiB` (`tables.device_variant`, `NativePeak.memory_bytes`): its pod #2 was a RunPod "RTX 4090"
reporting 49140 MiB (`hw.vram_mb`, host `6745e19b6940`, AMD EPYC 7763 x256, load 32-74).  This lane re-produces the three modes on
the datasheet part, twice each.

## Task 1: the reference-part gate (`research pods check-part`, commit 381c045)

`tools/research/src/research/pods/part.py` (~95 lines incl. docstring) + `tests/test_pods_part.py` (6 tests, no pod):

* `[families.<hw.family>] vram_mb` in `~/.research/machines.toml` (added: rtx4090 24564, a100 81920, h100 81559, rtx5090 32607,
  l40s 46068, b200 183359 -- the `hw.vram_mb` values of the store's attempts on those boards, `attempt_conditions`; the RTX 4090
  variant shows as 49140 on 3 attempts).
* `verdict(sku, vram_mb, families)`: family by `env.sku_family`; `reference` when |memory.total/vram_mb - 1| <= 12 %
  (`tables.device_variant`'s tolerance), else `variant (+N %)` (49140 -> `variant (+100 %)`; an H100 NVL 95830 named H100 ->
  `variant (+17 %)`); `unknown` without a fact or a families entry.
* `research pods check-part <machine|pod-id> [--json]`: one read-only ssh probe (`nvidia-smi --query-gpu=name,memory.total`,
  nproc, /proc/cpuinfo model, /proc/loadavg, hostname) -> `name x count  VRAM (reference N)  host CPU  load  hostname -> verdict`;
  exit 3 on a variant.  `research pods create <runpod create flags> [--require-reference-part]`: `research.pods.runpod create`
  (its argparse moved into `runpod.create_args`, `create()` now returns the pod), `wait_ssh`, the same verdict; exit 3 (pod left
  running, terminate command printed) unless the board is the reference part.  Other verbs pass through to `research.pods.runpod`.
* On this lane's pod: `vy-ada-ref  NVIDIA GeForce RTX 4090 x1  24564 MiB (reference 24564 MiB)  host AMD EPYC 7642 48-Core
  Processor x96  load 6.58  7f578b0efe5f  ->  reference` (exit 0).

## Provisioning: one try

| try | pod | DC | hostname | GPU / VRAM | host CPU | load at check | verdict |
|---|---|---|---|---|---|---|---|
| 1 | `7ctvlc53czdxqt` | US (RunPod SECURE; `machine.location: US`) | `7f578b0efe5f` | RTX 4090 / 24564 MiB (torch total_memory 25250627584 B = 23.5 GiB; result.json memory_total_bytes 25757220864 = 23.99 GiB) | AMD EPYC 7642 48-Core x96, 251 GB RAM, 13 vCPU / 35 GB for the pod | 6.6-7.2 (1-min) | **reference** |

No variant was seen; no re-creation needed.  Driver 580.159.04, power limit 450 W, max SM clock 3105 MHz, cgroup cpu.max shown in the
bootstrap log.

## Task 2: the runs (K=1536, frozen `bench-instances-fp8-ada/v1` / `vu-k1536-fp8-ada`, [0, 4096], seed 20260922, manifest e66ff0f2…; target 2^-128; median of 3 reps; 4096 VUs as 49 sub-batches of <= 85 VUs, l = 4096)

Exactly the ada-fp8-dumps flow: `research run --on vy-ada-ref --project verity --campaign r21-ada-ref --source . --tool bench_vu_fp8
--scratch triton --exclusive --require-result --stage S -- /workspace/venv312/bin/python -m backends.direct.ligero.run --relation
fp8-ada bench-vu [--zk] --mode M --batch 4096 --total-vus 4096 --reps 3 --device cuda --dump-dir '$RESEARCH_RUN_DIR/proofs' --out
'$RESEARCH_RUN_DIR/result.json'`.  Order: the three modes (attempt 1), then the three modes again (attempt 2); the same mode's two
attempts are 2 m 41 s - 4 m 48 s apart.  Native peak 330.3e12 FLOP/s (fp8-ada-mma-draft/2026-09-22).

| mode / proof_class | attempt | run | t.total median (3 reps) | s/VU | R_proved | overhead vs 330.3e12 | achieved | Python cold self-check | Rust `batch` rep1 (self-check) |
|---|---|---|---|---|---|---|---|---|---|
| non-ZK interactive control, NON_ZK_PROOF_DIAGNOSTIC | 1 | r20260923-013530-6693 | **1.960** (2.105, 1.959, 1.952) | 4.79e-4 | 6.42e6 | **5.15e7** | 2^-128.62 (t=198) | 147/147 | 49/49 own coins, 128.6156 bits, 1.165 s wall |
| same | 2 | r20260923-014018-6e60 | **2.009** (2.169, 2.009, 1.991) | 4.90e-4 | 6.26e6 | **5.27e7** | 2^-128.62 | 147/147 | 49/49 own coins, 128.6156, 1.139 s |
| ZK Fiat-Shamir, COMPLETE_HVZK_BACKEND | 1 | r20260923-013832-dea1 | **2.402** (2.556, 2.367, 2.402) | 5.86e-4 | 5.24e6 | **6.31e7** | 2^-128.40 (t=302, 2^60 FS queries) | 147/147 | 49/49, 128.4001, 1.558 s |
| same | 2 | r20260923-014113-4a0c | **2.432** (2.583, 2.396, 2.432) | 5.94e-4 | 5.17e6 | **6.38e7** | 2^-128.40 | 147/147 | 49/49, 128.4001, 1.551 s |
| ZK interactive (+coins), COMPLETE_ZK_BACKEND | 1 | r20260923-013925-3a9e | **2.246** (2.391, 2.231, 2.248) | 5.48e-4 | 5.60e6 | **5.90e7** | 2^-128.40 (t=203) | 147/147 | 49/49 own coins, 128.3957, 1.173 s |
| same | 2 | r20260923-014211-f9b7 | **2.285** (2.414, 2.240, 2.288) | 5.58e-4 | 5.51e6 | **6.00e7** | 2^-128.40 | 147/147 | 49/49 own coins, 128.3957, 1.132 s |

Run-to-run on one host: +2.5 % / +1.2 % / +1.7 % (non-ZK / FS / int) between the two attempts, load 6.3-7.9 at start; within a run
rep 1 is 5-8 % slower than reps 2-3 (warm-up), the median never picks it.  Proof bytes 169.9 / 263.9 / 181.5 MB per rep (identical to
ada-fp8-dumps and fp8-proof: same statements, same t).  Peak device memory 0.98 GB.

Per-phase medians, attempt 1 (non-ZK / ZK-FS / ZK-int): witness 1.067 / 1.073 / 1.065 s (torch hints 0.379-0.383 + witness 0.688-0.690),
encoding+commitment 0.095 / 0.167 / 0.167 (encode 0.046 / 0.118 / 0.117, Merkle 0.048-0.049: cupy GPU Merkle active), arithmetic tests
0.579 / 0.786 / 0.749, ZK masks 0 / 0.040 / 0.039, serialization (openings) 0.217 / 0.336 / 0.224; Python verifier on the pod 1.61 /
1.81 / 1.60 s per rep of 49.  Versus ada-fp8-dumps (48 GiB variant, EPYC 7763 x256, load 32): 1.917 / 2.463 / 2.340 -> **+2 % / -2 % /
-4 %** here, i.e. the same to within run-to-run noise; versus fp8-proof's vy-sp1 (1.643 / 2.055, EPYC 7K62 x96): +19 % / +17 %.  GPU
phases match all three hosts to the millisecond (encode 0.046, Merkle 0.048); the gap is the host-side phases (tests 0.579 vs 0.435,
openings 0.190 vs 0.144, hints 0.379 vs 0.29) -- the host CPU, not the board.  The reference-part number is therefore the same as the
variant's; the variant's board memory did not buy or cost prover time (the workload peaks at 0.98 GB), which is consistent with the
device-variant rule being about *which datasheet the row divides by*, not about a measured effect.

### Contract (main 710e851)

`contract.validate(result) == []` for all six.  `tables.reject_reasons(result, [], None, FP8_ADA_MMA, B-Ligero)` on the interactive-ZK
results (3a9e, f9b7): **exactly one reason**, "not independently verified: no label independently_verified=True|true or
verified=accepted by a non-producer" -- no `device variant`, no same-SKU (memory_total_bytes 25757220864 = 23.99 GiB vs the 24 GiB
reference).  6693 / 6e60 / dea1 / 4a0c: that reason plus the expected "proof_class ... is not B-Ligero's declared class
COMPLETE_ZK_BACKEND" (drill-down rows).  Checker: `/tmp/ada-ref/check.py` (scratch).

### Rust self-check (`rust_selfcheck_rep1`, run r20260923-014417-ef0d on the pod; NOT independent: same pod, same tree 381c045)

`/workspace/bin/ligero-verify` built on the pod from 381c045 (`cargo build --release`, rustc 1.98.1; binary sha256 3f318550…),
`system-digest` on every `proofs/system.bin`: sys_id 6b570eef…, table digest 443e4fc7…, **pinned_relation fp8-ada** (m=3769 L=589 Q=3532
pins=192).  `batch --system proofs/system.bin --dir proofs/rep1 --target-bits 128` (pinned, `.coins` beside each interactive proof picked
up as `--coins`): 49/49 accepted x 6, batch_accepted, python_agree 49/49, `own_coins` 49 for the interactive runs (`accept (interactive:
coins are this verifier's step-0 coins)`) and 0 for Fiat-Shamir (`accept`); 11 jobs x 1 thread: wall 1.13-1.17 s (interactive) / 1.55-1.56
s (FS) per rep of 49, verify-seconds-sum 10.9-14.5 s.  JSON verdicts + logs in that run's dir (`selfcheck_<run>.json/.out`).

## Store (R2 `s3://verity-dev`; everything below pushed from `main`, PRESERVED with etag-md5 / sha256-readback verification)

| run | stage | bench-result/v1 | run-files/v1 (dump tree) | objects / size | telemetry (events, resources) |
|---|---|---|---|---|---|
| r20260923-013530-6693 | fp8_nonzk_interactive_a1 | art:4d1d86de6a16b1c24fba06408f1593e1790c93fcf92670e4c20ec3115c8cf654 | art:c8274d84aa8df4b52d8a86dcccb66bcbdcea5f3058ca6e5c67bb8c58ad6a2ee6 | 445 / 551.2 MB (147 stmt + 147 proof + 147 coins) | art:d172318e…, art:9696b0b5… |
| r20260923-013832-dea1 | fp8_zk_fiat_shamir_a1 | art:0553e315be32fe37acd29899752cbded1eb265a99517bd2a58672b7e7881063b | art:61398900a7b676103f11263f553417daf9b125a8d22c71b272be82b0b128564c | 298 / 833.0 MB (no coins: FS) | art:dc109b7f…, art:ed669675… |
| r20260923-013925-3a9e | fp8_zk_interactive_a1 | art:bf3fe88c905f07a0c100e51497594332a19ef468255c9bf24591bca752fb40a0 | art:f809a699fb0ea2cb6901fec8f866d01c4355bb4aa3be4fa883e245ce9e974e88 | 445 / 585.8 MB | art:a079bea1…, art:38cc4a94… |
| r20260923-014018-6e60 | fp8_nonzk_interactive_a2 | art:5988587ea5209794715f9591188e0c8b147cd5960369a985447d8a30482818cc | art:f81e351968e95782143de43aab458aa2c09ea4f9a92fe3ede43754e2ac7b45f9 | 445 / 551.2 MB | art:50742515…, art:7229b0b5… |
| r20260923-014113-4a0c | fp8_zk_fiat_shamir_a2 | art:98e4fabc4ed9b15cc13220aa303eb2a9add342570dd6f185cb62198ed41540fa | art:f743f214d743e5d211c9549f01e9744c2658afbb51bce6b4e437a0451752eb7d | 298 / 833.0 MB | art:85c02961…, art:b62efa1e… |
| r20260923-014211-f9b7 | fp8_zk_interactive_a2 | art:191ff942a70c4972bb723418d966d7a70f0fe435d1b8b0eb14ed8dd85a311d03 | art:c140e0ba47bd240d735a76a75cadacf544f71171c166d71046fa8fbe156ea5ea | 445 / 585.8 MB | art:7a277791…, art:aef1dc5f… |

148 blobs of every dump tree were "already there" (system.bin + the 147 statements are byte-identical across runs of the same mode:
same frozen instances, deterministic statements), so the six trees cost 6 x ~300 uploaded objects.

Snapshot **ada-ref-v1** = art:368ecceaf0a72ead80db1bf3e77fc4a12a41e95b15ebd5ff93c1ba52fe5c1722 (12 members: the six results + their
run-files).  Labels (17 per result, `--by ada-ref --ref <run>`, from main): candidate=B-Ligero, proof_class, mode, zk (bool), K=1536,
B=4096, soundness (text), hardware=rtx4090, relation=fp8-ada, target=fp8-ada-mma-draft/2026-09-22, campaign=r21-ada-ref,
instances_dataset, instances_tier, authentication=excluded, overhead (number), seconds_per_vu (number), note (reference part, VRAM,
memory_total_bytes, host CPU, hostname, load_start/end, pod, attempt k of 2, Rust self-check).  `same_device` skipped (off-vocabulary).
No `verified*` label by this lane.  (Lane `verify` had already labelled 3a9e `verified=not-transferable` by 01:53Z -- its call, D7.)

Dump layout as ada-fp8-dumps: `proofs/system.bin` (ligero-system/v1), `manifest.json`, `rep{1,2,3}/sub_{00..48}.{stmt,proof[,coins]}`
(ligero-statement/v4 LIGSTM04, ligero-proof/v1), `verify_python.json` (147/147 cold, `independent: false`); listed under `artifacts`.

Fetch / pull flow: `research data pull <run> --from vy-ada-ref --project verity` (main) for all six; `research fetch <run> --all`
(preserved.json, sha256-verified against the pod) for 6693, dea1, 3a9e, 6e60 (NOT for 4a0c and f9b7: the laptop was at 1.5-2.0 GiB free when they finished; their bytes are in the store by `data pull`, artifact-id re-derived, and PRESERVED on R2 -- the run dirs hold the small records only); the local
run-dir `proofs/` copies were then removed after each run-files artifact was PRESERVED (`run-files.evicted.json` beside preserved.json,
the coordinator's schema for the ada-fp8-dumps runs) because the laptop had 5.8 -> 1.5 GiB free with other lanes pulling concurrently.
The store's own blob copies were left alone.

## Pod accounting

vy-ada-ref `7ctvlc53czdxqt` created 2026-09-23 01:21Z (REST), sshd 01:23Z, bootstrap r20260923-012733-59ff (01:27-01:35Z: venv312 torch
2.6.0+cu124 + cupy 14.2 + blake3 + pytest, rustup 1.98.1 + ligero-verify, `pytest backends/direct/ligero` green; the first bootstrap
launch r20260923-012511-8f54 failed rc=127: `bash '$RESEARCH_RUN_DIR/...'` is not expanded by bash -- `bash -c 'exec bash
"$RESEARCH_RUN_DIR/inputs/bootstrap.sh"'` is), six runs 01:35-01:43Z, self-check 01:44Z, pulls 01:39-01:52Z, TERMINATED 2026-09-23 01:59:01Z (created 01:20:43Z).
38.3 pod-minutes at $0.74/h = ~$0.47 (budget 1.5 pod-hours).  Watchdog was armed for 1.6 h at creation.

## Things wrong / worth knowing in the spec

* There was no `research pods` command before this lane: pods are created with `python -m research.pods.runpod create ...` and
  bootstrapped by a lane script shipped through `research run --on ... --send`.  `research pods create` now exists as that plus the
  verdict; "bootstrap" is still the lane's script, so the verdict is printed when sshd answers, not "after bootstrap".
* `research fetch <run> --all` does not put anything in the store; `research data pull <run> --from <machine>` does (what
  ada-fp8-dumps actually ran, per its pull log).  Both were run; `push --pending` then needs the pulled attempts.
* `research.env.conditions()` runs under the pod's system python (torch 2.4.1 in `rt.torch`), the workload under venv312 (torch 2.6.0
  in `software.toolchain`): pre-existing, same as ada-fp8-dumps.
* The reference-part re-run reproduces the variant's prover time to 2-4 %: the 17-20 % gap to fp8-proof's 1.643 s is the host CPU
  (EPYC 7642 / 7763 vs vy-sp1's 7K62 at low load), on both boards.  Same-SKU + reference-part hold; the row's prover time still
  depends on the pod's host by ~20 % (host not part of the invariant).  `hw.cpu` is in the note label and the footnotes (710e851).
* The laptop's disk (11 GiB free at start, 1.5 GiB at the low point with other lanes pulling) is the binding constraint for dump
  lanes: six dump trees are ~3.9 GB in the store plus the same again for `fetch --all`.  Local run-dir copies were evicted after
  PRESERVED (above); a store-side eviction policy is the coordinator's call.
