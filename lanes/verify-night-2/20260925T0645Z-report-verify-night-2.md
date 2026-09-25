---
lane: verify-night-2
kind: report
created: 2026-09-25T06:45Z
brief: launch message (coordinator), kb/TABLES.md (+ Amendment 2026-09-24 11:36 PM PT), kb/LANE-CONTRACT.md v2.0
branch: lane/verify-night-2 (worktree ~/projects/verity-main-wt/verify-night-2), base main@7fcedf47
final: 16:00Z hard; budget $12
status: open
---

CHECKPOINT 4c437af (12:16Z) [open] 12:20Z 27 done 4/4 accepted. equiv 6fdeed7e accepted. Pod disk hit 98% on sha256 32768 (no label); fixed via push --verify head + evict. 32 running @2c92b9e3 (--custody-r2): 8 blake3-80gb, 2 sha256 x4, 5 poseidon malloc. No laptop fetches.
CHECKPOINT e2dc354 (11:54Z) [open] 11:55Z equiv art:6fdeed7e accepted (x4 4096 rule I), 9b80f566 accepted. 27 running (c9f4a645, 050ddede, 19be6afa); 30 queued w/ --custody-r2 (first +sha256 x4 32768 4aa258ee, poseidon H100 malloc x4). Earlier runs: custody push from pod at FINAL. No laptop fetches.
CHECKPOINT 672b23ae (11:39Z) [open] 11:40Z pod at main bfb0b928 (ligero-verify 8941c72d unchanged source). 27 running: b-ligero malloc re-runs 9b80f566, c9f4a645 (16384 not converged), 050ddede, 19be6afa. f70cf39f passes renderer check (payload-not-local issue). Missed 1037Z handoff in inbox, caught via ls.
CHECKPOINT 7091cd8f (11:21Z) [open] 11:22Z waiting on b-ligero equiv artifacts (rule I; 26-equiv.sh now also runs the renderer's _equiv_content) and blake3-80gb re-registered trees (old 4 superseded). Pod idle at 767115db, verifier 8941c72d. No laptop pulls.
CHECKPOINT 824a9924 (10:56Z) [open] 11:01Z all 4 fp8-ada+blake3 4090 + x4 4096/8192 accepted @3301c435; x4 equiv reproduces. Fail-closed: 5090 NVFP4 (reverify lacks fp4-nvf4), blake3-80gb 8 cells (no proofs/). Pod synced to main 767115db, rebuilding verifier for +sha256.
CHECKPOINT 3301c435 (10:35Z) [open] 10:37Z @3301c435 accepted: SP1 49695f7c (5/5 instance_roots, finding CLEARED), H100 x4 poseidon, +blake3 e9932b72 live + e7d59ab6 (granted; coord told). blake3-80gb x4 fail-closed (no proofs/). 23 running, 24 (5090 NVFP4) queued. MALLOC vars set. Cred re-minted 4h.
CHECKPOINT d6e36fb (10:12Z) [open] 10:13Z H100 BF16 32768 art:72e2b0ba accepted (3301c435). SP1 49695f7c rerun w/ full custody art:17f1205b: reps0-1 instance_roots true. 23 queued (8 +blake3 cells incl live e9932b72, x4 equiv f70cf39f; MALLOC vars set, verify-only). No laptop pulls.
CHECKPOINT 10996616 (09:56Z) [open] 09:57Z coord 0935Z: H100 x4 + BLAKE3 xcheck on main 3301c435 verifier/reverify (r20260925-093931-f022); no CLEARED until red-team ok. SP1 art:49695f7c: host repro vk 0x0098..3a66, my core stmt==dump; all-5-rep --batch running. Laptop: nothing big pulled. Next: blake3-80gb A100
CHECKPOINT e0fc636f (09:31Z) [open] 09:32Z verified BLAKE3 4090 cells art:5d20ad00 (vd 5c100a08) + plateau art:d6328cf5 (vd 41e8f1a0), handed off 0915Z/0930Z; poseidon-v1 4096 x3 labelled (66b0d958, 9a29580b, a4c00776); 32768 relabel + sp1c host build running
CHECKPOINT 10996616 (09:10Z) [open] 09:11Z poseidon-v1 4 results all checks PASS (labels refused by over-broad self-label guard, fixed); running r20260925-090956-57e5: BLAKE3 cells art:5d20ad00 + art:d6328cf5 (priority), pv relabels incl art:af008992, then sp1-committed host build
CHECKPOINT 1864945 (08:50Z) [open] 08:50Z red-team R4 fixed in 06/16 (proof-per-entry, stmt-on-disk==manifest, batch n==entries); 10 cleared re-PASS; RT dumps refused. Missed poseidon-v1 0800Z req, now running with 0835Z: 4 results (4090/A100, n=4096+32768) r20260925-084940-2e1f
CHECKPOINT cafa9464 (08:17Z) [open] 08:17Z idle-polling; 10 verdicts preserved (hash-commit x5 + R1/R2 recheck x5), nit fixed; pod vy-verify-night-2 idle at main 00ffe398; awaiting BLAKE3 full-relation cell from b-ligero-standard-hash
CHECKPOINT 00ffe398 (08:04Z) [open] R1/R2 recheck: 5 published +hash cells PASS (art:794365d3 art:271e0e3a art:5387c1b5 art:1abdf12a art:99867b4c; verdicts art:488f12f0..art:0ec89f16) + hash-commit x5 PASS; handoff coordinator 0805Z; polling for BLAKE3 cell
CHECKPOINT 00ffe398 (07:49Z) [open] coordinator 0745Z (red-team SH R1/R2): 06-core-roots strengthened (triple==untiled layout, per-rep disjoint coverage, binding via hashauth.binding_digest, count, roots); rechecking 5 published +hash cells + my 5 hash-commit results in r20260925-074901-8cce
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

| 2 | `20260925T0745Z-handoff-from-coordinator.md` (red-team SH R1/R2) | published +hash cells art:794365d3 [4] art:271e0e3a [8] art:5387c1b5 [12] art:1abdf12a [16] art:99867b4c [20]; re-check of #1 | A100 BF16 / H100 BF16 / H100 FP8 / 4090 FP8 / 5090 NVFP4, B-Ligero +hash | PASS x5 (+ #1 PASS x5) | art:488f12f0 art:1de26956 art:6844cc11 art:edb24a45 art:0ec89f16; #1: art:9909ec89 art:4c7497f2 art:eea752f6 art:0249a538 art:8460a8dd |
| 3 | `20260925T0835Z-handoff-from-red-team-standard-hash.md` (R4) | the 10 of #1 and #2 | (as above) | R4 fixed; 10/10 re-PASS, no verdict changes | none (recheck only) |
| 4 | `20260925T0800Z-handoff-from-poseidon-v1.md`, `20260925T0835Z-handoff-from-poseidon-v1.md` | art:d87b4895 (4090, n 4096) art:c8b52ee2 (4090, n 32768) art:289841b1 (A100, n 4096) art:b5a4454f (A100, n 32768) | RTX 4090 FP8 / A100 BF16, B-Ligero +hash (Poseidon2, alg.), TABLES.md sweep | accepted x4 | art:66b0d958 (d87b4895) art:a4c00776 (289841b1) art:2c83448c (c8b52ee2) art:258c8dd3 (b5a4454f) |
| 5 | `20260925T0850Z-handoff-from-coordinator.md` | sp1-committed art:49695f7c | RTX 4090 FP8, SP1 frame-v3 committed (2^-92.9, alg. hash in SP1) | accepted; CLEARED (5/5 reps instance_roots true) | art:58978516 |
| 6 | `20260925T0905Z-handoff-from-b-ligero-standard-hash.md` | art:5d20ad00 (4096 frozen) art:d6328cf5 (16384 plateau) | RTX 4090 FP8, B-Ligero +hash BLAKE3 (standard hash, full relation) | accepted x2 | art:5c100a08 art:41e8f1a0 |
| 7 | `20260925T0900Z-handoff-from-poseidon-v1.md` | art:af008992 (same run as art:289841b1) | A100 BF16 +hash, sweep bounded by the frozen set | accepted | art:9a29580b |
| 8 | `20260925T0925Z-handoff-from-poseidon-v1.md` | art:72e2b0ba (BF16 32768) art:23528a63 (FP8 65536) art:f25486f6 (BF16 4096) art:6c512437 (FP8 4096) | H100 BF16 / FP8, B-Ligero +hash (Poseidon2, alg.) @3301c435 | accepted x4 | art:31e5458f art:181ccbdb art:87ddb393 art:55208f00 |
| 9 | `20260925T0844Z-` + `0935Z-handoff-from-blake3-80gb.md` | art:855cc597 (A100 4096) art:f32eec55 art:3b78cbda (H100 4096) art:4d1d6d6e (H100 32768) | A100 BF16 / H100 BF16 / FP8, B-Ligero +blake3 | not re-verifiable yet (fail-closed: run_files lack proofs/) | none; blake3-80gb asked to re-register |
| 10 | `20260925T0958Z-` + `1008Z-handoff-from-b-ligero-standard-hash.md`, coordinator 1017Z / 1024Z | art:e9932b72 (live) art:e7d59ab6 (x1) art:5d20ad00 art:d6328cf5 (#6 again) art:017a7069 (x4 4096) art:6b6d4484 (x4 8192) | RTX 4090 FP8, B-Ligero +blake3 @3301c435 (class granted 1027Z, x4 1053Z) | accepted x6 | art:2cd1052b art:0a3efdaf art:2ba7f873 art:ddf49ecc art:953851f2 art:1914e46e |
| 11 | `20260925T1030Z-handoff-from-poseidon-v1.md` | art:70f275ac (4096) art:6740eb22 (131072) | RTX 5090 NVFP4, B-Ligero +hash (Poseidon2, alg.) | not re-verifiable yet (fail-closed: main's reverify has no fp4-nvf4 relation) | none |
| 12 | `20260925T1045Z-handoff-from-blake3-80gb.md` | art:6d067ed3 art:f4dc0501 art:4d43ab87 art:4d151f38 | H100 BF16 / FP8 +blake3 re-runs (75cbbac1) | not re-verifiable yet (fail-closed: no proofs/) | none |

### 9. +blake3 at 3301c435, 5090 NVFP4, and the pod at 767115db (runs r20260925-102219-11de, r20260925-103509-76d9, r20260925-105556-10f6; `23`, `24`, `25`)
- **#10:** every cell passes main 3301c435's reverify, and 04 / 06 / R4 / 05 all behave.
  - fp8-ada+blake3 roots at 4096: a 2f9ff265, b 0413c926, y 49023558 (e9932b72, e7d59ab6 and 5d20ad00 alike).
  - x4 4096 roots: a 5b6f7c44, b 65621cdd, y 5522d305, steps 12. x4 8192 roots: a 19b0779a, b ea406407, y 3a1f147d.
  - The x4 instance-equiv file art:f70cf39f re-derives (`--check`: "reproduces; equal=True"). Its candidate is c86e51a1… (the
    same as art:017a7069's ref), against frozen e66ff0f2….
- **Findings:** SP1 art:49695f7c had `finding=UNDER RE-VERIFICATION`, and I added `finding=CLEARED` with ref my verdict
  art:58978516. None of the +blake3 cells carried a finding.
- **#11:** reverify's `committed_trees` calls `relations.relation('fp4-nvf4')`, which raises "unknown --relation". My checks on
  art:70f275ac all pass: 04 BOUND; 06 ROOTS-MATCH a 84ce9030, b 3f2303f6, y 68c80a14; my verifier ACCEPTs 13/13 at 2^-128.11;
  and the 3 tampers REJECT. I stopped the plateau before its reverify.
- **#9 and #12:** eight blake3-80gb cells in total, handoffs 1030Z and 1100Z.
- **Pod:** synced to main 767115db, and ligero-verify rebuilt to sha256 8941c72d (cargo tests 34 + 7 + 27 ok). A LABEL=0 smoke
  test on e7d59ab6 passes. 596529d2 and d89cffc7 are kept. The credential was re-minted at 10:36Z with a 4 h TTL.

### 8. H100 poseidon-v1 cells and the 3301c435 verifier (run r20260925-093931-f022; `22-batch.sh`)
- ligero-verify was rebuilt from main 3301c435 (ligero-steps-pin merged) to sha256 596529d2; the old binary is kept as
  `ligero-verify-d89cffc7`. From here on, every verdict's detail names "ligero-verify sha256 596529d2 (main 3301c435)".
- The H100 cells, all ROOTS-MATCH, R4 ok and BOUND, with negatives base ACCEPT and 3 REJECT on all four trees:

| result | line | reverify | roots a / b / y | steps, K |
|---|---|---|---|---|
| art:72e2b0ba | bf16-hopper, 32768 | 193/193, 2^-128.47 | 29eb6f09 / 5dff9f39 / 0af34437 | (96, 1536) |
| art:23528a63 | fp8-hopper, 65536 | 193/193, 2^-128.47 | 957f1eac / 86563e13 / 58393eb1 | (48, 1536) |
| art:f25486f6 | bf16-hopper, 4096 | 25/25, 2^-128.05 | ce346697 / c7f14384 / 3f3fd633 | (96, 1536) |
| art:6c512437 | fp8-hopper, 4096 | 13/13, 2^-128.32 | 57ac9df1 / 170d0a18 / 22fa3c6e | (48, 1536) |

- The plateaus are bound to `relchain.instances(rel, N)`, whose first 4096 VUs equal the frozen set (0 mismatched).
- The #6 BLAKE3 cells get a dry-run PASS with main 3301c435's reverify (49/49, 193/193, pinned fp8-ada+blake3). They do not fail
  closed; fresh 3301c435 labels are in #10.
- **blake3-80gb (#9):** the run_files keep manifest.json and rep1/ at the root, and 3301c435's reverify refuses them ("has no
  proofs/ or dumps/ manifest.json"). 05 needs the same layout. So these are not re-verifiable yet (fail-closed), not PULLED.
  Handoff `lanes/blake3-80gb/20260925T1030Z-…`.

### 7. sp1-committed frame-v3 cell art:49695f7c (runs r20260925-095557-7799 failed on custody, r20260925-100420-dc5b; `18`, `19`)
- **Build:** host `--features relation-committed` from a git archive of b54e42ed, built on my pod with SP1 6.4.0 CPU. It
  reproduces ELF f4fc749f… and vk 0x00989332…3a66. The committed tests: 8 pass, and 2 committed_vllm tests fail (a missing
  vllm_v1 vectors file in the archive; not the frame-v3 path).
- **My statement:** written from my tree's fp8-ada set with `verity.commitments` only (sha256/row/v1 row leaves, u32 y leaves, v2h
  bindings, frame-v3 trees). It equals the dump's statement on every field. Roots a f3ffcf70, b 8cd05fd5, y bd462407.
- **Custody:** the attempt's run_files art:17f1205b holds all 5 reps. The handed-off art:9e3c06bd holds rep 0 only, and its
  rep 0 and statement are byte-equal. The first run used `research fetch <run>`, found nothing and failed the gate unlabelled.
- **`committed-verify --batch` against set art:4a6f7602 (sha 531a5c01):** ok with `instance_roots: true` on reps 0–4, against my
  statement and the dump's (10/10). The honest verify is ok (sp1_ok, vk pinned).
- **Negatives, 7/7 REJECT:** wrong root a, wrong root b, wrong root y, the dump's tampered proof, one proof byte flipped, my
  statement over [0, 4095), and tampered + adopt + batch.
- The coordinator's rule for this cell makes it CLEARED.
- **Finding:** SP1's y leaf is the raw chain-end FP32 word, while B-Ligero's is `pack_public` (22 bits). The y roots differ
  (bd462407 vs 49023558), and a and b agree. Reported to the coordinator 1030Z.

### 6. b-ligero-standard-hash BLAKE3 cells (run r20260925-090956-57e5; `21-batch.sh`, `20-cells.sh`)
- The manifest's `relation.name` is `fp8-ada`, and the leaf is in `statement_relation` (`fp8-ada+blake3`). 06 now prefers
  `statement_relation`; with `name` alone it would have recomputed Poseidon2 roots. It also records every statement's
  (steps, K): (48, 1536), the canonical shape, which main's Rust `check_vu_shape` pins in pinned mode (v6 included).
- 4096: reverify 49/49 at 2^-128.40 (custody 148/148); BOUND; ROOTS-MATCH a 2f9ff265 b 0413c926 y 49023558 (= my
  core self-test at 07:37Z); R4 ok. Handoff 0915Z.
- 16384: reverify 193/193 at 2^-128.40 (custody 580/580); BOUND against `relchain.instances(fp8-ada, 16384)` (digest
  b8722924), whose first 4096 VUs equal the frozen set; ROOTS-MATCH a b25b4330 b 19f730ce y 72d46a23; R4 ok. Handoff 0930Z.
- 05 negatives on both trees: base ACCEPT, the three tampers REJECT. 05 now uses hard-linked copies, unlinking a file
  before rewriting it, so the 5.4 GB rep isn't copied four times.
- I used main's verifier plus my R1/R2/R4 checks, not the producer's fixed reverify (06176b41 + 806a2f73).

### 3. red-team SH R4 (proof per stmt entry; runs r20260925-084402-ec1a, r20260925-084744-69ed)
- 06 counts coverage only for entries with a `proof` and `proof_sha256` in the same rep dir. Each rep dir's `.stmt` files on
  disk must equal its manifest entries. 16 also requires reverify's per-rep batch `n` to equal 06's `entries_per_rep`.
- The red team's art:c7683eb2 dumps give MISMATCH: `fix/stmt-entry` (two entries without a proof, [0, 3) not tiled) and
  `fix/orphan-stmt` (3 `.stmt` on disk vs 1 entry). The `main/*` dumps contain only the manifest.
- The 10 cleared results re-PASS with R4 ok (batch n == entries: 25, or 13 for fp8-hopper and fp4-nvf4).
- Reply: `lanes/red-team-standard-hash/20260925T0850Z-handoff-from-verify-night-2.md`.

### 4. poseidon-v1 (run r20260925-084940-2e1f; `17-r4-poseidon-v1.sh`)
- I missed the 0800Z request when it arrived (the inbox didn't list it on my 08:17Z and 08:27Z polls). I found it at 08:37Z
  and took it together with 0835Z.
- The producer tree is lane/poseidon-v1 54ad119d = main + hash-commit's `--commit-reps` harness (6e1cc576) + the committer I
  accepted at 0715Z (b862be30). It is prover-side only; I verified with main's ligero-verify d89cffc7.
- n 4096: both PASS (reverify 25/25; BOUND; ROOTS-MATCH, with the same roots as #1 and #2; R4 ok). 05 negatives on both
  trees: base ACCEPT, proofbyte / stmtbyte / swapstmt REJECT.
- 11-label.py refused both: its guard matched "verify-night-2" in `meta.committer` ("... verified by verify-night-2 0715Z").
  `meta.lane` is poseidon-v1. The guard now refuses only on a producer field (lane / producer / by / author ...) naming
  this lane, on `lane/verify-night-2`, or on any mention when `meta.lane` is absent or this lane. Relabel pending.
- n 32768 is past the 4096-VU frozen tier. 04 binds to my tree's `relchain.instances(rel, 32768)` and checks that its first
  4096 VUs equal the frozen set. For fp8-ada that is the synthetic recipe continued; for bf16-ampere, frozen ids recycled
  i mod 4096. Whether such a point enters the tables is the renderer's call (poseidon-v1 coordinator 0730Z).

### 2. red-team SH R1/R2 recheck (runs r20260925-074901-8cce, r20260925-075910-98b2)
- `06-core-roots.py` strengthened. R1: each statement's (vu_index, x_index, w_index) equals the untiled layout (x = W = vu) over
  its dumped range, and each rep's sub-batch ranges tile [0, 4096) disjointly. R2: binding (hashauth.binding_digest, asserted
  equal to core identity_digest), owner, count and root recomputed from my tree's set, compared with every statement.
  Commit evidence is compared where present; old results carry none, which is fine.
- `16-sh-recheck.sh`: reverify --dry-run + 04 binding + 06, then a verdict per PASS via `11-label.py` (the detail states
  that R1/R2 were checked).
- All 10 PASS. The A100 needed the frozen vu-k1536 arrays built from my tree's seeds (6/6 sha256 = manifest). The 5090 fp4-nvf4
  leaf is a lane-formatted Poseidon2 (FP4Format: 72 nibbles on 24-bit lanes) with no core reference, so its row digests come
  from my tree's backend committer. The first run errored on it in the core `pack_words`; I reran it (r20260925-075910-98b2).
- Coordinator handoff 0805Z. Evidence: `evidence/r2-sh-recheck/`.
- red-team-standard-hash 0805Z: my `06` check() flags their R1 forgery as MISMATCH (leaf indices + y root; art:8f2112e2).
  They had one nit: pick exactly reverify's manifest (proofs/manifest.json, else dumps/). Fixed in 04 and 06. The rerun
  (r20260925-080440-d9e6) gives the same result for all 10: BOUND and ROOTS-MATCH, same roots.

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
- 07:16Z lane/verify-night-2 fast-forwarded to main 00ffe398 (pushed) and the pod re-synced. Rebuild r20260925-071601-985d:
  ligero-verify is still d89cffc7 (the crate is unchanged) and cargo test passes 32+7+27. pytest of the core commitments +
  leaf core_schema/conformance: 184 passed, 3 skipped (13.5 min on CPU).
- 07:40Z `06-core-roots.py` now picks the row leaf by relation suffix (+blake3 -> core `blake3_row_digest`, +sha256 ->
  `sha256_row_digest`). Self-test `15-blake3-selftest.py` (r20260925-073720-71cc): the core-only fp8-ada+blake3 roots equal
  the backend committer's (a 2f9ff265, b 0413c926, y 49023558; set bench-instances-fp8-ada/v1, manifest e66ff0f2). main's
  Rust PINS already carry ("fp8-ada", "blake3", 71f39e44…); b-ligero-standard-hash's branch adds only bf16-ampere and
  fp8-hopper pins.
- 08:30Z pre-review of lane/b-ligero-standard-hash (tip 8dace837) vs main, verifier side: auth.rs / hashauth.py
  `layout_error` (R1, 3af90e71) only adds refusals (x = W = vu, or an nx x nw tile); leaf.rs adds 2 pins; serialize.py
  extends the K check to v6; blake3 `leaf_bytes_many` is prover-side (my roots use core `blake3_row_digest`, not it);
  reverify R2 (de2fa317) mirrors my 06 check. Nothing that would need the producer's verifier build.
