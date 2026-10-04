---
id: 20261004T2202Z-report-relay-docs-band-vs-dense
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/band-vs-dense.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/band-vs-dense.md`, sha256 `f4367d5ab591096ee2ab783b4e42c417b0b11bdb95f3a933a8bfd72fbfcb5a71`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Band graph vs dense, at equal security

Memo, 28 Sep 2026. Proofs: `lean/submissions/band-chain/` (red-team §39: GO on the statement; proofs on the three
standard axioms, `leanchecker --fresh`).

**Bottom line.**
- Over the overwrite chain, a single-layer band graph with in-degree d ≥ D is exactly as secure as dense. It has the
  same hardness, the same certificate, and k = 111 at the 64 KiB point.
- It decodes a block in d + 1 calls instead of 256.5 on average: **43× cheaper at d = 5, 20× at d = 12.**
- The price is a cliff. Security holds only while the effective round budget stays at or below d, and it collapses
  one round past it. **Recommend d = 12.**

## Why it holds

- **A label comes only from its own row.** Each row starts from its own IV(dom v). A label that is not held comes only
  from its own row's pad call, after all of that row's calls (`chain_clock`, for every holding).
  - Nothing held for another row shortens it.
  - A held partial chain state h_{v,j} costs 1 + c/ℓ labels and yields only label v, so it never beats holding C_v.
- **Only the first D rows come free.** With d ≥ D, every row from D on is at least D + 1 calls, so only rows
  0 … D − 1 come free (`band_chain_hard`). That is dense's loss. Where the gaps fall is irrelevant.
- **The same certificate applies.** `band_meets_64` gives `Meets` at 64 KiB, B = 512, D = 5, Q = 2^20, k = 111 and
  ε = 2^−128, for every d ≥ 5. It reuses dense's certificate terms verbatim.
- **It is conditional, like dense's chain `Meets`.** It assumes `ChainExPostFactoG`, the DAG-generic form of dense's
  open `ChainExPostFacto`, and `chainExPostFactoG_spec` proves that `ChainExPostFactoG` implies `ChainExPostFacto`.

## The comparison

Same ρ = 18/19, δ = 1%, ε = 2^−128 and deadline (D = 5 Π₂ calls), per 32 MiB segment of B = 512 blocks of 64 KiB.

| | Dense | Band, d = 5 | Band, d = 12 |
|---|---|---|---|
| Decode calls for block v | v + 1, 256.5 on average | min(v, 5) + 1, 5.97 on average | min(v, 12) + 1, 12.85 on average |
| Decode work per segment | 131,328 calls | 3,057 (43× less) | 6,578 (20× less) |
| Decode depth (rows in parallel) | 512 calls | 6 (85× less) | 13 (39× less) |
| Encode depth (one chain) | 131,328 calls | 3,057 | 6,578 |
| One spot check (A1) | v + 1 calls, reading v parents (16 MiB on average) | 6 calls, reading 5 parents (320 KiB) | 13 calls, reading 12 parents (768 KiB) |
| k, overwrite chain | 111, given `ChainExPostFacto` | 111, given `ChainExPostFactoG` | 111, given `ChainExPostFactoG` |
| k, random-oracle H | 106, no hypothesis | none: a constant fraction rebuilds in one round (`b1_free_fraction`) | none |
| Storage | rate 1, \|C\| = \|W\|, no pp; state bound ⌊ρ\|C\|⌋ = 254,307,274 bits | same | same |
| Effective round budget D′ tolerated | any, degrading gracefully (next section) | D′ ≤ 5 | D′ ≤ 12 |

- **Per-block costs** are `depth_bandKey` (block v is min(v, d) + 1 calls) and dense's `depth_blockKeyOv` (v + 1).
  Work per segment is their sum. Encode is one chain, because row v starts once C_(v−1) is known.
- **The band's decode cost does not grow with B.** At B = 4,096 (256 MiB segments) the same certificate formula gives
  k = 88, where dense would pay 2,048.5 calls per block. This is computed by `band_vs_dense.py`, not in Lean.

## The cliff

Dense degrades gracefully when the adversary gets more rounds than the timing model assumed. The band does not.

| Effective budget D′ | Dense, at the deployed k = 111 | Band, d = 5 | Band, d = 12 |
|---|---|---|---|
| 5 | accepts ≤ 0.98% | same as dense | same as dense |
| 6 | ≤ 1.2% (1% again at k = 117) | **accepts 1** | same as dense |
| 8 | ≤ 1.9% (k = 130) | accepts 1 | same as dense |
| 12 | ≤ 4.7% (k = 168) | accepts 1 | same as dense |
| 13 | ≤ 5.9% (k = 181) | accepts 1 | **accepts 1** |

- **With d ≥ D′, the band behaves exactly like dense.** It has the same hardness at D′ (`band_chain_hard`), hence the
  same numbers. Dense's figures use the same chain certificate at D′.
- **At D′ = d + 1, the gap attack breaks it** (`band_gap_attack`). Hold every label except each (d + 1)-th. Each dropped
  row has all its parents held and is d + 1 calls, so every label is known within D′ rounds.
  - It frees ⌊511/(d + 1)⌋ blocks: 85 (16.6%) at d = 5, and 39 (7.6%) at d = 12.
  - Both exceed the 1 − ρ = 5.3% the state bound leaves, so the holding fits and passes every challenge.
  - This is proved at the deployment size: `band_cliff_d5` (d = 5 fails at D′ = 6) and `band_cliff_d12` (d = 12
    fails at D′ = 13). `band_d12_margin` proves d = 12 holds for every D′ ≤ 12.
- **A larger d only moves the cliff.** Only d ≥ 18 keeps the single-gap holding above the state bound, and longer
  budgets free runs of dropped blocks. Surviving any timing error means d near B, which is dense.

## Recommendation: d = 12

- **Deployment condition** (red-team §39): the effective D, meaning the sequential Π₂ calls an adversary completes
  within Δ + RTT, must not exceed d.
  - Today D = 5 rests on each 64 KiB call taking at least 483 µs, so a sixth call cannot finish within 2.90 ms.
- **Margin.** d = 12 holds while 13 call-times exceed Δ + RTT. That is 2.2× headroom on the per-call floor, or on the
  deadline.
  - d = 5 has none. At the edge of the covered deadline (Δ + RTT just under 2.90 ms), any Π₂ faster than the 483 µs
    floor fits a sixth call and breaks it outright. d = 12 needs the floor to drop below 223 µs.
- **Cost.** 12.85 calls per block, still 20× less decode work than dense and 39× less decode depth.
- **What remains open:**
  - `ChainExPostFactoG`. The dense prover is generalizing `ChainExPostFacto` to any DAG, and the band's `Meets` rests
    on it as dense's chain `Meets` rests on `ChainExPostFacto`.
  - The Feistel-SHAKE ideal-permutation heuristic and the timing assumptions, as for dense.
  - The band is a new scheme: the reference codec needs the graph change and new known-answer vectors.
