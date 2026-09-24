---
lane: verify-po
kind: report
created: 2026-09-24T21:12Z
brief: launch message (coordinator), kb/TABLES.md
branch: lane/verify-po (worktree ~/projects/verity-main-wt/verify-po), base main@ab9573fd
final: 03:45Z hard; budget $6
status: open
---

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

### Table 2 after these labels (laptop render 22:12Z, after `reindex --remote`; A100 and 5090 rows re-rendered 23:31Z)
| cell | before | now | art |
|---|---|---|---|
| RTX 4090 FP8, A-GKR | — | 3.0e7× (1.13 s) | art:1b4fd4a1 |
| RTX 4090 FP8, B-Ligero | 2.4e6× (art:fb4934af) | 2.2e6× (0.0840 s) | art:bb75ba4f (arith step 5) |
| RTX 5090 NVFP4, A-GKR | — | 1.4e8× (1.04 s), then 4.2e7× (0.314 s) at 23:31Z | art:fe57e68b, then art:ad8f92b9 |
| A100 BF16, B-Ligero | 2.2e7× (art:794365d3) | 5.9e6× | art:5bcbf3fb (arith a16-tip-r1) |

## Log
- 21:17Z pod created; 21:27Z synced (494 s); 21:30Z bootstrapped (only the GPU stage failed, as expected on a CPU pod).
- 21:35Z first reverify stalled in the pod-catalog `reindex --remote` (~150 manifests/min). I killed it at 21:51Z and
  relaunched with full art ids (get_manifest / get_attempt / fetch fall back to the remote); 03-reverify.sh keeps REINDEX=1
  as an option.
- 22:55Z SP1 labelled (verdict art:34582a00); /root/r2.env removed from the pod.
