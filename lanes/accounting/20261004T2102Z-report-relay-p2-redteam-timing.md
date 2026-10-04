---
id: 20261004T2102Z-report-relay-p2-redteam-timing
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for memory-accounting's 20:33Z request from store:pous/internal/efficient-crypto/attacks/p2-redteam-timing.md
role: redteam-p2-timing
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/efficient-crypto/attacks/p2-redteam-timing.md`, sha256 `6772dbbeb9087e6b43bbd64f211197c65c273fa1fd314b42f0f20410109602f7`, unchanged since it was written, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P2 red-team: timing margins under the settled timing model

28 Sep 2026. Red-team `redteam-p2-timing`, workstream 2. Scripts and logs are in `p2-redteam-timing/`: `regate.py`,
`decode.py`, `seqroot.py`, `find_primes.py`, plus a `.log` for each, `breakeven.log` and `coop.log`. All are models over the
measured anchor; this VM ran no new benchmarks.

**Verdict: NOT WORTH IT.** P2-5504 is **unsound** under the settled model: the one-root floor is 396 µs, which is 0.79×
of 0.5 ms. Re-gated to w = 16,448, P2 holds a 2× margin at the floor up to the band's 2.9 ms budget. There it decodes at
≈ 258 int32/B (R_seq ≈ 41×, ≈ 62–70 GB/s on an L40S, **≈ 41–46× the band's 1,532 MB/s**). That sits inside P3-ARX's
160–312 int32/B (26–50×), so P2 is no cheaper than the heuristic reference it had to beat. P2 is materially cheaper than
P3-ARX only if the round trip is measured at ≲ 0.4 ms. It never beats P3-ARX's optimistic end by 1.5×.

| # | Question | Finding | Effect | Verdict |
|---|---|---|---|---|
| 1 | Re-gate | The floor for one w-bit root is Zen 5 IFMA at 5.7 GHz with the best Toom/Karatsuba plan, including overheads; mulx is 2.8× slower. At 5504 bits the floor is **396 µs**, tier E 528 µs, and the measured kernel scaled to 5.7 GHz 1,336 µs. The smallest w at the floor: 6,096 / 8,000 (1× / 2×) at RTT 0, **9,440 / 12,592** at RTT 1 ms, **12,336 / 16,448** at RTT 2.4 ms | P2-5504 fails at zero round trip: 0.79× at the floor (the coordinator's 0.99× used the scout's 493 µs). At the 2.9 ms budget it fails by 2.2× (measured kernel) to 7.3× (floor). The coordinator's reading stands, slightly generous to P2 | 5504: UNSOUND. Re-gated w: table §1 |
| 2 | Decode cost | 16/w squarings per byte. X = 2cw/128 + 1.25 int32/B: 126 / 198 / 258 at w = 8,000 / 12,592 / 16,448 (c = 1). R_seq 20.7 / 32 / 41.5. L40S 115–127 / 79–88 / 62–70 GB/s | 41–83× the band's throughput, but 0.4–0.8 / 0.6–1.2 / **0.8–1.6×** P3-ARX's cost | Cheaper than P3-ARX only at RTT ≲ 0.4 ms |
| 3 | SeqRoot | No shortcut inside the model. The generic depth is ≥ w − 3. SNFS precomputation costs 2^164–2^220 (> 2^128) at w ≥ 8,000. Smoothness root-finding succeeds with probability ≤ 2^−2700. Tables in the 1/19 slack are the same attack. Outside the model, **4–8 cooperating cores give 2.3–4.1×** at w = 12–16 kbit, and one GPU SM is within 1.2× of the CPU floor | Sound as a named hypothesis only if "one core" is strict. The multi-core gain grows with w; hash chains have no such gain | Holds in the model; fragile at the model's edge |
| 4 | One-root gate | Skipping both roots needs ≥ w/2 known bits of r **and** ≥ w/2 of c (Coppersmith, degree 2; 4w/3 at dimension 3). The c-lattice needs σ(r) exactly, so the hints do not share bits. Partial-exponent hints cost more; guessing saves ~13 bits | No saving from skipping both. Only the first root is skippable (the zero-root route through a dense mask stays H2) | Confirmed: one root gates |
| 5 | Verdict | See the verdict line | | **NOT WORTH IT** (vs P3-ARX) |

## 1. Re-gate (Q1)

**Model** (`regate.py`). One root is (w − 2) squarings plus about 20 multiplications, counted as 40 squaring-equivalents.

- **Floor F: the fastest shipping core.** A Zen 5 desktop core at 5.7 GHz with the full 512-bit datapath.
  - Assumed ≤ 2 zmm IFMA per cycle and ≤ 4 vector ops per cycle, at 100% issue efficiency. This Xeon measures
    2.0 IFMA per cycle; the throttled Zen 5 pod measured 1.3–1.5 but confirmed the 4-cycle latency. The 2-per-cycle,
    5.7 GHz combination is the adversary-favouring pair.
  - Cycles per squaring ≥ max(I/2, (I+O)/4) + 25, where I counts IFMA ops and O the other vector ops.
  - The recursion plan is the best of up to 5 levels of {Karatsuba, Toom-3, Toom-4} over a symmetric schoolbook base.
  - Each node carries a linear overhead O: re-normalizing sub-operands to 52 bits (IFMA reads only 52 bits per lane),
    Toom evaluation and interpolation, and exact divisions. The overheads are 1.06n (Karatsuba), 3.25n (Toom-3) and
    6.1n (Toom-4) vector ops.
  - Top level: the fold by c0 and two carry passes.
- **mulx/adx** (1 full 64×64 product per cycle, 5.7 GHz) is 2.2–3.5× slower at every w, so IFMA sets the floor.
  AMX-int8 needs Toeplitz tiles rebuilt from each new operand (≥ 2n² MACs, ≈ 925 cycles at 5504 bits before tile
  construction), so it does not help. A double-precision FFT or an IFMA NTT loses by 2–3× at w ≤ 16 kbit.
- **Anchor.** The campaign's `ifma_ps2` kernel takes 1,374 cycles per 5504-bit squaring. That is 1.84× the schoolbook
  floor and **3.38× the best-plan floor** (Toom-3 + Karatsuba, 407 cycles). Tier E = F / 0.75. Tier M is the measured
  kernel scaled by schoolbook products at 5.7 GHz; it only bounds the adversary from above.
- **One GPU SM** (the "GPU core" reading, as a sensitivity check): RTX 4090, 64 IMAD per clock, Karatsuba, plus 60
  cycles of intra-SM sync. It lands within 1.0–1.2× of the CPU floor at 5.5–16 kbit, so the CPU still binds, narrowly.

**At w = 5504** (one root; ratio against the 0.5 ms and 2.9 ms budgets):

| Tier | τ per squaring | Root | vs 0.5 ms | vs 2.9 ms |
|---|---|---|---|---|
| F (floor) | 71.4 ns | 396 µs | 0.79× | 0.14× |
| E (optimized) | 95.2 ns | 528 µs | 1.06× | 0.18× |
| M (measured kernel at 5.7 GHz) | 241 ns | 1,336 µs | 2.67× | 0.46× |
| mulx floor | 199 ns | 1,103 µs | 2.21× | 0.38× |
| one SM (4090) | 87 ns | 483 µs | 0.97× | 0.17× |

**Smallest w** (step 16) with the root ≥ margin × budget, where the budget is 0.5 ms plus the round trip (RTT):

| RTT | Budget | Margin | **w at the floor** | w at E | w at M | Prime `2^w − c0` (≡ 3 mod 4) |
|---|---|---|---|---|---|---|
| 0 | 0.5 ms | 1× | 6,096 | 5,472 | 3,968 | `2^6096 − 1425` |
| 0 | 0.5 ms | 2× | **8,000** | 7,088 | 5,008 | `2^8000 − 54645` |
| 1 ms | 1.5 ms | 1× | 9,440 | 8,416 | 5,728 | `2^9440 − 26333` |
| 1 ms | 1.5 ms | 2× | **12,592** | 11,280 | 7,216 | `2^12592 − 10757` |
| 2.4 ms | 2.9 ms | 1× | 12,336 | 11,088 | 7,136 | `2^12336 − 5309` |
| 2.4 ms | 2.9 ms | 2× | **16,448** | 14,624 | 9,008 | `2^16448 − 21065` |

- The primes come from `find_primes.log`: a sieve, then 30 Miller–Rabin rounds. Every c0 is below 2^16, so the fold is
  still one small multiply.
- **Scaling.** The root costs roughly w^2.5 at the floor. A 2× error in the floor therefore moves w by about 1.3×,
  and a future core with 2× the IFMA throughput needs w × 1.3.

**The coordinator's reading, checked.**

- At the floor, P2-5504 fails even at zero RTT. The ratio is 0.79×, not 0.99×: the best plan with Toom-3 at the top
  is 20% below the scout's one-level Karatsuba floor of 493 µs.
- At the 2.9 ms budget it fails by 2.2× (measured kernel) to 7.3× (floor). The coordinator's "2–6×" is correct in
  direction and slightly generous to P2.

## 2. Decode cost at the re-gated w (Q2)

Pricing, in `decode.py`:

- X = 2cw/128 + 1.25 int32/B, with c = 1 for symmetric schoolbook, 1.5 for the sms5 upper end, and 0.6 for an
  optimistic, unmeasured two-level GPU Karatsuba.
- H100 R_seq = 2 + 0.158(X − 8).
- L40S: 142 SMs × 64 IMAD per clock × 2.52 GHz = 22.9 T IMAD/s, at 0.79–0.90 efficiency (CGBN on H100), combined with
  the 0.5B plaintext GEMM at 581 GB/s.

| w | Squarings/B | X at c = 0.6 / 1 / 1.5 | R_seq at c = 1 (range) | L40S GB/s, c = 1 (range over c) | × band | X ÷ P3-ARX (160–312) |
|---|---|---|---|---|---|---|
| 5,504 (unsound) | 0.0029 | 53 / 87 / 130 | 14.5 (9–21) | 153–168 (112–233) | 73–152× | 0.28–0.55 |
| 8,000 (RTT 0, 2×) | 0.0020 | 76 / 126 / 189 | 20.7 (13–31) | 115–127 (82–185) | 54–120× | 0.40–0.79 |
| 12,592 (RTT 1 ms, 2×) | 0.0013 | 119 / 198 / 296 | 32.0 (20–48) | 79–88 (55–133) | 36–87× | 0.63–1.24 |
| **16,448 (RTT 2.4 ms, 2×)** | 0.00097 | 155 / 258 / 387 | **41.5** (25–62) | **62–70** (43–108) | **28–70×** | **0.83–1.62** |

- **Against the band.** P2 is 28–150× the band's measured 1,532 MB/s at every width. The band pays ≈ 1.9 Keccak-f per
  byte, ≈ 6–9k int32/B.
  - This is not a like-for-like comparison: the band rests on SHAKE256 in a label game, while P2 rests on two
    heuristic hypotheses (SMS-IC(Δ) and SeqRoot at an *estimated* CPU floor).
  - The like-for-like reference is P3 on heuristic ARX primitives.
- **Against P3-ARX** (X for c = 1, from `breakeven.log`):
  - P2 is below P3-ARX's optimistic end (160) only for w ≤ 10,160, i.e. RTT ≤ 0.37 ms at a 2× margin.
  - It is below the pessimistic end (312) for RTT ≤ 4.1 ms.
  - It beats the optimistic end by 1.5× (X ≤ 107, w ≤ 6,768) only below 0.33 ms of total budget, which is impossible
    since the server path alone is 0.5 ms.
- **Honest encode** scales as c·w²/64 int32/B: ≈ 4.3M int32/B at 16,448 bits, ≈ 3.3 MB/s per H100. That is about
  1.2 H100-hours per 14 GB model, or 15 per 184 GB (*est.*).

## 3. SeqRoot at the re-gated w (Q3)

- **Generic lower bound.** In the generic group model the exponent of y in any computed element is at most 2^d after
  depth d. The shortest equivalent exponent is min_k |e − k·ord(y)| ≈ p/4 (QR inputs: e mod (p−1)/2 = (p+1)/4). So
  the depth is ≥ w − 3 multiplications at any parallelism, and input-independent preprocessing does not change this.
  Non-generic shortcuts are what SeqRoot assumes away; the three known ones follow.
- **SNFS individual logs for the special p** (`seqroot.log`; complexities with o(1) dropped):
  - The precomputation is L[1/3, 1.526]: 2^140 at 5504 bits, but **2^164, 2^197 and 2^220** at 8,000, 12,592 and 16,448.
    That is above the 2^128 preprocessor, so the route is closed before the descent matters.
  - The descent is 2^132–2^207, against about 2^24–2^36 online operations.
  - Re-gating strengthens this: at 5504 bits the attack was closed only by the descent.
- **Smoothness root-finding (ePrint 2024/873).**
  - The factor base is capped by the slack: 2^28 blocks × w/19 bits divided by w bits per stored root gives ≤ 2^23.8
    roots, so B ≈ 2^27.8.
  - A rational representation has a and b near 2^(w/2), so u = 144–296 and P(both smooth) ≈ 2^−2,700 to 2^−6,300 per
    trial. Dead.
- **Precomputed tables in the 1/19 slack.** Input-independent tables are covered by the generic bound. Tables of roots
  of small primes are the smoothness attack. Per-block hints are Q4.
- **Multi-core cooperative squaring (outside the model).** Each squaring needs at least one all-gather of slices and
  carries. The speedup is τ/(τ/k + t_sync), with t_sync = 20–80 ns on one CCD:

  | w | τ_F | k = 2 | k = 4 | k = 8 |
  |---|---|---|---|---|
  | 5,504 | 71 ns | 0.6–1.3× | 0.7–1.9× | 0.8–2.5× |
  | 12,288 | 221 ns | 1.2–1.7× | 1.6–2.9× (2.3× at 40 ns) | 2.1–4.6× (3.3×) |
  | 16,384 | 344 ns | 1.4–1.8× | 2.1–3.3× (2.7×) | 2.8–5.5× (4.1×) |

  - **The re-gate pushes w exactly where cooperation starts to pay.** At the widths that hold 2× against one core,
    4 cooperating cores take the whole margin. A Keccak-f chain step (band, P3) cannot be split this way.
  - If Daniel ever relaxes "one core" to 4–8 cooperating cores (`coop.log`, t_sync 20–40 ns), 2× at 2.9 ms needs
    w = 26,592–36,512, i.e. X ≈ 417–572. Then P2 loses to P3-ARX outright (above 312). Even at RTT 0 it needs
    w = 11,136–15,968.
- **GPU.** One SM is within 1.0–1.2× of the CPU floor (§1). On an H100, SM clusters with distributed shared memory
  would allow the same kind of cooperative split (*unverified*).

## 4. The one-root gate (Q4)

The adversary wants c without two full roots and with fewer than (18/19)·w stored bits.

- **The hint on r skips root 1** (the scout's attack): (2/3)w bits at dimension 3, ≥ w/2 asymptotically, because the
  relation r² ≡ ±y has degree 2.
- **A hint on c skips root 2 only if s = σ(r) is known exactly**, because the relation c² ≡ ±s has degree 2 in c. It
  needs ≥ w/2 known bits of c asymptotically, and (2/3)w at dimension 3.
- **Skipping both** needs r exactly (from its hint) and then the c-lattice. The hints share no bits, because the
  c-relation's right side is only available once r is known. Storage is ≥ w/2 + w/2 = w asymptotically (4w/3 at
  dimension 3), so there is no saving.
- **The joint lattice** on {x_r, x_c} is not polynomial: σ acts on r's low bits as x_r ⊕ K_lo, and the AND term costs
  2^wt(K_lo) guesses. That is the H2 question, which the coordinator's mask check left sound for a uniform K.
- **Partial-exponent hints.** Store the top bits of v = s^(e_hi), with c = v^(2^j)·s^(e_lo). The relation for v has
  degree 2^(j+1), so it needs (1 − 2^−(j+1))w stored bits, which is worse for every j ≥ 0. The same holds on the r side.
- **Brute-forcing dropped low bits of c.** Each guess checks in 2 squarings, so the saving is ≤ log₂(budget / 2τ)
  ≈ 13 bits per block at 16 kbit and 2.9 ms. That is the completion bound's log₂ Q term, not a gate break.
- **Cross-block relations.** Multiplicative relations among the y_j = m_j + t_j of independent data are the smoothness
  attack (dead), and the shared K adds nothing (the scout's argument).

**Result.** Exactly one root gates each block, and I found no way to skip both.

## 5. Verdict

**NOT WORTH IT.**

- P2-5504 is unsound under the settled timing model.
- P2 becomes sound with parameters only as w grows, resting on SMS-IC(Δ), SeqRoot at a modelled floor, and a strict
  "one core":
  - **w = 16,448, `2^16448 − 21065`** holds 2× at the floor up to the band's 2.9 ms budget. There it
    decodes at ≈ 258 int32/B (155–387), R_seq ≈ 41× on H100, ≈ 62–70 GB/s on an L40S, 41–46× the band.
  - That is 0.8–1.6× of P3-ARX's cost under the same class of heuristic assumption, so P2 is not materially cheaper
    than the reference.
- **Where it would be worth it.** Only if the measured RTT is ≲ 0.4 ms: w ≈ 8,000–10,000 and X ≈ 126–160, 1.3–2.5×
  below P3-ARX. Even then the margin rests on an unbuilt adversary kernel 3.4× faster than ours, and on the model
  excluding 4–8-core cooperation, which would eat that margin.
- **What would change this.**
  - A measured RTT below 0.4 ms.
  - A measured GPU decode at c ≤ 0.6 (Karatsuba), which would put 16,448 bits at X ≈ 155, the low end of P3-ARX.
  - A proof route that makes P2's assumption base materially stronger than P3-ARX's. None is in sight: both are
    heuristic idealizations.
