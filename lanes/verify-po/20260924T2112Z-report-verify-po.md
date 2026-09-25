---
lane: verify-po
kind: report
created: 2026-09-24T21:12Z
brief: launch message (coordinator), kb/TABLES.md
branch: lane/verify-po (worktree ~/projects/verity-main-wt/verify-po), base main@ab9573fd
final: 03:45Z hard; budget $6
status: open
---

CHECKPOINT ab9573fd (02:40Z) [open] idle: inbox empty since 02:15Z; 50 accepted + 6 held (45c5be4a 3ae971dd ad76c106 dfbc86c4 53a64e8b f277786d), 0 rejected; waiting for coordinator 'release' (31-release.sh staged); no cred on pod; polling
CHECKPOINT ab9573fd (02:18Z) [open] 5090 NVFP4 A-GKR art:f277786d (final; same stmt+proofs as dfbc86c4) verified; verdict art:4513180d PRESERVED, HELD (coordinator 0220Z). 50 accepted + 6 held, 0 rejected; release staged (31-release.sh); cred removed; polling
CHECKPOINT ab9573fd (02:13Z) [open] H100 FP8 A-GKR art:b0c27291 labelled (verdict art:eca0995c; Table 2 6.4e7x, 0.409 s); art:ad76c106 verdict art:b86ca2a8, HELD (coordinator 0214Z). 50 accepted + 5 held, 0 rejected; cred removed; awaiting 'release'; polling
CHECKPOINT ab9573fd (02:05Z) [open] red-team-lk 0200Z PASS noted; 4 held labels wait for coordinator 'release' (0050Z: coordinator sends it), release staged (31-release.sh). Verifying agkr-fp8 0203Z: H100 art:b0c27291 (unchanged stmt) + art:ad76c106 (merged, held) in r20260925-020532-8dac
CHECKPOINT none (02:00Z) [open] 5090 NVFP4 A-GKR art:53a64e8b (same stmt+proofs as dfbc86c4) verified; verdict art:223c8efe PRESERVED, label HELD (coordinator 0200Z). Held x4: 45c5be4a 3ae971dd dfbc86c4 53a64e8b. 49 accepted + 4 held, 0 rejected; cred removed; polling
CHECKPOINT none (01:41Z) [open] H100 FP8 A-GKR merged-LK art:3ae971dd 3/3 + stmt + LK-merge check OK; verdict art:e96f50ac PRESERVED, label HELD (coordinator 0142Z). Held: 45c5be4a 3ae971dd dfbc86c4. 49 accepted + 3 held, 0 rejected; cred removed; polling
CHECKPOINT 90c21455 (01:26Z) [open] 4090 FP8 A-GKR art:ecd96143 labelled (verdict art:eededf7d; Table 2 1.75e7x). 5090 art:dfbc86c4 verdict art:7d3aaf2e PRESERVED, label HELD (coordinator 0127Z x2). 49 accepted + 2 held, 0 rejected; cred removed; polling
CHECKPOINT ab9573fd (01:21Z) [open] labelled 4090 FP8 A-GKR art:ecd96143 (unchanged stmt; verdict art:eededf7d). art:dfbc86c4 (5090, BOOL_QUADRATIC+PAIRED) 5/5 + stmt + rewrite-equivalence check OK; registering verdict, label HELD
CHECKPOINT ab9573fd (01:05Z) [open] 4090 FP8 A-GKR merged-LK art:45c5be4a verified, verdict art:df4d2c3c registered, label HELD per coordinator 0050Z (handoff 0104Z); now art:ecd96143 (unchanged stmt, 0006Z handoff found in coordinator folder)
CHECKPOINT ab9573fd (00:41Z) [open] idle: inbox empty since 00:22Z; 48 accepted, 0 rejected; pod vy-verify-po up (no credential on it), polling every 10 min until 03:45Z
CHECKPOINT ab9573fd (00:22Z) [open] verified agkr-nvf4 5090 art:49757870 (716ea008, same proof bytes as 5adf62eb; verdict art:9618b325; A-GKR cell 2.5e7x; coordinator 0022Z). 48 accepted, 0 rejected; cred removed; idle-polling
CHECKPOINT ab9573fd (00:15Z) [open] d3-h100 LIVE x12 all PASS+BOUND, labelled (verdicts art:e13419b4..art:41e3a98b, coordinator 0017Z); Table 2 unchanged (also_valid, D3). 47 accepted, 0 rejected; idle-polling
CHECKPOINT ab9573fd (23:53Z) [open] verified 5090: agkr-nvf4 art:5adf62eb (verdict art:4791cc89, A-GKR cell 3.3e7x) + arith B-Ligero x4 (art:0b229064 art:c6a8328b art:f538c335 art:20b47418; also_valid behind d5c9e1f3). 35 accepted, 0 rejected; idle-polling
CHECKPOINT ab9573fd (23:45Z) [open] 2 new: agkr-nvf4 5090 art:5adf62eb (2b25df7f, supersedes ad8f92b9) + arith 5090 fp4-nvf4 B-Ligero x4 (art:97e0f3ba art:0e0e7ac5 art:c3d76d7b art:227aeb2a) verifying in r20260924-234455-6524
CHECKPOINT ab9573fd (23:30Z) [open] verified agkr-nvf4 5090 art:ad8f92b9 (verdict art:37ed86f2) and arith A100 x4 (art:50b44dad art:68fa7c52 art:ce07f815 art:38410b93; all PASS+BOUND). Table 2: 5090 A-GKR 4.2e7x, A100 B-Ligero 5.9e6x. 30 accepted, 0 rejected
CHECKPOINT ab9573fd (23:15Z) [open] 2 new requests: agkr-nvf4 5090 art:ad8f92b9 verifying (r20260924-231454-fa00; stmt regen from ab57df0a, verifier 3c769c6d build); arith A100 x4 (art:5bcbf3fb art:b83f1ff0 art:4e87bc8a art:228f07b1) reverify next
CHECKPOINT ab9573fd (22:55Z) [open] SP1 A100 BF16 sec134 (D2) art:e8c7c331: 5/5 accepted with sec134 host built on my pod (sha256 = producer's ad6ec855), stock host + y-flip rejected; verdict art:34582a00 (coordinator 2256Z). 25 accepted, 0 rejected; idle-polling
CHECKPOINT 0e8cc6ea (22:40Z) [open] arith H100 13/13 reverify PASS + BOUND, labelled (verdicts art:7d68f788..art:abe34544, coordinator 2240Z). SP1 sec134 host building (r20260924-223547-6b33; d1111579 build.sh VERIFIER_ONLY needs cargo fetch first). 24 accepted, 0 rejected
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
| 5 | `20260924T2212Z-handoff-from-agkr-fp8.md` | art:2e7baba7 | H100 FP8, A-GKR (new cell) | accepted | art:ccafc0f7 |
| 6 | `20260924T2220Z-handoff-from-sp1-128.md` | art:e8c7c331 | SP1 A100 BF16 sec134 (D2 row, not Table 2) | accepted | art:34582a00 |
| 7 | `20260924T2226Z-handoff-from-arith.md` (92dab0ad, H100) | h8 x6: art:e9ae289c art:c6271278 art:8182f9ae art:efd871f6 art:7a8443b4 art:709ab20c; h16 x3: art:415d6cde art:b23719dd art:16feee34; h16L x4: art:e3362256 art:064a3a75 art:593f8249 art:debd7e1d | H100 FP8 / H100 BF16, B-Ligero | accepted x13 | art:7d68f788 art:5d8c8aa1 art:750d53cf art:eb44f474 art:b1a0be1d art:aafc3c75; art:bfc56de7 art:a5a7e8c8 art:5d94cfae; art:a7ed0d9b art:830956b0 art:65f9b4d7 art:abe34544 |
| 8 | `20260924T2305Z-handoff-from-agkr-nvf4.md` (ab57df0a) | art:ad8f92b9 | RTX 5090 NVFP4, A-GKR (supersedes art:fe57e68b) | accepted (same verifier merge as #4) | art:37ed86f2 |
| 9 | `20260924T2306Z-handoff-from-arith.md` (92dab0ad, A100) | a16-tip r1-r4: art:5bcbf3fb art:b83f1ff0 art:4e87bc8a art:228f07b1 | A100 BF16, B-Ligero | accepted x4 | art:50b44dad art:68fa7c52 art:ce07f815 art:38410b93 |
| 10 | `20260924T2335Z-handoff-from-arith.md` (92dab0ad, 5090) | f4-tip r1-r4: art:97e0f3ba art:0e0e7ac5 art:c3d76d7b art:227aeb2a | RTX 5090 NVFP4, B-Ligero (also_valid; cell stays art:d5c9e1f3) | accepted x4 | art:0b229064 art:c6a8328b art:f538c335 art:20b47418 |
| 11 | `20260924T2350Z-handoff-from-agkr-nvf4.md` (2b25df7f) | art:5adf62eb | RTX 5090 NVFP4, A-GKR (supersedes #4, #8) | accepted (same verifier merge as #4) | art:4791cc89 |
| 13 | `20260925T0005Z-handoff-from-agkr-nvf4.md` (716ea008) | art:49757870 | RTX 5090 NVFP4, A-GKR (supersedes #11; same proof bytes) | accepted (same verifier merge as #4) | art:9618b325 |
| 14 | `20260925T0045Z-handoff-from-agkr-fp8.md` (3be6a35f) + `20260925T0050Z-handoff-from-coordinator.md` (HOLD) | art:45c5be4a | RTX 4090 FP8, A-GKR, merged LK | PASS, label HELD (coordinator) | art:df4d2c3c |
| 15 | `lanes/coordinator/20260925T0006Z-handoff-from-agkr-fp8.md` (f2363663; sent to coordinator's folder, found 01:05Z) | art:ecd96143 | RTX 4090 FP8, A-GKR, unchanged statement | accepted | art:eededf7d |
| 16 | `20260925T0100Z-handoff-from-agkr-nvf4.md` (b7cec878) | art:dfbc86c4 | RTX 5090 NVFP4, A-GKR, BOOL_QUADRATIC + PAIRED | PASS, label HELD (coordinator 0050Z) | art:7d3aaf2e |
| 17 | `20260925T0132Z-handoff-from-agkr-fp8.md` (3be6a35f) | art:3ae971dd | H100 FP8, A-GKR, merged LK | PASS, label HELD (coordinator 0050Z) | art:e96f50ac |
| 18 | `20260925T0150Z-handoff-from-agkr-nvf4.md` (00145f51) | art:53a64e8b | RTX 5090 NVFP4, A-GKR (supersedes #16; same statement and proof bytes) | PASS, label HELD (coordinator 0050Z) | art:223c8efe |
| 19 | `20260925T0203Z-handoff-from-agkr-fp8.md` (a97576b5; quotes its 0146Z and 0158Z notes, sent to the coordinator's folder) | art:b0c27291 | H100 FP8, A-GKR, unchanged statement (supersedes art:b1010ac8, 2326Z, never sent to me) | accepted | art:eca0995c |
| 20 | same handoff (a97576b5) | art:ad76c106 | H100 FP8, A-GKR, merged LK (same statement and proofs as #17) | PASS, label HELD (coordinator 0050Z) | art:b86ca2a8 |
| 21 | `20260925T0210Z-handoff-from-agkr-nvf4.md` (c97d2ad2) | art:f277786d | RTX 5090 NVFP4, A-GKR (final; same statement and proofs as #16/#18) | PASS, label HELD (coordinator 0050Z) | art:4513180d |
| - | `20260925T0200Z-handoff-from-red-team-lk.md` | - | red-team-lk PASS on all five A-GKR rewrites; "verify-po may release" | not acted on: 0050Z says the coordinator sends "release" (coordinator 0214Z) | - |
| 12 | `20260924T2351Z-handoff-from-d3-h100.md` (main 1d9c3198, live) | b16b r1-3: art:c6e250c2 art:c1c05324 art:166551a5; f8b r1-3: art:971820ba art:7be63d37 art:c58d45c6; b16h r1-3: art:137b923a art:60d0622f art:d9d21d03; f8h r1-3: art:83c7d5a7 art:9aed3426 art:5b6d6d6d | H100 BF16/FP8 (+hash) B-Ligero LIVE, D3 (also_valid in Table 2) | accepted x12 | art:e13419b4 art:209fdd63 art:ed310632; art:d0aeef7f art:fe61cce4 art:f765ab6c; art:649e27ed art:0b754787 art:1e442d10; art:cc7fa7cd art:549ee1d3 art:41e3a98b |

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

### 6. sp1-128 SP1 A100 BF16 sec134 art:e8c7c331 (host r20260924-223547-6b33, verify r20260924-224326-a84c)
- Hosts built on my pod. The stock host is from main ab9573fd (`--locked`, relation-bare), sha256 06e0d736. The sec134 host
  uses d1111579's `sec128/build.sh VERIFIER_ONLY=1` over main's unmodified backends/sp1; its sha256 is ad6ec855, the same
  bytes as the producer's copy. Both report ELF f11cf2cc and vk 0x00dfced1. The patched sp1-primitives 6.6.0 differs from
  stock only in the core query count (124 -> 175) and the sp1-cuda connect retry (10 -> 300).
- The build script needs a `cargo fetch --locked` first on a CPU pod. Without it, build.sh stops with "sp1-cuda retry loop not
  found once", because a CPU stock build never downloads sp1-cuda (`17-sp1-sec134-build.sh`).
- I wrote the statement from main's frozen bf16-ampere set (vu-k1536, manifest 059103cf): 8263 B, sha256 5e0dd245. It is
  byte-identical to the dump's statement.bin.
- 5/5 proofs are accepted: ok, verdict and statement_match are true and unsound is false. Verify takes 2.13-2.15 s per proof,
  ~38 s per process including setup.
- Negatives, both rejected: the last y byte flipped (statement_match false), and the STOCK host on rep0 (ok false).

### 7. arith H100 B-Ligero, 13 results (run r20260924-222928-d816)
- All 13 PASS (fp8-hopper-v3x4: custody 40/40, 13/13, 2^-128.33; bf16-hopper-v3x4: custody 76/76, 25/25, 2^-128.05) and all
  13 BOUND (0 y words and 0 operand VUs differ over 4096 VUs). The live-verifier arm h16 is verified the same way from its
  dumps.
- Negatives (05) on art:db78aa36 (h8-r1) and art:508debf5 (h16-r1): the base is accepted and all three changes are rejected.
- Verdict custody: `data preserved` on all 13 returns rc 0.
- The SP1 host build shared the CPU during this run. `verifier_seconds` may be inflated, but no table reads it.

### 8. agkr-nvf4 A-GKR RTX 5090 NVFP4 art:ad8f92b9 (run r20260924-231454-fa00)
- The verifier is the same f271e422 build as request 4: `diff -r` of backends/gkr/verifier between the 3c769c6d and ab57df0a
  archives on my pod is empty. The statement was regenerated with the ab57df0a archive (`10-agkr-nvf4-verify.sh PREV=ab57df0a`).
- 3/3 proofs accepted (sha256 b6cf5f09 for all three): 98304 units, 24 steps, 976 slots, 2694 msgs, 9491200 bytes, 11666 rows
  and 47782943 elements. Each takes 0.74-0.99 s at 15 threads.
- circuit (485 columns, depth 1, tables E2M1X2 + LK), epilogue, chain and manifest are byte-identical to the export. public.bin
  equals main's `instances_fp4(4096)` (s, t, f), with 0 rows mismatched. The FP8 y16 regression still accepts.
- Negatives, all rejected: `mutate --sample 24` (148/148); s flip, t+1, f+1 (LogUp E2M1X2 sum mismatch); the public line
  reordered, and removed (panic, rc 101).

### 9. arith A100 BF16 B-Ligero, 4 results (reverify r20260924-231754-94c0, binding r20260924-232320-531a)
- All 4 PASS (bf16-ampere-v3: custody 76/76, 25/25, 2^-128.05; ligero-verify d89cffc7).
- The first binding attempt errored because bf16-ampere's frozen relation reads the built x / W arrays, which my pod lacked
  (bootstrapped without BENCH_INSTANCES=1). `20-bench-instances-binding.sh` builds them from my tree's committed seeds (6
  arrays, sha256 = manifest). After that, all 4 are BOUND: 25 statements, 0/4096 y and 0/4096 operand VUs differ.
- Negatives (05) on art:61bc4902 rep1: the base is accepted (25/25). proofbyte is rejected ("linear constraints failed"), and
  so are stmtbyte and swapstmt ("column challenge mismatch").
- Verdict custody: all 4, plus art:37ed86f2, `data preserved` rc 0.

### 10-11. RTX 5090: arith B-Ligero x4 and agkr-nvf4 art:5adf62eb (one run, r20260924-234455-6524)
- agkr-nvf4 (`10-agkr-nvf4-verify.sh PREV=2b25df7f`): the verifier sources are identical (diff -r), and the f271e422 build
  was used. 3/3 proofs accepted (sha256 091fecad): 700 slots, 1689 msgs, 9467080 bytes, 11666 rows, 47782943 elements;
  0.63-0.79 s each. The circuit (485 columns, depth 1, one table LK 89119), epilogue, chain and manifest are byte-identical
  to the export. public.bin shows 0 rows mismatched against main's frozen set. Negatives, all rejected: mutate 148/148; s/t/f
  (LogUp LK sum mismatch); public line reordered or removed. The FP8 regression accepts.
- arith: all 4 PASS (fp4-nvf4: custody 40/40, 13/13, 2^-128.11) and all 4 BOUND (0/4096 y, 0/4096 operand VUs). Negatives
  (05) on art:09209e8a rep1: the base is accepted, proofbyte is rejected (merkle path 120), and stmtbyte and swapstmt are
  rejected (column challenge mismatch).
- Custody: all 5 verdicts `data preserved` rc 0.

### 12. d3-h100 H100 LIVE x12 (run r20260924-235403-7c78)
- `git diff ab9573fd 1d9c3198` touches only tools/research, so my tree's verifier, relations and fixtures are main 1d9c3198's.
- reverify: all 12 PASS (dumped rep 1 with the live verifier's coins). bf16 v3x4 and +hash: 76/76, 25/25, 2^-128.05.
  fp8 v3x4: 40/40, 13/13, 2^-128.33. fp8 +hash: 40/40, 13/13, 2^-128.32.
- Binding: all 12 BOUND, 0/4096 y. The v3x4 operands also match (0/4096). The +hash statements carry no operand words, since
  the operands are hash-authenticated.
- Negatives (05) on art:d0ada343 (f8b-r1) and art:585e4182 (b16h-r1): both bases are accepted and all changes are rejected.
  On the hash tree, stmtbyte fails with "auth: y: multiproof rejected (root mismatch)".
- Custody: all 12 verdicts `data preserved` rc 0. Table 2 (00:16Z) is unchanged: all 12 are also_valid.

### 13. agkr-nvf4 art:49757870 (run r20260925-001640-4f37)
- `10-agkr-nvf4-verify.sh PREV=716ea008` on its own tree (art:78b3aadf). All 5 reps are accepted; each is sha256 091fecad,
  the same bytes as #11. Each takes 0.66-0.81 s. The statement is byte-identical to 716ea008's export, public.bin shows 0 rows
  mismatched, and every negative is rejected (mutate 148/148). Table 2 (00:21Z): 2.5e7× (0.1905 s).

### 14. agkr-fp8 A-GKR 4090 FP8 merged LK art:45c5be4a (run r20260925-005647-bf66; verdict r20260925-010004-3e5d) -- HELD
- The coordinator's hold (0050Z): register the verdict, write no label until red-team-lk passes and the coordinator sends
  "release". Table 2 reads labels only; verdicts feed only the drilldown's verify-CPU column. Release command:
  `25-verdict-45c5be4a.sh` with HOLD=0 VID=art:df4d2c3c (11-label.py `--vid`).
- main's verifier (a48eac01) accepts 3/3 (sha256 c31c1cd8): 727 slots, 1790 msgs, 17966656 bytes; 1.29-1.43 s each. The
  statement is byte-identical to 3be6a35f's export, and public.bin shows 0 mismatches against main's frozen fp8-ada set.
- Rewrite: `git diff 07a8edd6 3be6a35f -- backends/gkr/gpu/v2` is only `merge_tables`, which I reviewed and found sound.
  `--no-merge` reproduces art:1b4fd4a1's verified statement, byte for byte. `23-lk-merge-check.py` (main's parser) finds the
  dump to be exactly its tag-merge: 150/150 queries, 10 tables, 261819 rows as a multiset, unique first column below P.
- Negatives, all rejected: mutate 356/356; my VU-17 +1; the producer's r5_key / shift_out / t_op_out / tnorm_out ("LogUp LK
  level 0: final check") and 4 claim negatives. The honest case is accepted.

### 15. agkr-fp8 A-GKR 4090 FP8 art:ecd96143 (run r20260925-010528-640f; label r20260925-010712-c573)
- The request was written to the coordinator's folder at 00:06Z; I found it at 01:05Z. The statement is unchanged
  (f2363663, before merged LK), so it was labelled as usual. Coordinator handoff 0127Z (4090-agkr-ecd96143).
- main's verifier (a48eac01) accepts 3/3 (sha256 b5ef0238), taking 1.28-1.48 s each. The statement is byte-identical to
  f2363663's export, and public.bin has 0 mismatches.
- Negatives, all rejected: mutate 356/356; my VU-17 +1; the producer's exp_plus, sign_flip, word_minus and word_plus
  (art:9398f028). The honest case is accepted.

### 16. agkr-nvf4 A-GKR 5090 NVFP4 art:dfbc86c4 (run r20260925-010734-e1f8; check r20260925-011927-349e; verdict r20260925-012106-7e86) -- HELD
- The statement is new: BOOL_QUADRATIC + PAIRED. Release command: `28-verdict-dfbc86c4.sh` with HOLD=0 VID=art:7d3aaf2e.
  Coordinator handoff 0127Z (5090-agkr-dfbc86c4-held).
- The 3c769c6d build (f271e422) accepts 5/5 (sha256 ebe7c545), taking 0.62-1.39 s each. The verifier sources at b7cec878
  are identical to 3c769c6d's, the statement is byte-identical to b7cec878's export, public.bin has 0 rows mismatched, and
  the fp8 regression is accepted.
- Negatives, all rejected: mutate 148/148; my s_flip, t_plus, f_plus and public_reordered (LK level 1 sum mismatch) and
  the removed public line (parse error). The producer named no negatives tree.
- `27-nvf4-rewrite-check.py` (main's parser) compares with the 2b25df7f circuit (#11) and finds the same 226 lookup facts
  per unit. The 46 R1 lookups become 46 e·e product wires with asserts w − e = 0, and the PR blocks are exactly all
  (x + 2^b·y, x, y). v1 (r20260925-011239-a1df) failed on three bugs in the checker itself: the tag is on column 0,
  product indices shift, and the block hash included the tag column. v2 fixes them. Sent to red-team-lk (0123Z).

### 17. agkr-fp8 A-GKR H100 FP8 merged LK art:3ae971dd (run r20260925-013458-825f; verdict r20260925-013819-badc) -- HELD
- The rewrite is the same as #14's, at model hopper_e4m3_wgmma_k32. Release command: `29-verdict-3ae971dd.sh` with HOLD=0
  VID=art:e96f50ac. Coordinator handoff 0142Z (h100fp8-agkr-3ae971dd-held); red-team-lk informed (0142Z).
- main's verifier (a48eac01) accepts 3/3 (sha256 0021aa91): 703 slots, 1703 msgs, 17078296 bytes; 1.06-1.17 s each. The
  statement is byte-identical to 3be6a35f's export, and public.bin has 0 mismatches against the fp8-hopper set.
- `--no-merge` reproduces #5's (art:2e7baba7) statement, byte for byte. `23-lk-merge-check.py` passes: 139/139 queries,
  10 tables (R6), 261968 rows as a multiset.
- Negatives, all rejected: mutate 356/356; my VU-17 +1; the producer's r6_key, shift_out, t_op_out and tnorm_out (LK level 0
  final check) and 4 claim negatives (art:70bbba68). The honest case is accepted.

### 18. agkr-nvf4 A-GKR 5090 NVFP4 art:53a64e8b (run r20260925-015434-8c48; verdict r20260925-015724-d06b) -- HELD
- The changes are prover-only (0.1462 s); the statement and proofs are those of #16. Release command:
  `30-verdict-53a64e8b.sh` with HOLD=0 VID=art:223c8efe. Coordinator handoff 0200Z (5090-agkr-53a64e8b-held), which also
  corrects 0127Z's attribution of the #16 negatives.
- `10-agkr-nvf4-verify.sh PREV=00145f51` (source shipped by `git archive`): 5/5 accepted (0.47-0.53 s), the verifier sources
  are identical to 3c769c6d's, the statement is byte-identical to 00145f51's export, and public.bin has 0 rows mismatched.
  Every proof and statement file equals #16's (cmp), and `27-nvf4-rewrite-check.py` passes.
- Negatives, all rejected: mutate 148/148; my s flip, t+1, f+1, reordered public line and removed public line.

### 19-20. agkr-fp8 A-GKR H100 FP8 art:b0c27291 and art:ad76c106 (run r20260925-020532-8dac; label/verdict r20260925-021048-f428)
- One run, `32-agkr-h100-a97576b5.sh`, on a97576b5's source (shipped by `git archive`). Its verifier and `export.py` are
  unchanged from 3be6a35f. `08-agkr-verify.sh` gained `EXPORT_ARGS` because a97576b5's export merges by default.
- b0c27291 (0.409 s): main's verifier accepts 3/3 (sha256 f80ecc53): 2711 slots, 8912 msgs; 0.95-1.07 s each. The statement
  is byte-identical to `--no-merge`'s export, and public.bin has 0 mismatches. All files equal #5's (art:2e7baba7). Negatives,
  all rejected: mutate 356/356; my VU-17 +1; the producer's 4 claim negatives (art:07b5adb8). The honest case is accepted.
  Labelled.
- ad76c106 (0.280 s), HELD: 3/3 accepted (sha256 0021aa91; 0.87 s each). The statement is byte-identical to the export,
  public.bin has 0 mismatches, `--no-merge` reproduces #5's statement, and `23-lk-merge-check.py` passes. All files equal
  #17's. Negatives, all rejected: mutate 356/356; my VU-17 +1; the producer's 4 LK-aimed and 4 claim negatives
  (art:70bbba68). Release: `34-verdict-ad76c106.sh` with HOLD=0 VID=art:b86ca2a8, included in `31-release.sh`.

### 21. agkr-nvf4 A-GKR 5090 NVFP4 art:f277786d (run r20260925-021500-3af9; verdict r20260925-021635-b48c) -- HELD
- The checks are #18's, via `35-agkr-nvf4-f277786d.sh` from c97d2ad2's source. 5/5 accepted (0.47-0.53 s), the verifier
  sources are identical to 3c769c6d's, the statement is byte-identical, and public.bin has 0 rows mismatched. Every file
  equals #16's, the rewrite check passes, and the negatives are all rejected (mutate 148/148 plus my 5). Release:
  `36-verdict-f277786d.sh` with HOLD=0 VID=art:4513180d (in `31-release.sh`). Coordinator handoff 0220Z.

### Table 2 after these labels (laptop render 22:12Z, after `reindex --remote`; A100 and 5090 rows re-rendered 23:31Z)
| cell | before | now | art |
|---|---|---|---|
| RTX 4090 FP8, A-GKR | — | 3.0e7× (1.13 s); 1.75e7× (0.666 s) at 01:24Z | art:1b4fd4a1; art:ecd96143 |
| RTX 4090 FP8, B-Ligero | 2.4e6× (art:fb4934af) | 2.2e6× (0.0840 s) | art:bb75ba4f (arith step 5) |
| RTX 5090 NVFP4, A-GKR | — | 1.4e8× (1.04 s); 4.2e7× (0.314 s) at 23:31Z; 3.3e7× (0.245 s) at 23:52Z; 2.5e7× (0.1905 s) at 00:21Z | art:fe57e68b; art:ad8f92b9; art:5adf62eb; art:49757870 |
| A100 BF16, B-Ligero | 2.2e7× (art:794365d3) | 5.9e6× | art:5bcbf3fb (arith a16-tip-r1) |
| H100 FP8, A-GKR | 1.08e8× (art:2e7baba7, 0.688 s) | 6.4e7× (0.409 s) at 02:13Z | art:b0c27291 |

## Log
- 21:17Z pod created; 21:27Z synced (494 s); 21:30Z bootstrapped (only the GPU stage failed, as expected on a CPU pod).
- 21:35Z first reverify stalled in the pod-catalog `reindex --remote` (~150 manifests/min). I killed it at 21:51Z and
  relaunched with full art ids (get_manifest / get_attempt / fetch fall back to the remote); 03-reverify.sh keeps REINDEX=1
  as an option.
- 22:55Z SP1 labelled (verdict art:34582a00); /root/r2.env removed from the pod.
- 01:24Z /root/r2.env removed, `reindex --remote` rc 0, art:eededf7d and art:7d3aaf2e PRESERVED, 0 verify-po labels on
  45c5be4a and dfbc86c4. The verify-po worktree's .venv is empty, so the laptop tables render now runs main's
  `.venv/bin/python` read-only from /tmp with PYTHONPATH unset.
