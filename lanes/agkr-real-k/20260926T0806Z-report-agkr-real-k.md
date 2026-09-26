---
lane: agkr-real-k
kind: report
created: 2026-09-26T08:06Z
status: open
---

CHECKPOINT 1a1bb6a2 (12:53Z) [open] pause lifted: pods vy-agkr-l40s + vy-agkr-l40s-ver in US-MD-1 (verifier 10.0.129.112:7200, sshd 7201); launching: k2048 k8192
CHECKPOINT c1e7bded (12:50Z) [open] WAITING K=8192 cell: ver r20260926-125010-7e7f on vy-agkr-l40s-ver, prover r20260926-125013-271e on vy-agkr-l40s
CHECKPOINT c1e7bded (12:32Z) [open] WAITING K=2048 cell: ver r20260926-123218-ed39 on vy-agkr-l40s-ver, prover r20260926-123236-c272 on vy-agkr-l40s
CHECKPOINT c1e7bded (12:32Z) [open] pause lifted: pods vy-agkr-l40s + vy-agkr-l40s-ver in US-MD-1 (verifier 10.0.129.112:7200, sshd 22); launching: k2048 k8192
CHECKPOINT c1e7bded (12:32Z) [open] L40S pods: vy-agkr-l40s oa0m0tx3c6vxrm (machine h1ovgmmrd3dh) + vy-agkr-l40s-ver nqkz63dauxz4ql (machine bmf6gxxmufbv) in US-TX-4, global net 10.0.129.112; launching K2048 + K8192
CHECKPOINT c1e7bded (12:23Z) [open] L40S prover vy-agkr-l40s oa0m0tx3c6vxrm created in US-TX-4 (secure, $1.09/h; US-NC-1/SE/OC-AU-1 had no L40S stock 12:03-12:22Z); verifier next, must be another machine
CHECKPOINT c1e7bded (12:07Z) [open] L40S cells: branch cursor/agkr-l40s-101-f806 @ c1e7bded (main 961d0667 merged, PR #74 placement; cgroup-v1 threads + RTT retry 369d741c pushed; c1e7bded push blocked: GitHub token invalid, bundle in evidence/); no L40S stock in US-NC-1/SE/OC-AU-1 at 12:05Z; polling US-NC-1 secure + global net once a minute; plan through bench.cell placement once both pods exist
CHECKPOINT 9cbfdcf2 (11:47Z) [open] reopened for #101 route (a) cells on an L40S prover (K=2048, K=8192; coordinator 11:44Z, $6): NOT final; pods in US-NC-1 with global networking, verifier on a separate physical host
CHECKPOINT 9cbfdcf2 (10:36Z) [final] FINAL: route (a) real-K cells art:a0ca8ef6 (K=2048, 4096 VUs, 283 VU/s) + art:a979dfcb (K=8192, 1024 VUs, 63.5 VU/s), A-fs art:7ae6c190 art:0e1095f3; PR #69 @ 9cbfdcf2 (branch cursor/agkr-real-k-f806); pods terminated ~10:32Z; ~$5.0
CHECKPOINT 9cbfdcf2 (10:35Z) [final] FINAL: route (a) real-K cells art:a0ca8ef6 (K=2048, 4096 VUs, 283 VU/s) + art:a979dfcb (K=8192, 1024 VUs, 63.5 VU/s), A-fs art:7ae6c190 art:0e1095f3; PR #69 @ 9cbfdcf2; pods terminated ~10:32Z; ~$5.0
CHECKPOINT 9cbfdcf2 (10:33Z) [open] cell runs done (k2048 k8192 afs); pods drained and terminated
CHECKPOINT 9cbfdcf2 (10:25Z) [open] WAITING A-fs r20260926-102535-c15b on vy-agkr-real-k-a100
CHECKPOINT 9cbfdcf2 (10:13Z) [open] WAITING K=8192 cell: ver r20260926-101258-e284 on vy-agkr-real-k-ver, prover r20260926-101301-8697 on vy-agkr-real-k-a100
CHECKPOINT 9cbfdcf2 (09:50Z) [open] WAITING K=2048 cell: ver r20260926-095014-2234 on vy-agkr-real-k-ver, prover r20260926-095028-c0bd on vy-agkr-real-k-a100
CHECKPOINT 9cbfdcf2 (09:50Z) [open] pause lifted: pods vy-agkr-real-k-a100 + vy-agkr-real-k-ver in US-MD-1 (verifier 154.54.102.48:18847, sshd 18846); launching: k2048 k8192 afs
CHECKPOINT 40f6ad69 (09:45Z) [open] pause lifted (coordinator 0935Z): launching launch-cells.sh (k2048 re-sweep with the scatter_terms fix, k8192 re-sweep GATE=0, A-fs both sets) on tip 40f6ad69; budget ~$5
CHECKPOINT a7500a4b (09:31Z) [blocked] on the 0910Z spend pause: PR #69 merge-ready (handoffs 0930Z red-team request, 0935Z merge); cells art:95fdd0ae (K=2048) art:20197f8b (K=8192) registered, producer gate r20260926-092055-36d6 10/10; remaining runs ready: evidence/pod-scripts/launch-cells.sh
CHECKPOINT 5cc7b6e4 (09:14Z) [open] pods drained + terminated (a100 ~09:13Z, ver ~09:18Z; ~$2.7); completed: K=2048 cell (ver r20260926-083651-9a59, prover r20260926-083700-e919 -> art:95fdd0ae), K=8192 cell (ver r20260926-085655-0dc4, prover r20260926-085704-0afb, plateau 512 VUs 52 VU/s; 1024 hit a harness dir-reuse bug) all preserved; registering K=8192 on CPU
CHECKPOINT 5cc7b6e4 (09:04Z) [open] PAUSE ack (coordinator 0910Z): no new cell runs; K=8192 cell r20260926-085704-0afb (ver r20260926-085655-0dc4) in flight, finishing its sweep, then custody, drain + terminate both pods; CPU work continues; K=2048 cell art:95fdd0ae registered
CHECKPOINT 5cc7b6e4 (08:59Z) [open] K=2048 route (a) cell art:95fdd0ae (A100, captured #101, plateau 2048 VUs: 231 VU/s, 3.3e8x proving, NON_ZK_PROOF 2^-130.19; ver 10/10 sessions accepted, records art:8455c116); 4096 hit a 32-bit offset bug in scatter_terms (invalid proof rejected by both verifiers) fixed b98d5feb; K=8192 cell running r20260926-085704-0afb
CHECKPOINT d602c576 (08:39Z) [open] tip d602c576: K=2048 cell relaunched after 2 setup fixes (flock-gpu-link patch, CARGO_TARGET_DIR): ver r20260926-083651-9a59, prover r20260926-083700-e919 (pod tests: cargo 39+4, pytest 60 ok; flock-link selftest 49/49 at K=2048 and K=8192); gate at 1024 VUs running
CHECKPOINT efb71424 (08:31Z) [open] code efb71424 pushed (K param, real-K pins, commit pins = B-Ligero roots, A-route-a driver + cell.sh); K=2048 cell running: ver r20260926-082825-17ce on vy-agkr-real-k-ver, prover r20260926-082839-8d9e on vy-agkr-real-k-a100 (both US-MD-1 A100, no CPU stock there)
CHECKPOINT e3a2d81d (08:06Z) [open] started (agent bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806, branch cursor/agkr-real-k-f806 from main e3a2d81d): survey done; A-GKR circuits uniform in K, flock-link K-generic (16-bit words); implementing K param + pins + A-route-a bench.cell driver

# agkr-real-k: A-GKR route (a) at K = 2048 / 8192 on the #101 captured sets

Branch `cursor/agkr-real-k-f806` (the cloud naming policy, not lane/*), [PR #69](https://github.com/danielreuter/verity/pull/69),
tip a7500a4b with origin/main merged.

## What A-GKR assumed about K
- The circuit files (unit, epilogue, chain) are uniform in K. Only the manifest's `steps` fixes K, and pins.txt pins it.
- The GPU prover, witness generator, link layout and Rust verifier are K-generic: they take steps from the manifest and K from
  commitment.txt.
- K = 1536 was hard-coded in the drivers (`tools/cell.py`, `bench_result.py`), the lowering, and `gpu/commit.py`'s frozen-set
  identity.
- flock-link, route (a)'s Flock side, is generic in the row length (`--k`) but hashes 16-bit words only. The FP8 sets therefore
  need a Flock statement change before route (a) can prove them.
- "A-interactive" has no implementation of its own. A-GKR's interactive form is route (a) with live prime coins (A-route-a).
  A-fs proves only the weaker private-operand relation, so it can't run a committed statement through bench.cell.

## Done
- Pins: `bf16-ampere-k2048(+blake3)` and `-k8192(+blake3)` at steps K / 16, with the same digests as K = 1536. Commitment pins for
  the #101 sets' sweep sizes; at 6,272 VUs the roots equal B-Ligero's art:be42c41a.
- The A-route-a bench.cell driver and `backends/gkr/cell.sh`; `tools/cell.py` input set / K / finish / register;
  `bench_result.py --input-set` (A-fs).
- Gates at both K, with a loopback verifier: the honest session is admitted except non_producer, a stale prime state is rejected by
  the record replay, a Fiat-Shamir prime prover is refused, and the wrong-K claim is refused. flock-link selftest passes 49/49 at
  both K.
- Fixes: the `scatter_terms` 32-bit offsets (an invalid proof at K = 2048 / 4,096 VUs, rejected by both verifiers); cell_gate's
  Flock replay at K; cell.sh directories keyed by K.

| cell | art | runs (verifier / prover) | plateau | t.total | VU/s | proving overhead | rounds | RTT |
|---|---|---|---|---:|---:|---:|---:|---:|
| A100 BF16 K = 2048, captured #101 (art:123dc234) | art:95fdd0ae | r20260926-083651-9a59 / r20260926-083700-e919 | 2,048 (4,096: kernel bug) | 8.87 s | 231 | 3.3e8× | 3,975 | 0.218 ms |
| A100 BF16 K = 8192, captured #101 (art:927a4c3a) | art:20197f8b | r20260926-085655-0dc4 / r20260926-085704-0afb | 512 (1,024: harness bug) | 9.78 s | 52.3 | 3.6e8× | 3,944 | 0.208 ms |

Other sizes: 185 VU/s at 1,024 VUs (K = 2048), 38.6 VU/s at 256 VUs (K = 8192). The serving commit takes 25.3 s on the CPU
reference committer. Verifier records: art:8455c116 and art:15e93b91. Producer gate over both cells: r20260926-092055-36d6
(10/10 pass except non_producer).

## Paused (coordinator 09:10Z spend guard)
Pods were drained and terminated at 09:13Z and 09:18Z. Ready to launch:
`bash $RESEARCH_NOTES/lanes/agkr-real-k/evidence/pod-scripts/launch-cells.sh` runs the K = 2048 re-sweep with the fix, the K = 8192
re-sweep, and A-fs on both sets.

Handoffs sent: `lanes/coordinator/20260926T0930Z-handoff-from-agkr-real-k.md` (red-team request; red-team-flock is final) and
`lanes/coordinator/20260926T0935Z-handoff-from-agkr-real-k.md` (merge-ready).
Handoffs received: `20260926T0910Z-handoff-from-coordinator.md` (pause): acted on, pods drained, CPU work continued.

## Blocker: the FP8 spine sets need a statement change, not just K
A-GKR binds operands only through route (a), and route (a) can't prove an E4M3 statement today:
1. **flock-link hashes 16-bit words.** `Chain::new(vus, k)` sets row bytes to 2k. Σ's preimage says `bits 16` and
   `n = leaves·k·16`, and the operands file is LE u16. E4M3 rows are K bytes: 2 chunks at K = 2048 and 8 at K = 8192, both
   admissible. So this needs a `bits` parameter (8 | 16) through the Chain, Σ, `leaf_digests`, `words` and the operands reader.
   The prime side is already generic: `gpu/link.py` and `link.rs::derive` take bits 8 or 16, and `link.rs` checks Σ's `bits` line
   against commitment.txt. It is a Flock-side statement change, so it needs a red team (the link audit covered 16-bit words).
2. **The committed y word.** The FP8 spine sets record the FP32 accumulator as u32 (relchain 9ef1d11f). C-Flock checks
   "the words the committed y opens (fp8: y << 10)". A-GKR's FP8 epilogue publishes the 22-bit packing. A committed FP8 statement
   needs the epilogue's public word to be the committed one: a public column y32 = packing · 2^10 bound in the epilogue circuit.
   That means new FP8 circuit files, new pins and a red team.
3. **tools/cell.py.** REL, MODEL and BITS are Ampere BF16 constants, and the witness uses `Generator(ops, REAL)`. It would need a
   per-relation (model, params, bits, y) table, like bench_result.py's `relation_params`.
A-fs (A-GKR alone) can run the FP8 sets at real K after one change: `bench_result.py --input-set` must also convert an FP8 set's
FP32 y to the packing (`rel.y_public`). The pins are one line per relation and K, the same files at steps K / 32. But A-fs proves
the weaker private-operand relation (a drill-down), not the committed statement B-Ligero and C-Flock prove.

## Re-sweeps after the pause lifted (09:45–10:32Z, launch-cells.sh on tip 9cbfdcf2)
The pod pair was new, again in US-MD-1: a prover A100 and the verifier on a second A100 (still no CPU stock). The first create made
a pod whose registration failed on the stale registry entry, so I adopted and re-registered it. Both pods were drained and
terminated with all attempts preserved; this round cost about $2.3.

| cell | art | runs (verifier / prover) | sweep (VUs: VU/s) | plateau | t.total | proving overhead | RTT |
|---|---|---|---|---|---:|---:|---:|
| A100 BF16 K = 2048, #101 | **art:a0ca8ef6** | r20260926-095014-2234 / r20260926-095028-c0bd | 1024: 186, 2048: 234, 4096: 283, 6272: OOM | 4,096 | 14.48 s | 2.7e8× | 0.184 ms |
| A100 BF16 K = 8192, #101 | **art:a979dfcb** | r20260926-101258-e284 / r20260926-101301-8697 | 256: 37.2, 512: 50.8, 1024: 63.5, 1920: OOM | 1,024 | 16.13 s | 3.0e8× | 0.213 ms |

- Evidence: verifier records art:f9da2094 and art:984dcba5; prover run_files art:460e9938 and art:e55da95a; prover run records
  art:76f1aeb5 and art:2f20e078.
- They supersede art:95fdd0ae and art:20197f8b. verify-flock-pure verified those at 09:52Z (r20260926-093954-dfd7).
- A-fs (drill-down: x, W private, Fiat-Shamir), run r20260926-102535-c15b, whole set per proof, 5 reps, pinned Rust 5/5:
  - art:7ae6c190: K = 2048, 6,272 VUs, 1.16 s, 5,408 VU/s.
  - art:0e1095f3: K = 8192, 1,920 VUs, 1.42 s, 1,353 VU/s.
  - Proofs are in the run record art:e92cad62.
- Handoffs sent: red-team-flock and verify-flock-pure (`20260926T1026Z-handoff-from-agkr-real-k.md`, the new ids);
  `lanes/coordinator/20260926T1035Z-handoff-from-agkr-real-k.md` (the cells registered).
- Handoffs received: `20260926T0935Z-handoff-from-coordinator.md` (pause lifted: acted on, ran the launcher) and
  `20260926T1020Z-handoff-from-coordinator.md` (paused again: nothing was left in flight, pods drained and terminated, cells sent).

## FINAL

~~~text
tip: cursor/agkr-real-k-f806 @ 9cbfdcf2 (base main@e3a2d81d; origin/main merged at a7500a4b)    merge-with: none (PR #69)
known-failures: none of mine (test_every_registered_kernel_is_self_checked_here fails only if backends/numerical tests run before packages/verity's)
pod: vy-agkr-real-k-a100 and vy-agkr-real-k-ver terminated about 10:32Z (first pair about 09:13Z / 09:18Z); about $5.0 in all
artifacts: art:a0ca8ef6 art:a979dfcb art:7ae6c190 art:0e1095f3 art:95fdd0ae art:20197f8b art:e92cad62 art:f9da2094 art:984dcba5 art:460e9938 art:e55da95a art:8455c116 art:15e93b91
~~~

A-GKR reached vLLM's reduction lengths without a redesign: the circuit files are uniform in K, the new pins are steps-only, and
flock-link takes `--k`. Route (a) cells at K = 2048 (283 VU/s) and K = 8192 (63.5 VU/s) are registered at their memory-cap
plateaus. The first two are verified by verify-flock-pure; the re-sweeps await verification. red-team-flock is reviewing. The new
cells supersede the first two once verified, and the coordinator is asked to see that `superseded_by` is written. Not reached: the
FP8 spine sets (the blocker section above) and a standalone A-interactive (none exists; route (a) with live coins is A-GKR's
interactive form).
