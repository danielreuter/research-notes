---
lane: coordinator
kind: handoff
from: agkr-real-k (bc-90879fa8-ea65-5d51-8e4d-ddeb832bf806)
created: 2026-09-26T09:30Z
---

# RED-TEAM REQUEST (please route; red-team-flock, route (a)'s auditor, is final): A-GKR route (a) at K = 2048 / 8192, two cells to label

**Cells to label** (proof_class NON_ZK_PROOF claimed, composed bound 2^-130.19; A100-SXM4-80GB prover, verifier on a second pod in
US-MD-1, 0.21 ms RTT; captured #101 sets):
- art:95fdd0ae: `bf16-ampere-k2048+blake3` at 2,048 VUs of art:123dc234, 231 VU/s, 3.3e8× proving.
- art:20197f8b: `bf16-ampere-k8192+blake3` at 512 VUs of art:927a4c3a, 52.3 VU/s, 3.6e8× proving.

I operated the verifier, so these still need a non-producer verification (G3). My producer pre-check is run
r20260926-092055-36d6: all 10 timed sessions pass every tools/cell_gate.py check except non_producer.

**What changed in the statement** (branch cursor/agkr-real-k-f806, [PR #69](https://github.com/danielreuter/verity/pull/69)):
1. **pins.txt:** `bf16-ampere-k2048+blake3` and `-k8192+blake3` are the K = 1536 linked circuit files (c0a6809d…, 187b9395…,
   f09b3087…) at steps 128 and 512. The bare `bf16-ampere-k2048` / `-k8192` are the same for A-fs (afefd92f…). The relation name
   carries K. Please check that nothing besides steps fixes K: the link layout (`link.rs::derive`: steps × 16 = K from
   commitment.txt, bits 16) and the per-VU chain linkage over steps units. Gate evidence: the proof claimed as `bf16-ampere+blake3`
   is refused ("circuit files are the pinned bf16-ampere-k2048+blake3 circuits…").
2. **commitments.rs:** 8 pins. They are the frame-v3 blake3-keyed/row/v2 roots of VUs [0, n) of the two #101 sets, with
   n ∈ {1024, 2048, 4096, 6272} and {256, 512, 1024, 1920}, bound as B-Ligero binds a set (dataset `vllm-vu-set/v1:<set>`, tier
   `<set>`, the set manifest's SHA-256, [0, n), K). At 6,272 VUs they equal B-Ligero's art:be42c41a roots byte for byte. The
   verifier's own leaf digests (computed from the set on its pod) equal the prover's at both K.
3. **The Flock side is unchanged code:** flock-link at `--k K` uses rows of 2K bytes, i.e. K / 512 BLAKE3 chunks. At the cell
   sizes that is 2^19 rows (m_link 28) at K = 2048 / 2,048 VUs and 2^18 at K = 8192 / 512. The composed bound reuses your audited
   Flock terms (flock-128-r2 2^-195.5 at dense m = 33; link reduction 2^-243.9). Please confirm they hold at these statement
   sizes. flock-link selftest passes 49/49 at K = 2048 and 8192 (8 VUs), on the pod and locally.
4. **tools/cell_gate.py:** the Flock replay (G2) now builds the statement at sigma.txt's K. It always built K = 1536's, so it
   refused every real-K record.
5. **Prover only:** `gpu/kernels.py scatter_terms` now uses 64-bit offsets. At K = 2048 and 4,096 VUs (524k units × 776 columns
   × 6 > 2^31) the functional wrapped, and both verifiers rejected the proof (linear functional value mismatch). Soundness held.
   This is why art:95fdd0ae stopped at 2,048.

**Gate at both K** (loopback verifier; runs r20260926-083700-e919 and r20260926-085704-0afb, out/gate): the honest session is
admitted except non_producer. A stale prime state is rejected by the record replay ("R2-prime: round 5: the proof's messages differ
from those committed before the coin"), and a Fiat-Shamir prime prover is refused at Hello.

Files: `backends/gkr/verifier/{pins.txt,src/commitments.rs}`, `backends/gkr/tools/{cell.py,cell_gate.py}`, `backends/gkr/gpu/kernels.py`.
Session records: art:8455c116 (K = 2048) and art:15e93b91 (K = 8192). Timed proofs: run_files art:eb4977b8 and art:c2b10a12.
Statements: the prover run records art:b7b5298a and art:05aa00b9 (out/statement-<n>).
