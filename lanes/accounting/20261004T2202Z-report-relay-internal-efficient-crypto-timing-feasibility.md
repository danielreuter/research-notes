---
id: 20261004T2202Z-report-relay-internal-efficient-crypto-timing-feasibility
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/efficient-crypto/timing-feasibility.md
role: analyst-timing-feasibility
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/efficient-crypto/timing-feasibility.md`, sha256 `6ac0b8eee5ee1dee3323cc653ded44cd64e98022f6575b8dca4edbcb239db534`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Timing feasibility: 2× at decode batch under Daniel's timing facts, and what they mean for P3

**Verdict.** 2× at decode batch is not reachable by any known sound DRG design under Daniel's timing facts.

- **Best sound design at Daniel's point.** At Daniel's single point (one CPU core, 58 ns per light hash, Δ = 300 µs strict, so D = 5,172 light-hash rounds), the cheapest known sound design is the shipping drU stack (4,6,4) moved to **128 KB blocks**.
  - Margin: 1.20× over D.
  - Cost: *est.* 3.85–4.20× memcpy standalone, R_e2e 5.0–5.4 on the fused harness at B = 8, **R_seq 7.2–7.8**.
  - With about 2× margin the cheapest is (5,6,4) at 128 KB: margin 1.87×, *est.* R_seq 8.5–9.2.
  - Nothing at 64 KB passes except DSaG-5 and DSaG-6, at *est.* R_seq ≥ 10.
- **What 2× requires.** R_seq ≤ 2 leaves the whole decoder about **1.0 ns·SM per 32 B node** by the measured drU fused slope, or 2.1 ns·SM optimistically.
  - At the l = 4 that D forces at ≤ 128 KB, that is **0.26 (at best 0.53) ns·SM per layer**: 14% (28%) of a shipping layer.
  - In the brief's units, that is about 2.4 (3.8) of I-per-parent, e.g. d = 1 with r ≈ 1.3.
  - No allowed lever or combination gets there. The only combination that does, a register window plus a hash-free key, is ruled out by the reverse move.
  - The brief's "2× ≈ 1.2–1.3× memcpy" holds only for the harness end-to-end (e2e) ratio. In R_seq, the Goal's metric, the 2× line is 0.75–0.92× memcpy, below the l = 1 floor.
- **P3.** One P3.1 level at n = 220, m = 8192 is about 16 sequential 1 KB permutation calls. Each call is *est.* 1.3–2.5× a light hash, so a level takes *est.* 1.2–2.3 µs on a CPU core.
  - At 300 µs, D is 2,055–4,110 oracle rounds, which buys the adversary 128–257 levels against a certified 10: **P3 as specified survives no point**. At the most lenient point it is still short by 4–9×.
  - At 1 KB labels no degree gives 2× margin, because m ≥ 30n caps n at 273. Wider labels are the only workable lever, which confirms workstream 1's 64 KB re-parameterization (`p3-scheme.md` §2c).

Conventions:
- *est.* marks arithmetic on measured constants or on unmeasured kernels. *(unverified)* marks claims taken on trust.
- All depth numbers are attacks from the depth game (pebbling model, whole-word storage, unbounded parallelism), never lower bounds.
- Gates follow the 5.26% deficit with a δ = 1% audit at k = 1024:
  - m = 8 tolerated misses: q ≥ 1.69%, so the attacker may save at most 3.57%.
  - m = 0, strict: q ≥ 0.45%, so it may save at most 4.81%.
  - "Margin" is D_gate / D.
- Scripts and logs are in `timing-feasibility/` (§ Files).

## Q1. Operating points

D = Δ / t_min, where t_min is one light hash: a 4-DR injection-ARX step on 32 B with 6 parents (brief UPDATE 15:00Z; `prior-gpu-notes.md` §4). Daniel's 15:10Z decision fixes the first row and supersedes the others; I keep them as sensitivity rows.

| point | t_min | Δ | policy (gate) | D (light-hash rounds) | brief's figure |
|---|---|---|---|---|---|
| **Daniel 15:10Z (binding)** | 58 ns, one Xeon core | 300 µs | strict, m = 0 (≤ 4.81%) | **5,172** | "≈ 5,200" ✓ |
| lenient | 58 ns | 100 µs | m = 8 tolerated (≤ 3.57%) | 1,724 | "≈ 1,700" ✓ |
| ASIC 10 ns | 10 ns *est.* | 100 / 300 µs | tolerated / strict | 10,000 / 30,000 | |
| ASIC 5 ns | 5 ns *est.* | 100 / 300 µs | tolerated / strict | 20,000 / **60,000** | "≈ 60,000" ✓ |
| ASIC 2.5 ns | 2–4 ns (S2/S3 review, CATALOG §3.7) | 100 / 300 µs | | 40,000 / 120,000 | |

With r = 3 the light hash is 45 ns, so every D grows 1.29× (5,172 → 6,667 at Daniel's point). Fewer rounds therefore also cost depth, not only security.

## Q2. Cheapest known sound design

**Attack depths.** A new checkpoint-attack solver (`ckpt_profile.py`, niced, one core, 25 s in total) computes, for one drU d = 6 layer at 64 KB–2 MB, the smallest depth δ(m) that each known removal family reaches: greedy, periodic and iterated Valiant. It then optimizes the split Σ m_j ≤ (1 − ε)n over layers by dynamic programming (the additive depth profile).
- **Validation.** At 64 KB it gives DSaG-4 3,886 at 3.57% and 3,961 at 4.81%. This is 5–7% *below* the prior 4,083–4,280 (`dsag_curve.csv`), a slightly stronger attack. At 128 KB it gives 7,224–7,356 against the prior 7,187.
- **Stacks.** For stacks (identity connectors) the prior local-cascade envelopes are lower still and are used where they exist (64–256 KB). Above 256 KB the checkpoint value is only an upper bound for a stack.
- **Scaling.** D_ckpt/n falls with n, from 1.90 to 1.29 for l = 4 between 64 KB and 2 MB (`ckpt_small.log`, `ckpt_large.log`).
- **Prior artifacts.** The prior "butterfly" DSaG thresholds at 128 and 256 KB (5,190 and 9,648) are interpolation artifacts: linear from a zero point on a doubling grid. Cite 7,187–7,356 and 13,764–14,054 instead.

**Costs.**
- Standalone x = t_node/2.81, with t_node from CATALOG §3.1 (64 KB constants).
- Fused R_e2e(B = 8) = 0.591 + 1.140·x, a least-squares fit to the 8 measured fused points (CATALOG §3.2, within 0.08).
- R_seq = (8.83·R_e2e − 3.17)/5.66. The harness step is 5.66 ms of matmuls plus 3.2 ms of unencoded rest (`trusted4/region.md` §3.1). This gives 6.49 for the shipping point, against region.md's own 6.08–6.43.
- At 128 KB the decoder time is ×1.10–1.20 *est.*: 1 CTA/SM (CATALOG §6 item 2). KV pages measured +19% at 128 KB (CATALOG §3.3).
- Connectors cost +0.5 layer each *est.* (CATALOG §6 item 1b; kernel unbuilt).

Candidates at Daniel's point (strict gate 4.81%, D = 5,172 at r = 4):

| design | block | D_gate | margin | x memcpy | R_e2e B = 8 | R_seq | kernel |
|---|---|---|---|---|---|---|---|
| stack (4,6,4), shipping | 64 KB | 2,232 | 0.43 ✗ | 3.42 measured | 4.52 measured | 6.49 | exists |
| stack (5,6,4) | 64 KB | 4,702 | 0.91 ✗ | 4.16 | 5.33 | 7.76 | exists |
| DSaG-4 (4,6,4) | 64 KB | 3,961 | 0.77 ✗ | 4.49 *est.* | 5.71 *est.* | 8.35 *est.* | connectors unbuilt |
| DSaG-5 (5,6,4) | 64 KB | 5,942 | 1.15 | 5.49 *est.* | 6.85 *est.* | 10.1 *est.* | connectors unbuilt |
| stack (4,6,3) | 128 KB | 6,186 | 0.93 ✗ (D = 6,667 at r = 3) | 3.50–3.82 *est.* | 4.6–4.9 *est.* | 6.6–7.2 *est.* | 128 KB unbuilt |
| **stack (4,6,4)** | **128 KB** | **6,186** | **1.20** | **3.85–4.20 *est.*** | **5.0–5.4 *est.*** | **7.2–7.8 *est.*** | 1 CTA/SM 128 KB unbuilt |
| DSaG-4 (4,6,4) | 128 KB | 7,356 | 1.42 | 4.94–5.39 *est.* | 6.2–6.7 *est.* | 9.2–10.0 *est.* | both unbuilt |
| stack (5,6,4) | 128 KB | 9,647 | 1.87 | 4.58–4.99 *est.* | 5.8–6.3 *est.* | 8.5–9.2 *est.* | 128 KB unbuilt |
| DSaG-5 (5,6,4) | 128 KB | 11,116 | 2.15 | *est.* | 7.5–8.1 *est.* | 11.1–12.1 *est.* | both unbuilt |
| stack (4,6,4) | 256 KB | 9,909 | 1.92 | unpriced | | | exceeds the 228 KB SMEM: DSMEM or L2 |
| DSaG-3 (3,6,4) | 256 KB | 6,626 | 1.28 | unpriced | | | same |

The margins reproduce Daniel's calibration: D* × 58 ns = 130 µs, 367 µs and 598 µs for the (4,6,4) stack at 64, 128 and 256 KB, and 274 µs for (5,6,4) at 64 KB.

Blocks above 228 KB cannot live in one SM. An L2-resident decode moves at least 32 B/B at l = 4 (6 parents plus the lower word plus the write, per layer), which is *est.* ≥ 7× memcpy-time on traffic alone at 5.5–7 TB/s L2 *(unverified)*. That is worse than the SMEM kernel's 3.4×. DSMEM gathers are latency-bound and unmeasured.

Sensitivity at the superseded points (`costs.log` §5b; r = 4; priced only when SMEM-resident). At the lenient point:
- margin ≥ 1: the shipping (4,6,4) 64 KB, 1.14×, R_seq 6.5;
- margin ≥ 2: (4,6,4) 128 KB, 3.3×, R_seq 7.2–7.8 *est.*

On an ASIC, nothing at ≤ 128 KB passes except DSaG-5 128 KB at the 10 ns tolerated point (1.11×, R_seq 11–12 *est.*). The brief's strict point (D = 60,000) needs DSaG-5 at 1 MB for margin 1.24×, or 2 MB for 2.3×. Those are cluster or L2 kernels and unpriced; the stacks are unknown above 256 KB.

Narrow-state compression check (brief 15:10Z): passes for every row above.
- Each key is the full 32 B Davies–Meyer output of a state at least that wide, and absorbs whole parent words.
- The 128-bit replica key is public.
- The standing caveat is unchanged: 32 B labels leave the depth results in the pebbling model (Pietrzak's bridge is vacuous, brief 15:00Z).

## Q3. What 2× requires

**The claim "2× ≈ decode at 1.2–1.3× memcpy" holds only for the harness e2e ratio** (the whole step at ctx 512, 36% of it unencoded):
- Fit: R_e2e = 2 at x = 1.24. It sits between (2,6,3) at 1.42–1.53× (2.16–2.34× fused) and the l = 1 floor at 1.20× (R_e2e 1.96).
- R_e2e = 2 corresponds to R_seq = 2.56.
- Under the Goal's metric (R_seq ≤ 2 over the matmul sequence) the line is at **x ≤ 0.75–0.92**, depending on the mapping (e2e fit, region model standalone, or K2's fused floor of 0.52 TB/s).
- On that line, (2,6,3) is R_seq 2.81–3.09 and the l = 1 floor is R_seq 2.50 at 64 KB and 2.18 at 32 KB.

**The brief's 15:20Z comparison mixes the two ratios.** It says "the real drU kernel ran about 15% above this idealized chain (4.52× against 3.85×)", but 4.52× is R_e2e. The real (4,6,4) kernel's R_seq is 6.1–6.5 (region.md §3.1), which is **60–70% above** the idealized 30 ARX/B chain, not 15%. The gap is the parent gathers (58% of a layer). Any gather-heavy candidate priced from `arx_rseq.csv` alone is therefore about 1.6× too cheap.

Budget and levers:
- Per-node cost is Σ_j c_j, with c = S + I·d + F·r ns·SM per layer (S = −0.22, I = 0.20, F = 0.221).
- R_seq is priced two ways: by the measured drU fused slope (R_seq = 1.28 + 0.702·Σc, from the three drU 64 KB fused points), and by the optimistic region model with the decoder intercept hidden (0.745 + 0.592·Σc).
- l = 4 is the minimum at ≤ 128 KB for D = 5,172. l = 3 needs 256 KB (DSaG-3, 1.28×), and l = 2 fails at every size up to 2 MB (D_ckpt ≤ 2,463).

| row | c per layer | Σc at l = 4 | R_seq, drU slope | R_seq, optimistic | effect on D / D* | status |
|---|---|---|---|---|---|---|
| **2× requires** | **≤ 0.26 (≤ 0.53 optimistic)** | ≤ 1.03 (≤ 2.12) | 2.0 | 2.0 | | about 1 parent + 1.3 DR per layer |
| shipping (4,6,4) | 1.864 | 7.46 | 6.51 | 5.16 | baseline | |
| r = 3 | 1.643 | 6.57 | 5.89 | 4.63 | D ×1.29 (45 ns) | 3-DR related-parent distinguisher (CATALOG §3.7) |
| r = 2 | 1.422 | 5.69 | 5.27 | 4.11 | D ×1.8 | broken at 2 DR: ruled out |
| d = 5 | 1.664 | 6.66 | 5.95 | 4.68 | timed envelope unmeasured | W = n leak 0.4% (CATALOG §3.7) |
| register window winW64L2u (I / 2.25) | 1.197 | 4.79 | 4.64 *est.* | 3.58 *est.* | timed envelope unmeasured | kernel unbuilt; bidirectional leak 0 / 0.44% at l = 4 (CATALOG §3.7) |
| hash-free key (F·r → ~0.1) | 1.080 | 4.32 | 4.31 | 3.30 | t_min falls to an XOR tree, D ×~20 *est.* | **ruled out**: reverse move, 12–28% leak |
| DSaG-4 connectors | 2.563 *est.* | 10.25 | 8.47 | 6.81 | D* ×1.9 at 64 KB | kernel unbuilt |
| more degree instead of layers | | | | | | ruled out: (3,12,4) > (4,6,4) (CATALOG §3.9 #8) |
| winW + r = 3 | 0.976 | 3.91 | 4.02 *est.* | 3.06 *est.* | D ×1.29 | cheapest unruled combination; unmeasured |
| winW + hash-free key | 0.413 | 1.65 | 2.44 | **1.72** | | the only fit, optimistic only; **ruled out** |
| l = 3 / l = 2 (6,4) layers | 1.864 | 5.59 / 3.73 | 5.20 / 3.89 | 4.05 / 2.95 | need ≥ 256 KB / > 2 MB | not SMEM-resident |

Tile-shared parents (15–30% leak), the tensor-core mixer (2.3× slower) and fusion (9–10%) are settled negatives (CATALOG §3.9) and not re-priced here. Even the cheapest unruled combination at 64 KB, winW with r = 3 (R_seq ≈ 4.0 *est.*), is twice the line, and it does not pass the depth gate at 64 KB.

## Q4. P3, as input for the root coordinator

1 KB permutation P: 8–16 butterfly stages.
- CPU core: about 32 cycles per stage on 16 AVX-512 registers at 3.5 GHz, so 73–146 ns *est.* (`p3-scheme.md` §2b's method).
- ASIC: 2 dependent ops per stage at 0.15 ns, so 2.4–4.8 ns *est.*

A P3.1 level is sequential for the adversary: digest 1, absorb 12 digests at rate 512 B, squeeze 2, then P, for 16 calls. The ideal-model accounting charges 2 calls per level (H, P).

| adversary | t_P vs light hash | calls / level | t_level | Δ | D in oracle rounds (Δ / t_P) | levels d (certified: 10; ≤ 14 for any band at n = 220) | whole-segment re-encode (2 × 220 levels) |
|---|---|---|---|---|---|---|---|
| CPU core | 73–146 ns = 1.3–2.5× | ideal 2 | 0.15–0.29 µs | 300 µs (**Daniel**) | 2,055–4,110 | 1,027–2,055 | 64–128 µs (< Δ: a store-nothing attack) |
| CPU core | | P3.1: 16 | 1.2–2.3 µs | 300 µs (**Daniel**) | 2,055–4,110 | **128–257** ✗ (13–26×) | 0.51–1.03 ms |
| CPU core | | P3.1: 16 | 1.2–2.3 µs | 100 µs | 685–1,370 | 43–86 ✗ (4–9×) | 0.51–1.03 ms |
| ASIC *est.* | 2.4–4.8 ns = 0.24–0.96× | P3.1: 16 | 38–77 ns | 300 / 100 µs | 62,500–125,000 / 20,800–41,700 | 3,900–7,800 / 1,300–2,600 ✗ | 17–34 µs |

The per-level CPU figures agree with `p3-scheme.md` §2b (1.2–2.5 µs), reached independently.

**P3 at n = 220, m = 8192 survives no point.** The width condition m ≥ 30n (w_c > log₂ Q ≈ 30) caps n at 273, so certifiable depth is at most about 12 at any degree.

To re-parameterize, use a self-consistent search (`costs.log` §7): the newest-first sponge makes a level k + 1 sequential calls, so degree slows the adversary too.
- Search at Daniel's point with the band law from §2a/§2b: k − 2 ≥ d, n ≥ max(22d, 2dk/(k − d)), m ≥ 30n. That law is proved only at (220, 12) *est.*
- Cost follows §2c's convention: (k + 1) × ARX/B per call, idealized SASS, before data movement.

| label m | margin 1× | margin 2× |
|---|---|---|
| 1 KB (as specified) | k = 166, n = 264: 2,000 ARX/B | **none** |
| 16 KB | k = 10, n = 176, 2.8 MB segment: 198 ARX/B | k = 14, 4.1 MB: 270 |
| 64 KB (§2c uses k = 12, n = 220: d_phys = 2, margin 5×, 273 ARX/B) | k = 5, n = 66, 4.1 MB: 126 | k = 8, n = 88, 5.5 MB: 189 |
| 128 KB | k = 4, 5.5 MB: 112 | k = 6, 11 MB: 158 |

Reading:
- **Segment depth or degree cannot rescue 1 KB labels.** Only wider labels work, because per-byte cost grows like log m while per-level latency grows like m.
- §2c's 64 KB point is consistent with this. If new band certificates at k = 5–8 were proved, decode would fall *est.* from 273 to 126–189 ARX/B. That is still about 15–22× R_seq at decode batch on `arx_rseq.csv`'s idealized anchors (§2c says 26–50× with data movement), and the segments are 4–14 MB and not SMEM-resident.
- For the root coordinator, the useful parts are the lower-k certificates and t_Π at 64 KB on a Xeon core. Nothing here changes §2c's verdict that P3 is a secure-first point, not a 2× point.

## Flags

1. **Two ratios.** The 2× budget line in the brief (1.2–1.3× memcpy) is R_e2e, and so is the "4.52× vs 3.85×" comparison. The Goal is R_seq. They differ by 1.28× at the line (R_e2e 2 = R_seq 2.56), and by 1.4× at the shipping point (4.52 vs 6.49).
2. **Prior interpolation artifacts.** The prior DSaG thresholds above 64 KB are interpolation artifacts (Q2). The new checkpoint split attack is 5–7% stronger than the prior at 64 KB, and attacks gain with n (D_ckpt/n falls about 0.1 per doubling at l = 4). **The biggest risk** is that the 1.20× margin of the recommended 128 KB design erodes under a better attack. It rests on the prior stack envelope (6,186 at 4.81%); my checkpoint DP gives 7,356 for the same graph.
3. **Unbuilt kernels.** Every 128 KB, connector and ≥ 256 KB cost above is *est.* on unbuilt kernels.

## Requests (the coordinator routes)

- **GPU (H100):**
  - The 1 CTA/SM 128 KB weight decode, (4,6,4) and (5,6,4), standalone and fused at B = 8. This sets the best cost.
  - A DSMEM-cluster decode at 256 KB. This prices every ≥ 2× margin stack.
- **CPU jobs (no GPU):**
  - The timed depth envelope of winW64L2u. It is the only unruled lever, at −29% R_seq *est.*
  - t_Π for 1 KB and 64 KB ARX permutations on one Xeon core.
- **Lean:** nothing pinned is needed for this memo.
- **Decisions for Daniel:**
  1. Is the 2× target R_seq (the Goal) or the harness e2e step (the calibration)? The best design is 7.2–7.8 on the first and 5.0–5.4 on the second, so neither changes the no-go.
  2. Is a 1.2× margin over D enough? The alternative is about 2× at +18% cost: (5,6,4) at 128 KB.
  3. Does a multi-SM DSMEM cluster count as one responder? This matters for ≥ 256 KB blocks here and for P3 §2c.

## Files

In `$S/internal/efficient-crypto/timing-feasibility/`:
- `envelopes.py` and `envelopes.log`: operating points, audit gates, and prior envelope thresholds.
- `ckpt_profile.py`: the checkpoint-attack dynamic program.
  - Logs: `ckpt_small.log` (64–256 KB) and `ckpt_large.log` (512 KB–2 MB).
  - Data: `ckpt_2048_4096_8192.csv`, `ckpt_16384_32768_65528.csv`, `profile_2048_4096_8192.csv` and `profile_16384_32768_65528.csv`.
- `costs.py` and `costs.log`: cost fits, budgets, levers, block tables, cheapest-per-point designs, and P3.
