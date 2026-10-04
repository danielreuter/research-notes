---
id: 20261004T1836Z-report-relay-p2-verdict
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for memory-accounting's 18:25Z question from store:pous/internal/efficient-crypto/p2-verdict.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/efficient-crypto/p2-verdict.md`, sha256 `f5407c0abf471d10939d2ad113a1f7007667188023dde78c562576fe6ec95c23`, unchanged since it was written, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P2 verdict (overnight push, 28 Sep 2026, 05:30Z)

**Verdict: SOUND WITH PARAMETERS, and worth a Lean statement.**
- **Sound where it matters.** P2-5504 fails the settled timing. Re-gated to w ≈ 16,448 bits, P2 survives both red teams
  inside the decided model.
- **Measured decode.** About 14× the band at that width on the same L40S, and 26× if the round trip is near zero.
  **Corrected 08:45Z:** those figures used the M2 schedule, which the proof does not cover. The covered (M1,
  per-block-key) figure is 25.0 GB/s, about 16.3× the band (see the correction below).

> **Correction, 28 Sep 08:45Z (found by the POUS MVP owner, bc-13eada34).**
> - **What was wrong.** Every GPU throughput figure in this document used the scout's "cheap keys": a shared mask K
>   with tweaks `t_j = t0 + j·step`, i.e. model M2. The pinned `P2MeetsM1Uncond` covers only fresh per-block keys
>   (M1).
> - **The covered measurement.** Fresh per-block keys at w = 16,448, on Qwen2.5-0.5B, on an L40S:
>   - **25.0 GB/s** effective weight bandwidth, 16.3× the band's 1,532 MB/s on the same workload, against 25.6 GB/s
>     for the shared key in the same run (per-block keys cost 2.3%);
>   - 2,048 sampled blocks with 0 mismatches; the timed audit accepted 20 of 20; the negative control accepted 0;
>   - Attempt `r20260928-081028-0c5f`.
> - **Caveats:**
>   - Its keys were derived on the host and read from device memory, about 2 GB for a 0.99 GB model. A deployment
>     inside the 1.05× space bound must derive them on the device, at a cost not yet measured (≈ 2% *est.* for a
>     ChaCha8-class expander). Assigned to the MVP owner by the root coordinator (09:20Z).
>   - It used 2^19 blocks, not the pinned 2^23. **Closed 09:20Z:** `P2MeetsM1B19Uncond` (exactly 2^19) and
>     `P2MeetsM1FamilyUncond` (2^8 to 2^23), both at k = 88, both pinned and proved unconditionally in abstract M1.
> - **Also M2-based:** the scout's 14.5–21× cost estimate and k = 101–102, and the timing red team's 258 int32/B
>   decode cost (no key generation counted).
- **Price, for Daniel:**
  - a novel instantiation heuristic (the square–mask–square map as a per-block slow-inverse permutation) where the band
    uses the standard Feistel-SHAKE;
  - a timing margin that cooperating CPU cores could erode.
- **Against its own class,** P3 on heuristic ARX primitives, it is only on par.

## Evidence

| Input | Result | Source |
|---|---|---|
| Timing re-gate | 5504 bits: one root ≥ 396 µs on the fastest core (Zen 5 IFMA at 5.7 GHz, best Toom/Karatsuba plan), 0.79× of the 0.5 ms deadline even with zero round trip. 2× margin needs w = 8,000 / 12,592 / 16,448 at round trips 0 / 1 / 2.4 ms (prime 2^16448 − 21065) | `attacks/p2-redteam-timing.md` |
| One-root gate | Skipping both roots needs ≥ w stored bits. Confirmed twice: analytically by the timing red team, and by lattice runs at w = 128–256 (every success needed ≥ 1.055w; everything ≤ 1.005w failed) | `attacks/p2-redteam-timing.md` Q4; `attacks/p2-redteam-algebra.md` Q1 |
| Mask | Sound for a uniform K: XOR-after-reduction is not polynomial over Z_p. The only known route guesses or stores the masked bits and saves nothing above weight ≈ 0.11w | `attacks/p2-mask-check.md` |
| SeqRoot shortcuts | None inside the model: SNFS precomputation > 2^164 at w ≥ 8,000, smoothness root-finding ≤ 2^−2700, storage-slack tables reduce to these | `attacks/p2-redteam-timing.md` Q3 |
| Cooperating cores | 4–8 cores speed each squaring 2.3–4.1× and eat the margin. A hash chain (band, P3) can't be split this way. If allowed, w ≈ 27–37 kbit | `attacks/p2-redteam-timing.md` |
| L40S decode (measured, bit-exact, 99,573 blocks; **M2 schedule, not covered**) | 51.1 / 39.7 / 31.7 / 26.9 / 24.1 GB/s at w = 5504 / 8192 / 10240 / 12288 / 14336, i.e. 33 / 26 / 21 / 18 / 16× the band's 1,532 MB/s. CGBN without the squaring shortcut; a tuned kernel may be 1.5–2× faster | `candidates/p2-gpu-decode.md`, Attempt `r20260928-050251-7f91` |

**Tuned kernel (07:15Z; measured, replaces the extrapolation; M2 schedule, not covered by the proof).**
- **Throughput:** 44.3 / 24.2 / 15.5 GB/s at 8,192 / 16,448 / 32,768 bits, i.e. 28.9× / 15.8× / 10.1× the band.
- **Kernel:** a half-split squaring or Karatsuba, with CGBN at the leaves. That is 1.14–1.55× over CGBN re-measured in
  the same run, with issue use at 34–43% because register pressure limits occupancy.
- **Verification:** 64,293 blocks bit-exact. One variant is excluded and used for no number: Karatsuba at 16,448
  bits with TPI 16, which mismatched 782 of 2,075 blocks, cause not found.
- **Run:** `r20260928-065407-16f0`; GPU spend $0.80 in total.

**Throughput at the widths the timing requires** (M2-schedule measurements; M1 per-block keys measured 2.3% lower
at 16,448 bits) (linear in w from the measured points; *est.* beyond 14,336):

| Round trip | w (2× margin) | L40S decode | vs band (1.532 GB/s) |
|---|---|---|---|
| ≈ 0 | 8,000 | ≈ 40 GB/s | ≈ 26× |
| 1 ms | 12,592 | ≈ 27 GB/s | ≈ 17× |
| 2.4 ms (the band's covered budget) | 16,448 | ≈ 22 GB/s *est.* | ≈ 14× |
| cooperating cores allowed | ≈ 32,768 | ≈ 12 GB/s *est.* | ≈ 8× |

## Framed against the band

- **Where the band spends:** its decode is compute-bound on Keccak-f, at 12.85 Feistel-SHAKE calls per 64 KB block.
- **Where P2 spends:** two big-integer squarings per block, with no Keccak at all. Its asymmetry (cheap forward
  squarings, sequential inverse roots) is exactly what the band lacks, since the band's decode pays the same kind of
  call the adversary pays. So P2 moves the decode ceiling by an order of magnitude at every width the timing admits.
- **Same proof shape:** an ideal-model `Meets`, plus an instantiation heuristic and a timing assumption kept outside Lean
  (the project convention).
- **The assumptions differ in kind:**
  - *Band:* the Feistel-SHAKE ideal-permutation heuristic (standard primitive, standard construction) and a per-call
    latency floor of hash-chain type, which cooperating cores can't split.
  - *P2:* "SMS with per-block keys behaves as a slow-inverse ideal permutation" (novel, algebraic; the sms5 reductions
    review shows no black-box reduction to a single-stage assumption exists), and SeqRoot, whose unit (one big
    squaring) cooperating cores can split.

## Next step: a Lean statement, no new trusted definitions

**The claim is the pinned M1 model at P2's parameters.**
- The model: `Pous.Model.M1`, B independent forward-only ideal permutations, block j = Π_j⁻¹(W_j).
- The statement: `Meets (m1 B w) .sequential D Q k εMax` at w = 16,448 (and 8,192), B for a 14 GB model.
- It follows from the pinned, proved `A3PrimeLam`, the pinned but open `A2LemmaAM1` (M1 Lemma A, generic in B and ℓ),
  and a parameter certificate at ℓ = w (the analogue of `A7Params`).
- It needs no B1′: in M1, B1′ follows from A2 and A3′. So the one proof obligation is **A2**, a combinatorial
  compression lemma already pinned in the trusted layer and parked by workstream 1 as RW–SMS-specific.

**Outside Lean, as the project convention puts it:**
- that SMS with per-block keys (ChaCha8 `K_j, t_j`, which adds about 1.3 to R_seq) instantiates M1;
- SeqRoot: one w-bit root takes longer than Δ + round trip on the fastest core.

**Order of work:**
1. Draft the submission `lean/submissions/efficient-crypto/p2/` (started 05:35Z): a theorem `A2LemmaAM1 → Meets …`
   plus the certificate.
2. Red-team the statement.
3. Ask the root coordinator to pin the P2 target.
4. Prove A2.

**Done at 05:47Z: step 1, with no `sorry`** (`lean/submissions/efficient-crypto/p2/`, `P2Meets.lean` and `NOTES.md`).
- **Headline:** `p2_meets_m1 (hA2 : Pinned.A2LemmaAM1) : ∀ D, Meets (m1 (2^23) 16448) .sequential D (2^20) 88 εMax`,
  i.e. 2,056-byte blocks, 17.2 GB, any depth, k = 88.
- **Second instance:** `p2_meets_m1_8192` at `m1 (2^24) 8192`, k = 90.
- **Only hypothesis:** A2; B1′ isn't needed.
- **Proved in the file:** A2 → Lemma A; A3PrimeLam, reused; a generalized parameter row `P2Row` with domain 2^w (the
  pinned `A7Row` hard-codes 2048 bits); Correct, CodeHoldsW, SpaceBound; and a non-vacuity lemma (k = 85 provably
  fails).
- **Checks:** axioms are Lean's three only, both targets grade PASS against a pin added only in a scratch copy, and
  `lean/pous` is unchanged (TRUSTED.sha256 verifies).
- **To pin:** `P2MeetsM1`, optionally `P2MeetsM1W8192` (root coordinator). The statement carries no timing content; the
  SMS instantiation and SeqRoot stay outside Lean.

**Decisions for Daniel before deployment (not before the statement):**
- whether the novel SMS instantiation heuristic is acceptable in exchange for about 16× faster decode than the band
  (covered per-block-key measurement at 16,448 bits; the 14–26× range was M2);
- whether an adversary may cooperate across cores on one squaring, which sets w at 16,448 or about 32,768.
