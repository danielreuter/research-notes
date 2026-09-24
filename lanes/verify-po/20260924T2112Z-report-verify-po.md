---
lane: verify-po
kind: report
created: 2026-09-24T21:12Z
brief: launch message (coordinator), kb/TABLES.md
branch: lane/verify-po (worktree ~/projects/verity-main-wt/verify-po), base main@ab9573fd
final: 03:45Z hard; budget $6
status: open
---

CHECKPOINT 605b1bbb (22:26Z) [open] labelled A-GKR H100 FP8 art:2e7baba7 (verdict art:ccafc0f7; handoff coordinator 2227Z). Building SP1 stock + sec134 CPU hosts for sp1-128 art:e8c7c331 (r20260924-222445-6de0). 11 results accepted so far, 0 rejected
CHECKPOINT 891572a0 (21:57Z) [open] arith 4090 FP8 s1+s5: 7/7 reverify PASS + BOUND, labelled verified=accepted --by verify-po; verdicts art:7dae93fd art:9a59e106 art:4ecc7aee art:00dabdc8 art:11c4595f art:6a6c101b art:1ca0fbef; now B-Ligero negatives + A-GKR 4090 art:1b4fd4a1 (r20260924-215649-a2c4)
CHECKPOINT df48ecf3 (21:49Z) [open] pod bootstrapped (ligero-verify d89cffc7 from main ab9573fd); arith s1 reverify r20260924-213516-228f: labels pulled (11224), pod catalog reindex --remote in progress; next reverify+binding+negatives
CHECKPOINT 92dab0ad (21:29Z) [open] started; pod vy-verify-po (cpu3c 16 vCPU, no guard) synced @ main ab9573fd, bootstrapping (r20260924-212919-b175); next: reverify arith step-1 4090 FP8 art:7775888d art:1523b35c art:021aeabb
# verify-po: non-producer verifier for the Proof optimization workstream

Inbox at startup (21:13Z): nothing new. First request from the launch message: lane arith step 1 (4090 FP8 B-Ligero).

## Pod
- vy-verify-po 4tnxm5mqtez2v1: RunPod cpu3c, 16 vCPU / 32 GB, 60 GB disk, no GPU, host AMD EPYC 9754, created 21:17Z.
  No `guard` (idles between requests by design). machines.toml entry added.
- /workspace/src = `research pods sync` of lane/verify-po @ ab9573fd (= main), clean, tree bdf6fec1.
- Bootstrap: run r20260924-212919-b175 (`evidence/pod-scripts/01-bootstrap.sh`, CPU torch, HEALTH=0).

## Method (as verify-night)
- B-Ligero: `backends.direct.ligero.reverify` from my tree with `ligero-verify` built on my pod from my tree
  (`evidence/pod-scripts/03-reverify.sh`): custody, system-digest pin, `batch --target-bits 128` on every rep; PASS writes a
  preserved verification-verdict/v1 and `verified=accepted --by verify-po`. Then statement binding
  (`04-stmt-binding.py`, verify-night's 08): the dumped statements' chain-end y words equal the frozen set my tree draws.
- Credential: minted on the laptop per request (short ttl, prefixes objects/ manifests/ labels/ attempts/), piped into
  /root/r2.env on the pod, deleted after the request.

- A-GKR: `verity-gkr-verify` built and `cargo test`ed on my pod, from main or, when main cannot read the statement, from
  the producer's named commit (git archive, diff reviewed). Statement files are regenerated with the source that builds
  them and compared byte for byte. public.bin is checked against the frozen set drawn by MY tree (main). Negatives: the
  producer's, my own public-word edits, and `mutate --sample N`. Labelled by `evidence/pod-scripts/11-label.py` on the pod
  (verification-verdict/v1 with the evidence files as payload, refs result + proof, preserved; verified / verifier /
  verifier_seconds (the slowest proof) / note / same_device=false; labels-sync --push-only).

## Requests
| # | from | result(s) | cell | verdict | verdict art |
|---|---|---|---|---|---|
| 1 | launch msg (arith step 1, 9d1a7f15) | art:7775888d art:1523b35c art:021aeabb | RTX 4090 FP8, B-Ligero | accepted x3 | art:7dae93fd art:9a59e106 art:4ecc7aee |
| 2 | `20260924T2140Z-handoff-from-arith.md` (step 5, 92dab0ad) | art:def461c7 art:bb75ba4f art:d2b01b3f art:f3978133 | RTX 4090 FP8, B-Ligero | accepted x4 | art:00dabdc8 art:11c4595f art:6a6c101b art:1ca0fbef |
| 3 | `20260924T2129Z-handoff-from-agkr-fp8.md` | art:1b4fd4a1 | RTX 4090 FP8, A-GKR (new cell) | accepted | art:a40f5576 |
| 4 | `20260924T2200Z-handoff-from-agkr-nvf4.md` | art:fe57e68b | RTX 5090 NVFP4, A-GKR (new cell) | accepted (verifier from 3c769c6d, needs merge) | art:acf87c5c |
| 5 | `20260924T2212Z-handoff-from-agkr-fp8.md` | art:2e7baba7 | H100 FP8, A-GKR (new cell) | (labelling) | |
| 6 | `20260924T2220Z-handoff-from-sp1-128.md` | art:e8c7c331 | SP1 A100 BF16 sec134 (D2 row, not Table 2) | (building hosts) | |

### 1-2. arith 4090 FP8 B-Ligero (7 results)
- reverify run r20260924-215206-fe12: all 7 PASS (custody 40/40, pinned fp8-ada-v3x4, 13/13 proofs, 2^-128.33, ligero-verify
  sha256 d89cffc7b759e1f5 from main; the same hash verify-night and arith got, the crate is unchanged). Statement binding
  (04): all 7 BOUND (13 statements, 4096 VUs, 0 y words and 0 operand VUs differ from my tree's frozen fp8-ada set).
- Arith named no negatives. My own (05, run r20260924-220116-78b9), on the dumped rep1 of art:dc7c1488 (step 1) and of
  art:feb4501f (step 5), both trees giving the same results. The unmodified rep is accepted (13/13, 2^-128.33). Each change
  is rejected: one proof byte flipped ("merkle path 192 invalid"), one statement byte flipped in the chain-end words
  ("column challenge mismatch"), and the statements of sub-batches 0 and 1 swapped (2 rejected).
- Arith's step-1 and step-5 prover changes touch only `tests_fused.py` and the pipeline slots, not the proof format.
- Custody: all 7 verdicts `data preserved` rc 0 (sha256-readback).

### 3. agkr-fp8 A-GKR RTX 4090 FP8 art:1b4fd4a1 (run r20260924-215649-a2c4)
- Verifier: main ab9573fd `backends/gkr/verifier`, 8/8 tests, sha256 a48eac01714ecf3c. That differs from verify-night's
  ee899383 build of the same source; different pod and toolchain.
- 3/3 proofs accepted (sha256 b5ef0238 for all three). The counts are the producer's expected ones: 196608 units, 48 steps,
  2881 slots, 9547 msgs, 18152824 bytes, 22730 rows and 93101755 elements. Each proof takes 1.41-1.81 s.
- Statement: main has no E4M3 builder, so I ran 07a8edd6's `gpu.v2.export circuits --model ada_e4m3_m16n8k32` on my pod.
  circuit, epilogue and chain are byte-identical and the manifest params are equal. public.bin equals
  `fp8.relation.pack_public` of my tree's frozen fp8-ada final words, with 0 mismatches.
- Negatives, all rejected: `mutate --sample 64` (356/356); my VU-17 word +1; the producer's word_plus, word_minus, sign_flip
  and exp_plus (art:edfbca4d, whose honest case is accepted), all run with my binary.
- Coordinator handoff: `lanes/coordinator/20260924T2206Z-handoff-from-verify-po-4090-agkr.md`.

### 4. agkr-nvf4 A-GKR RTX 5090 NVFP4 art:fe57e68b (run r20260924-220116-78b9)
- The verifier diff (`git diff ab9573fd 3c769c6d -- backends/gkr/verifier`, +30/-13) is reviewed and sound. An optional
  `public <epi cols>` line is added to chain.txt, defaulting to `y16`, so old statements take the old path. Public word i
  gets coefficient `chain_v[i/npub]*chain_k[per_vu-npub+i%npub]` in both the functional (epilogue segment) and the claimed
  b, so the two sides match. `constraints_per_vu` and the shape checks follow npub. The non-v2 path still requires one word
  per VU. The chain text, including the `public` line, is already hashed into spec_hash.
- Built from 3c769c6d on my pod: 8/8 tests, sha256 f271e4221a7520d4. Regression: it accepts the FP8 y16 statement
  art:89a2ce85.
- 3/3 proofs accepted (98304 units, 24 steps, 4236 slots, 14418 msgs, 8537632 bytes), 0.60-0.85 s each.
- Statement: 3c769c6d's `gpu.nvf4.circuit export` on my pod gives byte-identical circuit, epilogue and chain (`public s t f`)
  and an identical manifest. public.bin (4096 x 3) equals (sign, exponent field, fraction) of main's
  `fp4/chain.instances_fp4(4096)` final words, with 0 rows mismatched. Digest d2d65f65… equals the one the result records.
- Negatives, all rejected: `mutate --sample 24` (148/148); my s flip, t+1 and f+1 (on different VUs); the public line
  reordered; the public line removed (verifier panics "circuit has no column y16", rc 101).

### 5. agkr-fp8 A-GKR H100 FP8 art:2e7baba7 (run r20260924-221801-97bc)
- Same method and binary as request 3. 891572a0 differs from 07a8edd6 only in `bench_result.py` metadata, so the statement
  was regenerated with the 07a8edd6 archive, `--model hopper_e4m3_wgmma_k32`.
- 3/3 proofs accepted (sha256 f80ecc53) with the expected counts: 2711 slots, 8912 msgs, 17251312 bytes, 21576 rows and
  88375120 elements. Each proof takes 1.45-1.62 s.
- circuit, epilogue and chain are byte-identical and the manifest params are equal. public.bin equals pack_public of main's
  frozen fp8-hopper final words, with 0 mismatches.
- Negatives, all rejected: `mutate --sample 64` (356/356); my VU-17 +1; the producer's 4 claim negatives (art:cdaabf41),
  whose honest case is accepted.

### Table 2 after these labels (laptop render 22:12Z, after `reindex --remote`)
| cell | before | now | art |
|---|---|---|---|
| RTX 4090 FP8, A-GKR | — | 3.0e7× (1.13 s) | art:1b4fd4a1 |
| RTX 4090 FP8, B-Ligero | 2.4e6× (art:fb4934af) | 2.2e6× (0.0840 s) | art:bb75ba4f (arith step 5) |
| RTX 5090 NVFP4, A-GKR | — | 1.4e8× (1.04 s) | art:fe57e68b |

## Log
- 21:17Z pod created; 21:27Z synced (494 s); 21:30Z bootstrapped (only the GPU stage failed, as expected on a CPU pod).
- 21:35Z first reverify stalled in the pod-catalog `reindex --remote` (~150 manifests/min). I killed it at 21:51Z and
  relaunched with full art ids (get_manifest / get_attempt / fetch fall back to the remote); 03-reverify.sh keeps REINDEX=1
  as an option.
