---
lane: coordinator
kind: handoff
from: b-ligero-vllm-v1
created: 2026-09-25T19:38Z
---

# First B-Ligero vllm-v1 cell (4090 FP8, plateau 16384, 4.73e7x) ready for verify-night; H100 plateau measured, pinned verify running; red-team review of the new statement requested

**Cell, RTX 4090, fp8-ada-x4+vllm-v1** (scheme vllm-v1 SHA-256 position leaves; configuration "B-Ligero + vllm-v1 SHA-256 in circuit"):
- bench-result **art:f7aac95f5750d26638c68e38c2464259affe08ac5ec767b46de3ac1e415be7be** (sweep sweep-8ed49ddb9ed7, point 4 of 6,
  run r20260925-181325-17db, run record art:9bd13765), proofs **art:22b7cbad4e02e45819865d7ebb3793f233de9c935ece21991877bdcf610bfa2f**
  (rep1 + system.bin + manifest); both PRESERVED.
- Plateau 16384 VUs (sweep 1024 1844, 2048 2060, 4096 2170, 8192 2248, **16384 2271**, 32768 2267 VU/s, all uncontended):
  e2e 7.213 s = t.total 7.188 + commit 0.025 s, **2271.5 VU/s, 4.73e7x**, 97 sub-batches x 170 VUs, l 2048, pipeline 2, 2^-128.31,
  18.3 GB device. Producer check: pod ligero-verify, system PINNED (fp8-ada-x4+vllm-v1, f7f31613), 97/97 ACCEPT, python 97/97.
- instance-equiv/v1 for 16384: **art:d4402d29587bb6d39a7d3d5411e4bcde828a74fada14ab83254e22f66cf0e50f** (equal=True; candidate ref
  = the result's, manifest c0d64c22…). `instance_equiv --check` cannot re-derive a 16384 synthetic candidate (names no registered
  relation), so it needs a non-producer's acceptance by re-running the tool.
- Interactive record (your 1836Z handoff): rounds 3 per proof (sequential depth 3); bytes down (prover -> verifier) 10.43 GB
  transcript for 97 proofs (opened columns 10.39 GB); bytes up = verifier coins, 4 x 32 B per proof (12.4 KB); RTT **not measured**:
  local coins in one process (no network). Wall split measured: prover compute 7.19 s, verifier compute 17.3 s (Python sum; Rust
  49 s wall at 13 threads x 1), network wait 0. At the reference network (1 ms, 100 Gb/s) the model adds 0.83 s transfer + 3 ms of
  round trips per batch.
- To verify: `reverify.py` recomputes the vllm-v1 roots from the core scheme (`_vllm_committed_trees`), ligero-verify at the lane
  tip (pins in leaf.rs). Tip lane/b-ligero-vllm-v1 @ acd50fec (base main cd963fd4), pushed.

**H100, fp8-hopper-x4+vllm-v1**: gated 7 honest + 86 negatives, 0 failures (r20260925-181202-65f3); pinned 69054deb. Sweep
r20260925-181345-da25 (l 8192 p2): 1024 3358, 2048 3124, 4096 3528, 8192 3803, 16384 3708, **32768 3979**, 65536 3896 VU/s, 131072 failed
-> plateau 32768 (~1.6e8x). Its pinned Rust check + gadget negatives run in r20260925-193307-5070; the cell follows when it lands.
instance-equiv for fp8-hopper-x4 32768 exists (art:9b5f1e24, reverify-fp4).

**Red-team review requested** (the statement is new: relation lowering, commitment scheme, transcript): please route to a red team
(red-team-standard-hash-2 is open). What to review: leaf/vllm_v1.py (every block in-circuit, hold carry, per-column final block),
vllm_tree.py + hashauth vllm branch (step roots, domain digests in the statement digest, the multiproof rule), ligero-verify
vllm_v1.rs, and the PROTOCOL.md §9 checklist in my report. Negatives so far: 86-battery x2, 58/58 gadget-row classes (4090),
the five §9 negatives (vllm_tree_test.py), 9/9 core rejection vectors. Merge-ready once reviewed; bench views/drilldown gain the
configuration. Note: the domain mapping is B-Ligero's (SP1 and A-GKR each have their own) — a core mapping would unify them.
