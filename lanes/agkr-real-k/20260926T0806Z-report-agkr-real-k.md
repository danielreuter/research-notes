---
lane: agkr-real-k
kind: report
created: 2026-09-26T08:06Z
status: open
---

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
