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

CHECKPOINT cc21a7d94 (00:40Z) [open] profile done (M0 #20 K=2048): verifier 10.46s vs prover 0.78s; lincheck structure work 3.1-3.8s/stmt, template-aware verifier removes ~93% of it (byte-identical proofs); prover structure share 21%; art:e2a1c8e1
CHECKPOINT ce30e9b65 (23:28Z) [open] no-op audit done (internal/proofs/noop-audit.md): padding excluded pre-proof by host executed_prefix rule; lifted/Serve@3 reps exist only in vllm, unprovable by C-Flock; study next
# proofs-arch: restructuring C-Flock for FP matmuls, hashes and no-ops

Daniel (Sep 30, 4:20 PM PDT): keep arbitrary Boolean circuits as the fallback, and ask what shape the prover takes if
it bakes in structure (lookups, uniform copies, hashes, no-ops). Experimental: prototypes and measurements only.
Branch `cursor/proofs-arch-95d4` (worktree `/tmp/proofs-arch`, off `origin/main` `ce30e9b65`).

## 1. No-op audit (4:30 PM PDT)

Full text: Project store `internal/proofs/noop-audit.md`.
- Post-EOS and padding positions are **excluded before proving**. `check/executed_prefix.py` sets
  `executed_prefix_len` (served + LAG, or the cap). It's host Python linked to Match G6, and not in any proof.
- The explicit representations live only in the vLLM integration: `Serve@3` (a live bit, unguarded bodies) and
  `LServe_v2` / `Lifted[F]_v2` (⊥ = `1<<w` tag bit, `LEnable_v1`). The opt-in `--padded-finalize` Commit writes ⊥ words.
  Only tests build lifted Programs.
- `verity.ir` has no ⊥ or enable. C-Flock's `ir_lower` raises `NoPiece` on every lifted primitive. A strict lift
  replays every gate, so ⊥ would cost full price.

## 2. Restructuring study

Pending: Project store `internal/proofs/flock-restructure-study.md`.

## 3. Prototypes

Pending.
