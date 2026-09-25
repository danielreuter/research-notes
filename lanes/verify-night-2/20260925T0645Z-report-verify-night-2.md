---
lane: verify-night-2
kind: report
created: 2026-09-25T06:45Z
brief: launch message (coordinator), kb/TABLES.md (+ Amendment 2026-09-24 11:36 PM PT), kb/LANE-CONTRACT.md v2.0
branch: lane/verify-night-2 (worktree ~/projects/verity-main-wt/verify-night-2), base main@7fcedf47
final: 16:00Z hard; budget $12
status: open
---

CHECKPOINT 00ffe398 (07:31Z) [open] idle-ready: pod at main 00ffe398, ligero-verify d89cffc7 (cargo 66/66), core commitments+leaf conformance 184 pass; 06-core-roots now handles +blake3/+sha256 core row leaves; inbox empty; polling
CHECKPOINT 7fcedf47 (06:45Z) [open] started 06:40Z; pod vy-verify-night-2 (cpu3c 16 vCPU, no guard) created, syncing @ main 7fcedf47; next: bootstrap, then hash-commit 4090 fp8-ada P2 baselines art:71a37756 art:abb219fa + 20-run byte identity
# verify-night-2: non-producer verifier for the Proof optimization workstream (night 2)

Inbox at startup (06:40Z): nothing new. First request from the launch message: hash-commit's 4090 fp8-ada Poseidon2
committer baselines (`lanes/coordinator/20260925T0612Z-handoff-from-hash-commit.md`).

## Pod
- vy-verify-night-2 24p5jceya2gfbn: RunPod cpu3c, 16 vCPU / 32 GB, 60 GB disk, no GPU, host AMD EPYC 9655, created 06:42Z.
  No `guard` (idles between requests by design). Registered (machines.d/vy-verify-night-2.toml).

## Method (as verify-night / verify-po)
- B-Ligero: `backends.direct.ligero.reverify` from my tree with `ligero-verify` built on my pod from my tree
  (`evidence/pod-scripts/03-reverify.sh`): custody, system-digest pin, `batch --target-bits 128` on every rep; PASS writes a
  preserved verification-verdict/v1 and `verified=accepted --by verify-night-2`. Statement binding (`04-stmt-binding.py`):
  the dumped statements' chain-end y words equal the frozen set my tree draws. Negatives: `05-negatives.sh` plus the
  producer's. Commitment roots (`06-core-roots.py`): the statement's tree roots recomputed from my tree's instance set with
  the core reference only (`verity.commitments`: `CommitmentDomain`, `MerkleTree`, `rowleaf`, `poseidon2_babybear` /
  the scheme's leaf), compared with the dumped statements' auth block and the run's commit-evidence.
- Credential: minted on the laptop per request (short ttl, prefixes objects/ manifests/ labels/ attempts/), piped into
  /root/r2.env on the pod, deleted after the request.

## Requests
| # | from | result(s) | cell | verdict | verdict art |
|---|---|---|---|---|---|
| 1 | launch msg + `lanes/coordinator/20260925T0612Z-handoff-from-hash-commit.md` | art:71a37756 (before) art:4be5c412 art:381bcee8 art:9fdb64e0 art:abb219fa (after) | RTX 4090 FP8, B-Ligero +hash (Poseidon2, alg.) | accepted x5 | art:9b700f03 art:7b57c75f art:ae489182 art:2cb926f3 art:403784a7; bundle art:ad2bc9e1 |

### 1. hash-commit 4090 fp8-ada Poseidon2 committer (runs r20260925-065838-66e5 checks, r20260925-070823-6d5a labels)
- The verifier is ligero-verify d89cffc7, built from main 7fcedf47. hash-commit's diff touches only Python: auth, hashauth, hashchain,
  leaf/poseidon2, relchain and run.
- reverify: all 5 full trees PASS (custody 76/76, pinned fp8-ada+hash, 25/25, 2^-128.50, interactive mode, runner's coins).
- Binding (04): all 5 are BOUND (25 statements, 0/4096 y). Core roots (06): the roots recomputed with `verity.commitments` only
  equal the statements' auth block and both commit-evidence copies (a c8c8746a, b 886cef1f, y 49023558). The pure-Python
  Poseidon2 over 8192 rows took 15 s on 16 cores.
- Byte identity (07), all 20 trees: one commit-evidence.json (3df32610), one evidence sha (247e44ca), one rep-1 statement
  cat (897697c9), one system.bin (c540b778) and one root set. The 5 full trees check 82/82 files and the 15 slim ones 57/57
  against proofs.sha256.
- Negatives (05) on trees 13e1c916 (after) and cc2e80a9 (before): the base is accepted, proofbyte is rejected (merkle path
  115), stmtbyte is rejected (auth y multiproof root mismatch) and swapstmt is rejected (column challenge mismatch). The producer
  named no negatives.
- Steps: main's Rust `check_vu_shape` pins them (steps-pin c5cf7f6d). The 25 statements carry (48, 1536), which is canonical.
- The 15 slim runs are not labelled: they carry no proofs (F). Evidence: `evidence/r1-hash-commit/`. Coordinator handoff 0715Z.

## Log
- 06:42Z pod created; synced lane/verify-night-2 @ 7fcedf47 (= main) in 557 s; 06:57Z bootstrapped (r20260925-065505-84c9;
  only the GPU stage failed, as expected), ligero-verify d89cffc7.
- 07:15Z request 1 done. main has moved to 00ffe398 (#15 core-schemes: frame-v3 SHA-256/BLAKE3 row leaves and vllm-v1 in
  `verity.commitments`; #18 views admit algebraic hashes). I will rebuild from it for the BLAKE3 cell.
