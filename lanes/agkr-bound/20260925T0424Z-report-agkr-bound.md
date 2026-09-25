---
lane: agkr-bound
kind: report
created: 2026-09-25T04:24Z
status: open
---

CHECKPOINT 89433d06 (12:08Z) [open] 12:08Z: FP8 link OK (MALLOC_MMAP_MAX_=0 TRIM=1e12): prove 0.607->0.778 s, PyV 0.489->0.648, Rust 1.71->2.35; 11/11 negs rejected Py+Rust; art:60cabb96. PROTOCOL 17.4 89433d06. Custody-r2 adopted (1146Z). Reindex running on pod (laptop's killed). Next: drain + FINAL.
CHECKPOINT 78b1a62e (11:51Z) [open] 11:50Z: Flock AVX-512/GPU nums in drill-down (A100 BF16 route a ~2.29 s w/ Flock-CUDA). FP8 sigma link on A100 (MALLOC_MMAP_MAX_=0 TRIM=1e12): prove 0.6025->0.7816 s, py verify 0.489->0.648; Rust rerun (unpinned flag) r20260925-114925-2f5c. Laptop reindex SIGKILLed again; moving it to pod.
CHECKPOINT 011a9f1 (11:39Z) [open] 11:40Z: link built+verified (78b1a62e): prove 1.20->1.53 s, PyV 1.25->1.56, Rust 3.41->4.68 s (+0.44 derive); 11/11 negs rejected Py+Rust incl vu_remap; art:bd3d8b2c+fc687ece; handoff 1140Z. MALLOC env set. Laptop reindex killed w/o output (retry later). Drill-down L.
CHECKPOINT ac2a497 (11:20Z) [open] 11:21Z: link kernels optimized (fused y+sigma, TC plane sums, nibble eq): prove +0.385 s (1.20->1.59, 4a0823bd), final rerun at 78b1a62e running; Rust verify 3.42->4.63 s +0.44 derive; 10/10 negs rejected Py+Rust; PROTOCOL 17 bfd9d7e3. MALLOC env set. Drill-down L.
CHECKPOINT 824a9924 (10:56Z) [open] 10:57Z: link built both sides (e366e14f+6d55db3f). 31_link_rust: prove 1.20->1.92 s, Py verify 1.25->1.80, Rust 3.38->5.23 s (+derive 1.77 at load, optimizing now); 10/10 negatives rejected Py+Rust. MALLOC_MMAP_MAX_=0/TRIM set explicitly (1040Z noted, env.sh not sourced). Drill-down L.
CHECKPOINT 0f71b5b4 (10:39Z) [open] 10:40Z: sigma-form link (S1) in-repo at 136a714c (gpu/link.py, C1 GF(2^256) one point, verifier-derived bijective Λ, booleanity check). Launching 30_link_build (timing+prime-side negatives; MALLOC_MMAP_MAX_=0/TRIM set). Rust verifier side next. Drill-down (L) only.
CHECKPOINT a7f3f26 (10:24Z) [open] Dense check folded into the real BF16 in-unit A100 proof: prove 1.20->1.41 s, Py verify 1.25->1.47; gap_alt_operand accept->REJECT. Link map is a bijection (27). art:64220e14, art:400126e2. MALLOC env set. Scaffold only.
CHECKPOINT ee2a319f (10:05Z) [open] Dense check 0.066 s/point on A100 (int8 tensor-core coefs); route (a) prime side 0.776->1.30 s (1 pt) / 1.36 s (2 pts). gap_alt_operand rejected by link identity (62/128, 69/128 planes). art:64220e14. Handoff 1005Z. Nothing big on laptop.
CHECKPOINT 10996616 (09:55Z) [open] Dense GF(2^128) check at N=201,326,592 (BF16 batch) on A100: fused Triton 0.367 s; int8 tensor-core coefs 0.066 s (eq 0.023, coef+ip 0.044), cross-checked vs torch. u_t 0.032 s. Now: gap_alt_operand vs link checks (r20260925-095534-ad8c). Scaffold only.
CHECKPOINT 88b82757 (09:34Z) [open] Per 0922Z: link bits in-unit (86f86084) BF16 A100 0.776->1.199s (+55%), Rust verify accepts; negatives bit_flip/non_boolean/alt_honest_bits rejected, alt_alt_bits accepted (link residual). Dense GF(2^128) check 0.875s A100 / 0.85s CPU; u_t 0.03s. art:35bce6f5.
CHECKPOINT 04286bb (09:10Z) [open] Bit-link prime side merged into real BF16 A100 proof: 0.819->1.401s (+71%), proof 21->61MB (py verify accepts). Red team reproduced my 4 pinned roots. Waiting on coordinator re handoff 0858Z (route, AVX-512 Flock, tag, vllm-v1 mapping, fp4).
CHECKPOINT 74a016e (09:03Z) [open] Spike registered art:c35a50cd, scaffold+negatives art:f2f07e3c (NEGATIVES OK 4 cells incl vllm-v1). A-GKR BF16 CPU 361.5s; in-field SHA ~28x (not building); bit-link prime side +38% CPU/+64% GPU. Handoff 0858Z: route + 4 decisions.
CHECKPOINT 58b113bc (08:47Z) [open] Link stub (512 op bits/unit, k=1) at 393k units: CPU 138s, A100 GPU 0.55s warm (vs BF16 cell 0.86s, +214M committed). k=2/4 slower. Flock portable SHA-256 393k ~7.5s CPU. In-field flat SHA ~1e4 s CPU, GPU infeasible. Running A-GKR BF16 CPU ref.
CHECKPOINT e10e1d6 (08:29Z) [open] Spike: in-field flat SHA-256 (Rust CPU, 13 thr) B=64 3.26s, B=4096 106.7s (arith-bound, ~1e4 s/393k-compression batch). Flock portable (Zen2): SHA-256 52k/s, BLAKE3 120k/s. Link stub k=1 at 393k units 138s. Next: same-pod A-GKR BF16 CPU ref.
CHECKPOINT 02927b7b (08:07Z) [open] vllm-v1 dev run done: bf16/fp8 +vllm-v1 roots match pins, rust tree rebuild OK, scaffold verdict as designed. Survey adopted: launching CPU hash spike (flat SHA-256 in BabyBear via Rust CPU prover B=64/4096 + Flock benches). Link protocol not built.
CHECKPOINT de225a9b (07:56Z) [open] 3 frame-v3 commit cells accept natively, roots match (bf16-ampere+sha256 0.883s, fp8-hopper+blake3 0.459s, fp4-nvf4+sha256 0.402s). Negatives: all expected but 1 stale expectation (fixed). vllm-v1 variant de225a9b: 27 cargo tests vs vectors ok; pins added; bench running.
CHECKPOINT 14b0cf9f (07:38Z) [open] commit scaffold d48f5bc2: frame-v3 native check + pins bf16-ampere+sha256/fp8-hopper+blake3. bf16-ampere --commit sha256: t.total 0.883s, native tree check accepts, roots match; R+sha256 claim refused (no circuit pin, by design). fp8/fp4 cells running; negatives next.
CHECKPOINT 14b0cf9f (07:29Z) [open] pod vy-agkr-bound2 (A100 SXM, guard 90) up 07:18Z. 44e18670: gpu/commit.py + bench_result --commit + commitment.txt absorbed in both transcripts. Running r20260925-072901-b125: cargo/pytest/root pins/3 commit cells. Survey not in.
CHECKPOINT 4b57e526 (07:09Z) [open] survey-gated non-hash parts: 4b57e526 adds verifier commitments.rs (frame-v3 tree check vs core vectors, commitment.txt, R+sha256/R+blake3 claims, root pins empty). Next: gpu/commit.py, prover scaffold, pod tests. No pod up; no survey yet.
CHECKPOINT a7e88ab1 (06:49Z) [open] Unblocked (coordinator 0640Z/0650Z): retarget to frame-v3 SHA-256/BLAKE3 row digests; FINAL 15:00Z, cap $100. Now: merge main >= 00ffe398 (core frame_v3/vllm_v1), then non-hash parts (native tree check, digest publication, relation names/pins, commitment bucket, negatives scaffold); gadget waits for the survey.
CHECKPOINT a7e88ab1 (06:38Z) [blocked] Still blocked on coordinator decision (estimate v2 0557Z). No pod; ~$2.2 spent; lane tip a7e88ab1 pushed.
CHECKPOINT a7e88ab1 (06:17Z) [blocked] Waiting on coordinator decision on revised estimate v2 (0557Z: IRS/SHA-256 column commitment as a new core scheme; options a/b/c). No pod, ~$2.2 spent.
CHECKPOINT a7e88ab1 (05:57Z) [blocked] Acted on 0546Z (non-algebraic hash): revised estimate v2 handoff 0557Z recommends a verifier-checked IRS/SHA-256 column commitment bound via my existing functional hook (+1-5% prover); needs core-scheme + scope decision. No pod.
CHECKPOINT a7e88ab1 (05:44Z) [blocked] Still waiting on coordinator (revised estimate 0540Z + correction 0550Z: in-circuit Poseidon2 costs ~4-8x A-GKR t.total because layers span all wires; recommend b or c). No pod.
CHECKPOINT a7e88ab1 (05:43Z) [blocked] Waiting on coordinator re 'agkr-bound revised estimate' (committed x/W/y variant: options a extend / b dev-only / c park). Integration v2 2994bd25 (art:3f562102) and public-input binding (art:559147e1) delivered. No pod running.
CHECKPOINT 4c0c3418 (05:22Z) [blocked] Integration v2 2994bd25 ready (art:3f562102, handoff 0535Z). Public-input binding done (art:559147e1). Committed x/W/y version does not fit budget/FINAL: blocked on handoff 'agkr-bound revised estimate' (0540Z). Pod terminated 05:37Z, ~$2.2 spent.
CHECKPOINT ff486b0b (05:05Z) [open] Acting on coordinator handoff (PR #13 pins): merged origin/main c1891d48 -> ff486b0b. Bound variant = relation R+bound (circuits pinned under R, instances pinned under R+bound); fp8/nvf4 pin lines added; merge_tables torch-free. Pod r20260925-050511-c8ce: cargo test + pytest + merged-LK lines.
CHECKPOINT 082866ff (04:57Z) [open] integration a2edab4d: cargo+pytest ok, 4 cells byte-identical (art:c347036b), handoff sent; operands-bound impl 6b39234e/082866ff: bf16-ampere bound 0.85s A100 accept, negatives ok bar mutate fix; next: dev rerun, then recorded rows
CHECKPOINT a2edab4d (04:24Z) [open] merged agkr-fp8+agkr-nvf4 as a2edab4d (pushed); A100 pod vy-agkr-bound up, bootstrap r20260925-042151-5f88 running; next: integration tests + proof byte-identity, then operand-binding impl

## Progress (05:40Z)

**Step 1, integration.**

- v1 is a2edab4d (art:c347036b, handoff 0500Z).
- v2 is **2994bd25** = a2edab4d + origin/main c1891d48 + pins (fp8-ada and fp8-hopper, merged-LK and `--no-merge`; fp4-nvf4) + a
  torch-free `merge_tables`. Evidence art:3f562102, run r20260925-051328-c48b, handoff 0535Z:
  - cargo test 11+4; pytest all green;
  - 4 cells with `--relation` and `circuit_pinned` true, each proof sha256 byte-identical.

**Step 2, public-input binding.** Complete as an intermediate, art:559147e1, run r20260925-050836-bdba, lane b5299000.

- The bound relation is named `R+bound`: circuits pinned under R, instance files under R+bound (`instances.rs`).
- Negatives are OK on bf16-ampere, fp8-hopper and fp4-nvf4:
  - wrong operand with the honest y → rejected by Rust, Python and clear mode;
  - the unbound gap is shown (accepted under plain R);
  - the naming rules are enforced both ways;
  - an altered x.bin is rejected by the pin;
  - mutate 17/17 rejected.
- A100 t.total, 1 rep (not Table 2 cells): bf16-ampere 0.843, fp8-hopper 0.399, fp4-nvf4 0.327. The unbound figures are
  0.839, 0.374 and 0.288.

**Scope correction (coordinator 0507Z).** The target is x, W and y committed with `verity.commitments` leaf/v2h
(Poseidon2-w24 under SHA-256 Merkle) and bound in-proof.

- Estimate: it does not fit the $15 cap and the 12:00Z FINAL. The A-GKR unit circuits are product-depth 1, and Poseidon2 adds
  +426 to +1280 committed columns per unit.
- Handoff "agkr-bound revised estimate" (0540Z) gives options a, b and c. The lane is **blocked** on it.
- Pod vy-agkr-bound was drained and terminated at 05:37Z. Spend so far is about $2.2 (A100, about 04:15–05:37Z).

## Progress (08:10Z)

**Retarget (coordinator 0640Z/0650Z): frame-v3, then vllm-v1 row digests, checked natively.** Lane tip 02927b7b.

- Verifier `commitments.rs` rebuilds frame-v3 trees (sha256/row/v1, blake3-keyed/row/v2) and, since de225a9b, vllm-v1
  trees (`vllm_v1.rs`, pos-leaf/v0, StepDomain chunk null) from x.bin/W/y, and compares them with `commitment.txt`.
  sha256(commitment.txt) is absorbed in both transcripts; the digests are published as 32 epilogue limbs per VU.
- Relations are `R+sha256`, `R+blake3`, `R+vllm-v1`. Root pins: bf16-ampere+sha256, fp8-hopper+blake3 (d48f5bc2),
  bf16-ampere+vllm-v1, fp8-hopper+vllm-v1 (83582436). No circuit is pinned under these relations yet, so every cell's
  status is `failed` by design ("scaffold": the digest columns are not constrained in-proof).
- A100 cells, 1 rep, scaffold check accepted and roots match:
  - bf16-ampere+sha256: t.total 0.883 s; serving commit 0.36 s; Rust verify 1.95 s.
  - fp8-hopper+blake3: 0.459 s. fp4-nvf4+sha256: 0.402 s (no fp4 pin).
  - bf16-ampere+vllm-v1: 0.862 s, serving commit 0.33 s, verify 1.96 s (r20260925-075248-f4dc).
  - fp8-hopper+vllm-v1: 0.431 s, serving commit 0.09 s, verify 0.97 s.
- Python and Rust agree on vllm-v1 roots and domain digests. The pins were computed in Python and the Rust verifier
  rebuilt the same roots.
- Negatives r20260925-074931-1329, on bf16-ampere+sha256 and fp8-hopper+blake3: wrong digest, swapped W, y word,
  limb range, spec manifest, spec leaf, no commitment and relabelled claims are all rejected.
  `gap_alt_operand` is ACCEPTED: this is the expected scaffold gap. One expectation (wrong_digest_up) was stale and is
  fixed in 10; the rerun with pins compiled in, including vllm-v1, is still pending.
- The vllm-v1 operand-domain mapping (program/ctx/geo/layout under "verity/gkr-commit/vllm-v1") is PROVISIONAL and
  owned by integration.

**Survey (0752Z) adopted.** I have not built the link protocol and will not build it until the red-team.

- Spike r20260925-080740-fb11 (running) covers two things:
  - in-field Longfellow flat SHA-256 in BabyBear (`tools/sha256_flat.py`: 6,657 committed columns, 30,272 products,
    7,024 asserts, depth 5 per compression), proved by the Rust CPU prover at B = 64 and 4,096;
  - Flock b684b12 `hash_throughput` on the same CPU.
- Caveat: the pod CPU is an EPYC 7742 (Zen 2) with no AVX-512 or VPCLMULQDQ, so Flock falls back to its portable path
  and its numbers are pessimistic.
- The GPU prover can't take the flat-SHA circuit: `gpu/circuit.layers()` spans every wire per layer, with dense wiring.
  The Rust CPU prover is sparse.

## Hash spike (survey §4.3), 08:55Z

**Setup.** One RunPod A100-SXM4-80GB pod, vy-agkr-bound2. Its CPU is an EPYC 7742 (Zen 2) with a 13-thread cgroup cap
and no AVX-512, so Flock runs its portable path. Runs: r20260925-080740-fb11, r20260925-081528-c188 and
r20260925-084251-099a. Lane tip caacca10 (tools `sha256_flat.py`, `link_stub.py`); pod scripts 12–16.

A 4,096-VU BF16 batch is 393,216 units and 393,216 SHA-256 compressions (96 per VU: the x row and the W column, 48
blocks each).

| per 4,096-VU BF16 batch | committed elements | CPU prover s | A100 prover s | rounds |
|---|---|---|---|---|
| A-GKR BF16 alone | 175M CPU v1 (444/unit); 109M GPU cell | 361.5 | 0.86 | 355 / 328 |
| (b) in-field flat SHA-256 | 2.62e9 (6,657 per compression) | ≈10,240 (extrap.) | infeasible | 266 |
| (a) Flock SHA-256 | binary field | ≈7.5 | CPU only | – |
| (a) Flock BLAKE3 | binary field | ≈3.3 | CPU only | – |
| (a) link, A-GKR side (stub, k = 1) | 214M (545/unit) | 138.3 | 0.55 | 84 |

**(b) In-field flat SHA-256.** Longfellow flat layout ported to BabyBear.
- Cost: B = 64 takes 3.26 s and B = 4,096 takes 106.7 s (arith 101.6 s, commit 4.4 s, 9.1 GB, verify 3.2 s, proof 5.5 MB).
- The 10,240 s figure is linear from B = 4,096. The run is arithmetic-bound: 36,929 wires per compression against the
  BF16 unit's 290.
- Soundness checks: the honest witness is accepted, and the negative (one committed bit of new a flipped) is rejected by
  check-witness.
- On GPU it is infeasible: `gpu/circuit.layers()` gives each layer dense wiring over all 2^16 wires.
- Against A-GKR alone that is about 28× on CPU. The survey projected about 3–6× bare, and that projection does not hold
  for A-GKR.

**(a) Flock b684b12 `hash_throughput`** (one compression per input, best of 3):
- 13 threads: SHA-256 is 0.038 / 0.107 / 1.17 / 5.00 s at 2^8 / 2^12 / 2^16 / 2^18. BLAKE3 is 0.024 / 0.061 / 0.54 /
  2.18 s at the same sizes.
- 1 thread: SHA-256 takes 56.9 s at 2^18 and BLAKE3 26.3 s.
- The bench rejects batches below 2^8, so B = 64 is reported as 2^8.
- At B = 4,096 Flock is about 1,000× cheaper than route (b).

**(a) Link, A-GKR side.** A stub of the survey's §3.8 prime side: 512 operand bits per unit, booleanity, and a
recomposition into the 32 words. The cross-field check itself is not built (red-team gate).
- CPU: 138.3 s at 393k units (+38% of A-GKR; verify 23.7 s; 32.6 GB).
- A100: 0.55 s warm (+64% of the cell; proof 40.7 MB; 33 GB).
- Packing makes it worse on CPU: k = 2 takes 173 s and k = 4 takes 563 s, because the range-check products replace
  commitment work. The survey's link also needs single bits.
- Not modelled: the dense linear check (N = 2.0e8 GF(2^128) eq terms and about 16 byte-table lookups per bit, on both
  prover and verifier) and the u_t commitment (about 3.7k elements).
- If the bits were merged into the unit circuit rather than proved as their own segment, the GPU cost would be higher:
  layers span all wires, so the unit goes from 290 to about 1,314 wires (2^9 to 2^11).

**Adoption.** I recommend route (a), Flock plus the bit link, as the only viable one for A-GKR.
- On CPU its total is about 150 s against 361.5 s.
- On GPU, Flock on the CPU (3.3–7.5 s, portable path) dominates the 0.86 s A-GKR cell. Flock on AVX-512 hardware or a
  GPU binary-field prover would be needed for a GPU row.
- I am NOT building the in-field fallback (b) into A-GKR. It is about 28× on CPU and can't run on the GPU prover.
- I am NOT building the link until the red team has reviewed it.

**Registered.**
- Scaffold: art:f2f07e3c (frame-v3 + vllm-v1 cells; negatives with pins, NEGATIVES OK on 4 cells, r20260925-085244-5d8e).
- Hash spike: art:c35a50cd.
- Both are gate-log/v1 and preserved. Runs are preserved through `04_store.sh push`, and `data reindex --remote` succeeded.
- Handoff 0858Z asks five questions: the route, Flock on AVX-512, the binding tag, the vllm-v1 domain mapping, and fp4 pins.

**Link, merged (09:10Z, r20260925-090709-6528, pod scripts 18_link_merged.sh and 18_wrap.py).** The stub runs as a third
segment of the real BF16 A100 proof: 4,096 VUs, 1 warm-up and 3 reps, Python verifier.
- The base cell's median t.total is 0.819 s, and its proof sha is f2c05851, byte-identical to the pinned cell.
- With the link segment the median is 1.401 s: **+0.58 s, +71%**. Of that, arith is +0.30 s, open +0.15 s and commit
  +0.04 s. The proof grows from 21.2 MB to 61.4 MB.
- The Python verifier accepts. The Rust verifier rejects with "message count exceeds the statement's bound", as expected,
  because it doesn't know the segment.

## Coordinator 0922Z and the route (a) prime-side costs (09:35Z)

**Rulings (0922Z).**
- Route (a) is confirmed and (b) is dropped. The link is benchmarks and scaffold only until the red team clears
  `flock-link-protocol.md`, and no cell counts.
- No AVX-512 pod. I had created vy-agkr-bound-cpu (Threadripper 7960X) at 09:12Z, before this reply. It was drained at
  09:23Z unused, for about $0.15; take Flock's AVX-512 number from flock-bench-80gb's FINAL instead.
- Keep B-Ligero's v2h tag. The vllm-v1 mapping stays PROVISIONAL (integration owns it). fp4 stays unpinned, a gap in the
  drill-down.

**Survey miss.** The in-field route was projected at 3–6× and measured at about 28× on CPU. The link's prime side adds
+55–71% t.total before the dense check and before Flock.

**Link bits in the unit** (`tools/link_stub.extend_unit`, 86f86084; run r20260925-092253-7da8). The unit's 32 operand
columns (the ones the GKR layers consume) get 16 bits each, with booleanity and recomposition. The unit grows from 264
columns / 290 wires to 776 / 1,314, under the R+sha256 scaffold statement, on A100 with 4,096 VUs.
- Median prove goes from 0.776 to 1.199 s (**+55%**; +71% as a separate segment). Committed elements go from 109M to
  311M and the proof from 21 to 59 MB.
- The Rust verifier accepts in 3.38 s (`--allow-any-circuit --require-commitment`).
- `bit_flip`, `non_boolean` and `alt_honest_bits` (an altered operand, a valid unit, the frozen operand's bits) are
  rejected by Rust and Python.
- `alt_alt_bits` (an altered operand with its own bits) is ACCEPTED. That is the residual only the cross-field link
  closes; it is the in-circuit half of the red team's "the published limbs are the digests of the rows the GKR layers
  consume".

**Dense check and u_t** (r20260925-092724-d4f8). N = 201,326,592 bits, m = 28, with random public-coin values:
- A100, torch, unfused: 0.875 s (eq(r, i) 0.35, BabyBear^6 byte-table coefficients 0.51, inner product 0.02).
- CPU EPYC 7742, C with PCLMUL: about 0.85 s at 13 threads and 9.2 s at 1 thread. The verifier pays this too.
- u_t (128 × 29 bits) as its own second-round Ligero proof: 0.032 s, 471 KB.

**Route (a) per BF16 batch on A100, before Flock.** About 0.78 s rises to about 2.1 s: in-unit bits +0.42 s, dense check
+0.88 s (an upper bound), u_t +0.03 s. Flock adds 3.3–7.5 s on Zen 2 CPU; the AVX-512 number comes from
flock-bench-80gb. On the verifier side: Rust 2.0 s rises to 3.4 s, plus about 0.85 s for the dense check.

## Dense-check kernels and gap_alt_operand (10:05Z)

Benchmarks and scaffold only: the link protocol is not built and no cell counts. Registered as art:64220e14 (gate-log/v1,
refs art:35bce6f5 and art:f2f07e3c). All runs are preserved and `data reindex --remote` succeeded.

**Dense GF(2^128) check, one challenge point, N = 201,326,592 bits (m = 28), A100.** Both kernels pass the eq spot checks
and match the torch reference's BabyBear^6 value exactly.

| kernel (pod script) | run | eq(r, i) s | coefficients + inner product s | total s |
| --- | --- | --- | --- | --- |
| torch, unfused (21) | r20260925-092724-d4f8 | 0.35 | 0.53 | 0.875 |
| Triton, fused byte tables (23) | r20260925-094400-b761 | 0.023 | 0.345 | 0.367 |
| Triton, int8 tensor-core coefficients, block 256 (24) | r20260925-094840-969f | 0.023 | 0.044 | **0.066** |

- The tensor-core kernel computes c_i = Σ_t ρ_t bit_t(eq_i) as bits[B, 128] × ρ split into 7-bit limbs (int8 → int32),
  then folds in b_i per block. Block 128 gives 0.080 s; block 512 spills registers and takes 1.15 s.
- The byte-table kernel is gather-bound (96 table loads per bit). eq is memory-bound: it writes 4.3 GB for 2^28 entries.
- The kernel produces the claimed inner product. In A-GKR the dense check instead enters the one materialised Ligero
  functional as `a[pos(i)] += c_i`, which is measured on the real proof in the next section (10:25Z).
- flock-bench's handoff (0946Z) estimated this prover step at "a few ms on GPU, derived, not run". Measured on A100 it is
  66 ms per point, 23 ms of it the eq expansion, so their GPU figure is about 10× optimistic. Their CPU figure, 0.51 s per
  point on Zen4 16T, is consistent with my 0.85 s on Zen 2 13T.

**Route (a), per BF16 batch on A100 (prime side), revised.** The base is 0.776 s. In-unit bits add +0.42 s, the dense check
+0.066 s per point, and u_t +0.03 s. That gives about **1.30 s with 1 point (+67%)** and **1.36 s with the 2 points 2^-128 needs
(+76%)**, replacing the 2.1 s upper bound above. Flock is extra: BLAKE3 is 0.29 s on a 5090 (Flock-CUDA) and 2.33 s on
Zen4 16 vCPU; SHA-256 is 5.47 s on Zen4 CPU and has no GPU number. flock-bench's handoff sets "A-GKR's 54 s CPU prover"
against the link, without a source; it may come from a machine with more cores. At this pod's 13-thread cap my BabyBear
CPU measurement is 361.5 s, where the link is about 1%, not 4–6%.

**gap_alt_operand vs the link's prime-side checks** (r20260925-095534-ad8c, pod script 25_gap_dense). The witness is the
same altered operand as `alt_alt_bits`: x ^= 1 at a word with w = ±0, public words honest. The in-unit proof accepts that
witness. The script checks what the link's two sides see instead.

| cell | altered | link bits that differ | altered x-row leaf digest = committed? | honest: planes with S_t ≠ 2u_t + z_t, combination | altered: planes mismatched, combination |
| --- | --- | --- | --- | --- | --- |
| bf16-ampere+sha256 | VU 21, word 9, 0x0 → 0x1 | 1 of 201,326,592 | no (64e6477f.. vs 28ba8a70..) | 0/128, 0 | 62/128, nonzero |
| fp8-hopper+blake3 | VU 0, word 47, 0x12 → 0x13 | 1 of 100,663,296 | no (56742485.. vs 974ea8c5..) | 0/128, 0 | 69/128, nonzero |

- The binary side proves the committed digest, so it can only open the honest preimage, and its z is the honest bits'
  value. The altered bits then break parity on about half the planes, and no range-valid u_t (< 2^29) fixes an odd
  residual. The BabyBear^6 ρ-combination is nonzero, so the check rejects.
- Assumption, not built: z is computed over the honest bits in prime-side order. The operand-to-message bit layout (the
  gadget's prefix, padding and offsets, which the red team asked about) is taken as given. An altered word appears in
  exactly one unit here, so duplicated operands were not exercised.

**Incoming (0945Z–0946Z).**
- vllm-rf-c1 recommends relabelling the four vllm-v1 operand-domain digests as "backend-owned" rather than "provisional,
  integration owns". I have not changed anything: ruling 4 (0922Z) stands until the coordinator decides.
- The laptop disk rule is noted. This lane has pulled nothing large to the laptop; all evidence is on the pod and in R2.

## Link layout, and the dense check inside the real proof (10:25Z)

Benchmarks and scaffold only: pod scripts 27 and 28, with no repo change, the link protocol not built and no cell
counts. Every measured run from here sets MALLOC_MMAP_MAX_=0 and MALLOC_TRIM_THRESHOLD_=1000000000000 (coordinator,
1003Z).

**Operand-to-message layout** (r20260925-100729-6578, pod script 27_layout; this is the red team's "digest-to-operand
binding" question).
- The generator orders units VU-major: unit u = v·U + s, with U = K/k = 96 for BF16 and 48 for fp8. Unit s consumes
  x[v, k·s … k·s + k − 1] and the same words of W column v.
- Every operand word appears in exactly one unit, so the link map from unit bits to leaf value bits is a **bijection**.
  That is 201,326,592 bits on both sides for BF16 and 100,663,296 for fp8. There is no duplication for the link to
  dedupe.
- `sha256/row/v1`: the value starts after one constant 64-byte prefix block, so it is block-aligned at bit offset 512. A
  leaf is 50 compressions, or 49 given the prefix midstate. Row words are little-endian u16, while the SHA-256 schedule
  reads big-endian 32-bit words: a fixed bit permutation.
- `blake3-keyed/row/v2` has no prefix.
- U = 96 and 48 are not powers of two, so bit index → (v, s, word, bit) is not a concatenation of bit fields. A verifier
  that wants eq(r, π(i)) succinctly would need padded unit slots. The O(N) verifier used here does not care.

**The dense check as one more term of A-GKR's batched Ligero functional** (r20260925-101520-bc72, pod script
28_link_dense, bf16-ampere+sha256 in-unit statement, A100, 4,096 VUs, 1 warm-up + 3 reps).
- A-GKR opens every residual claim as one materialised functional ⟨a, X⟩ = b (`gpu/prover.py` `Acc`,
  `ligero.prove_open`). The script wraps `prove_open` and `verify_open`:
  - The prover draws r ∈ GF(2^128)^28 from the transcript, computes eq(r, i) and the plane sums S_t, and absorbs
    u_t = ⌊S_t/2⌋. This stands in for u_t's own commitment, measured separately at 0.032 s and 471 KB.
  - It then draws ρ_t ∈ BabyBear^6 and adds c_i = Σ_t ρ_t bit_t(eq_i) into a at the link-bit columns.
  - The verifier does the same O(N) work into its own a, and adds b += Σ_t ρ_t (2u_t + z_t). z is a stand-in computed
    from the honest message bits; the Flock side is not built.

| | in-unit bits only | + dense check | link term (median) |
| --- | --- | --- | --- |
| median prove | 1.201 s | **1.413 s** | 0.211 s |
| Python verify (GPU) | 1.246 s | 1.469 s | 0.155 s (binary-side z stand-in excluded) |
| honest | accept | accept | |
| gap_alt_operand, altered operand with its own bits | **accept** | **reject** ("ligero: linear functional value mismatch") | |

- The link term is 3× the bare kernel (0.066 s). The extra cost is the transcript challenges, the numpy table build,
  a separate plane-sum pass over the eq table, and the read-modify-write of `a` (4.8 GB). I have not optimised it.
- **Route (a) prime side per BF16 batch on A100, measured on the real proof.** 0.776 s (no link) → 1.20 s (in-unit bits)
  → 1.41 s (+ dense check, one point), plus u_t's commitment at about 0.03 s. That is about **1.44 s (+86%)** with one
  point, or about 1.65 s (+113%) with the two points 2^-128 needs if the link term just repeats. This replaces the
  kernel-only 1.30 s / 1.36 s estimate above. Flock is extra.
- Registered as art:400126e2 (gate-log/v1, refs art:64220e14 and art:35bce6f5). Runs r20260925-100729-6578 and
  r20260925-101520-bc72 are preserved.

## The link built: sigma form, both verifiers (11:30Z)

Per coordinator 1020Z (build allowed to the checklist; sigma-in-clear for A-GKR, NON_ZK_PROOF class only; one
GF(2^256) point; verifier-derived injective maps) and red-team-link §4 ("build the prime side now").  lane/agkr-bound
78b1a62e: `gpu/link.py` (prover + Python verifier), `verifier/src/link.rs` (Rust verifier), PROTOCOL.md §17.

**What is built (prime side), against the checklist.**
- C1: one point r in GF(2^256)^28 (x^256 + x^10 + x^5 + x^2 + 1), each coordinate one whole transcript digest
  (`challenge_bytes`, its own coin slot), drawn after the Ligero root, every GKR message and root_b (C2 ordering).
- C5: both verifiers derive Lambda_F from the unit circuit (column names, order) and the checker-v2 layout, and check
  it is a bijection onto [0, n_pos) with a bitmap.  C6: n_cells = n_pos <= p - 1 enforced (BF16 at K = 1536: <= 40,960
  VUs), sigma_t canonical in [0, n_cells].  C7: booleanity and recomposition assertions checked for every link bit.
- S1: 256 sigma_t messages in the clear, parity = bit_t(y), then one rho and the 256 constraints as one dense term of
  the batched Ligero functional (no new rows, no second commitment).
- STAND-IN binary side: root_b = SHA-256(TAG, "/root-b-standin/", commitment.txt); y from `x.bin` / `w.bin`, which
  the Rust verifier first requires to hash (sha256/row/v1) to every VU's public digest limbs.  Not built: C3 (Flock at
  2^-128), C4 (chain glue), C8 (accountant), Lambda_B's SHA-256 big-endian bit order (F2, binary side).

**Results** (A100 80GB vy-agkr-bound2, bf16-ampere+sha256 in-unit statement, frozen bench-instances/v1, 4,096 VUs,
1 warm-up + 3 reps, MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 set in every run; final run
r20260925-112019-a85e at 78b1a62e; breakdown r20260925-112412-a19c):

| | in-unit bits | + sigma link | delta |
| --- | --- | --- | --- |
| median prove | 1.2016 s | **1.5418 s** | +0.340 s (+28%) |
| Python verify (GPU) | 1.249 s | 1.575 s | +0.33 s |
| Rust verify (13 threads, EPYC 7742) | 3.419 s | 4.665 s | +1.25 s, plus 0.435 s Lambda_F derivation at load |
| proof bytes | 58,988,200 | 58,994,344 | +6,144 (256 messages) |

- Prover link time 0.333 s: eq table 0.137 (2^28 x 32 B, nibble-table levels), z bits 0.010, y and sigma plane sums
  in one fused int8 tensor-core pass 0.062, the term of a 0.124 (five per-limb int8 dots into one tile).  First build
  was 0.72 s (r20260925-104121-b263); the fused pass, the per-limb tile and the nibble tables took it to 0.33 s, each
  step re-verified by the independent Rust verifier.
- Rust verifier: GF(2^256) products by PCLMULQDQ (cargo test against shift-and-add), eq split 2^14 x 2^14, one product
  and 32 byte-table lookups per cell in the row fill; derivation first 1.77 s, 0.44 s after removing the divisions.
- **Route (a) prime side per BF16 batch on A100, measured**: 0.776 s (no link) -> 1.20 s (in-unit bits) -> **1.54 s**
  (sigma link, one GF(2^256) point), about +99% over no link.  This replaces the 1.44 s / 1.65 s estimates of 10:25Z
  (GF(2^128), u committed).  Flock (binary side) is extra: flock-bench-80gb measured 0.745 s on A100 BF16 as shipped.

**Negatives** (each rejected by the Python AND the Rust verifier; honest and honest-without-link accepted by both):

| case (red team #) | Python | Rust |
| --- | --- | --- |
| bit_flip (1) | GKR assertions | GKR assertions |
| non_boolean (4) | GKR assertions | GKR assertions |
| alt_alt_bits, altered operand with its own bits (3) | sigma parity | sigma parity |
| sigma_range, sigma_0 + n_cells + 2, parity kept (6) | sigma range | sigma range |
| sigma_plus2, in range, parity kept | functional value | functional value |
| root_b_changed, points change with roots (11) | sigma parity | sigma parity |
| z_differs, verifier's z altered (10) | sigma parity | statement: x.bin no longer hashes to the digest |
| vu_remap, prover's sigma under Lambda with VUs 0 and 1 swapped, honest witness (7) | sigma parity | sigma parity |
| dup_cell, two link columns one name (8) | derive | derive |
| no_booleanity, one assertion dropped (C7) | derive | derive |

Not run: the forged middle block (needs Flock chaining, C4).  vu_remap was added in the confirming run
r20260925-113047-d490 (same commit; prove 1.1994 -> 1.5286 s, Python verify 1.261 -> 1.564 s, Rust 3.414 ->
4.676 / 4.719 s): 11 of 11 negatives rejected by both verifiers.  Registered art:bd3d8b2c (gate-log/v1, refs
art:400126e2, art:64220e14) and the addendum art:fc687ece; runs preserved.  Drill-down only (L).
- BabyBear cap: the code enforces n_cells <= p - 1, i.e. at most 40,960 BF16 VUs at K = 1536 (p - 1 = 40,960 x
  49,152); the red team's figure is 40,959, one VU stricter.  Both are far above 4,096; I kept the derived bound.

**red-team-flock 1130Z (read 11:41Z).** Flock NOT GRANTED (unbound reps, no live challenger), grantable with R1-R8.
Two points touch this lane:
- A-GKR sets the route's composed bound at 2^-130.2. If the accountant counts A-GKR's hash budget (2^-127.7), the
  proof misses 2^-128 whatever Flock does. That is a C8 decision for the coordinator; the link adds only
  m/2^256 + 255/p^6.
- Their R5 (Flock's coins only after root_F, the link points and y) matches this build's order. Here y is absorbed
  before the sigma messages, so the Flock side must take its coins after that absorb.
No action on the prime side.

## Drill-down: route (a) with Flock's measured side (11:43Z)

Numbers from flock-bench-80gb's FINAL and flock-128's 1128Z handoff (not re-measured here). Per the 0922Z ruling, Flock's
AVX-512 number comes from the H100 host (SPR Xeon 8468, AVX-512 + VPCLMULQDQ). The table uses the as-shipped `Fast`
profile, at 4096 VUs, with prime-side costs from this lane:

| BF16 batch, 4096 VUs | prime side (this lane) | Flock side | route (a) total |
| --- | --- | --- | --- |
| A100, Flock-CUDA pair as shipped | 1.54 s | 0.745 s | ~2.29 s |
| A100 prime + Flock CPU union, AVX-512 host (H100 host, 16 thr) | 1.54 s | 1.317 s | ~2.86 s (sequential) |
| A100 prime + Flock CPU union, Zen 2 host (A100 host) | 1.54 s | 5.370 s | ~6.9 s |

Flock at 2^-128 (flock-128-r2, two `Fast100` runs with live coins; not granted, needs the red-team audit):
- Flock-CUDA: 1.00x today's time on H100 BF16.
- CPU union: 2.00x.
- So the A100 GPU line stays at about 2.3 s if the 1.00x carries over from H100 (not measured on A100).

Both Flock sides overlap with the prime side in time only if run concurrently. The totals above are sums. Caveats:
- fp4 is still unpinned, so there is no fp4 line.
- The vllm-v1 mapping is PROVISIONAL.
- Everything above is drill-down only (L).

## The link on FP8 (11:55Z)

Run r20260925-114925-2f5c used the same build (78b1a62e) and the same 31 harness on fp8-hopper:
- 4,096 VUs, 8-bit words, n_pos = 100,663,296.
- sha256 row leaves, so the Rust loader can check x/w, with an unpinned commitment (`--allow-unpinned-commitment`).
- A100, 1 warm-up + 3 reps, MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1e12.

| FP8, 4,096 VUs | in-unit bits, no link | + sigma link |
| --- | --- | --- |
| median prove | 0.6068 s | **0.7782 s** (link 0.178 s) |
| Python verify | 0.489 s | 0.648 s |
| Rust verify | 1.706 s | 2.360 / 2.337 s, plus 0.219 s derivation at load |
| proof | 35,978,392 B | +6,144 B |

- 11 of 11 negatives were rejected by both verifiers, for the same reasons as BF16, and honest plus honest_nolink were accepted.
- The first attempt, r20260925-114542-3ca4, was refused by the Rust verifier as an unpinned commitment. That was policy,
  not a link result, and the flag above fixed it.
- Route (a) prime side per FP8 batch on A100 goes from about 0.46 s (fp8-hopper+blake3 committed, 1 rep, 07:56Z) to
  0.78 s, about +70%. BF16 was +99%.
- Flock is extra. flock-bench-80gb has no A100 FP8 line; H100 FP8 is 0.330 s Flock-CUDA as shipped and 0.741 s for the
  CPU union on the AVX-512 host.
- Registered as art:60cabb96 (gate-log/v1, ref art:bd3d8b2c), and both runs are pushed and preserved.
- Drill-down only (L). The FP8 statement is not pinned under any relation.
