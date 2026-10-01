---
id: 20260930T2330Z-report-proofs-arch
campaign: verity
lane: proofs-arch
kind: report
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72); worker bc-e222fd63
cursor:
  subagentId: "bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4"
---

CHECKPOINT b9b724e9d (02:02Z) [open] b9b724e: session verifier phase timers (eb51d8b) + template-aware lincheck FC_LINCHECK=partial default (8db1cb5), equal to upstream's on arch_proto k=13-25 and K=64 selftests (38/38); node-1 stage job pa-stage-b9b724e queued (0 GPU, 112-127), GPU job next
CHECKPOINT 94993e0f9 (00:49Z) [open] study done (/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/flock-restructure.md; both handoffs acted on, copy model = Rows.stack d1bf7c38a): template-aware lincheck verifier -3.1..3.5s/stmt K=2048 same proofs; step slots 4.97e6->3.0e6; rows hashed once/stmt ->1.7e6 needs cross-block wiring; lookups +18%; art:09f36906; branch cursor/proofs-arch-95d4 94993e0f9
CHECKPOINT cc21a7d94 (00:40Z) [open] profile done (M0 #20 K=2048): verifier 10.46s vs prover 0.78s; lincheck structure work 3.1-3.8s/stmt, template-aware verifier removes ~93% of it (byte-identical proofs); prover structure share 21%; art:e2a1c8e1
CHECKPOINT ce30e9b65 (23:28Z) [open] no-op audit done (internal/proofs/noop-audit.md): padding excluded pre-proof by host executed_prefix rule; lifted/Serve@3 reps exist only in vllm, unprovable by C-Flock; study next
# proofs-arch: restructuring C-Flock for FP matmuls, hashes and no-ops

Daniel (Sep 30, 4:20 PM PDT): keep arbitrary Boolean circuits as the fallback, and ask what shape the prover takes if
it bakes in structure (lookups, uniform copies, hashes, no-ops). Experimental: prototypes and measurements only.
Branch `cursor/proofs-arch-95d4` (worktree `/tmp/proofs-arch`, off `origin/main` `ce30e9b65`).

Handoffs acted on: `20260930T2329Z-handoff-from-proofs-daniel-priorities` (no-ops dropped, interactive, uniform copies
first, then lookups, then hashes; SHA-512 + A3 only) and `20261001T0005Z-handoff-from-proofs-advisor-notes` (the
prototype's copy model is the soundness package's `Rows.stack` / `placement_stack`, commit `d1bf7c38a`).

## 1. No-op audit (4:30 PM PDT)

Full text: Project store `internal/proofs/noop-audit.md`.
- Post-EOS and padding positions are **excluded before proving**. `check/executed_prefix.py` sets
  `executed_prefix_len` (served + LAG, or the cap). It's host Python linked to Match G6, and not in any proof.
- The explicit representations live only in the vLLM integration: `Serve@3` (a live bit, unguarded bodies) and
  `LServe_v2` / `Lifted[F]_v2` (⊥ = `1<<w` tag bit, `LEnable_v1`). The opt-in `--padded-finalize` Commit writes ⊥ words.
  Only tests build lifted Programs.
- `verity.ir` has no ⊥ or enable. C-Flock's `ir_lower` raises `NoPiece` on every lifted primitive. A strict lift
  replays every gate, so ⊥ would cost full price.

## 2. Restructuring study (5:45 PM PDT)

Full text: `/cursor/stores/bc-7f347b4b-6175-4b6e-84c6-731add2f8589/docs/flock-restructure.md`. Statement profiled: M0 #20
(`r20260930-184956-61fe`), K=2048 and K=8192 at m = 35.

- **The session is verifier-bound.** The GPU prover takes 0.78 s per statement; the loopback verifier takes 10.46 s
  (K=2048) or 27.42 s (K=8192). Prover circuit-structure work is 21%, and the lincheck is only 6%.
- **Idea 1, the template-aware lincheck verifier.** It computes the lincheck's final value from the slot template plus
  Δ in O(nnz(T) + |Δ|), and never builds a 2^k vector. Proofs and transcript are byte-identical. It saves 3.1–3.5 s
  per statement at K=2048 and 2.9–5.8 s at K=8192. Lean needs `CircuitFold.partial` plus one level-3 theorem,
  `partial_eq_halve_fold`; the soundness package needs nothing new.
- **Idea 2, step-sized slots.** Bits per MAC fall from 2048 to 1170 (K=2048) and from 4096 to 2048 (K=8192). Prover
  overhead falls from 4.97e6 to 3.0e6 and from 9.84e6 to 5.0e6. `placement_stack` already covers it, instantiated at
  the step.
- **Idea 3, each row hashed once per statement.** Hashes are 37% of bits at K=2048 and 69% at K=8192. Hashing each row
  once gives 534 and 547 bits per MAC, and prover overhead of 1.7e6 for both shapes. It needs cross-block wiring, a
  statement-format decision.
- **Lookups.** A char-2 lookup is a grand product proved with upstream `product_gkr`. It costs as much as about 149
  bits of zerocheck, so it breaks even at about 45 committed bits replaced. Products, alignment and normalization win;
  the max exponent doesn't. It gains 18% on top of idea 3.
- **Not located:** about 6.7 s (K=2048) and about 21 s (K=8192) of verifier time per statement is neither the lincheck
  nor the region claims. An instrumented M0 statement is the next profile.
- **Decisions for Daniel:** the cross-block wiring format; one 128-bit rep instead of two Fast100 reps (for
  `proofs-security`); weights bound at registration or commitments reused; lookup gates; the instrumented M0 profile.

## 3. Prototypes

All on `cursor/proofs-arch-95d4` under `backends/flock/arch_proto/` (head `94993e0f9`). The Rust benches are upstream
flock b684b12 examples; build notes are in their headers. Evidence:
`art:09f3690625239edc1ab2721b3c9a4f6daa2ec5b60a20474f9043d1edf8541837` (label `question`), which supersedes
`art:e2a1c8e1…`.

| file | what | commit |
|---|---|---|
| `step_template.py` | P1's sm_120 BF16 k16 step as a 2^13-row slot | `c019ed6d7` |
| `export_template.py` | the slot in `Rows.stack` order (inputs, computed rows, constant at nIn + nComp) | `1ace46f50`, `d1bf7c38a` |
| `uniform_copies.rs` | N copies in one block: flat, unit, step and template-aware verifiers | `3b80c24fb`, `d1bf7c38a` |
| `layout_model.py` | committed bits per MAC and session overhead, today against ideas 1–5 | `1b048fa25` |
| `lookup_cost.rs` | a product-GKR leaf priced against a zerocheck bit | `94993e0f9` |

- The prototype is correct in honest mode at k = 13–25, and at k = 13–22 in `Rows.stack` order. All five verifiers
  return the prover's claim, and a tampered `z_partial`, round message or Δ entry is refused.
- The lincheck proof is 1248 + 32·(k − 13) bytes for every description.
- The template-aware verifier is 10–40× faster than today's `BlockCircuit` fold (k = 26: 0.137 s against 1.71–1.90 s a
  rep).
- GPU was not run, which deviates from the handoff. The proofs are byte-identical, so a GPU comparison would measure no
  difference.
