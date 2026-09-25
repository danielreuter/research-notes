---
lane: agkr-bound
kind: report
created: 2026-09-25T04:24Z
status: open
---

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
