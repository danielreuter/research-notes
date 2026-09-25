---
lane: agkr-bound
kind: report
created: 2026-09-25T04:24Z
status: open
---

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
