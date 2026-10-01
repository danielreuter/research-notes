---
id: 20261001T0938Z-handoff-from-proofs-flock-fp-fp-ladder-done-next-is-packing
campaign: overnight
lane: proofs
kind: handoff
status: open
repo: verity
origin: proofs-flock-fp (bc-15199603)
---

# The FP ladder is done at all 12 points; next I'd pack FP elements into the u16 frame

to: proofs (bc-8416bc72). From proofs-flock-fp. My lane's 09:34Z and 09:40Z checkpoints in
`note:proofs-flock-fp/20261001T0738Z-report-proofs-flock-fp` have the step-by-step numbers.

## Best point per format and K

Every point is byte-identical and carries the statement digest red-team-proofs-554 listed. E4M3 node-2 values have the
node-1 equivalent (/0.95) in brackets. NVF4 and MXF4 points are node-2-only.

| | K=16384 | K=8192 | K=4096 | K=2048 |
|---|---|---|---|---|
| E4M3 | 4.70e7, node 1, `r20261001-090911-7571` | 4.56e7, node 1, `r20261001-090552-7923` | 4.69e7 (4.94e7), node 2, `n2h-20261001-083947-f311` (step 2) | 4.56e7 (4.80e7), node 2, `n2h-20261001-090541-3667` |
| NVF4 | 9.58e7, `n2h-20261001-085239-68db` | 9.42e7, `n2h-20261001-090030-a396` | 9.03e7, `n2h-20261001-085049-fb8c` | 9.19e7, `n2h-20261001-090421-9ffc` |
| MXF4 | 9.44e7, `n2h-20261001-090130-b8c8` | 9.33e7, `n2h-20261001-085119-feee` | 9.24e7, `n2h-20261001-085148-10f6` | 8.98e7, `n2h-20261001-084507-9248` (step 2) |

The cells marked step 2 have a step-3 point within noise of them. The others are step 3, and they carry
`verifier-c0-once-unreviewed`. MXF4 also carries `no-campaign-target`.

## What each step bought (same node, against the step below)

- **Step 1, the fold:** −22 to −43% at every format and K, on node 1.
- **Step 2, the overlap:**
  - E4M3 on node 1: −85% and −69% at K=16384 and 8192. At K=4096 and 2048 (node 2 against node 1, /0.95): −64% and −43%.
  - MXF4 on node 2, against the step-1 copies moved back at 09:28Z: −82%, −75%, −64% and −50% at K=16384 down to 2048.
  - NVF4 has no node-2 step 1, so its step-2 gain is uncredited under the node-2-only rule.
- **Step 3, the structured lincheck:**
  - E4M3 on node 1: −31% and −33% at K=16384 and 8192.
  - Every other point stays under 20% on both samples: FP4 K=16384 −16 to −19%, K=8192 −6 to −12%, and ±5% below that.

## Why the ladder is done

- At step 3, overhead is 1.01–1.04× its prove-only overhead for FP4 and 1.05–1.08× for E4M3.
- Prove-only matches step 0's within noise (E4M3 4.3–4.6e7, FP4 8.3–9.3e7), so the overlapped verifiers cost the prover
  nothing measurable.
- bf16-hill's two-server lever (−25% at BF16 K=8192) removes non-prove time. FP has only 1–8% of that left, under the 12–19%
  spread, so the lever couldn't be credited here.
- RUNS=96 is a measurement check, not a lever (bf16-hill), and the tile is an OBJECT.

## What I'd run next, in order

1. **Pack sub-16-bit elements into the frame's u16 words: four FP4 a word, two E4M3.**
   - Today the frame holds one FP4 element per word. The SHA-512 hashing of the input rows is about 85% of the block: 12.1M of
     14.2M rows at MXF4 K=4096 (k_log 24, n = 2048).
   - Packed four to a word, the block is about 5.1M rows and fits k_log 23. That doubles n at m = 35, and since a statement
     proves in about 0.75 s at m = 35 either way, overhead about halves: an estimate of 4.6e7 for FP4.
   - E4M3 at two a word comes to about 8.1M rows, borderline for k_log 23, so it needs measuring.
   - It's a new statement and circuit. The digest changes, so it starts a new curve, and it needs circuit-check and a
     statement reviewer.
2. **The prover's time per statement**, about 0.75 s at m = 35, which every format now sits on. bf16-hill's pipeline depth 2,
   running on node 2, is the first format-independent candidate. I'd port it if it wins there.
3. **Tiles**, if Daniel rules for cross-Call grouping and Q2's `stage_tiled` is fixed.

## Open, for you

- **Q3c covers my step 3 too.** `ab5087cd4` has the same patch id (`f4edb518bbb30905`) as bf16-hill's `750e344fd` and
  proofs-arch's `acca35385`, the commit bf16-hill asked about in
  `note:proofs/20261001T0926Z-reply-from-proofs-bf16-hill-fold-granted-c0-once-unreviewed` (review target
  `art:2aef6594e7d5510a22c7cb7e7afa54fd20d954ceabf3d910a7437567ba204686`). A grant there clears `verifier-c0-once-unreviewed`
  from all 24 of my step-3 points, as a re-label.
- **The overlap flag.** My steps 2 and 3 carry the same verifier overlap that bf16-hill says no #554 scope covers (`84dff1e81`,
  `f7d3e55fe` here). Whatever you rule for theirs, I'll apply to mine.
- **NVF4's step 2 on node 2.** Four node-2 step-1 copies would credit it. My recommendation is to skip them: MXF4's same-node
  pairs (−50 to −82%) already show the lever on FP4, and the copies would duplicate node-1 points.
- **A side note for n2-hill's FP4 parity.** Node 2's MXF4 step-1 copies against node 1's step 1:
  - K=2048: 1.79e8 against 1.71–1.86e8;
  - K=4096: 2.68e8 against 2.56e8;
  - K=8192: 4.03e8 against 4.38e8;
  - K=16384: 6.39e8 against 7.40e8.

  Step 1's overhead is mostly verification on the CPU, so this says nothing about the GPU-bound parity. It does suggest
  node 2's CPU slices are no slower at large K.
