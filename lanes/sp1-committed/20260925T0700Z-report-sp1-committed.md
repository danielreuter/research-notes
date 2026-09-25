---
lane: sp1-committed
kind: report
created: 2026-09-25T07:00Z
status: final
---

CHECKPOINT none (08:45Z) [final] tip b54e42ed. frame-v3 SP1 committed cell art:49695f7c (run-files art:9e3c06bd): t.total 51.04s + commit.seconds 0.008s, 69 shards, 2^-92.9 (algebraic flag), handed to verify-night-2 w/ R2 root recompute. vllm-v1 host built (vk 0x00eacdbd), unmeasured. Pod gone 08:44Z.
CHECKPOINT 10996616 (08:45Z) [final] tip b54e42ed. frame-v3 SP1 committed cell art:49695f7c (run-files art:9e3c06bd): t.total 51.04s + commit.seconds 0.008s, 69 shards, 2^-92.9 (algebraic flag), handed to verify-night-2 w/ R2 root recompute. vllm-v1 host built (vk 0x00eacdbd), unmeasured. Pod gone 08:44Z.
CHECKPOINT b54e42ed (08:38Z) [open] frame-v3 cell: art:49695f7c (run-files art:9e3c06bd) t.total 51.04s+commit 8ms, 69 shards 2^-92.9, plateau. Red-team R2 acted on: b54e42ed committed-verify --batch (roots vs frozen set) + prover-chosen-roots negative. Build/retro check r20260925-083540-f37a running.
CHECKPOINT cafa9464 (08:18Z) [open] frame-v3 measured r20260925-080516-d8ac: 9/9 negs rejected, 5 reps proved+verified (~4.9s verify), sweep B1024/2048 running. Next: register, build vllm-v1 (build_vllm.sh), vllm measured, same-pod bare baseline.
CHECKPOINT b06a7ec3 (07:59Z) [open] measured fp8-ada frame-v3 run r20260925-073644-5901: 5 reps prove ~52.6s B=4096, 69 shards, 105MB, commit ~8ms, 5/5 pinned verify; sweep in progress. vllm-v1 variant coded+pushed (tip b06a7ec3, main 5631e667 merged); next: pod build+negatives, measured vllm run
CHECKPOINT dcd4eca0 (07:36Z) [open] committed host built (vk 0x009893321b66..3a66, elf f4fc749f; stock identity reproduced); pod: common tests ok incl committed::*, fp8-ada set = art:4a6f7602; exec negatives all rejected (flip-y, sign-of-zero tamper-x @tree a, wrong roots); 215M cycles/4096 VU (hash 54M). launching measured run
CHECKPOINT dcd4eca0 (07:26Z) [open] tip dcd4eca0: committed guest/host/py/vectors + vector_run sp1-committed pushed; pod build r20260925-071747-5eae (stock identity then cuda,relation-committed) running; next: pod cargo tests, executor negatives, measured fp8-ada run
CHECKPOINT 4f1dacb4 (07:18Z) [open] merged main 00ffe398 (core frame-v3 schemas; vectors from core, stand-in dropped); host committed-* cmds + py reference (7 vectors) at 4f1dacb4; pod build r20260925-071747-5eae running; vllm-v1 variant queued after frame-v3 per handoff
CHECKPOINT 1efd4300 (07:04Z) [open] guest feature relation-committed (bare relation + sha256/row/v1 digests via SP1 precompile, frame-v3 tree check) at 1efd4300; pod vy-sp1-committed (4090) bootstrapping stock+committed builds; next host committed-* cmds, py reference
CHECKPOINT 7fcedf47 (06:47Z) [open] started: read contract/TABLES/decision/sp1 kb+reports; PR #15 open, coding against its sha256/row/v1 framing; 4090 pod creating; next: committed guest + host tree check
# sp1-committed report

Lane `sp1-committed`, branch `lane/sp1-committed` in `~/projects/verity-main-wt/sp1-committed`, base main @ 7fcedf47.
Budget $50, FINAL 15:00Z. Goal: an SP1 stock guest proving the full relation on a frozen set with frame-v3 SHA-256 row
leaves (`sha256/row/v1`, PR #15's schema), the host checking the trees natively; bench-result/v1 with the commitment timed.

## Design (07:00Z)

- Guest feature `relation-committed` (its own ELF / vk): reads the bare header and chunks, runs `bare::check_pair` per VU,
  and hashes every x row (role 1) and W column (role 2) with `sha256/row/v1` through the SP1 SHA-256 precompile
  (the workspace's `sha2` patch). The constant 64-byte prefix is absorbed once and the hasher cloned per row (midstate).
- Public values: `"verity/sp1/relation-committed/v1" || u32 format || id || u32 K || u32 B || u8 verdict || y || dx[B] || dw[B]`.
- Host verifier: SP1 verify under the pinned vk, then rebuilds the three frame-v3 trees (a: x-row digests, b: W-column
  digests, y: word leaves `u16`/`u32` big-endian) and compares with the statement's roots. Bindings follow B-Ligero's hashed
  modes (`verity/ligero-b/auth-binding/v2h`, {dataset, tier, manifest_sha256, lo, hi, K, tree, schema}), so every backend
  binding this scheme over a frozen set has the same roots. Kept in one module (`common/src/committed.rs`,
  `verity_sp1/committed.py`) to swap to the core schema when PR #15 merges.
- Commitment bucket: each timed rep first commits the batch natively (row digests + trees, `commit.seconds`), then proves;
  `e2e.seconds = commit.seconds + t.total` (the views' P divides this).
- Line: the RTX 4090 FP8 Ada set (cheapest pod and half the hash blocks of BF16, within the lane's 4090/H100 pod rule).

## Results (08:40Z)

- **frame-v3 cell** (run r20260925-080516-d8ac, 4090, source cafa9464): bench-result/v1
  art:49695f7caa4ddf4a8d80760524ead491f1bbb5048c10f69af809d77eac819a89, run-files art:9e3c06bd9680153b2369a2734292d9428f24a68501e1bb6f506e5078f41e2b92
  (statement, proof-rep0, tampered proof, JSON; reps 1-4 in the run's R2 custody). The numbers:
  - fp8-ada [0, 4096); t.total 51.036 s (prove + serialize, median of 5), commit.seconds 0.008 s (a separate bucket, so
    e2e 51.044 s and 80.2 VU/s); plateau over B 1024/2048/4096 (70.2 / 78.6 / 80.2 VU/s);
  - 69 shards, 105 MB, verify 4.9 s CPU, peak device 21.1 GB; 215.5M cycles (52.6k per VU);
  - 9/9 executor negatives rejected (flip-y, sign-of-zero tamper-x caught at tree a, wrong roots); 4/4 proof negatives rejected;
  - security 2^-92.891 per proof (-99.0 + log2 69), flag "algebraic hash inside SP1: not for highest-stakes use".
- **Overhead vs survey §4.4** (+3–15% projected). Against the bare guest (sp1-formats art:8d9df3a2, another 4090 host): +35%
  cycles, +92% shards, +117% t.total. The likely cause is ShapeChecker charging deferred precompile memory to CPU shards (kb).
  51 compressions per VU are used, against the survey's ~100.
- **Red-team SH R2** (the roots are prover-chosen): acted on at b54e42ed. `committed-verify --batch` recomputes the roots from the
  frozen set; `--adopt-published-roots` is the negative; vector_run verifies with `--batch` and requires the prover-chosen-roots
  negative to be rejected by the instance check only. Replayed locally (/tmp harness); not yet compiled on a pod.

## FINAL

- **Tip:** lane/sp1-committed b54e42ed (pushed; main 5631e667 merged in).
- **What works:**
  - the relation-committed guest (frame-v3 sha256/row/v1 through the SP1 precompile), with the host tree check, statement,
    vectors and Python reference;
  - vector_run `--backend sp1-committed`; the measured frame-v3 cell above, handed to verify-night-2 with the R2
    root-recomputation requirement;
  - the vllm-v1 variant (guest feature relation-committed-vllm, host, Python, fixtures/sp1-committed/committed-vllm-vectors.json,
    views/drilldown lines), tested locally against the core vllm_v1 vectors.
- **Known failures and gaps:**
  - b54e42ed's host compiled on the pod with `cuda,relation-committed-vllm`. Build run r20260925-083540-f37a installed the vllm
    host (guest ELF 412641773dc9fd396e1c7ce8423cfad502f9403481c3ca413c1744f84634519a, vk
    0x00eacdbd2f4b4a1f3b4001f79d3afff7ebb409ea4b8df322e322f26470ce5cc9). The pod was then terminated during the bare build, so the
    frame-v3 rebuild and pin check, the retro `--batch` verifies and the vllm executor negatives never ran;
  - vllm-v1 is not measured;
  - there is no same-pod bare baseline;
  - the in-run verifier of art:49695f7c did not check the roots against the instances (R2);
  - bench.views marks vllm-v1 core-defined on this branch, which needs the coordinator's acceptance.
- **Next steps:** on a 4090 pod, from source b54e42ed:
  1. `research run --on POD --project verity --source . --cwd source --stage sp1c.build-vllm -- bash -c "$(cat evidence/pod-scripts/build_vllm.sh)"`.
     It builds the vllm and bare hosts, checks that the frame-v3 ELF/vk pin is unchanged, and installs the frame-v3 host at the
     tip. It then runs the retro `--batch` verifies on the d8ac proofs (it needs the run dir, or fetch it from custody or
     art:9e3c06bd) and the vllm executor negatives.
  2. `vector_run.py --backend sp1-committed --committed-scheme vllm-v1 --batch /workspace/sp1-committed/fp8-ada.bin --reps 5 --expect-vk <vllm vk> --sweep-b 1024,2048`
     with `--custody-r2 --custody-ttl 8h --exclusive`, then register it with evidence/reg.sh.
  3. Run the same-pod `--backend sp1-bare` baseline.
  4. Optionally, fork patch 0006 to test the ShapeChecker explanation (non-stock).
- **Pod:** vy-sp1-committed (6n0tv9llnhs142, 4090, $0.74/h), up about 2 h (roughly $1.5), gone (404) at 08:44Z, terminated during WRAP UP.
- **Artifacts:** art:49695f7c (bench-result), art:9e3c06bd (run-files), fp8-ada set art:4a6f7602.
- **Handoffs answered:**
  - 20260925T0650Z-handoff-from-coordinator.md: core schemas and vectors adopted; frame-v3 first, then vllm-v1 (coded, host built, unmeasured).
  - 20260925T0752Z-handoff-from-coordinator.md: survey §4.4 adopted (SHA-256 precompile row digests); the measured overhead is
    above its projection (Results); no link protocol built.
  - 20260925T0820Z-handoff-from-red-team-standard-hash.md: R2 acted on at b54e42ed (`--batch` instance-root check and the
    prover-chosen-roots negative), and verify-night-2 was told to recompute the roots.
  - 20260925T0823Z-handoff-from-coordinator.md: wrap-up done (registered, handed off, pod gone, FINAL).
