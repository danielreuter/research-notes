---
id: 20261004T2202Z-report-relay-docs-scheme-choice-e2e
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/scheme-choice-e2e.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/scheme-choice-e2e.md`, sha256 `8ce2fad0b655e2b8dbccc57105eb9187677dfdae059927f5b4b5c3d0ccc95ef8`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# End-to-end secure-first scheme: dense or P3?

Decision memo for Daniel, 27 Sep 2026.

**Common setup.**
- Both schemes use the reference primitives: 64 KB labels (m = 65,560 B), with H the overwrite chain over the Feistel-SHAKE Π_2 (2m + 512 bits).
- **P3** adds a tweakable P_T, a second layer and the transpose, on B(220, 12).
- **Dense** is one layer on the complete DAG per segment: `C_i = W_i ⊕ H(C_(i−1), …, C_0)`.
- Costs use the [instantiation](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/p3-instantiation.md)'s H100 pricing, and latency assumes 1.4 µs per Keccak-f on one GPU thread. Both are estimates unless marked measured.

**The proved dense instance is not usable as is.**
- `dense_meets` fixes 1 KB labels, B = 2^16 and D = 64. A 1 KB Π_2 call takes 7.5 µs at the floor, so D = 64 covers only 0.49 ms, below Δ.
- Decode would also cost about 1,200× P3's.
- The column below is therefore the re-parameterized point: 64 KB labels, B = 512 blocks per segment, D = 5.

| | P3, as integrated | Dense, B = 512, D = 5 |
|---|---|---|
| Decode work | 26 Π_2 + 2 P_T calls per label: ≈ 23,800 SASS/B (≈ 3,800× at decode batch, 150× at prefill) | 256 Π_2 calls per label on average: ≈ 227,000 SASS/B, 9.5× P3 (≈ 36,000× / 1,400×) |
| One 32 MiB tensor (4096² bf16) | ≈ 50 ms of work; **latency ≈ 0.36 s** (28 sequential wide calls) | ≈ 0.45 s of work; **latency ≈ 7 s** (a 512-call chain per row) |
| Demo (L40S, Qwen2.5-0.5B, unfused) | measured: 4 × 6 tokens in 237 s (plaintext 0.2 s); GPU encode 175 s | not run: ≈ 40–75 min for the same run (scaling by work and by latency); encode is 131k sequential calls per segment, ≈ 5 min on one CPU core per segment |
| Storage, space bound | rate 1, \|C\| = \|W\|, 24 B salt; `SpaceBound 21/20` proved; 14.4 MB segments | rate 1, \|C\| = \|W\|, no `pp`; space bound proved; 33.6 MB segments |
| Audit k, deadline | k = 117 (the demo runs 132). D = 10 rounds of at least 242 µs, so it covers Δ + RTT < 2.66 ms | k = 106. D = 5 calls of at least 483 µs, so it covers Δ + RTT < 2.90 ms |
| **Proved** (Lean, kernel-replayed) | `p3_meets_64_D10_of_decode` and its 14 GB form: `Meets` from `DecodeHyp3` and the proved `Theorem1iiSeq`, with random-oracle H and an ideal tweakable P. The band certificate is proved | `dense_meets`: `Meets` with **no hypothesis**, random-oracle H (at the pinned point). `dense_timedINC` is generic in (B, ℓ, D, Q). Over the chain, the pebbling side `chainDense_hard` is proved |
| **Missing** | (1) `DecodeHyp3` for forward-only adversaries: a sizeable, mechanical decode. (2) **With P^(−1): open**, the DGO19 / PIEs Conj. 1 core, plus two statement changes (key parts, a root-overflow term). (3) The core restatement after `FreshnessInvariant` fell. (4) The chain version: held chaining values in the column game, re-certifying X, a two-permutation kernel | (1) Re-certify at this point (numeric), plus a disjoint-union pebbling lemma for many segments (small). (2) `ChainExPostFacto`, B5 for Π_2, in progress in `sponge-dense`. Labels are one-way, so there is no P^(−1) step |
| Integration | done: reference #166 and demo #172 pass bit-exactness, the setup-root check, 20/20 honest audits and 0/20 on the negative control | reuse Π_2, the chain, the Merkle `vk`, the responder and `TimedVerifier`. Replace the two-layer codec with one layer, drop P_T and the transpose, and add new known-answer vectors |

**Deadline.**
- The demo's p99.9 round-trip allowance (about 0.6 ms in total) leaves about 4.5× for both schemes.
- Its calibration-maximum allowance (3.44 ms) is outside both certificates, so keep the p99.9 allowance.

**Assumptions outside Lean, for both:**
- timing: no ASIC, and Keccak-f takes at least 50 ns;
- perfect isolation;
- Feistel-SHAKE behaving as ideal permutations inside the storage game (Ristenpart–Shacham–Shrimpton).

## Recommendation

**Make the dense scheme the workstream-1 scheme at 64 KB labels, B = 512, D = 5, k = 106.**
- Its full proof has no open research step. The random-oracle proof is done and needs only a numeric re-certificate, and the chain lemma follows B5's pattern and is underway.
- P3's proof ends at an open conjecture. Its forward-only milestone does not cover a real adversary, because P^(−1) is public.
- **The price:** about 10× P3's decode work and 20× its latency. The demo stays feasible on Qwen2.5-0.5B, with fewer tokens.
- **Keep P3's codec** in the reference behind the same interface, as the performance candidate, and continue its forward-only milestone.
- **If Δ + round trip stays under 0.7 ms,** B = 256 and D = 2 halve the dense cost (4.8× P3, k = 101) and keep a 2× margin.
