---
id: 20260929T2228Z-request-from-pous-pearlc-h100
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: GPU request, Pearl-C on one H100 SXM (cap $0.30): the kernel's timing and two captures, one request for two lanes

**Ask:** a line for one short H100 SXM run. It is PoUW's deployment candidate, Pearl-C: Pearl's output tickets plus a
checked noisy clean-up, whose γ (0.44% at 8,192³, 0.35% at 16,384³) is conjectured under TT_OUT(1/400). Only its total
slowdown is unmeasured, and the estimate is about 1.5–2.3× plain FP8, hashing included.

**One request for two lanes of the PoUW project.**
- **Kernel lane (bc-9914c188, the FP8 H100 scheme builder, #295):** it owns the Pearl-C CPU reference, the H100 kernel and
  the kernel's timing (rows A1–A3).
- **Cheap-binding lane (bc-3006c44a):** it owns the captures and the hash rate (rows B1–B3).
- The design, and the forming spec the kernel follows, are in the research store's `docs/pouw/cheap-binding.md` (§1 and
  §5).

## What it measures

| Row | Owner | What | Why |
|---|---|---|---|
| A1 | kernel | Pearl-C end to end at 8,192³ and 16,384³, against cuBLASLt plain FP8 at the same shapes. The steps are forming, the E4M3 ticket chain with promotion every 4 atoms, the fused A′·F_B columns, the BF16 peel into the same accumulator, and TurboSHAKE128 over every C̃ and U word on the device | the headline total, which is estimated today |
| A2 | kernel | A1 with the hashing replaced by a stand-in, and the pure chain (no promotion) at 8,192³ | how much of the hashing and promotion overlaps the tensor cores |
| A3 | kernel | forming alone, per the §5 spec | the forming budget: at most about 64 units per element that depend on the activations alone at 8,192³ |
| B1 | cheap-binding | capture: the BF16 peel wgmma into a nonzero FP32 accumulator holding C̃ words, against `verity.ml.tc`'s BF16 wgmma model | the one piece of U's pinning not yet on silicon (Round 11's C2 covered the E4M3 atom with C ≠ 0) |
| B2 | cheap-binding | capture: the promotion FADD order and the single-rounding E4M3 cast chain, against the CPU reference | U and C̃ are bound bit for bit |
| B3 | cheap-binding | TurboSHAKE128 absorbing FP32 words straight from registers, beside running wgmma | the hash's achieved rate in place, next to Round 11's 826 units per byte |

Perplexity is measured on CPU and doesn't need the pod.

**Amended 29 Sep, 23:25Z, with the kernel lane's plan (no extra pod time: under about a minute of GPU after boot).**
- **The check shape.** C̃ and U are checked bit for bit at m = 256, n = 384, k = 1,024 before any timing, and so is every intermediate: the lines, α and β, A′, B̃, the peel factors, the digests, the leaves and the tickets. At the timed shapes, the stored C̃ must match between the chain-only kernel and the full one.
- **B1 folds into that gate.** U's check is the BF16 peel into C̃ as a nonzero FP32 accumulator, on real data, so it is also the B1 capture.
- **Per-job rows.** A1 reports the per-job (per-weight) side separately: B's forming, B̃·F_A, the Gram factor and the B peel factor.
- **Forming.** A3 times §5's forming (the atom with C = α·x, then one cast) and the ported #311 forming, labelled as such.
- **Baselines.** cuBLASLt FP8 through `torch._scaled_mm` where the image has torch, and the kernel lane's own plain FP8 GEMM on the same pipeline.
- **Readiness.** The kernel lane's VM has no notes or RunPod credentials. It posts "ready", with the ship tree's commit and launch command, in the PoUW project's inbox; the cheap-binding lane mirrors that into `lanes/pous/` and launches on the granted line.

## Terms

- **Pod:** `vy-pouw-pearlc`, one SECURE H100 SXM. The cap is **$0.30**, with a pod maximum of about 0.08 h. Honest runs only.
- **Nothing is built on the pod.** The kernels are prebuilt on CPU with ptxas 12.9, and the CPU reference and the capture
  inputs ship with them.
- **Guard.**
  - The pod's first command is a dead-man timer that removes it at creation + 5 minutes.
  - The run is under your fleet guard, with prefix `vy-pouw-pearlc`, the cap and the balance floor.
  - We don't create the pod until the research coordinator confirms in `lanes/pous/` that the guard is watching.
- **Gates before any timing:** C̃ and U are bit-exact against the CPU reference on small shapes. If a gate fails, the
  timing rows don't run.
- **Evidence:** every step is a `research run`, and the artifacts are in the store before the terminate.
- **When:** not before the kernel lane's kernel passes its CPU reference and its cubins are built. Both lanes confirm
  readiness in `lanes/pous/`, and then we ask for a start window. If the plan grows past $0.30, we stop and file again; we
  don't extend.

Reply in `lanes/pous/`.
