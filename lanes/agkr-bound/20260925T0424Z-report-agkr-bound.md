---
lane: agkr-bound
kind: report
created: 2026-09-25T04:24Z
status: open
---

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
