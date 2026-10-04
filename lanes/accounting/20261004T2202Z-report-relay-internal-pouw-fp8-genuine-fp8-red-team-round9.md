---
id: 20261004T2202Z-report-relay-internal-pouw-fp8-genuine-fp8-red-team-round9
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw-fp8/genuine-fp8-red-team-round9.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw-fp8/genuine-fp8-red-team-round9.md`, sha256 `5ff6e4b988f0c133466343cebb8d2ccaefa252e3a0f3ea628b47f3b16eb9d08f`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Red team Round 9: D-3s and D-3m at Round 9 prices, the Y16 row statistic, and commitment order

Written by the strike worker, 18:33Z to 19:20Z, CPU only. Prices are from `internal/pouw/gpu-constants.md` §14 (run
r20260928-181753-0070). The reference is Track A's bit-exact D-3s in PR #295 (`protocols/pouw/verity_pouw/schemes/fp8_is.py`,
`d3_trace` and `D3Family`). Scripts sit beside this file:
- `red-team-round9-gamma.py` and `.json`: prices and γ;
- `red-team-round9-order.py` and `.json`: the bit-exact item-3 check on PR #295's own `D3Family`;
- `red-team-round9-shapes.py` and `.json`: D-4, the shape condition and real layers ("D-4 and serving shapes");
- `red-team-round9-readings.py`, `-f16-codes.py`, `-f16-witness.py` and `-sass-probe.py`, each with its `.json`: Track A's
  Round 9 claims;
- `red-team-round9-decoded.py` and `.json`: the decoded-weight grid ("Decoded-weight cells (Daniel 20:31Z)").
- `red-team-round9-frontier.py` (`--sass`, `--md`) and `.json`: the frontier cells at Round 11's `round11` (D-3 and
  H-1T, γ at each design's FADD), real time against plain FP8, the m × n grid, the sensitivities, the weight-side
  cache note, the credit correction, A6's hashed rows at Round 11's h and B's combined variant re-priced ("Frontier
  restatement (Daniel 20:41Z)"), and F₁ keyed per call against per strip ("Sampled proofs: the per-strip weight-noise
  caveat");
- `red-team-round9-pair.py` and `.json`: the structural-pair check at A = 0 for the D-3 designs, with H-1T and posted H-1
  as controls (G.7).

## Verdict

1. **Nothing in Track A's specification clears at Round 9 prices, at any FADD price.**
   - Track A's schedule M4 (f32 block values, one rounding) costs 600 per activation element and 470 per weight element on
     Y16 with the copy. At 16,384³ with r = 1 that gives γ = 1.32–1.42% at FADD 32.00. Every cell's FADD threshold is
     31.73–31.79, below the H32 floor of 32.
   - **Correction (19:55Z):** this M4 omits the widen of h: 64 per activation element, and 64 per weight element when
     decoded. #295's M4 charges it and is 0.06–0.13 points higher (D.1 under "D-4 and serving shapes").
   - The cause is HADD2.F32. Round 9 found no two-source form: a sum of two f16 values in f32 is a convert (64) plus an
     FADD, 96 per block value at FADD 32 against the 36 assumed. That adds 180 units per side.
   - **Only a different schedule clears (M2q).** It needs a spec change to f16 block values, which is Track B's measured
     schedule, plus the four-code f16x2 → e4m3 cast at 48 per code, which is unmeasured. With both, 7 of the 8 cells
     clear at FADD 32.00. D-3s on Y16 with the copy is best: 0.918%, with a FADD threshold of 32.053.
   - **At the measured 32.11 nothing clears in any schedule.** The best cell is 1.087%.
2. **FADD: 32.11 is reproducible, but it is not shown to be the class floor.**
   - Rounds 8 and 9 agree to four digits. The best one-source pair in the same framework sits at 32.04.
   - About 0.04 is plausibly framework overhead common to every issue-bound loop, and about 0.07 is specific to
     two-source FADD. Neither is separated.
   - The decision is sharp: even under M2q, D-3s Y16 clears only if FADD is at most 32.053 with the copy (32.022
     decoded).
   - §2 proposes a probe; I did not run it.
3. **The additive-W1 reading is right.** The honest step's 57.0–69.9 per add word is time, not a class price. γ uses class
   prices, and the measured step runs below its W1 charge (57.01 against 32 + 32.11 = 64.11), so `AdmitsRef` holds on the
   main chain. The real-time honest overhead is **5.4×** against a plain FP8 GEMM at the best measured shape, and 5.5–6.6×
   at the others. The floor is 3.04× and the best shape at full dispatch would be 3.39×. Getting to 5× needs the tensor
   core to keep at least 60.5% of its rate (56.1% measured), and 4× needs at least 75.8%.
4. **Item 2: Track A is right.** The statistic has to be a function of committed data. 17f's 390 computes it on the
   model's f32 A/s, which nobody commits, so the verifier cannot check rms′.
   - Committing the f32 statistic too is possible, but it needs a verifier interval rule and leaves 2–3 bits of prover
     choice in rms′.
   - It saves 2.46 units per element at Round 9 (4.27 at Round 8), which is 0.0025 γ points (0.0043). Not worth it.
5. **Item 3: the proposed ruling is unsound for PR #295 as written.**
   - #295's weight stream F₁ = SHAKE256(tag/F1, salt, index, weight, j) does not read root_A. Under #218's order the salt
     comes before the activations, so B̃ is known before A_u and the program are fixed. That is X-D3-3's premise, now at r = 1.
   - Bit-exact on #295's own code, blocks 1 and 2 of each spike slice have at most 3 functions of E₁ across 64 identical
     columns (§5.2), for **ε ≈ 6.8% at the column limit**. #295's witnesses vary the whole salt with A fixed, so they
     don't cover this case.
   - **The fix is F₁ = SHAKE256(tag/F1, salt, index, root_A, weight, j).** It costs nothing in W1, because r = 1 already
     forms the weight side per unit. With it, the same witness gives 64 distinct functions.
   - #218's lifecycle order needs no change, and the int8 `ncp-v1` is unaffected by this mechanism.
   - §0 should say: a unit's activations are committed before *any* of that unit's noise is derived, on either side.

## 1. γ at Round 9 prices (16,384³, r = 1, additive W1)

**Check.** `red-team-round9-gamma.py` first runs PR #295's own `d3_trace` at `PRICES["round8"]`. It reproduces Track A:
- D-3s: 0.9398% with the copy and 0.9718% decoded, FADD thresholds 32.0392 and 32.0184;
- D-3m: 0.9718% and 1.0038%.

The budget for f_a + f_b is 744.48 at FADD 32.00, 683.08 at 32.04 and 575.63 at 32.11 (15.35 units per 0.01).

### 1.1 What Round 9 changes, per element

| Item | Round 8 (Track A) | Round 9 | Where it enters |
|---|---:|---:|---|
| Block value f32(h + n) | 36 (a two-source HADD2.F32, assumed) | **64 + FADD** (the convert, then FADD) | 3 per side |
| Partner max, floor max (HMNMX2) | 18 | **32** | 2 per activation element |
| X_q unpack, weight decode | 32 | **48** (a four-code register) | 1 |
| Prescale h·2⁻⁸ (HMUL2 a·K) | 18 | 16.085 | 1 |
| Sum-of-squares widen, per 256 | (36 + 32)/256 | (64 + FADD)/256 | 1 |
| f16 pack (Y16), LOP3 on f16x2, two-source half2 | 32, 32, 18 | 32, 32, 18 (unchanged) | |
| Centre HFMA2 with two immediates | 18 | 18, **unmeasured** (31.8 if it prices like HADD2 a+K) | 1 per side |
| e4m3 cast from an f32 pair | 32 per code | 32 (**unmeasured** into a four-code register) | 3 per side |
| e4m3 cast from f16x2 | 64 per code (with a PRMT per F2FP) | 64; **48 unmeasured** into a four-code register | M2 only |

LOP3 stays at 64 per instruction. Its 32.04 is reached only 1:1 beside a VIADD or IMAD on another pipe. Under additive
W1 that is a time effect of co-issue, the same reading as for the honest step, not a class price. It appears only as a
sensitivity (§1.3).

### 1.2 The table

Schedules, per side:
- **M4** is Track A's specification. s = HADD2(e, e∘P), three block values f32(h + n) (a convert + FADD each), three
  f32-pair casts.
- **M4s** forms s in f32 from cvt(e). This is a law change, since s is no longer rounded to f16.
- **M2** keeps the block values in f16, with v3 = −(v1 + e∘P), and uses the measured f16x2 + PRMT cast. This is a spec
  change.
- **M2q** is M2 with the four-code f16x2 cast at 48 per code (unmeasured).

Every schedule assumes, as Track A's trace does, that e∘P is available in registers without a gather. A threshold below
32 cannot clear under H32.

| Cell | M4 f_a / f_b | M4 @32.00 | M4 @32.11 | M4 threshold | M4s @32.00 | M2 @32.00 | M2 threshold | M2q f_a / f_b | M2q @32.00 | M2q @32.04 | M2q @32.11 | **M2q threshold** |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| D-3s, Y16, copy | 600.5 / 470 | 1.325% | 1.493% | 31.789 | 1.225% | 1.014% | 31.991 | 396.5 / 266 | **0.918%** | **0.979%** | 1.087% | **32.053** |
| D-3s, Y16, decoded | 600.5 / 518 | 1.373% | 1.540% | 31.757 | 1.273% | 1.062% | 31.960 | 396.5 / 314 | **0.966%** | 1.027% | 1.135% | 32.022 |
| D-3s, X_q, copy | 616.5 / 470 | 1.341% | 1.509% | 31.778 | 1.241% | 1.030% | 31.981 | 412.5 / 266 | **0.934%** | **0.995%** | 1.103% | 32.043 |
| D-3s, X_q, decoded | 616.5 / 518 | 1.388% | 1.556% | 31.747 | 1.289% | 1.078% | 31.949 | 412.5 / 314 | **0.982%** | 1.043% | 1.151% | 32.012 |
| D-3m, Y16, copy | 632.5 / 470 | 1.357% | 1.525% | 31.768 | 1.257% | 1.046% | 31.970 | 428.5 / 266 | **0.950%** | 1.011% | 1.119% | 32.033 |
| D-3m, Y16, decoded | 632.5 / 518 | 1.404% | 1.572% | 31.737 | 1.305% | 1.094% | 31.939 | 428.5 / 314 | **0.998%** | 1.059% | 1.167% | 32.001 |
| D-3m, X_q, copy | 648.5 / 470 | 1.373% | 1.540% | 31.757 | 1.273% | 1.062% | 31.960 | 444.5 / 266 | **0.966%** | 1.027% | 1.135% | 32.022 |
| D-3m, X_q, decoded | 648.5 / 518 | 1.420% | 1.588% | 31.726 | 1.321% | 1.110% | 31.928 | 444.5 / 314 | 1.014% | 1.075% | 1.183% | 31.991 |

Thresholds count each cell's own forming FADDs: three per side in M4, four in M4s, and 1/256 in the sum of squares.

**Per side, D-3s on Y16 with the copy at FADD 32:**
- Activation pre-items, 130.46 in total:
  - pack 32;
  - prescale 16.085;
  - sum of squares 18.375;
  - two HMNMX2 at 32 each.
- Noise: 86 in M4 (u 32, centre 18, scale 18, s 18). M2 drops s, leaving 68.
- Blocks:
  - M4: 3 × (64 + 32) + 3 × 32 = 384;
  - M2: 3 × 18 + 3 × 64 = 246;
  - M2q: 3 × 18 + 3 × 48 = 198.
- X_q adds 16 (unpack 48 against the pack's 32). D-3m adds 32 (the cell-mask LOP3). Decoding the weights adds 48.

### 1.3 Sensitivities (D-3s, Y16, copy, unless noted)

| Change | M4 @32.00 | M2 @32.00 | M2q @32.00 | M2q threshold |
|---|---:|---:|---:|---:|
| as priced | 1.325% | 1.014% | 0.918% | 32.053 |
| centre HFMA2 with immediates at 31.8 (as HADD2 a+K) | 1.352% | 1.042% | 0.946% | 32.035 |
| LOP3 at 16.02 (the 1:1 pair price; not W1) | 1.293% | 0.982% | 0.886% | 32.074 |
| f32-pair cast at 48 per code into a four-code register (A) | 1.420% | n/a | n/a | |
| M2q with block 3 through s, Q(−(h + s)), as Track A's law has it | | | 0.954% | 32.030 |
| X_q decoded with the unpack at 32 (not reachable for four-code registers) | 1.357% | 1.046% | 0.950% | 32.033 |

### 1.4 What clearing would take

All of the following are needed:
1. **A spec change to f16 block values** (Q(f16(h + e)), and so on). PR #295's `side()`, its vectors and the D-3s
   witnesses would have to be re-run, because the double rounding (to f16, then e4m3) moves e4m3 ties.
2. **The four-code f16x2 → e4m3 cast measured at 48 per code** (F2FP, F2FP, PRMT, as the unpack's four-code row is).
   At Round 8's measured 64, M2 fails in every cell.
3. **A FADD class price of at most:**
   - D-3s: 32.053 (Y16, copy), 32.043 (X_q, copy), 32.022 (Y16, decoded), 32.012 (X_q, decoded);
   - D-3m: 32.033, 32.022 and 32.001 (Y16 copy, X_q copy, Y16 decoded). D-3m on X_q decoded never clears.
4. **The centre HFMA2 with immediates at the two-source price (18).** At 31.8, D-3s Y16 copy clears only to FADD 32.035.

## 2. FADD: is 32.11 real or measurement bias?

**What is known (§13, §14.3):**
- Two-source FADD is 32.30 measured and 32.11 loop-free, identical in Rounds 8 and 9. So it is not noise.
- In the same framework and run:
  - VIADD+LOP3 and IMAD+LOP3 pairs, one register source and one immediate each, reach 32.04 loop-free;
  - HMUL2 a·K (split) reaches 32.17;
  - two-source HADD2 is capped at 36.01 (113.75 of 128 issued), which §13.3 attributes to two register sources.
- `wgmma` runs at exactly 32.00 per accumulator register. But it issues one instruction per many clocks, so it says
  nothing about the dispatch path.

**Reading.** FADD issues 127.56 of the 128 instructions per SM per clock that dispatch allows. The gap splits roughly
in two:
- **About 0.04 appears in every issue-bound loop measured**, including the best one-source integer pair. Candidates are
  the loop-free fit's residual, the loop branch and i-cache refetch at the loop wrap, ptxas's scheduling control codes
  (stall counts or yield hints), and tail imbalance across warps.
- **About 0.07 is specific to two-source FADD.** Candidates are register-bank conflicts, which depend on the allocation,
  or a small operand-collector cap.

So 32.11 is what a ptxas-compiled two-source FADD stream achieves. It is not shown to be the FADD class's floor, and
it is not shown to be bias either. Under additive W1 the class price is the loop-free measurement, so 32.11 stands until
a probe moves it.

**The probe (not run).** It fits in the existing `r8`/`r9` framework: one pod launch, same cap as Round 9. Report every
row loop-free and per register.
1. **Unroll sweep.** Two-source FADD at U = 32, 64, 128, 256, 512 and 1,024, with 4, 8 and 16 chains, at full and half
   occupancy. Fit p(U) = p∞ + c/U. If p∞ = 32.00 ± 0.01, the 0.11 is loop overhead that the loop-free correction misses.
2. **A source-count ladder, same loop shape.**
   - One source: FADD a+K and FMUL a·K. ptxas does not fold floating-point chains without fast-math; check it in SASS.
   - Two sources: FADD a+b, and FFMA a·K + b.
   - Three sources: FFMA a·b + c.

   If the one-source forms sit at 32.04 and the two-source forms at 32.11, the 0.07 is a register-read effect.
3. **Register banks and reuse.** Dump the SASS register numbers and reuse flags of the FADD stream, and count same-bank
   source pairs. Build variants with no same-bank pairs and with all same-bank pairs (by permuting chain registers, or
   with a SASS assembler). If the price follows the fraction of same-bank pairs, the 0.07 is real but depends on the
   allocation. An honest kernel can then aim for the good allocation, and W_ref could be priced there only if that
   allocation is shown in the honest kernel's own SASS.
4. **Control codes.** Decode the stall and yield fields of the FADD loop and the VIADD+LOP3 loop (for example with
   `nvdisasm --print-raw` or CuAssembler). A yield hint or a stall of 2 every N instructions would explain a fixed
   fraction such as 0.04.
5. **A cross-pipe pair.** FADD (two sources) 1:1 with IMAD. If the pair reaches 32.04 per instruction, the FADD excess
   lies in the FP32 pipe's operand reads; if it stays at 32.11, the excess lies in dispatch.
6. **FADD in the honest pattern.** The running-sum adds on `wgmma`'s own accumulator register allocation, with `wgmma`
   disabled. That is the price the honest reference pays.
7. **Run length and references.** TARGET_MS = 200 and 400, with `wgmma` and the integer pair as same-run references, to
   rule out tail effects.
8. **The same launch should also price the unmeasured items that decide §1:**
   - the four-code f16x2 → e4m3 cast (F2FP, F2FP, PRMT);
   - the f32-pair e4m3 cast written into a four-code register (does it need a PRMT?);
   - the centre HFMA2 with two immediates.

## 3. The additive-W1 reading, and real-time overhead

**The reading is right.**
- Additive W1 charges every instruction of the honest reference its class price. The honest step's 57.0–69.9 per add
  word (§14.4) is the wall-clock throughput of one kernel family, and γ does not read it.
- W1 charges the main chain 32 (atom) + 32.11 (FADD) = 64.11 per add word. The measured step runs at 57.01 because the
  tensor core and the FP32 pipe overlap. So the honest prover runs below its W1 charge, and `AdmitsRef` holds for the
  main chain at every measured shape.
- §14.3's "fails 1.78×" compares the whole step with 32.02. That is a throughput target (adds hidden under the tensor
  core), not a W1 price.
- **One caveat, not new:** W1 is additive and the hardware overlaps pipes, so γ bounds an adversary's saving in W1 work,
  not in wall-clock time.

**Real-time honest overhead** is honest time over a plain FP8 GEMM's (k/32 accumulating atoms per output at the full
tensor rate). It is ≈ 3 × (per add word)/32 + f/k, and the forming term is 0.04 at W1 prices.

| Shape (§14.4) | Per add word | Tensor share | Overhead |
|---|---:|---:|---:|
| n128, B = 1, U = 4 (best) | 57.01 | 56.1% | **5.39×** |
| n64, B = 1, U = 4 | 58.49 | 54.7% | 5.52× |
| n64, B = 2, U = 2 | 59.86 | 53.5% | 5.65× |
| n128, B = 2, U = 2 | 63.56 | 50.3% | 6.00× |
| n128, B = 1, U = 1 | 69.87 | 45.8% | 6.59× |
| best shape at full dispatch (35.75) | 35.75 | 89.5% | 3.39× |
| adds fully hidden (the floor) | 32.00 | 100% | 3.04× |

- **Every measured shape misses Daniel's 3–5×.** The best misses 5× by 8%. 5× needs a tensor share of at least 60.5% and
  4× at least 75.8%.
- The fix is a kernel, not a price: producer/consumer with TMA and `setmaxnreg`, more warpgroups in flight, or the
  in-flight double buffer that ptxas serializes (C7514). These are §14.8's unmeasured shapes.
- §13.6's FADD–`wgmma` contention (37% tensor share beside independent FADD chains) may be a structural cap, and that
  should be settled first.

## 4. Item 2: the Y16 row statistic

**Track A is right.**
- The amplitude's floor term rms′ enters every noise value, so the verifier has to recompute it from what is committed.
  On the Y16 route that is the Y16 words, and Track A computes the statistic on them (prescale, HFMA2 lanes, widen per 256).
- 17f's 390 runs an FFMA sum of squares on the model's f32 A/s before packing, and those values are never committed. The
  prover could then claim any rms′. At best that degrades D-3s to "σ a constant", the floor-type law that 17f itself
  shows grows the branching gap to a third of the credit.
- So 17f's D-3s Y16 figure should read 394.27 (Track A), not 390, at Round 8: +0.0043 γ points (0.9398% against 0.9355%).

**The alternative: commit the f32 statistic too.**
- **The rule.** One f32 word per row, bound in com(A_u), with rms′ = max(f16(rms_committed), 2⁻⁶).
- **The verifier's check.** It has to check the committed word against Y16, in exact arithmetic, within a stated
  interval. Each Y16 entry is within 2⁻¹¹ relative of A/s, and the prover's f32 lane sums add about 2⁻¹⁶. So
  |rms_committed / rms(Y16) − 1| ≤ 2⁻⁹ is safe.
- **What it leaves the prover.** A choice among 5–9 f16 values of rms′ per row (±2 to ±4 ulps, 2.3–3.2 bits), made
  before E₁. That is harmless for `DistinctLive`, where A is adversarial anyway, but it is a new rule and a new committed field.
- **Price.** One FFMA per element at the FP32 class price, against Track A's 16.085 + 18 + (64 + FADD)/256 = 34.46 at
  Round 9. That saves 2.46 units per element:

| | Statistic, per element | f_a (Y16, D-3s) | γ |
|---|---:|---:|---:|
| Round 8, Track A | 36.27 | 394.27 | 0.9398% |
| Round 8, committed f32 | 32.00 (32.11 with FFMA at the FADD class price) | 390.0 | 0.9355% |
| Round 9 M4, Track A / committed | 34.46 / 32.00 | 600.46 / 598.0 | 1.3249% / 1.3224% |
| Round 9 M2q, Track A / committed | 34.46 / 32.00 | 396.46 / 394.0 | 0.9179% / 0.9155% (thresholds 32.0534 / 32.0550) |

**Recommendation: keep Track A's statistic.** The alternative buys 0.0025 points at Round 9 for a committed field, an
interval rule in the verifier, and 2–3 bits of prover choice. It never changes whether a cell clears.

## 5. Item 3: commitment order

### 5.1 The orders as written

- **#218's lifecycle** (`protocols/pouw/PROTOCOL.md` on #295's branch, lines 27–49):
  - the salt is `derive(beacon, "verity/pouw/salt/v1", {"weights": weights_root})`, drawn after the weights;
  - then, per matmul, the activation rows are committed, bound to the salt and index;
  - the scheme derives its noise from (salt, matmul, roots).
- **`ncp-v1` (int8):**
  - E₁ comes per unit from frame(salt, index, root_A, weight, i);
  - F₁ comes per (epoch, weight) from frame(salt, weight, j).
- **PR #295's `D3Family` (d3s-v0, d3m-v0):**
  - E₁ = SHAKE256(tag/E1, salt, index, root_A, weight, i);
  - **F₁ = SHAKE256(tag/F1, salt, index, weight, j)**: per unit, but without root_A.

**Consequence.** Under #218's order the prover knows the salt before it commits A_u. #295's F₁ is then computable before
A_u, so B̃_u (a function of W, F₁ and the public P) is known before A_u and the prover's program are fixed. The only
randomness drawn after the program is E₁. `DistinctLive` therefore has to hold for words taken as functions of E₁ alone,
with B̃ fixed. That is exactly X-D3-3's premise (from the D-3 strike, where B̃ was fixed per epoch), so X-D3-3 now
applies at r = 1.

### 5.2 Bit-exact check (`red-team-round9-order.py`, PR #295's own `D3Family`)

**The witness.**
- 64 identical weight columns and one activation row, each with one 288 (E4M3 0x79) per spike slice at the same position.
- Every spike's NCP partners π(s) and π⁻¹(s) lie outside all spike slices; P is public.
- The spike count is the largest for which every zero entry's code stays at or below 2.75 on both sides, so its products
  truncate under 288².
- 12 draws of root_A model E₁'s fresh draws, and grinding.
- For each spike slice and block, the script counts the distinct functions root_A → word over the 64 columns.

PR #295 `D3Family("d3s", "xq")`, 64 columns, 12 root_A draws:

| | k = 4,096, #295 seeds | k = 4,096, F₁ bound | **k = 16,384, #295 seeds** | **k = 16,384, F₁ bound** |
|---|---|---|---|---|
| Spike slices per row | 26 of 128 (20.3%) | the same | 104 of 512 (20.3%) | the same |
| rms′ (f16); largest zero-entry code | 0x4DBD = 22.95; 2.75 | the same | 0x4DBD; 2.75 | the same |
| One-product in blocks 1 and 2, every slice, column and draw | yes | yes | yes | yes |
| Functions of root_A per spike slice, block 1 | **3** on all 26 | 64 on all 26 | **3** on all 104 | 64 on all 104 |
| Block 2 | **3** on all 26 | 64 on 25, 63 on 1 | **3** on all 104 | 64 on 102, 63 on 2 |
| Block 3 | 64 | 64 | 64 | 64 |
| Weight spike codes at draw 0 (256, 288, 320) | 467, 717, 480 | 461, 729, 474 | 1,850, 2,945, 1,861 | 1,873, 2,882, 1,901 |
| Exposed share of the credit, n → ∞ (n = 64) | **6.78%** (6.46%) | none | **6.77%** (6.46%) | none |

The 63s under the fix are coincidences of 12-draw code sequences between two columns. Their expected count is about
0.015 per slice-block, so about 0.8 at 4,096 and 3 at 16,384; more draws separate them.

- **Under #295's seeds**, blocks 1 and 2 have at most 3 functions per spike slice over 64 identical columns. The weight
  spike's noised code takes 3 values (256, 288, 320), and the copy plan is known before the program is fixed.
  - The exposed I words are 2·n_s·(1 − 3/n) per column, out of 2T − 1 credited words.
  - That is 6.8% at the column limit, and 6.46% at n = 64, against ε = 1/400.
  - The fraction does not depend on k, because the spike count scales with k. As in X-D3-3, R words add about 0.5% more.
- **With F₁ bound to root_A** (`Bound`, the only change), the same witness gives 64 functions per slice in every block
  (one slice-block at 63, a 12-draw coincidence).
  - The spike slices stay low-entropy per draw (3 × 3 codes at about 0.28, 0.44 and 0.28 per side, so H∞ ≈ 2.0 bits per
    word; D-3m's is 1.93 bits, D-3m strike §2.2). That is the
    r = 1 status the red team already accepted, with the branching gap named separately.
- **Block 3 is not one-product** (its zero entries carry s = e + e∘P) and stays distinct in both modes.

**#295's witnesses don't cover the ruling.**
- `test_d3_family_repairs_the_refuted_inputs` and `test_d3_family_weight_noise_is_per_unit` vary the whole salt, or the
  unit index, with A fixed. `test_d3_identical_weight_columns_are_distinct` (on d3-v0) compares two columns at one draw.
  None of them fixes F₁ and varies only E₁.
- Varying the salt moves E₁ and F₁ together. It is the right model only when every per-unit stream is derived after
  com(A_u), which is the fix, not the code as it stands.
- Once F₁ reads root_A, those tests model the ruling correctly: for any A chosen from the salt, (E₁, F₁) are fresh random-
  oracle outputs on (salt, com(A_u)).
- They should gain a fixed-F₁ negative control (this script's `pr295` mode) and a positive test that varies only root_A.

### 5.3 What must change

- **PR #295 (FP8), required.**
  - In `D3Family.form`, F₁ becomes SHAKE256("verity/pouw/fp8-is/<tag>/F1", salt, index, **root_A**, weight, j), and the
    docstring and `PROTOCOL.md`'s ncp description say so.
  - The vectors (`tests/vectors/fp8_is.json`) are regenerated.
  - Cost:
    - zero W1, since the weight side is already formed per unit at r = 1;
    - no new serialization, since E₁ already waits for root_A.
  - The only operational loss is that B̃_u can no longer be formed ahead of A_u's commitment.
- **#218's lifecycle: no change.**
  - Weights registered before the epoch salt, and activations committed after it, is sound, provided each scheme's
    per-unit noise reads com(A_u).
- **§0's wording.** "Activations are committed before the salt" should become:

  > A unit's activations are committed before any of that unit's noise is derived: every stream that forms the unit's
  > checked operands, on either side, reads com(A_u). Weights are registered before the epoch salt. A stream that does
  > not read com(A_u) (a per-epoch weight stream) is fixed before the prover's program, and the scheme's `DistinctLive`
  > must hold with it fixed.

  The last sentence is the r ≥ 2 condition, which the D-3 family fails (X-D3-3).
- **int8 `ncp-v1`: no change from this finding.**
  - Its F₁ is per epoch by design, so B̃ is fixed before the program, and `ncp-v1` has to meet the last sentence above.
  - X-D3-3's mechanism needs one-product slices whose word depends on one few-valued noised weight code. ncp-v1 adds
    6-bit uniform noise to every activation entry and its products are exact integers, so every slice word reads the
    whole column slice. Column-keyed F₁ separates identical columns with probability 1 − 2^(−6w) per pair over a slice of
    w entries.
  - Whether TTNCP_U's statement quantifies over A chosen after F₁ belongs to the int8 lane. I did not check it.

## 6. Named findings

- **X-R9-1 (fatal to Track A's specification at Round 9):** f32 block values cost HADD2.F32 + FADD = 96 each, not 36, and
  every D-3s and D-3m cell's FADD threshold falls below 32 (1.32–1.42% at FADD 32). Clearing needs f16 block values and an
  unmeasured four-code cast, and even then only at FADD ≤ 32.00–32.05.
- **X-R9-2 (major, spec):** under #218's order, PR #295's F₁ is known before the program, and X-D3-3 recurs at r = 1
  (ε ≈ 6.8% at k = 4,096 and 16,384). The fix is to key F₁ on root_A, at zero cost.
- **X-R9-3 (minor):** 17f's D-3s Y16 price of 390 rests on an uncommitted statistic. Track A's 394.27 is the right figure.

## §3 log line (Round 9)

- 19:20Z strike (bc-79ab9271): Round 9 (`internal/pouw-fp8/genuine-fp8-red-team-round9.md`, `red-team-round9-*.py`).
  - **Price:**
    - Track A's M4 fails every cell at every FADD ≥ 32 (1.32–1.42%). HADD2.F32 is a convert, so a block value is 64 + FADD.
    - Only f16 block values plus an unmeasured four-code cast clear: D-3s Y16 copy 0.918%, FADD ≤ 32.053.
    - At 32.11 nothing clears.
  - **FADD:** 32.11 is reproducible; about 0.04 is plausibly framework and 0.07 two-source; the probe is proposed.
  - **W1:** the honest step is a time effect (57.01 < 64.11 W1); the real-time overhead is 5.4× (5× needs a ≥ 60.5%
    tensor share).
  - **Y16 statistic:** Track A is right; the committed-f32 alternative saves 0.0025 points, not worth it.
  - **Order:** #295's F₁ lacks root_A, so X-D3-3 recurs at r = 1 (6.8%). Key F₁ on root_A; #218 is unchanged.

## D-4 and serving shapes

Written 19:20Z to 19:55Z, CPU only. The request is Track D's D-4 (`tracks/track-d-round9-routes.md`) at 32,768³ and
65,536³, the (m, n, k, r) condition for γ < 1%, the real layers that meet it, and a check of the #295 seed fix. The script is
`red-team-round9-shapes.py` and `.json`, beside this file. It needs `red-team-round9-gamma.py` beside it, and
`--check-295 <checkout>` re-derives #295's rows from its `d3_trace`.

### D.1 Verdict

1. **Correction to Round 9: my M4 is 64 low per activation element (and per decoded weight element). #295's M4 is the
   price of record.**
   - An f32 block value is f32(h) + f32(e_b). §14.5 prices one widen plus one FADD *given* f32(h), and h itself needs one
     more widen per element (64), shared by the three blocks.
   - Round 9's M4 charged three widens per side, not four. Track A's #295 at f31ad2dd charges the fourth (`widen_once`)
     on the activation side, and on the weight side when decoded. With the copy, it registers an f32 copy, so that widen
     is free.
   - My γ equals #295's `FP8IS` certificate exactly in every cell I cross-checked, at #295's FADD 32.11. `--check-295`
     confirms the forming coefficients in all 8 cells.
   - Round 9 §1's M4 rows rise by 0.06–0.13 points: D-3s Y16 copy at 16,384³ is 1.388% at FADD 32.00, threshold 31.747.
     No Round 9 verdict changes, since M4 already failed. M2q has no widen and is unaffected.
   - Track D's D-4 figures (f_A = 602.60) lack the same widen; they match my old M4 to within 0.001.
2. **D-4 at FADD 32.11 under #295's M4:**
   - At 32,768³, only D-3s with the copy survives: Y16 0.9919%, threshold 32.115; X_q 0.9999%, threshold 32.110. Every
     decoded cell and every D-3m cell fails.
   - At 65,536³ every cell survives, with thresholds 32.274–32.300.
   - If only ruling (ii)'s FP16 copy is free, and not #295's f32 copy, then 32,768³ fails every cell at 32.11
     (1.024–1.048%). 65,536³ still clears (0.723–0.735%). See D.6.
   - Under M2q, and under #295's cheaper `round9-sass` f16 row (M2s), every D-4 cell survives, with thresholds ≥ 32.238.
3. **k drops out; n and m are what matter.** Track D's scope note ("all three dimensions ≥ 32,768") is the wrong test.
   - γ < 1% iff f_a(p)/n + f_b(p)/m < B(p, k). B depends on k only through a term ≤ 0.24/k, which is 0.07% of the budget at
     k = 8,192. It also changes by 32.24/k for each uncredited word per output; the D-3 family has none.
   - So the condition is a hyperbola in (n, m) with floors n > n_min and m > m_min. At 32.11 those are n > 18.9k–20.3k and
     m > 13.4k–16.6k under #295's M4, and n > 9.5k–10.4k and m > 6.7k–7.6k under M2s.
   - The real layers that clear need m of 8k–46k. k can be as small as 2,048.
4. **Real layers (lead cell D-3s Y16 copy, FADD 32.11, per GPU as vLLM shards them):**
   - Under #295's M4, only the FFN gate/up projections clear:
     - 70B gate_up at TP 1: m ≥ 20,032;
     - 70B gate/up (n = 28,672, or gate_up at TP 2): m ≥ 39,424;
     - 405B gate/up (or gate_up at TP 2): m ≥ 20,800;
     - 405B gate_up at TP 4: m ≥ 46,336.
   - Under M2s, these are added: 405B o/down (m ≥ 16,064–16,128), 405B qkv at TP 1 (13,952), 405B gate_up at TP 8
     (23,616) and 70B gate_up at TP 4 (20,032).
   - At 32.11, nothing clears for 70B o/down, for 70B qkv, for any separate k/v projection, or at decode.
5. **Seed fix: confirmed in #295 (a388ffc3).**
   - F₁ reads (salt, index, root_A, weight, j), so the weight noise is per unit and r = 1 holds by construction, as
     priced.
   - The static weight data stays free, registered offline under ruling (ii): the FP16 copy of the base codes, rms′,
     partner and floor maxima, and P.
   - Only the noise path is per unit: 236 (M2s), 266 (M2q) or 470.33 (M4) per weight element with the copy.
   - M4's copy cells need an f32 copy to be free, which ruling (ii) as written doesn't grant.

### D.2 The D-4 table (square m = n = k, r = 1; γ at FADD 32.00 / 32.11; FADD threshold = the price at which γ = 1%)

Schedules:
- **M4 (#295)** is #295's `PRICES["round9"]` with f32 sums: Track A's specification with four widens.
- **M2q** is Round 9's f16 block values with the four-code f16x2 cast at 48 per code (unmeasured).
- **M2s (#295)** is #295's `PRICES["round9-sass"]` with f16 sums:
  - the PRMT-free four-code cast and unpack at 32 per code, counted from ptxas's SASS but untimed in the honest kernel;
  - one VHMNMX for both maxima, assumed at 64;
  - s kept, as in Track A's law;
  - so X_q prices as Y16.
- Bold marks a cell above 1% at FADD 32.11.

**32,768³**

| Cell | M4 (#295) 32.00 | M4 (#295) 32.11 | M4 (#295) threshold | M2q 32.00 | M2q 32.11 | M2q threshold | M2s (#295) 32.11 | M2s threshold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D-3s, Y16, copy | 0.822% | 0.992% | 32.115 | 0.585% | 0.755% | 32.269 | 0.709% | 32.299 |
| D-3s, Y16, decoded | 0.879% | **1.048%** | 32.079 | 0.609% | 0.779% | 32.254 | 0.725% | 32.289 |
| D-3s, X_q, copy | 0.830% | 0.9999% | 32.110 | 0.593% | 0.763% | 32.264 | 0.709% | 32.299 |
| D-3s, X_q, decoded | 0.887% | **1.056%** | 32.074 | 0.617% | 0.787% | 32.248 | 0.725% | 32.289 |
| D-3m, Y16, copy | 0.838% | **1.008%** | 32.105 | 0.601% | 0.771% | 32.259 | 0.725% | 32.289 |
| D-3m, Y16, decoded | 0.895% | **1.064%** | 32.069 | 0.625% | 0.795% | 32.243 | 0.741% | 32.278 |
| D-3m, X_q, copy | 0.846% | **1.016%** | 32.100 | 0.609% | 0.779% | 32.254 | 0.725% | 32.289 |
| D-3m, X_q, decoded | 0.903% | **1.072%** | 32.063 | 0.633% | 0.803% | 32.238 | 0.741% | 32.278 |

**65,536³**

| Cell | M4 (#295) 32.00 | M4 (#295) 32.11 | M4 (#295) threshold | M2q 32.00 | M2q 32.11 | M2q threshold | M2s (#295) 32.11 | M2s threshold |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D-3s, Y16, copy | 0.537% | 0.707% | 32.300 | 0.418% | 0.588% | 32.377 | 0.565% | 32.392 |
| D-3s, Y16, decoded | 0.565% | 0.735% | 32.282 | 0.430% | 0.600% | 32.369 | 0.573% | 32.387 |
| D-3s, X_q, copy | 0.541% | 0.711% | 32.297 | 0.422% | 0.592% | 32.374 | 0.565% | 32.392 |
| D-3s, X_q, decoded | 0.569% | 0.740% | 32.279 | 0.434% | 0.605% | 32.367 | 0.573% | 32.387 |
| D-3m, Y16, copy | 0.545% | 0.715% | 32.295 | 0.426% | 0.596% | 32.372 | 0.573% | 32.387 |
| D-3m, Y16, decoded | 0.573% | 0.744% | 32.277 | 0.438% | 0.609% | 32.364 | 0.581% | 32.382 |
| D-3m, X_q, copy | 0.549% | 0.719% | 32.292 | 0.430% | 0.600% | 32.369 | 0.573% | 32.387 |
| D-3m, X_q, decoded | 0.577% | 0.748% | 32.274 | 0.442% | 0.613% | 32.361 | 0.581% | 32.382 |

**Comparison with Track D, and the other rows:**
- **Round 9's three-widen M4 matches Track D.**
  - 32,768³: 0.960% / 0.984% (copy / decoded) at 32.11, against Track D's 0.961% / 0.985%. Thresholds 32.136 / 32.121,
    against Track D's 32.1356 / 32.1199.
  - 65,536³: 0.691% / 0.703%, thresholds 32.310 / 32.303.
  - The residual 0.001 is Track D's convention. It prices forming at a fixed 32.11 and its f_A is 602.60 against my
    600.79; my forming FADDs scale with p. The JSON carries both.
- **M4 (#295) with only an FP16 copy free** (the weight's widen paid per unit, f_b = 438 + 3p):
  - 32,768³: 1.024–1.048% at 32.11, thresholds 32.079–32.095, so it fails.
  - 65,536³: 0.723–0.735%, thresholds 32.282–32.290.
- **16,384³ under M2s (#295):** D-3s Y16 copy is 0.995% at 32.11, threshold 32.113. This row is newer than Round 9 (its
  cast and max are SASS-counted and untimed). It is the first row in which any 16,384³ cell clears at the measured FADD.

**So, does 32,768³ survive FADD at 32.11?** Under #295's own price, only D-3s with the copy survives: Y16 by 0.008
points, X_q by 0.0001. That rests on the f32 copy being free. Under an FP16-only copy it fails, and it survives
comfortably only under f16 block values (M2q or M2s). 65,536³ survives in every schedule to FADD ≥ 32.27.

### D.3 The shape condition

For an m × k by k × n unit with r units sharing a formed weight, the variables are:
- T = 3k/32 atom words per output;
- a uncredited words per output (a known-final-value allowance; 0 for the D-3 family, where R_T carries each block's
  truncation and FP32 rounding);
- credit 32(2T − 1 − a);
- main chain 32T + p(T − 1);
- forming f_a(p)·k/n + f_b(p)·k/(r m).

Then γ = 1 − (399/400)·credit/(main + forming), and γ < 1% is exactly

    f_a(p)/n + f_b(p)/(r·m)  <  B(p, k, a) = 1/22 − 3(p − 32)/32 − (32(1 + a)·133/132 − p)/k

    B(32.00, k, 0) = 0.0454545 − 0.24242/k        B(32.11, k, 0) = 0.0351420 − 0.13242/k

Each allowance word subtracts 32.24/k from B: 0.00394 at k = 8,192. Equivalently,

    (n − n_min)(r·m − m_min) > n_min·m_min,   where n_min = f_a(p)/B and m_min = f_b(p)/B,

so the smallest m for a given n is m_min·n/(r(n − n_min)), and no m suffices when n ≤ n_min. The condition is linear in p,
so each shape's FADD threshold is

    p* = [67/22 − 1064(1 + a)/(33k) − f_a0/n − f_b0/(r m)] / [3/32 − 1/k + f_an/n + f_bn/(r m)].

The coefficients, with f(p) = f0 + f_n·p (f_n counts forming's own FADDs):

| Schedule | f_a(p), D-3s Y16 | f_b(p), copy / decoded | X_q | D-3m | n_min at 32.00 / 32.11 (D-3s Y16; D-3m X_q) | m_min at 32.00 / 32.11 (copy; decoded) |
|---|---|---|---:|---:|---|---|
| M4 (#295) | 568.335 + 3.0039p | 374 + 3p / 486 + 3p | +16 | +32 | 14,618 / 18,917; 15,674 / 20,283 | 10,340 / 13,384; 12,804 / 16,571 |
| M4 (Round 9, three widens) | 504.335 + 3.0039p | 374 + 3p / 422 + 3p | +16 | +32 | 13,210 / 17,096; 14,266 / 18,462 | 10,340 / 13,384; 11,396 / 14,750 |
| M2q | 396.335 + 0.0039p | 266 / 314 | +16 | +32 | 8,722 / 11,282; 9,778 / 12,648 | 5,852 / 7,569; 6,908 / 8,935 |
| M2s (#295) | 334.335 + 0.0039p | 236 / 268 | 0 | +32 | 7,358 / 9,517; 8,062 / 10,428 | 5,192 / 6,716; 5,896 / 7,626 |

(n_min and m_min are at k → ∞; at k = 8,192 they are 0.07% higher.)

**What the condition says about scope:**
- **k barely enters.** FADD's excess (3(p − 32)/32, 0.0103 at 32.11, 23% of the budget) and any allowance are
  shape-independent in n and m. k enters only through B's 1/k term.
- **So Track D's "all of m, n, k ≥ 32,768" is sufficient in most cells, but neither necessary nor the right test.**
  - k can be 2,048: 405B o_proj at TP 8 clears under M2s at 32.11 for m ≥ 16,128.
  - m and n must both be large, but with respect to the per-schedule floors above, not 32,768. n far above n_min lets m
    fall toward m_min, and vice versa.
- **The one place k matters is an allowance.** With a = 1 (int8 `ncp-v1`'s known final value), 405B o_proj at TP 4
  (k = 4,096) goes from 16,064 to 34,624 under M2s, and at TP 8 (k = 2,048) to never. At k ≥ 16,384 it moves min m by
  about 20% or less. The JSON's `a = 1` rows carry this.
- **The domain.** #295's `FP8IS.check` requires `mnk_min ≤ m, k, n ≤ 2^16` in all three dimensions.
  - At `mnk_min = 32768` no real layer enters. At 16,384 (the D-3 cells' default), every 70B layer is out (k or
    n = 8,192), and so is 405B at TP 8.
  - The domain that matches the bound is: the alignments (64 | m, 64 | n, 32 | k), m, n, k ≤ 2^16, and the inequality
    above at the certificate's p, with a margin.
  - The certificate's ω would then be the boundary's γ, just under 1%, not a cube's. `wref` already takes the unit's
    shape. `certificate.omega` evaluates only the cube at `mnk_min`.
- **m and n are the unit's.** f_b is amortized over the unit's m rows and f_a over its n columns. The unit must therefore
  be the whole matmul, which #295 charges as one unit per matmul (`wref`), and m is the step's batched tokens.
  - Track D is right that padding or block-diagonal aggregation cannot enter the domain.
  - vLLM caps m at `max_num_batched_tokens`. The repo's recorded workloads use 2,048–29,304, so m ≥ 20k is a
    configuration choice (with its latency cost), not a default.

### D.4 Real layers

Layers are per GPU as vLLM shards them:
- qkv_proj and gate_up_proj are fused and column-parallel (n/TP); o_proj and down_proj are row-parallel (k/TP).
- 70B class: hidden 8,192, FFN 28,672, 64 q and 8 kv heads of 128.
- 405B class: hidden 16,384, FFN 53,248, 128 q and 8 kv heads.

The table gives the smallest m (rounded up to 64) with γ < 1%, for D-3s Y16 with the copy at FADD 32.00 / 32.11. The last
column is the worst cell, D-3m X_q decoded, at 32.11. "—" means no m ≤ 2¹⁶ clears.

| Layer (k, n) | M4 (#295) | M2q | M2s (#295) | Worst cell at 32.11, M4 (#295) / M2s |
|---|---:|---:|---:|---:|
| 70B gate_up, TP 1 (8,192, 57,344) | 13,952 / 20,032 | 6,912 / 9,472 | 6,016 / 8,064 | 25,664 / 9,344 |
| 70B gate or up; gate_up TP 2 (8,192, 28,672) | 21,184 / 39,424 | 8,448 / 12,544 | 7,040 / 10,112 | 56,768 / 12,032 |
| 70B gate_up, TP 4 (8,192, 14,336) | — / — | 14,976 / 35,648 | 10,688 / 20,032 | — / 28,032 |
| 70B qkv, TP 1 (8,192, 10,240) | — / — | 39,680 / — | 18,496 / — | — / — |
| 70B o or down, any TP (1,024–28,672, 8,192) | — / — | — / — | 51,136–53,760 / — | — / — |
| 405B gate or up; gate_up TP 2 (16,384, 53,248) | 14,272 / 20,800 | 7,040 / 9,664 | 6,080 / 8,192 | 26,816 / 9,536 |
| 405B gate_up, TP 4 (16,384, 26,624) | 22,976 / 46,336 | 8,768 / 13,184 | 7,232 / 10,496 | — / 12,544 |
| 405B gate_up, TP 8 (16,384, 13,312) | — / — | 17,024 / 49,728 | 11,648 / 23,616 | — / 35,264 |
| 405B qkv, TP 1 (16,384, 18,432) | 50,112 / — | 11,136 / 19,584 | 8,704 / 13,952 | — / 17,600 |
| 405B qkv, TP 2 (16,384, 9,216) | — / — | — / — | 25,856 / — | — / — |
| 405B o or down, TP 1–8 (2,048–53,248, 16,384) | — / — | 12,544–12,608 / 24,320–24,512 | 9,472 / 16,064–16,128 | — / 20,992–21,120 |

**Layers that never clear, in any schedule at any FADD ≥ 32:**
- separate k or v (n = 1,024);
- 70B qkv at TP ≥ 2 (n ≤ 5,120);
- 405B qkv at TP ≥ 4 (n ≤ 4,608);
- 70B gate_up at TP 8 (n = 7,168).

405B gate_up at TP 1 has n = 106,496 > 2¹⁶, so it runs as separate gate and up units (the 405B gate-or-up row). Under
Round 9's three-widen M4, the lead-cell floors are lower: 70B gate_up TP 1 19,136, 405B gate/up 19,776, 405B o/down never
at 32.11 (in the JSON).

**What clears at realistic deployments:**
- **405B in FP8 needs TP 8 on 80 GB H100s.** There, M4 (#295) clears nothing at any FADD ≥ 32. Under M2s at 32.11, o_proj
  and down_proj clear at m ≥ 16,064–16,128 and gate_up at m ≥ 23,616; qkv never clears. Under M2q, o/down need
  m ≥ 24,384–24,512 and gate_up m ≥ 49,728.
- **70B at TP 1 or 2:**
  - gate_up clears under M4 (#295) at m ≥ 20,032 (TP 1) or 39,424 (TP 2), and under M2s at m ≥ 8,064 or 10,112.
  - o, down and qkv never clear at 32.11. At 32.00, o and down clear only under M2s (m ≥ 51k), and qkv at TP 1 under
    M2q (39,680) or M2s (18,496).
- **By FLOPs,** gate_up and down are about 82% of a layer's linear work in both classes (qkv about 10%, o about 8%).
  So at 405B TP 8, M2s at m ≥ 23,616 covers everything but qkv (about 90% of the linear FLOPs). At 70B TP 2, only
  gate_up is covered (about 55%).

### D.5 Decode

Forming's weight side is amortized only over the unit's m tokens, since r = 1 by construction. Decode (m of at most a few
hundred) therefore never clears. For M2s (#295), D-3s Y16 copy at FADD 32.00:
- 70B gate/up: 38.3% at m = 64, 13.7% at 256, 7.5% at 512, 4.1% at 1,024;
- 405B gate/up: the same to within 0.1 points.

M2q is 7–12% higher. A decode step joins the prefill tokens of its step into one matmul, so what matters is the step's
total m, not each request's.

### D.6 The #295 seed fix

1. **Implemented.** #295's a388ffc3 (19:20Z) keys F₁ as SHAKE256("verity/pouw/fp8-is/<tag>/F1", salt, index, root_A,
   weight, j) for every D-3 cell (`D3Family.stream`). E₁ is keyed the same way. It adds a regression on the scaled spike
   witness and regenerates the vectors. With root_A in F₁, B̃_u depends on the unit's committed activations, so it is
   re-formed per unit. There is no epoch amortization, and r = 1 holds by construction. `FP8IS.wref` charges the weight
   side once per matmul, which is the r = 1 price used throughout.
2. **Ruling (ii) still applies to the base codes.**
   - The FP16 copy of the weight codes is static and salt-independent, so root_A does not touch it.
   - The same holds for everything #295's `d3_trace` registers offline per column: rms′, the cell widths, the partner and
     floor maxima (functions of the static codes and the fixed P), and P itself.
   - Per unit, the weight side pays only the noise path. That is the u field (LOP3, 32), the centre (18), the scale (18)
     and s (18), then the three block values and the three casts:

     | Schedule | Block values | Casts | Total per weight element |
     |---|---|---|---:|
     | M4 | 3 × (64 + p) | 3 × 32 | 470.33 at 32.11 |
     | M2q | 3 × 18 | 3 × 48 | 266 (no s) |
     | M2s | 3 × 18 | 3 × 32 | 236 |

   - Decoding instead of using the copy adds 48 per element in M2q, 112 in M4 (48 plus the widen) and 32 in M2s (its
     PRMT-free unpack).
3. **One gap: M4's copy is f32.**
   - #295 registers "its f32 copy when `weight_copy`", so M4's widen of the weight is free. Ruling (ii) as written grants
     an FP16 copy.
   - If only the FP16 copy is free, M4 pays 64 more per weight element per unit. D-4 at 32,768³ then fails every cell at
     FADD 32.11 (D.2).
   - The ruling should say whether an f32 copy (4 bytes per weight, 4× the E4M3 codes) is also registered data. The f16
     schedules need only the FP16 copy.
4. **Not in the price, but changed in real time.**
   - Raw XOF words are free by the interface's convention ("Raw XOF noise words are free in every price here"), so the fix
     costs nothing in W1.
   - In real time, F₁ is now 2k bytes per weight column per unit rather than per epoch. A unit's stream volume goes from
     2mk to 2(m + n)k bytes, and B̃_u's forming cannot start before root_A.

### D.7 §3 log line (D-4 and serving shapes)

- 19:55Z strike (bc-79ab9271): D-4 and serving shapes (`genuine-fp8-red-team-round9.md` "D-4 and serving shapes",
  `red-team-round9-shapes.py`).
  - **Correction:** Round 9's M4 and Track D's D-4 omit h's widen (64 per activation element, and per decoded weight
    element). #295's M4 charges it, and my γ equals #295's certificate.
  - **D-4 at 32.11 under #295's M4:**
    - 32,768³ survives only for D-3s with the copy (Y16 0.992%, threshold 32.115; X_q 0.9999%), and only if the f32 copy
      is free. Decoded and D-3m fail.
    - 65,536³ survives every cell (thresholds ≥ 32.274).
    - M2q and M2s clear every D-4 cell (thresholds ≥ 32.238).
  - **Shapes:**
    - γ < 1% iff f_a/n + f_b/m < B(p, k) = 1/22 − 3(p − 32)/32 − (0.24 + 32.24a)/k (the 0.24 is 0.13 at 32.11). k drops out.
    - The floors at 32.11 are n > 18.9k and m > 13.4k for M4 (#295), and n > 9.5k and m > 6.7k for M2s. Track D's
      k ≥ 32,768 is unnecessary; the domain should be the condition.
  - **Real layers at 32.11 (D-3s Y16 copy):**
    - M4 (#295): only gate/up; 70B at m ≥ 20k (TP 1) or 39k (TP 2), 405B at m ≥ 21k (TP ≤ 2) or 46k (TP 4).
    - M2s adds 405B o/down (m ≥ 16k, any TP), qkv at TP 1 (14k) and gate_up at TP 8 (24k).
    - Never at 32.11: 70B o/down/qkv, k/v, decode.
  - **Seed fix:** in #295 (a388ffc3); r = 1 by construction, and the price is unchanged. Ruling (ii) covers the base
    codes; the f32 copy that M4 needs is not in the ruling.

## Track A's Round 9 claims

Written 19:45Z to 20:25Z, CPU only. The source is Track A's Round 9 report (`tracks/track-a-round9.md`, §2.1.A to §8)
and PR #295 at f31ad2dd. Four scripts sit beside this file, each with its `.json`:
- `red-team-round9-readings.py`: both price rows through #295's `d3_trace`, the lead cells, each disputed item alone,
  the sensitivities, Track A's numbers, the floors and the smallest m per layer. It needs `red-team-round9-shapes.py`
  beside it.
- `red-team-round9-f16-codes.py`: the code distributions under f32 and f16 sums. Its numpy pipeline is checked
  bit-exactly against #295's `D3Family.side`.
- `red-team-round9-f16-witness.py`: §5.2's spike witness with f16 sums. It needs `red-team-round9-order.py` beside it.
- `red-team-round9-sass-probe.py`: chain-shaped kernels for the untimed items, through Track A's
  `prototype/track_a_sass_counts.py`.

The first three need #295 on `PYTHONPATH`.

Track A's SASS counts (`prototype/track_a_sass_counts_results.json`) reproduce exactly with ptxas 12.4.131 and 12.9.86
and nvdisasm 12.9.88.

### E.1 Verdict

1. **The `-f16` variant is #295's M2 law priced at the `round9` row.** It is neither my M2q nor the `round9-sass` row,
   and it is sound.
   - The law is the same as `round9-sass` M2; only the price row differs.
   - It is not M2q, which also drops s (a law change).
   - f16 sums move 0.07–0.34% of codes, each by one step, at E4M3 ties only.
   - The noise law, its amplitude and `DistinctLive` are unchanged.
   - Track B's quality runs used FP16 forming, which is this law, so no re-measure is needed.
2. **The four price items: Track A is right on the compiled code for all four.** (a) and (c) hold for ptxas 12.9 only;
   (b) and (d) hold for both versions. All four are static counts.
   - (d) runs at a timed rate and is settled.
   - The rates for (a), (b) and (c) are untimed. Round 10 must time them from 12.9 builds, in the chain shapes E.3
     names.
3. **Track A's "m ≥ 32,768" is a sufficient domain, not the condition.**
   - The condition is (n − n_min)(m − m_min) > n_min·m_min, where m is the tokens of one unit (r = 1; there is no
     weight epoch).
   - 32,768 on m suffices only when n is large too (n ≥ 18.5k under `round9` M2 at 32.11).
   - The layers Track A lists clear well below it: 405B gate/up at m ≥ 12.6k, 70B gate_up at 12.3k (M2), or 20.0k
     under M4.
   - The LM head's m in serving is the number of sequences, not the number of tokens.

### E.2 Item 1: the f16-sums variant

**What it is.**
- The `-f16` tags are #295's `D3Family(…, sums="f16")`:
  - each block value is fl16(h + e_b), one HADD2;
  - each cast is `cvt.rn.satfinite.e4m3x2.f16x2`;
  - block 3 keeps s = fl16(e + e∘π), as M4 does.
- The price row does not touch the law. Track A's headline numbers (0.82%, 0.73%, 0.71%) are the default `round9`
  row.

| Variant | Law | Cast per code | X_q unpack | Amplitude | f_a / f_b (Y16 copy, 32.11) | 16,384³ | 32,768³ |
|---|---|---:|---:|---|---:|---:|---:|
| `-f16` at `round9` (Track A's headline) | M2, s kept | 64 (with PRMT) | 48 | 2 HMNMX2 | 462.46 / 332 | 1.218% | 0.821% |
| M2q (Round 9) | M2, s dropped | 48 | 48 | 2 HMNMX2 | 396.46 / 266 | 1.087% | 0.755% |
| `-f16` at `round9-sass` (M2s) | M2, s kept | 32 | 32 | 1 VHMNMX | 334.46 / 236 | 0.995% | 0.709% |

- `round9` M2 = M2q + 18 (s) + 3 × 16 (a cast at 64 rather than 48), on each side.
- M2q's dropped s is Track A's candidate E, a change to block 3's rounding. The other two rows share one law.

**Track A's numbers reproduce** (`red-team-round9-readings.json`, "Track A's claims"):
- 0.8215% at 32,768 × 4,096 × 32,768;
- 405B gate/up at m = 32,768: 0.732%;
- the LM head as two units of 64,128 columns: 0.708%.

"Every cell with m, n ≥ 32,768 clears whatever k is" holds under `round9` M2 at FADD 32.11:
- The worst cell is D-3m X_q decoded at the smallest k (32), at 0.925%. At k ≥ 4,096, every D-3s cell is ≤ 0.853%.
- It holds only up to FADD ≈ 32.2; the thresholds at 32,768³ are 32.205–32.226.
- It does not hold under M4: 32,768³ decoded is 1.048%.

**Soundness.**
- **What changes.** Only the rounding of each block value before its cast. A, e, e2 and s are the same f16 values
  under both sums (s was already fl16 in M4), so the noise law's amplitude and its alignment to the cells are
  unchanged.
- **Checked numerics.** Forming is not credited (`credited = (0, 0)`), and the verifier re-forms with the tag's own
  sums. So the check stays exact for whichever law the tag names.
- **The code distributions** (every 8th f16 mantissa in [2⁻⁹, 448], both signs, 4,546 entries; blocks 1–2 over all
  1,024 words, block 3 over 1,024 × 16 pairs):

  | Amplitude | Block | Codes differing | Fewest codes per entry (f32 / f16) | Top-code probability (f32 / f16) | Largest increase | Total variation per entry (mean / max) |
  |---|---|---:|---|---|---:|---|
  | A = \|h\| | 1–2 | 0.336% | 2 / 2 | 0.6436 / 0.6445 | 0.0039 | 0.336% / 0.59% |
  | A = \|h\| | 3 | 0.336% | 4 / 4 | 0.7992 / 0.8000 | 0.0038 | 0.336% / 0.54% |
  | A = 2\|h\| | 1–2 | 0.337% | 2 / 2 | 0.5723 / 0.5723 | 0.0029 | 0.337% / 0.59% |
  | A = 8\|h\| | 1–2 | 0.249% | 3 / 3 | 0.5186 / 0.5186 | 0.0020 | 0.249% / 0.98% |
  | A = rms′ = 1/8, entries below it | 1–2 | 0.069% | 4 / 4 | 0.3760 / 0.3789 | 0.0029 | 0.069% / 0.49% |

  The JSON has the remaining block-3 rows; they are no worse. No entry's support shrinks. The largest top-code
  probability rises by at most 0.004, which is under 0.01 bit of min-entropy.
- **Only ties move.**
  - In blocks 1–2 at A = |h|, 2|h| and 8|h|, 42,928 codes differ. Each moves by exactly one step, with no sign flip.
  - In every one of them, fl16(h + e) sits exactly on an E4M3 midpoint. Double rounding can land on a tie, never cross
    one, so Track A's "the codes differ only at E4M3 ties" is right.
  - There is no f16 overflow (|h + e| ≤ 504) and no underflow to zero (h + e lies on the 2⁻²⁴ grid).
- **`DistinctLive`** (the spike witness at k = 4,096, 26 slices, 64 columns, 12 draws of root_A):
  - #295 with f16 sums gives 64 of 64 on every slice in all three blocks. With f32 sums it gives 64 on 25 slices of
    block 2 and 63 on one, the 12-draw coincidence of §5.2.
  - The control with F₁ keyed without root_A collapses to 3 in blocks 1–2 under both sums.
  - So f16 rounding merges neither words nor noise.

**Quality.**
- Track B measured this law, not M4:
  - `track_b_fp16_forming_quality.py`'s `form_xq` computes `(xh + e1).float()` on half operands, an f16 sum then a
    widen;
  - the lead noise-law results are labelled "H100 FP16 forming".
- M4 (f32 sums) is the unmeasured variant, and it is close:
  - it is 0.31–0.34% of codes away (Track B's own check on Qwen2.5-0.5B, `track_b_f16_block_sum_check.json`;
    0.07–0.34% here), one step at a tie;
  - Track B's §9.1 puts FP16 against FP32 forming at −0.06% ± 0.39% (C-2, Qwen 0.5B).
- No re-measure is needed to choose f16 sums.
- One caveat: Track B's harness is not bit-exact to #295. Its noise centre, (2·(raw ≫ 6) + 1)/1024 − 1, sits half a
  step from #295's 2t − 3, and its statistic prescale differs. A number for the `-f16` tags themselves needs #295's
  `D3Family` in the loop. That is cheap, and it does not block anything.

### E.3 Item 2: the four price items

| Item | Round 9 | Track A | ptxas 12.4.131 | ptxas 12.9.86 | Right on the compiled code | Static or timed | Alone, on `round9` M2 (Y16 copy, 32.11) |
|---|---|---|---|---|---|---|---|
| (a) four-code cast f16x2 → e4m3 | 64 per code (Round 8's single-cvt harness: a PRMT per F2FP); M2q 48 | 48 (12.4), 32 (12.9) | 2 F2FP…UNPACK_B_MERGE_C + 1 PRMT | 2 F2FP, no PRMT | Track A. 12.9 changes it; 12.4's is 48, not 64 | static; the rate of F2FP.E4M3.F16 alone is inferred (timed only beside its PRMT) | −96 per element per side: 1.027% at 16,384³, 0.725% at 32,768³ |
| (b) X_q unpack, four codes → two f16x2 | 48 per code | 32 | 2 UNPACK_B, the second reading `.H1`, no PRMT | the same | Track A, both versions. Round 9's PRMT came from its high-half chain | static; the `.H1` rate is untimed (`.H0` timed at 64) | −16 per X_q activation element and per decoded weight element; 0 on the Y16 copy cell |
| (c) partner and floor max | 2 HMNMX2 (64) | 1 VHMNMX (32 at 64 per instruction) | VHMNMX with abs lowered badly (4 HADD2 + 6 PRMT); with LOP3 masks, 2 LOP3 + 1 VHMNMX, no cheaper than two HMNMX2 | 1 VHMNMX, \|·\| folded | Track A for 12.9 | static; VHMNMX was never timed. Three f16x2 register sources | −32 per activation element: 1.186% / 0.805% |
| (d) widen of h (M4) | 600.5 at FADD 32 (omitted) | 664.79 at 32.11 (664.46 at 32) | 2 HADD2.F32 + 1 FADD per f32(a) + f32(b); 4 HADD2.F32 + 3 FADD per element for three blocks | the same | Track A (conceded in D.1) | static, at a timed rate (HADD2.F32 64, §14.5) | +64 per activation element and per decoded weight element, M4 only |

`round9-sass` is `round9` with (a), (b) and (c) together. Under 12.9 all three are facts of the compiled code, but none
of their rates has been timed.

**Chain shapes** (`red-team-round9-sass-probe.json`, 16 registers × 8-deep chains, both versions). A timing loop is a
chain, and the chain's shape decides whether the PRMT-free forms survive:
- **The cast pair** is PRMT-free under 12.9 only when both inputs are fresh every step. `cast4_chain_add_both` gives 256
  F2FP and no PRMT under 12.9, against 322 PRMT under 12.4.
  - With one input invariant (`cast4_chain_add`), ptxas hoists that input's cast (144 F2FP, not 256) and emits 112
    PRMT. XOR feedback does the same.
  - Even the f32 pair gains 119 PRMT in an XOR chain under 12.9.
  - The honest forming loop is the both-fresh shape: every block value is new.
- **The unpack** is PRMT-free under both versions when one register's two halves are consumed (`unpack4_chain`).
  Round 9's high-half chain (`unpack_hi_chain`) adds 112 PRMT per 128 under both versions, so that is where its 48 came
  from.
- **The VHMNMX chain** is clean under 12.9: 128 VHMNMX and nothing else. Under 12.4 it is 512 HADD2 + 891 PRMT beside
  the 128.

**What Round 10 must time** (built with ptxas 12.9; nvdisasm on each timed cubin must show the counted SASS):
1. **The four-code cast pair:** 2 × `F2FP.SATFINITE.E4M3.F16.UNPACK_B_MERGE_C`, no PRMT, both inputs fresh every step.
   It decides 96 per element per side under M2.
2. **`UNPACK_B` reading `.H1`**, in the four-code shape (both halves of one register). It decides 16 per X_q or
   decoded element.
3. **`VHMNMX` with |·| operands,** alone and beside forming's HADD2/HFMA2 (a three-source instruction, so the risk is
   register reads). It decides 32 per activation element; at 128 it saves nothing.
4. **The FADD class probe** (§2). Under `round9-sass` M2 with the copy, 16,384³ clears only while FADD ≤ 32.113. Under
   `round9` M2, it never clears at FADD ≥ 32 (threshold 31.967).
5. **Optional:** the D-3s M2 forming loop end to end, to check that the static count runs at the summed rates.

The widen of h needs no timing. The honest kernel must pin ptxas ≥ 12.9 and keep the centre's −3/8 and the field's
0x3C003C00 in registers for `round9-sass` to apply. Under 12.4, the matching row is `round9` with the cast at 48
(M2q's count).

### E.4 The lead cells under both readings

D-3s, r = 1. Each cell shows γ at FADD 32.00 / γ at 32.11 / the FADD threshold. The Y16 and X_q routes differ only
under `round9`.

| Reading, schedule, cell | f_a / f_b at 32.11 | 16,384³ | 32,768³ |
|---|---:|---|---|
| `round9` M4, Y16 copy | 664.79 / 470.33 | 1.388% / 1.556% / 31.747 | 0.822% / **0.992%** / 32.115 |
| `round9` M4, Y16 decoded | 664.79 / 582.33 | 1.499% / 1.667% / 31.674 | 0.879% / 1.048% / 32.079 |
| `round9` M4, X_q copy | 680.79 / 470.33 | 1.404% / 1.572% / 31.737 | 0.830% / **0.9999%** / 32.110 |
| `round9` M2, Y16 copy | 462.46 / 332 | 1.050% / 1.218% / 31.967 | 0.652% / **0.821%** / 32.226 |
| `round9` M2, Y16 decoded | 462.46 / 380 | 1.098% / 1.266% / 31.936 | 0.676% / **0.845%** / 32.211 |
| `round9` M2, X_q copy | 478.46 / 332 | 1.066% / 1.234% / 31.957 | 0.660% / **0.829%** / 32.221 |
| `round9-sass` M4, copy | 632.79 / 470.33 | 1.357% / 1.525% / 31.768 | 0.806% / **0.976%** / 32.126 |
| `round9-sass` M4, decoded | 632.79 / 566.33 | 1.452% / 1.620% / 31.705 | 0.855% / 1.024% / 32.094 |
| `round9-sass` M2, copy | 334.46 / 236 | 0.826% / **0.995%** / 32.113 | 0.539% / **0.709%** / 32.299 |
| `round9-sass` M2, decoded | 334.46 / 268 | 0.858% / 1.027% / 32.093 | 0.555% / **0.725%** / 32.289 |
| `round9-sass` M2, copy, VHMNMX at 128 | 366.46 / 236 | 0.858% / 1.027% / 32.093 | 0.555% / **0.725%** / 32.289 |
| `round9-sass` M2, copy, cast at 48 (12.4's) | 382.46 / 284 | 0.922% / 1.091% / 32.051 | 0.587% / **0.757%** / 32.268 |

- **16,384³:** only `round9-sass` M2 with the copy clears at 32.11, by 0.005 points, and only while FADD ≤ 32.113. It
  fails if VHMNMX runs at 128 or the cast keeps a PRMT.
- **32,768³:**
  - every M2 cell clears under both readings, D-3m included (thresholds ≥ 32.195);
  - M4 clears only with the copy: D-3s under both readings (thresholds 32.110–32.126), and D-3m only under
    `round9-sass` (0.992%);
  - D-3m adds 32 per activation element (the cell-width LOP3); its rows are in the JSON.

### E.5 Item 3: the serving-shape claim

**The correct statement.**
- F₁ reads root_A (a388ffc3), so r = 1. There is no weight epoch: forming's weight side is paid once per unit, and m
  is the rows of one unit, i.e. the tokens of one matmul in one forward step.
- At that unit's k, schedule and FADD price p, γ < 1% iff (n − n_min)(m − m_min) > n_min·m_min, with
  n_min = f_a(p)/B(p, k) and m_min = f_b(p)/B(p, k).
- A rectangle m ≥ M0, n ≥ N0 lies inside that region for every k ≥ K0 iff (N0 − n_min)(M0 − m_min) ≥ n_min·m_min, with
  the floors taken at K0. The square version is N0 ≥ n_min + m_min.
- So Track A's "m ≥ 32,768" is a valid domain together with n ≥ 32,768 (for every `-f16` cell at 32.11, under both
  readings). It is not the condition:
  - **Not necessary.** Under `round9` M2 at 32.11, 405B gate/up (n = 53,248) clears at m ≥ 12,608, and 70B gate_up at
    TP 1 at m ≥ 12,288. Under M4, the same 70B layer clears at m ≥ 20,032, which is my 20k.
  - **Not sufficient alone.** Under `round9` M2 at 32.11, 405B down (n = 16,384) needs m ≥ 48,064, and 405B gate_up at
    TP 8 (n = 13,312) needs 843k. Under M4, 405B down never clears.
- Both statements are right on their own terms. Mine is the exact condition, and Track A's is a sufficient square
  inside it.

**The floors** (D-3s Y16 copy; n_min / m_min, with the square floor in parentheses, at k → ∞; they rise by under 0.2%
at k = 4,096). N0 is the smallest n that makes m ≥ 32,768 sufficient, at k ≥ 4,096.

| Schedule | FADD 32.00 | FADD 32.11 | N0 at 32.00 / 32.11 |
|---|---|---|---|
| `round9` M4 | 14,618 / 10,340 (24,958) | 18,917 / 13,384 (32,301) | 21,398 / 32,029 |
| `round9` M2 (`-f16`) | 10,174 / 7,304 (17,478) | 13,160 / 9,447 (22,607) | 13,114 / 18,515 |
| `round9-sass` M4 | 13,914 / 10,340 (24,254) | 18,007 / 13,384 (31,390) | 20,367 / 30,486 |
| `round9-sass` M2 | 7,358 / 5,192 (12,550) | 9,517 / 6,716 (16,233) | 8,757 / 11,984 |

**The smallest m** (a multiple of 64) at 32.11, with 32.00 in parentheses. "—" means none within m ≤ 2¹⁶.

| Layer (k, n per GPU) | `round9` M4 | `round9` M2 | `round9-sass` M4 | `round9-sass` M2 |
|---|---:|---:|---:|---:|
| 405B gate or up, or gate_up at TP 2 (16,384, 53,248) | 20,800 (14,272) | 12,608 (9,088) | 20,288 (14,016) | 8,192 (6,080) |
| 405B gate_up, TP 8 (16,384, 13,312) | — | — (31,040) | — | 23,616 (11,648) |
| 405B o or down, any TP (2,048–53,248, 16,384) | — | 48,064–48,512 (19,328–19,456) | — | 16,064–16,128 (9,472) |
| 70B gate_up, TP 1 (8,192, 57,344) | 20,032 (13,952) | 12,288 (8,896) | 19,584 (13,696) | 8,064 (6,016) |
| 70B gate_up, TP 2 (8,192, 28,672) | 39,424 (21,184) | 17,536 (11,392) | 36,032 (20,160) | 10,112 (7,040) |
| LM head, two units of 64,128 (8,192 or 16,384, 64,128) | 19,008 (13,440) | 11,904 (8,704) | 18,624 (13,248) | 7,936 (5,888) |

**Serving caveats.**
- **m is capped by the step's token budget** (vLLM's `max_num_batched_tokens`). The repo's recorded workloads use
  2,048–29,304. Only long-prefill steps with a large budget reach 8k–20k, and decode steps never do (D.5).
- **The LM head in serving** computes logits only for the positions being sampled, so its m is the number of sequences
  in the step (hundreds). Track A's LM-head rows apply to training or prompt-logprob scoring, not to serving.
- **405B gate/up at n = 53,248 per GPU needs TP ≤ 2,** with pipeline parallelism for memory (FP8 405B is about 405 GB).
  At TP 8, fused gate_up clears only under `round9-sass` M2 (m ≥ 23,616).

### E.6 §3 log line (Track A's Round 9 claims)

- 20:25Z strike (bc-79ab9271): Track A's Round 9 claims (`genuine-fp8-red-team-round9.md` "Track A's Round 9 claims";
  `red-team-round9-readings`, `-f16-codes`, `-f16-witness` and `-sass-probe`, each `.py`/`.json`).
  - **`-f16`:**
    - It is #295's M2 law at the `round9` row: 462.46 / 332, 1.218% at 16,384³ and 0.821% at 32,768³. It is not M2q
      (M2q drops s), and it is the same law as `round9-sass`.
    - It is sound: 0.07–0.34% of codes move, one step, ties only; supports and amplitude are unchanged; the witness
      gives 64 of 64.
    - Track B measured FP16 forming, which is this law, so no re-measure is needed.
  - **Prices:** Track A is right on all four items. (a) and (c) are 12.9-only and (b) and (d) hold under both; all four
    are static counts, and (d)'s rate is timed.
    - Round 10 (ptxas 12.9, SASS-checked) must time the PRMT-free cast pair with both inputs fresh, `UNPACK_B .H1` in
      the four-code shape, `VHMNMX` with |·| operands, and the FADD class.
  - **Lead cells at 32.11, 16,384³ / 32,768³, D-3s Y16 copy:**
    - `round9`: M4 1.556% / 0.992%, M2 1.218% / 0.821%;
    - `round9-sass`: M4 1.525% / 0.976%, M2 0.995% / 0.709%.
  - **Shapes:** the condition is (n − n_min)(m − m_min) > n_min·m_min, with m the unit's tokens (r = 1).
    - m ≥ 32,768 is sufficient only with n ≥ 18.5k (`round9` M2, 32.11). 405B gate/up clears at m ≥ 12.6k and 70B
      gate_up at 12.3k (M2), or 20.0k under M4.
    - The LM head's serving m is the number of sequences.

## Decoded-weight cells (Daniel 20:31Z)

Written 20:32Z to 21:05Z, CPU only. Daniel's rulings of 20:31Z:
- no weight copy of any kind: weights are decoded from their FP8 codes per unit;
- ptxas ≥ 12.9 for the honest kernel;
- 16,384³ stays the target.

This section re-states every FP8 cell under them. The script is `red-team-round9-decoded.py` and its `.json` is the
machine-readable grid. It needs #295 (f31ad2dd) on `PYTHONPATH`, and `red-team-round9-shapes.py` and
`red-team-round9-gamma.py` beside it. Its checks:
- `round9` with VHMNMX at 128 prices every cell exactly as #295's `round9` row does with two HMNMX2;
- D-3s M4 Y16 decoded is #295's 664.79 / 582.33;
- H-1's f_a is Phase 19's 318.5 (X_q) and 270.5 (Y16), and its lead is 0.902% at 16,384³.

### F.1 Verdict

1. **At 16,384³, no D-3 cell under #295's law clears at FADD 32.11, under either reading.**
   - Under `round9-sass`, every M2 cell (D-3s and D-3m, either route) clears at FADD 32.00. The target, D-3s M2 on X_q,
     is 0.858% at 32.00 and 1.027% at 32.11, clearing while FADD ≤ 32.093.
   - Under `round9`, no D-3 cell clears at any FADD ≥ 32. The best is D-3s M2q on Y16, at 1.062% at 32.00.
   - The only D-3 cells below 1% at 32.11 are D-3s M2q under `round9-sass` with the amplitude registered: 0.991%,
     threshold 32.116. M2q is an unreviewed law change.
   - Withdrawing the copy cost the target its one clearing D-3 cell: D-3s M2 went from 0.995% to 1.027% at 32.11, and
     its threshold from 32.113 to 32.093.
2. **H-1 (B = 2, hybrid floor) clears every size at both FADD prices under both readings.** On X_q at 16,384³ it is
   0.902% under `round9` and 0.781% under `round9-sass`, with thresholds 32.174 and 32.252. This is conditional on the
   F19-2 repair and on clauses against `barrier`'s families A and B (the ±b pair, and P4-legal FP32 absorption;
   `lean-atom-scope.md` §5.1).
3. **D-4 (32,768³ and 65,536³):**
   - every M2 and M2q cell clears at FADD 32.11 under both readings, with the amplitude registered or per unit;
   - M4 clears 65,536³ in every cell;
   - M4 clears 32,768³ only at FADD 32.00 (thresholds 32.03–32.094). The copy cells that cleared it (0.976–0.9999%)
     are gone.
4. **A remaining per-weight table: #295's decoded pricing still registers the weight side's amplitude per element.**
   - What it registers: the partner and floor maxima, and D-3m's cell widths ("registered offline", `d3_trace`'s
     docstring).
   - As f16, that is 2 bytes per weight, the size of an FP16 copy.
   - Under "no copies of any kind", the weight side forms it per unit. That costs +64 (`round9`) or +32
     (`round9-sass`) per weight element for D-3s, and +96 or +64 for D-3m.
   - The grid shows both treatments (F.3, F.4). With the Track A rates confirmed, the strict treatment changes one
     verdict: D-3s M2q at 16,384³ and 32.11 goes from 0.991% to 1.023%. It also moves the target's threshold from
     32.093 to 32.072.
   - **Daniel should rule on it.** Per-column statistics (rms′, σ₈: n values per matrix) are not copies.
5. **What Round 10 decides now,** and whether anything can be dropped:
   - the PRMT-free cast and the FADD class decide the target;
   - VHMNMX and `.H1` move the target's threshold by about 0.02 each;
   - no row existed only for a weight copy, so none is dropped (F.6).

### F.2 The prices

- **`round9`** is #295's `PRICES["round9"]` with VHMNMX at 128, which is the same 64 per element as two HMNMX2. The
  cast is 64 per code (with its PRMT) and the unpack 48 per code.
- **`round9-sass`** is `PRICES["round9-sass"]`: the cast and unpack at 32 per code, VHMNMX at 64.
- **Decoding** costs the unpack per weight element (48 or 32), plus M4's widen (64).
- **M2q** is now #295's M2 with s dropped, −18 per side at each reading. My Round 9 M2q priced the cast at 48 (12.4's
  pair). With ptxas ≥ 12.9 that count is moot.
  - M2q is still meaningful only as Track A's candidate E, a law change: block 3 rounds v₁ + e∘P, so v₁'s rounding
    enters block 3.
  - It needs `DistinctLive` and a quality run before it counts. It is the only D-3 route to 16,384³ at 32.11, and only
    with the amplitude registered.
- **H-1's `round9-sass` repricing is mine.** Its two f16 → e4m3 casts go from 64.1 to 32 per code: x₁ and x₂ each
  fill four-code registers with both inputs fresh, which is the PRMT-free shape. The unpack goes from 48 to 32. Its
  HMNMX2s, LOP3, HFMA2 and HMUL2 stay at Phase 19's prices. H-1 has no weight forming (f_b = 0).

### F.3 The grid, weight amplitude registered (#295's decoded pricing)

Each size shows γ at FADD 32.00 / γ at 32.11, with the FADD threshold in parentheses. **Bold** means γ < 1% at that
FADD. The two routes price alike under `round9-sass` (the unpack and the Y16 pack are both 32).

| Cell | f_a / f_b at 32.11 | 16,384³ | 32,768³ | 65,536³ |
|---|---:|---|---|---|
| `round9` D-3s M4, X_q | 680.79 / 582.33 | 1.515% / 1.683% (31.664) | **0.886%** / 1.056% (32.074) | **0.569%** / **0.740%** (32.279) |
| `round9` D-3s M4, Y16 | 664.79 / 582.33 | 1.499% / 1.667% (31.674) | **0.878%** / 1.048% (32.079) | **0.565%** / **0.735%** (32.282) |
| `round9` D-3s M2, X_q | 478.46 / 380.00 | 1.114% / 1.282% (31.926) | **0.684%** / **0.853%** (32.205) | **0.467%** / **0.638%** (32.345) |
| `round9` D-3s M2, Y16 | 462.46 / 380.00 | 1.098% / 1.266% (31.936) | **0.676%** / **0.845%** (32.211) | **0.463%** / **0.634%** (32.348) |
| `round9` D-3s M2q, X_q | 460.46 / 362.00 | 1.078% / 1.246% (31.949) | **0.666%** / **0.835%** (32.217) | **0.458%** / **0.629%** (32.351) |
| `round9` D-3s M2q, Y16 | 444.46 / 362.00 | 1.062% / 1.230% (31.960) | **0.658%** / **0.827%** (32.222) | **0.454%** / **0.625%** (32.354) |
| `round9` D-3m M4, X_q | 712.79 / 582.33 | 1.547% / 1.714% (31.643) | **0.903%** / 1.072% (32.063) | **0.577%** / **0.748%** (32.274) |
| `round9` D-3m M4, Y16 | 696.79 / 582.33 | 1.531% / 1.698% (31.653) | **0.894%** / 1.064% (32.068) | **0.573%** / **0.744%** (32.277) |
| `round9` D-3m M2, X_q | 510.46 / 380.00 | 1.146% / 1.314% (31.905) | **0.700%** / **0.869%** (32.195) | **0.475%** / **0.646%** (32.340) |
| `round9` D-3m M2, Y16 | 494.46 / 380.00 | 1.130% / 1.298% (31.915) | **0.692%** / **0.861%** (32.200) | **0.471%** / **0.642%** (32.343) |
| `round9` D-3m M2q, X_q | 492.46 / 362.00 | 1.110% / 1.278% (31.928) | **0.682%** / **0.851%** (32.207) | **0.466%** / **0.637%** (32.346) |
| `round9` D-3m M2q, Y16 | 476.46 / 362.00 | 1.094% / 1.262% (31.939) | **0.674%** / **0.843%** (32.212) | **0.462%** / **0.633%** (32.348) |
| `round9-sass` D-3s M4, X_q = Y16 | 632.79 / 566.33 | 1.452% / 1.619% (31.705) | **0.855%** / 1.024% (32.094) | **0.553%** / **0.723%** (32.290) |
| `round9-sass` D-3s M2, X_q = Y16 | 334.46 / 268.00 | **0.858%** / 1.027% (32.093) | **0.555%** / **0.725%** (32.289) | **0.403%** / **0.573%** (32.387) |
| `round9-sass` D-3s M2q, X_q = Y16 | 316.46 / 250.00 | **0.822%** / **0.991%** (32.116) | **0.537%** / **0.707%** (32.300) | **0.394%** / **0.564%** (32.393) |
| `round9-sass` D-3m M4, X_q = Y16 | 664.79 / 566.33 | 1.484% / 1.651% (31.685) | **0.871%** / 1.040% (32.084) | **0.561%** / **0.731%** (32.284) |
| `round9-sass` D-3m M2, X_q = Y16 | 366.46 / 268.00 | **0.890%** / 1.059% (32.072) | **0.571%** / **0.741%** (32.278) | **0.411%** / **0.581%** (32.382) |
| `round9-sass` D-3m M2q, X_q = Y16 | 348.46 / 250.00 | **0.854%** / 1.023% (32.095) | **0.553%** / **0.723%** (32.290) | **0.402%** / **0.572%** (32.387) |

### F.4 The grid, weight amplitude formed per unit (X_q; Y16 is in the JSON)

| Cell | f_a / f_b at 32.11 | 16,384³ | 32,768³ | 65,536³ |
|---|---:|---|---|---|
| `round9` D-3s M4, X_q | 680.79 / 646.33 | 1.579% / 1.746% (31.622) | **0.919%** / 1.088% (32.053) | **0.585%** / **0.755%** (32.269) |
| `round9` D-3s M2, X_q | 478.46 / 444.00 | 1.178% / 1.346% (31.884) | **0.716%** / **0.885%** (32.185) | **0.483%** / **0.654%** (32.335) |
| `round9` D-3s M2q, X_q | 460.46 / 426.00 | 1.142% / 1.310% (31.908) | **0.698%** / **0.867%** (32.196) | **0.474%** / **0.645%** (32.341) |
| `round9` D-3m M4, X_q | 712.79 / 678.33 | 1.642% / 1.809% (31.581) | **0.951%** / 1.120% (32.032) | **0.602%** / **0.772%** (32.258) |
| `round9` D-3m M2, X_q | 510.46 / 476.00 | 1.241% / 1.409% (31.842) | **0.748%** / **0.917%** (32.164) | **0.500%** / **0.670%** (32.324) |
| `round9` D-3m M2q, X_q | 492.46 / 458.00 | 1.206% / 1.373% (31.866) | **0.730%** / **0.899%** (32.175) | **0.490%** / **0.661%** (32.330) |
| `round9-sass` D-3s M4, X_q = Y16 | 632.79 / 598.33 | 1.484% / 1.651% (31.685) | **0.871%** / 1.040% (32.084) | **0.561%** / **0.731%** (32.284) |
| `round9-sass` D-3s M2, X_q = Y16 | 334.46 / 300.00 | **0.890%** / 1.059% (32.072) | **0.571%** / **0.741%** (32.278) | **0.411%** / **0.581%** (32.382) |
| `round9-sass` D-3s M2q, X_q = Y16 | 316.46 / 282.00 | **0.854%** / 1.023% (32.095) | **0.553%** / **0.723%** (32.290) | **0.402%** / **0.572%** (32.387) |
| `round9-sass` D-3m M4, X_q = Y16 | 664.79 / 630.33 | 1.547% / 1.714% (31.643) | **0.903%** / 1.072% (32.063) | **0.577%** / **0.748%** (32.274) |
| `round9-sass` D-3m M2, X_q = Y16 | 366.46 / 332.00 | **0.954%** / 1.123% (32.030) | **0.603%** / **0.773%** (32.257) | **0.427%** / **0.597%** (32.371) |
| `round9-sass` D-3m M2q, X_q = Y16 | 348.46 / 314.00 | **0.918%** / 1.087% (32.053) | **0.585%** / **0.755%** (32.269) | **0.418%** / **0.588%** (32.377) |

### F.5 H-1, B = 2, hybrid floor (conditional: F19-2 repair, `barrier`'s families A and B)

Phase 19's credit is 32(2BT − 1) with T = k/32, and W_ref is 32BT + p(BT − 1) + f_a.

| Cell | f_a | 16,384³ | 32,768³ | 65,536³ |
|---|---:|---|---|---|
| `round9` H-1, X_q | 318.5 | **0.733%** / **0.902%** (32.174) | **0.492%** / **0.662%** (32.329) | **0.371%** / **0.542%** (32.407) |
| `round9` H-1, Y16 | 270.5 | **0.660%** / **0.830%** (32.221) | **0.456%** / **0.626%** (32.353) | **0.353%** / **0.524%** (32.419) |
| `round9-sass` H-1, X_q | 238.3 | **0.612%** / **0.781%** (32.252) | **0.431%** / **0.602%** (32.369) | **0.341%** / **0.511%** (32.427) |
| `round9-sass` H-1, Y16 | 206.3 | **0.563%** / **0.733%** (32.283) | **0.407%** / **0.577%** (32.384) | **0.328%** / **0.499%** (32.435) |

The row floor, B = 3 and Phase 19's other cells are in Phase 19 at `round9`. Every one of them clears 16,384³ there.

### F.6 What Round 10 now decides (`internal/pouw/gpu-constants.md` §15.7)

**At 16,384³, the target:**
1. **The PRMT-free four-code cast is decisive.** It is the row "four-code f16x2 cast by 12.9 at 128 per register".
   Without it, no D-3 cell clears at any FADD ≥ 32: the target is 1.050% at 32.00, threshold 31.967.
2. **The FADD class is decisive.** With the three Track A rates confirmed, every D-3 M2 cell clears at 32.00 and fails
   at 32.11. The thresholds are 32.093 (D-3s, amplitude registered), 32.072 (D-3s per unit, or D-3m registered) and
   32.030 (D-3m per unit).
   - The FADD outcome that saves D-3 is "clock bias" (the class price is 32.00).
   - "A loop-size artifact" does not save it: by §15.7 the honest n128 A = 2 loop is about 9 KB and pays the larger
     price, and the forming loop is larger still.
3. **`VHMNMX` at 64 and `UNPACK_B .H1` at 64 each move the target's threshold by 0.021.** They decide only if FADD
   lands between about 32.03 and 32.09.
   - At FADD 32.00, D-3s M2 on X_q clears even with both at their `round9` values: 0.922% registered, 0.986% per unit.
   - D-3m M2 per unit is the exception. At 32.00 it fails if VHMNMX runs at 128 (1.018%) or if both are unconfirmed
     (1.050%). With only the unpack at 48, it still clears (0.986%).
   - Registered, D-3m M2 clears at 32.00 even with both unconfirmed (0.954%).
   - With decoded weights, the unpack row now matters for every D-3 cell (16 per weight element), not only for the
     X_q and decoded ones.
4. **H-1 needs no Round 10 row** for its verdict. Its lead threshold is 32.174 at `round9`. The PRMT-free cast widens
   its margin (0.902% to about 0.78%).
   - The H-1 forming kernel being added to Round 10 (`round10-package.md`) should be read against 238.3 under ptxas
     12.9, not only against 318.5.

**At D-4 sizes:**
- M2 and M2q clear 32,768³ and 65,536³ at 32.11 under both readings, so Round 10 decides nothing there.
- M4 at 32,768³ is decided by the FADD class: thresholds 32.063–32.094 with the amplitude registered, 32.032–32.084
  per unit.

**Rows to drop:**
- **None.** No Round 10 row mattered only for a weight copy. Every row prices an instruction that decoded cells use too
  (casts, unpack, amplitude, FADD, the pipelined step), and the copy's own cost was never a row. This agrees with
  `round10-package.md`.
- **Two notes now that ptxas ≥ 12.9 is approved:**
  - The `x124` twins (12.4 builds) no longer decide a price; they remain a compiler cross-check.
  - A failed 12.9 fetch should now mean relaunching, not falling back. Without the 12.9 rows the target's verdict is
    undecided.

### F.7 §3 log line (decoded-weight cells)

- 21:05Z strike (bc-79ab9271): decoded-weight cells under Daniel's 20:31Z rulings (`genuine-fp8-red-team-round9.md`
  "Decoded-weight cells (Daniel 20:31Z)"; `red-team-round9-decoded.py`/`.json`).
  - **16,384³:**
    - no D-3 cell under #295's law clears at FADD 32.11 under either reading;
    - under `round9-sass`, every D-3 M2 cell clears at 32.00 (target D-3s M2 X_q 0.858% / 1.027%, threshold 32.093);
    - under `round9`, none clears at any FADD ≥ 32;
    - only M2q (s dropped, unreviewed) clears at 32.11: 0.991% at `round9-sass`, amplitude registered;
    - H-1 clears: X_q 0.902% at `round9`, 0.781% at `round9-sass` (conditional: F19-2 and `barrier`'s families A, B).
  - **D-4:** every M2 and M2q cell clears 32,768³ and 65,536³ at 32.11; M4 clears 32,768³ only at 32.00.
  - **Finding:** #295's decoded pricing still registers the weight amplitude per element (2 bytes per weight, the size
    of an FP16 copy). Forming it per unit costs +32 to +96 per weight element, moves the target's threshold from
    32.093 to 32.072, and takes M2q at 32.11 to 1.023%. Daniel should rule on it.
  - **Round 10:** the PRMT-free cast and the FADD class decide 16,384³; VHMNMX and `.H1` move the threshold by 0.02
    each. No row existed only for a copy, so none is dropped.

## Frontier restatement (Daniel 20:41Z)

Re-issued 21:10Z to 21:35Z, CPU only. Added since:
- 22:05Z: the centre HFMA2 note (G.6);
- 22:10Z to 00:40Z: Track H's credit correction, H-1T and the as-built FADD (G.2, G.4, G.7–G.8);
- 23:55Z to 00:40Z: A6, transcript hashing and the XOF (G.9);
- **04:00Z to 04:45Z: the Round 11 re-issue** (this issue, the requester's 04:00Z item).

This issue re-prices every table at Round 11's measured values (`internal/pouw/gpu-constants.md` §18; run
r20260929-033625-cb6e, with pod 1's partial r20260929-032519-dff5). It replaces the 00:40Z issue, whose headline was γ
at FADD 32.00 under `round10`, with D-3 as built at 32.05. What changed:
- **γ is read at each design's FADD, measured or predicted.** No Round 11 row times the adds apart from the atoms, so
  the FADD is §16.3's sweep at the design's loop (G.8):
  - D-3: **32.0118**, the dflow lead n64 A = 5 U = 2 (371 instructions, 0 of 320 FADDs same-bank; §17.3 @13), whose
    step is timed at 52.67 per add word (§18.3). The JSON also reads every D-3 cell at A = 4 U = 2's 32.0076 and at
    32.00.
  - H-1T: **32.0075**, `h1r_step` (282 and 281 instructions, 0 of 512). Its launch failed on both pods (§18.2), so the
    step is untimed and its FADD stays the sweep's prediction.
  - The n128 A = 2 U = 4 loop (567 instructions, 32.05) is retired as D-3's step.
- **Prices: `round11`,** which is `round10` with §18.4's instruction forms:
  - the centre as compiled (the split form: two registers and an immediate) at 64.00 per register, 32.0 per element.
    **The centre is settled as `imm`,** and the `split36` alternative is gone (G.6);
  - HADD2 a + b and HMUL2 a·b at 36.12 per register (ptxas puts half on HFMA2.MMA), HMUL2 a·K at 32.26, LOP3 at 64.14;
  - the sum-of-squares HFMA2 (h·h + ss) stays in the two-source class at 36.12. Pricing it as the timed
    three-register HFMA2 (60.57) is sensitivity (e), the one open pricing choice left (G.6);
  - `round11` prices D-3s M2 X_q at 351.22 per element per side at FADD 32.00, against 350.76 at `round10`.
  - The forming stays 12.9's compiled count (the requester, 04:00Z): pod 2's builds are 12.4, and the 12.9 `dstep` and
    `form` rows were lost with pod 1 (§18.3).
- **H-1T's f_a is timed** (§18.2, ptxas 12.9): `h1t_form_xq` at **260.75** per real element and `h1t_form_y16` at
  218.02, against Track H's model at 297.6. The row carries 16 IMAD.MOV per loop, 10 more than Track H's kernel, so
  260.75 is an upper bound for Track H's own moves. Track H's model and the 12.4 build (360.15) are now sensitivities.
  The 00:40Z high and low readings of HFMA2.MMA and HADD2 are retired, since the timed row is H-1T's own mix.
- **Real time against plain FP8 is a new table** (G.2): Track C's accounting at the timed dflow steps for D-3s, and at
  `h1r_step`'s shape (57.11 per add word) for H-1T.
- **A6 is at the measured h** (G.9): SHAKE256 (2,290.6 for the digest from registers, with 2,476.5 from L2 as a
  sensitivity; 2,199.2 for the noise), TurboSHAKE128 (826.3) and the SHA-256 tree (1,418.9). The break-even e is set
  against each build's own gap to its prediction.
- **B's combined variant is re-priced** (G.9.1) at H-1T's timed f_a and its step shape's tensor share.
- Posted H-1 (superseded since 00:40Z) is no longer re-priced.

The script is `red-team-round9-frontier.py` (`[--sass h1_kernel.sass] [--md] [out.json]`).
- `--fadd`, `--centre`, `--hash-units-per-byte` and `--sha256-tree-units-per-byte` are gone. The FADD is per design,
  the centre is settled, and the hash rates are Round 11's rows (`HASH`, each with its build's prediction).
- `--sass` records `h1r_step`'s two loops from Track H's SASS. It asserts that each is at most 390 instructions and has
  no same-bank FADD.
- `--md` prints the tables below.
- Its `.json` holds every cell, with γ at the design's FADD, at 32.00 and, for D-3, at 32.0076: both routes, every
  treatment and reading, the grids, the real-time table, the note's numbers, the credit correction before and after,
  A6's rows with their B, h and undercut readings, B's combined variant, and X-SPW.
- It loads `red-team-round9-decoded.py` beside it and needs #295 (f31ad2dd) on `PYTHONPATH`.
- **Checks** (`checks()` asserts each):
  - D-3: the default treatment at `round9-sass` with #295's 256-entry chain reproduces `docs/pouw-fp8/h100-scheme.md`
    §6.4's `d3s-v0-f16` row (5.566 / 3.058 / 1.757 / 1.093 / 0.758% at 32.11, threshold 32.049 at 16,384³);
  - `round10`'s target reproduces §18.3's 0.9751% at 32.0118 and 0.9687% at 32.0076, and §17.3's 1.0330% at
    32.0495 (threshold 32.028);
  - `round11` prices D-3s M2 X_q at 351.223 per element at FADD 32.00 (`round10`: 350.757);
  - H-1T, Track H's model: `h1-sass-counts.json`'s counts give f_a 297.6 / 363.8 / 263.8, and `gamma-h1t.json`'s
    headline entries match;
  - real time: Track C's published 5.2768× and 5.2372× (p 55.44, 336.71 per side) and its 5× step prices, 52.48 and
    52.91;
  - A6: 3,071 checked words per output at k = 16,384 (0.75 B per MAC), SHAKE256's old derivation (2,029.2), and the
    SHA-256 tree at 1,418.9 from Round 11's rows;
  - B's combined variant: `a6-combined.json`'s W1, capped time, credited γ, mix undercut and H-1T γ at 8,192 and
    16,384 (worst ε).
- **The lane chain** is min(256, k/64) entries, and **Y16** is within 0.001 points of X_q; its rows are in the JSON.

### G.1 Verdict

1. **The target clears at its lead loop's FADD.** D-3s M2, X_q, decoded, default weight side, at 16,384³ is **0.976% at
   32.0118** (the dflow A = 5 U = 2 lead), **threshold 32.027‡**. It is 0.970% at A = 4 U = 2's 32.0076 and 0.958% at
   32.00.
   - The margin is 0.015 of FADD, against a four-digit sweep prediction: no row times the adds apart from the atoms.
   - The centre is settled at 64.00 per register (§18.4), so the 00:40Z `split36` reading (0.929%) is out.
   - **Open: the sum of squares** (G.6). Priced as the three-register HFMA2 (60.57), the target is 1.0005% (32.011‡)
     at 32.0118 and fails. It clears at A = 4's 32.0076 (0.994%), and with the rms′ cache as well (0.954%, 32.042‡).
   - **Real time is 4.979×** at A = 5's 52.67, under 5× by 0.4%. That is inside §16.4's 0.5% run-to-run band. A = 4's
     53.12 gives 5.022× (G.2).
2. **Nothing clears 8,192³ at γ₀ = 1/400,** D-3 or H-1T. The best are H-1T on Y16 (1.034%), H-1T on X_q (1.150%), D-3s
   M2q (1.604%) and the target (1.676%). H-1T at γ₀ = 0 (the Lean target) clears 8,192³: **0.902% (32.071)**, now with
   margin.
3. **At 16,384³:**
   - D-3s M2 clears (0.976%, 32.027‡), and so does D-3s M2q (0.940%, 32.051). M2q is still the unreviewed candidate E.
   - **D-3m M2q now fails:** 1.004% (32.009‡). It clears at A = 4's 32.0076 (0.998%). D-3m M2 fails (1.040%, 31.986),
     and M4 fails for both laws.
   - H-1T clears: 0.708% (32.197) on X_q, 0.799% with F19-3's fix and 0.650% on Y16.
4. **At 32,768³ every cell clears.** The closest is D-3m M4 at 0.955% (32.041‡).
5. **The target's grid** clears only where m and n are both at least 16,384. Only the square 16,384 × 16,384 needs the
   knee (32.027‡); 16,384 × 32,768 has threshold 32.142.
6. **Verdicts that flip against the 02:51Z tables** (`round10`, γ at 32.00, D-3 as built at 32.05, H-1T at 32.00):
   - **Failing as built, now clearing** (threshold in [32.0118, 32.05)):
     - the target at 16,384³, X_q and Y16 (1.034% at 32.05 → 0.976%), and the grid's 16,384 square;
     - D-3m M4 at 32,768³ (1.013% → 0.955%);
     - sensitivities: (a) D-3m M2q at 16,384³ (1.027% → 0.970%); (c) D-3s M2 (1.001% → 0.943%) and D-3m M2q
       (1.029% → 0.971%) at 16,384³; (d) with two HMNMX2, D-3s M4 (1.012% → 0.953%) and D-3m M4 (1.044% → 0.986%) at
       32,768³.
   - **Clearing at 32.00, now failing** (threshold in (32.00, 32.0118); all were already failing as built at 32.05):
     - D-3m M2q at 16,384³ (0.985% → 1.004%);
     - (a) D-3m M2 (0.987% → 1.006%) and (c) D-3m M2 (0.988% → 1.006%) at 16,384³;
     - (b)'s grid cell m = 8,192, n = 32,768 (0.997% → 1.016%, threshold 32.001‡).
   - **H-1T, γ₀ = 0 at 8,192³** was 0.991% at 32.00 but failed at the sweep's 32.0075 (1.002%) and at the high reading
     (1.022%). At the timed f_a it is 0.902% (32.071). Of G.4's readings, it fails only under the 12.4 build (1.172%)
     and Track H's model (1.002%).
   - **D-3s real time at 8,192³** was 4.981× staged (A = 4 U = 2 at Track C's 52.23). Timed, it is 5.021× at A = 5
     and 5.063× at A = 4: now over 5×. At 16,384³ it goes from 4.939× to 4.979× (A = 5), still under, and 5.022×
     (A = 4), now over.
   - **A6:** no γ′ flips at the nominal h. But the condition the hashed rows held on, that the measured h is the
     fastest build anyone knows, now fails for SHAKE256 (item 8).
7. **Sensitivities at 16,384³ for the target** (G.4):
   - (a) the rms′ cache: 0.942% (32.050‡);
   - (b) the amplitude table: 0.908% (32.072);
   - `round10`: 0.975% (32.028‡); (c) `round9-sass`: 0.943% (32.049‡);
   - (d) the 12.4 builds: 1.530% with the 529 amplitude and 1.132% with two HMNMX2, both failing;
   - (e) the sum of squares at 60.57: 1.0005% (32.011‡), failing.
   - H-1T X_q under Track H's model is 0.758% at 16,384³ and 1.250% at 8,192³; under the 12.4 build, 0.844% and
     1.419%. H-1T must be a 12.9 build too (§18.2).
8. **A6 at the measured h** (G.9):
   - **Without hashing:** at 8,192³ NCP-FP8 is 5.021× (5.063× at A = 4) with γ 1.676%, and H-1T is 3.975× at its step
     shape (4.450× additive) with γ 1.150%; neither clears. At 16,384³: 4.979× (5.022×) and 0.976%; 3.953× (4.429×)
     and 0.708%.
   - **With SHAKE256:** NCP-FP8 is 1,722.9× at both sizes, and H-1T 1,269.6× (8,192³) and 1,267.6× (16,384³); γ′ is
     0.0025–0.0059%.
   - **With TurboSHAKE128:** 624.7× and 460.5× (8,192³), 624.7× and 459.8× (16,384³); γ′ 0.0068–0.0163%.
   - **The break-even e is 0.993–1.003% in every hashed cell.**
   - **The SHAKE256 build is 8.06% over its own prediction** (the digest from registers; Keccak-f is 7.9% over), so
     the measured h is not the adversary's minimum. An adversary who reaches the prediction gets γ′ = 8.03% in every
     SHAKE256 cell: those rows fail. TurboSHAKE128's build is 0.28% over its prediction (γ′ 0.28–0.29%, clearing), and
     SHA-256's beats its prediction.
   - Every hashed row still assumes no mixed ALU + FMA build exists. At that 23.8% bound, γ′ is 23.6–23.7%.
9. **B's combined variant** (G.9.1), re-priced at f_a 260.75 and the 56.03% share:
   - its credited γ goes from 0.935% to 0.857% at 8,192³ and from 0.532% to 0.494% at 16,384³;
   - its capped time goes from 3.83× to 3.95× and 3.94×, and W1 / k is 5.56× and 5.53×;
   - its mix undercut to 1% widens, 0.13% → 0.29% and 0.94% → 1.02%.
   - No verdict flips: the credited γ clears at both sizes, and the uncredited reading (50.6%) and the H32 floor
     (25.7%) fail, as before.

### G.2 Headline: `round11`, default weight side (no table, no rms′ cache), γ at the design's FADD (FADD threshold)

**Bold** means γ < 1%. **‡** marks a threshold in [32.00, 32.05), which needs a loop under the knee (≤ 390
instructions) with bank-clean SASS (§16.3: 17% same-bank pairs cost 34.7–36.1). Both designs' loops are (G.8). **FADD**
is the design's loop at §16.3's sweep. D-3 credits 2T − 1 words and H-1T 4T − 3 (G.7).

| Cell | FADD | 2,048³ | 4,096³ | 8,192³ | 16,384³ | 32,768³ |
|---|---:|---|---|---|---|---|
| D-3s M4, X_q | 32.0118 | 9.853% (25.858) | 5.285% (29.136) | 2.837% (30.801) | 1.568% (31.641) | **0.922%** (32.062) |
| D-3s M2, X_q | 32.0118 | 5.712% (28.782) | 3.051% (30.646) | 1.676% (31.568) | **0.976%** (32.027‡) | **0.623%** (32.256) |
| D-3s M2q, X_q | 32.0118 | 5.448% (28.971) | 2.913% (30.740) | 1.604% (31.615) | **0.940%** (32.051) | **0.605%** (32.268) |
| D-3m M4, X_q | 32.0118 | 10.277% (25.532) | 5.520% (28.971) | 2.961% (30.718) | 1.632% (31.599) | **0.955%** (32.041‡) |
| D-3m M2, X_q | 32.0118 | 6.176% (28.446) | 3.297% (30.478) | 1.802% (31.485) | 1.040% (31.986) | **0.656%** (32.235) |
| D-3m M2q, X_q | 32.0118 | 5.915% (28.635) | 3.159% (30.573) | 1.731% (31.532) | 1.004% (32.009‡) | **0.637%** (32.247) |
| H-1T X_q, f_a 260.75 | 32.0075 | 3.738% (30.180) | 2.021% (31.336) | 1.150% (31.910) | **0.708%** (32.197) | **0.485%** (32.341) |
| H-1T X_q, γ₀ = 0 (the Lean target), f_a 260.75 | 32.0075 | 3.497% (30.341) | 1.776% (31.498) | **0.902%** (32.071) | **0.459%** (32.359) | **0.236%** (32.503) |

- **H-1T** is Track H's §3.1 design: 29 real and 3 tag lanes per k32 slice, T = ceil(k/29). Its f_a is `h1t_form_xq`
  as compiled by 12.9 and timed (§18.2). It forms no weight-side noise (B′'s tag rows are fixed), so no weight-side
  treatment applies. With F19-3's literal fix (+2 ops per real register, f_a 326.96) it is a sensitivity row (G.4).
- **The γ₀ = 0 row** is the value once the Lean proof of the cross-column R words lands (Track H §5.3); until then
  ε = γ₀ = 1/400.
- The JSON holds each cell at 32.00 too and, for D-3, at A = 4 U = 2's 32.0076.

**Real time against plain FP8** (Track C's accounting, forming serial):

| Size | D-3s forming f_a + f_b | D-3s at 52.67 (dflow A = 5 U = 2, the lead) | D-3s at 53.12 (dflow A = 4 U = 2) | D-3s step price for 5× | D-3s step price for 5×, (e) | H-1T at 57.11 (h1r_step's shape; the step untimed) | H-1T additive W1 / k |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2,048³ | 707.7 | 5.2733× | 5.3152× | 49.74 | 49.612 | 4.0748× | 4.5497× |
| 4,096³ | 704.7 | 5.1048× | 5.1469× | 51.549 | 51.485 | 4.0173× | 4.4939× |
| 8,192³ | 703.2 | 5.0211× | 5.0633× | 52.444 | 52.412 | 3.9746× | 4.4503× |
| 16,384³ | 702.45 | **4.9794×** | 5.0216× | 52.89 | 52.874 | 3.9532× | 4.4285× |
| 32,768³ | 702.45 | **4.9586×** | 5.0008× | 53.112 | 53.104 | 3.9461× | 4.4216× |

- **The model.** D-3s is ((T − 1)p + 32)/k + f_a/n + f_b/m, with p the step's timed price per add word (§18.3) and the
  forming at 12.9's compiled count. The dflow rows are 12.4 builds of 12.9's SASS, so p holds for 12.9. H-1T is
  ((2T − 1)p + 32 + f_a)/k.
- **"Step price for 5×"** is the p at which the cube is exactly 5×:
  - A = 5's 52.67 is under it at 16,384³ (52.89) and 32,768³ (53.11), but not at 8,192³ (52.44) or below.
  - A = 4's 53.12 is over it at every cube, by 0.0008× at 32,768³.
  - Under (e), the 16,384³ step price is 52.874, so A = 5 still clears.
  - §18.3's "A = 5 clears 52.73 (every shape)" is Track C's serving shapes, not these cubes.
- **The 16,384³ margin is 0.22 per add word (0.4%),** inside §16.4's 0.5% run-to-run band, so one run doesn't settle
  it (§18.3 says the same of Track C's shapes).
- *(inferred)* §18.3's 12.4 `dstep` rows show n64 forming in place costing 1.7–1.9× its class price. If the 12.9
  build pays the same, 16,384³ becomes 5.009–5.018×. The 12.9 rows were lost with pod 1, so the forming here is serial
  at its compiled count.
- **H-1T at 57.11** is `h1r_step`'s shape (`pipe` n128 A = 1 U = 4, 56.03%), not `h1r_step` itself, whose launch
  failed. The additive W1 / k (γ's denominator) is the upper reading.

### G.3 The target's m × n grid: D-3s M2, X_q, default, `round11`, k = 16,384, FADD 32.0118 (γ, threshold)

Rows are m (the unit's tokens) and columns n (weight columns), r = 1.

| m \ n | 2,048 | 4,096 | 8,192 | 16,384 | 32,768 |
|---|---|---|---|---|---|
| 2,048 | 5.662% (28.824) | 4.369% (29.739) | 3.709% (30.197) | 3.376% (30.426) | 3.208% (30.540) |
| 4,096 | 4.369% (29.739) | 3.040% (30.655) | 2.362% (31.112) | 2.019% (31.341) | 1.847% (31.455) |
| 8,192 | 3.709% (30.197) | 2.362% (31.112) | 1.674% (31.570) | 1.326% (31.799) | 1.151% (31.913) |
| 16,384 | 3.376% (30.426) | 2.019% (31.341) | 1.326% (31.799) | **0.976%** (32.027‡) | **0.800%** (32.142) |
| 32,768 | 3.208% (30.540) | 1.847% (31.455) | 1.151% (31.913) | **0.800%** (32.142) | **0.624%** (32.256) |

The grids for (a), (b) and (e) are in the JSON. Under (e) the 16,384 square flips (1.0005%, 32.011‡). Under (b) the cell
m = 8,192, n = 32,768 misses by 0.016 points (1.016%, 32.001‡); it cleared at 32.00 in the 02:51Z tables.

### G.4 Sensitivities (γ at the design's FADD, threshold)

- (a) the rms′ cache: the column statistic registered, 2 bytes per column.
- (b) the amplitude table allowed: 2 bytes per weight; it folds rms′ in.
- `round10` and (c) `round9-sass`: the older prices, with the default weight side.
- (d) the 12.4 builds: the cast at 192.25 per register (48.1 per code) and the amplitude at 529.25 per result. The row
  "two HMNMX2" also gives the amplitude as two HMNMX2 at 64.13, in case |·| folds into them as #295's `round9` row
  assumes; §16.4 did not time that form.
- (e) the sum of squares as the three-register HFMA2, 60.57 per register (G.6).
- H-1T: F19-3's literal fix (HSET2 + HFMA2 per real register, f_a 326.96); Y16 (218.02, Daniel's comparison); the 12.4
  build (360.15); and Track H's model (297.56, the 02:51Z headline), the last two at both γ₀.

| Cell | FADD | 2,048³ | 4,096³ | 8,192³ | 16,384³ | 32,768³ |
|---|---:|---|---|---|---|---|
| D-3s M2: default, `round11` (headline) | 32.0118 | 5.712% (28.782) | 3.051% (30.646) | 1.676% (31.568) | **0.976%** (32.027‡) | **0.623%** (32.256) |
| D-3s M2: (a) rms' cache, round11 | 32.0118 | 5.441% (28.976) | 2.914% (30.739) | 1.607% (31.614) | **0.942%** (32.050‡) | **0.606%** (32.267) |
| D-3s M2: (b) amplitude table allowed, round11 | 32.0118 | 5.197% (29.150) | 2.786% (30.826) | 1.541% (31.657) | **0.908%** (32.072) | **0.589%** (32.278) |
| D-3s M2: round10, default | 32.0118 | 5.705% (28.787) | 3.048% (30.648) | 1.674% (31.570) | **0.975%** (32.028‡) | **0.623%** (32.256) |
| D-3s M2: (c) round9-sass, default | 32.0118 | 5.467% (28.957) | 2.922% (30.733) | 1.609% (31.612) | **0.943%** (32.049‡) | **0.607%** (32.267) |
| D-3s M2: (d) 12.4 builds, default | 32.0118 | 9.597% (25.866) | 5.144% (29.191) | 2.763% (30.842) | 1.530% (31.664) | **0.903%** (32.075) |
| D-3s M2: (d) 12.4 builds, amplitude as two HMNMX2, default | 32.0118 | 6.834% (27.964) | 3.647% (30.238) | 1.983% (31.365) | 1.132% (31.926) | **0.702%** (32.205) |
| D-3s M2: (e) sum of squares as the three-register HFMA2 (60.57), default | 32.0118 | 5.889% (28.654) | 3.145% (30.582) | 1.724% (31.536) | 1.000% (32.011‡) | **0.636%** (32.248) |
| D-3m M2: default, `round11` (headline) | 32.0118 | 6.176% (28.446) | 3.297% (30.478) | 1.802% (31.485) | 1.040% (31.986) | **0.656%** (32.235) |
| D-3m M2: (a) rms' cache, round11 | 32.0118 | 5.907% (28.640) | 3.160% (30.571) | 1.733% (31.530) | 1.006% (32.008‡) | **0.638%** (32.247) |
| D-3m M2: (b) amplitude table allowed, round11 | 32.0118 | 5.432% (28.982) | 2.910% (30.742) | 1.604% (31.615) | **0.940%** (32.051) | **0.605%** (32.268) |
| D-3m M2: round10, default | 32.0118 | 6.168% (28.452) | 3.293% (30.481) | 1.800% (31.486) | 1.039% (31.986) | **0.655%** (32.236) |
| D-3m M2: (c) round9-sass, default | 32.0118 | 5.933% (28.622) | 3.168% (30.566) | 1.736% (31.529) | 1.006% (32.008‡) | **0.639%** (32.246) |
| D-3m M2: (d) 12.4 builds, default | 32.0118 | 10.024% (25.530) | 5.380% (29.023) | 2.887% (30.758) | 1.594% (31.623) | **0.935%** (32.054) |
| D-3m M2: (d) 12.4 builds, amplitude as two HMNMX2, default | 32.0118 | 7.287% (27.629) | 3.890% (30.070) | 2.109% (31.281) | 1.196% (31.884) | **0.734%** (32.184) |
| D-3m M2: (e) sum of squares as the three-register HFMA2 (60.57), default | 32.0118 | 6.352% (28.318) | 3.390% (30.414) | 1.850% (31.453) | 1.065% (31.970) | **0.668%** (32.227) |
| H-1T X_q with F19-3's literal fix, f_a 326.96 | 32.0075 | 4.417% (29.710) | 2.373% (31.103) | 1.329% (31.792) | **0.799%** (32.138) | **0.531%** (32.312) |
| H-1T Y16 (comparison), f_a 218.02 | 32.0075 | 3.294% (30.483) | 1.793% (31.487) | 1.034% (31.985) | **0.650%** (32.235) | **0.456%** (32.360) |
| H-1T X_q, the ptxas 12.4 build, f_a 360.15 | 32.0075 | 4.754% (29.475) | 2.548% (30.985) | 1.419% (31.734) | **0.844%** (32.109) | **0.553%** (32.297) |
| H-1T X_q, the ptxas 12.4 build, γ₀ = 0, f_a 360.15 | 32.0075 | 4.515% (29.636) | 2.303% (31.147) | 1.172% (31.895) | **0.595%** (32.270) | **0.304%** (32.459) |
| H-1T X_q, Track H's model (the 02:51Z headline), f_a 297.56 | 32.0075 | 4.117% (29.919) | 2.217% (31.206) | 1.250% (31.844) | **0.758%** (32.164) | **0.510%** (32.325) |
| H-1T X_q, Track H's model (the 02:51Z headline), γ₀ = 0, f_a 297.56 | 32.0075 | 3.876% (30.080) | 1.972% (31.368) | 1.002% (32.006‡) | **0.510%** (32.326) | **0.261%** (32.486) |

Every cell under every sensitivity is in the JSON.

### G.5 For Daniel's rulings: the amplitude table and the rms′ cache, against forming both per unit

Timing uses H100 SXM nominal peaks, so treat it as an estimate. One price unit is about 1.01 fs (2 FLOP at 1,979 dense
FP8 TFLOPS), and HBM3 runs at 3.35 TB/s. The γ gain is at FADD 32.0118.

| Size | FP8 weights | amplitude table | its read per unit | ALU it saves, D-3s / D-3m | γ gain, D-3s / D-3m M2 | rms′ cache | ALU it saves | γ gain, D-3s M2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2,048³ | 4 MiB | 8 MiB | 2.50 µs | 0.29 µs / 0.42 µs | 0.515 / 0.744 | 4 KiB | 0.15 µs | 0.271 |
| 4,096³ | 16 MiB | 32 MiB | 10.0 µs | 1.15 µs / 1.69 µs | 0.265 / 0.387 | 8 KiB | 0.59 µs | 0.137 |
| 8,192³ | 64 MiB | 128 MiB | 40.1 µs | 4.60 µs / 6.77 µs | 0.135 / 0.198 | 16 KiB | 2.34 µs | 0.069 |
| 16,384³ | 256 MiB | 512 MiB | 160.3 µs | 18.4 µs / 27.1 µs | 0.068 / 0.100 | 32 KiB | 9.38 µs | 0.035 |
| 32,768³ | 1,024 MiB | 2,048 MiB | 641.0 µs | 73.6 µs / 108.4 µs | 0.034 / 0.050 | 64 KiB | 37.5 µs | 0.017 |

**The amplitude table** (excluded, 20:58Z):
- **Bytes and share:** 2 bytes per weight, 200% of the FP8 weights (a 3× footprint).
- **What it saves:** 67.815 per weight element per unit for D-3s (the statistic's 34.565 plus `VHMNMX`'s 33.25), and
  99.885 for D-3m.
- **Latency:** at 16,384² that is 18.4 µs of ALU, against 160 µs of HBM reads per unit, 8.7× longer.
- **Effect on γ:** +0.068 points at the target (threshold 32.027 → 32.072).
- The rest of the 20:47Z note stands: no smaller encoding saves ops for D-3s, it is built offline once per matrix, and
  verifying it is free if the law reads the codes and O(kn) plus a 2kn-byte hash if the law reads the table.

**The rms′ cache** (open):
- **Bytes and share:** 2 bytes per column, 2n bytes per matrix (32 KiB at 16,384²). That is 2/k of the FP8 weights:
  0.1% at k = 2,048 and 0.006% at 32,768. It is per-column metadata like the FP8 scales, not a copy.
- **What it saves:** the weights' prescale (16.13) and sum of squares (18.435), 34.565 per weight element per unit,
  9.38 µs of ALU at 16,384². Reading 32 KiB costs nothing measurable.
- **Built:** offline, once per matrix, from the codes alone (salt- and unit-independent).
- **Verifying:**
  - If the law defines rms′ from the codes, a verifier re-forming a sampled unit recomputes it: O(k) per sampled column,
    no extra cost.
  - If the law read a registered rms′, a prover could shrink it. That lowers every amplitude that floors at rms′, and it
    weakens the noise on small entries. Registration would then recompute it, O(kn) once, and hash 2n bytes.
- **Effect on γ:** +0.035 points at the target, moving the threshold from 32.027 to 32.050. At 8,192³ and below
  nothing clears either way.
- **My reading:** allowing the cache costs nothing in memory, bandwidth or verification, if the law defines rms′ from the
  codes.
  - At the lead loop the target clears without it (0.976%), so the cache is now margin (0.942%), not the verdict.
  - It is the verdict under (e): it brings the target from 1.0005% back to 0.954% (32.042‡). It does not rescue D-3m
    M2 under (e) (1.018%, 32.000‡).

### G.6 The centre is settled; the sum of squares is the open pricing choice

**The centre.** §18.4 times the split centre as compiled (one immediate and two register sources) at **64.00 per
register**, like Round 10's immediates form (64.02). So the headline's 32 per element was right, `--centre imm` is the
price, and the `split36` alternative (Round 8's 36 per register) is out. The 00:40Z flips under `split36` (D-3m M2 at
16,384³, D-3m M4 at 32,768³, (a) D-3m M2q, (d) D-3s M4) no longer apply.

**The sum of squares** (h·h + ss) is the one open choice. It reads h twice and ss once: two distinct registers, three
operand reads.
- The headline prices it in the two-source class, 36.12 per register (18.06 per element), like HADD2 a + b and HMUL2
  a·b (§18.4 @3 and @4).
- *(inferred from §18.4)* The limit that falls as sources are added is the register reads. If a repeated register
  counts twice, the instruction prices as the three-register HFMA2 a·b + c (@2), 60.57 per register. That is
  sensitivity (e): +12.225 per element wherever the statistic is formed.
- It is untimed. A `forms` row for HFMA2 h·h + ss would settle it.

| Sum of squares | Target γ at 32.0118 | at 32.0076 (A = 4) | at 32.00 | FADD threshold |
|---|---:|---:|---:|---:|
| Headline: two-source class, 36.12 per register | **0.976%** | **0.970%** | **0.958%** | 32.027‡ |
| (e) three-register HFMA2, 60.57 per register | 1.0005% | **0.994%** | **0.982%** | 32.011‡ |
| (e) with the rms′ cache (a) | **0.954%** | **0.947%** | **0.936%** | 32.042‡ |

Under (e) these verdicts flip against the headline: the target at 16,384³ (X_q and Y16) and the grid's 16,384 square.
No other cell flips, and the real time under (e) still clears 5× at 16,384³ (step price 52.874).

### G.7 The credit correction and the structural pair (Track H, 21:41Z)

**The correction** (`docs/pouw/hardness-shaped-matrices.md` §5.1). In an exact two-block design two checked words per
output are not forced at A = 0:
- R_2T is the useful output, salt-free up to rounding;
- R_(2T−1) = R_2T − I2_T equals I1_T whenever A is 0 on the first T − 1 slices, because block 2 is block 1 negated
  there.

So H-1T credits 4T − 3 words per output (I_1 .. I_2T and R_2 .. R_(2T−2)), not 4T − 1.

**No D-3 design has the pair, so D-3 keeps 2T − 1.** `red-team-round9-pair.py` runs #295's bit-exact `D3Family.side`
and `cell_words` over 24 salts and 4 Gaussian E4M3 columns (per-column scale 448). The rows are all zero, zero except on
the last slice, and Gaussian. It covers D-3s and D-3m, M2 and M4, at k = 2,048, and D-3s M2 at k = 16,384.
- **D-3:** no credited word is free, none duplicates another, and none is another's negation. R_T, D-3's useful output
  and a credited word, takes 24 distinct values over the 24 salts and is never ±0.
- **Controls:** the same census on Track H's reference (`h1_tagged`) finds exactly Track H's pair in H-1T and in posted
  H-1.
  - R_2T is free: R_142 at k = 2,048 and R_1130 at 16,384.
  - I1_T = R_(2T−1).
  - Up to T negation pairs I1_τ = −I2_τ appear. These are distinct words, so no credit is lost to them.
- **Why D-3 has no pair.** H-1's pair is an exact cancellation between two blocks: at A = 0, x2 = −x1 on every lane, so
  the chain returns to a salt-free value. None of D-3's structure produces one:
  - π is `admissible32` (no slice meets its image), so no slice's noise cancels another's;
  - Q is inexact: at A = 0 the codes Q(e) ∈ {0, ±2⁻⁹} are salted, so block sums are salted, not zero;
  - the three blocks run block-major and none is another's negation, so R_T carries salt.

**Before and after, the target:** D-3s M2 X_q at 16,384³ is **0.976% (32.027‡) before and after**. For scale only,
neither of these has a basis:
- dropping R_T anyway (2T − 2) would give 1.008% (32.006‡);
- dropping two words, as H-1 does (2T − 3), would give 1.041% (31.985), which fails.

**Before → after, H-1T** (γ at 32.0075, threshold):

| Cell | 2,048³ | 4,096³ | 8,192³ | 16,384³ | 32,768³ |
|---|---|---|---|---|---|
| H-1T X_q | 3.053% (30.637) → 3.738% (30.180) | 1.675% (31.564) → 2.021% (31.336) | **0.975%** (32.024‡) → 1.150% (31.910) | **0.620%** (32.254) → **0.708%** (32.197) | **0.441%** (32.370) → **0.485%** (32.341) |
| H-1T X_q, γ₀ = 0 (the Lean target) | 2.810% (30.799) → 3.497% (30.341) | 1.428% (31.726) → 1.776% (31.498) | **0.727%** (32.186) → **0.902%** (32.071) | **0.371%** (32.416) → **0.459%** (32.359) | **0.192%** (32.531) → **0.236%** (32.503) |
| H-1T X_q with F19-3's literal fix | 3.737% (30.168) → 4.417% (29.710) | 2.027% (31.330) → 2.373% (31.103) | 1.155% (31.907) → 1.329% (31.792) | **0.711%** (32.195) → **0.799%** (32.138) | **0.487%** (32.340) → **0.531%** (32.312) |

**At the timed f_a the correction now flips one H-1T cell:** X_q at 8,192³ would clear at 4T − 1 (0.975%, 32.024‡) and
fails at 4T − 3 (1.150%, 31.910). At 02:51Z it failed either way (1.063% → 1.238%).

### G.8 The FADD per design, and H-1T's timed forming

| Design | Loop | Instructions per loop | Same-bank FADDs | FADD (§16.3's sweep) | Step, per add word (§18.2–§18.3) |
|---|---|---:|---:|---:|---:|
| D-3, the lead | dflow n64 A = 5 U = 2 (§17.3 @13) | 371 | 0 of 320 | **32.0118** | **52.67** (60.75%) |
| D-3, the alternative | dflow n64 A = 4 U = 2 (@10) | 297 | 0 of 256 | 32.0076 | 53.12 (60.24%) |
| H-1T | `h1r_step`: m64n128k32 atoms, block 1 then block 2 | 282 / 281 | 0 of 512 | **32.0075** | untimed (launch failed); its shape, 57.11 (56.03%) |
| retired: D-3's n128 loop | `pipe` n128 A = 2 U = 4 | 567 | 1 of 512 | 32.0495 | 55.44 (57.72%) |

- **Verified from the SASS.** `--sass` parses `h1_kernel.sass` and asserts the result. `h1r_step` has two block loops
  (`.L_x_0`, `.L_x_1`) of 282 and 281 instructions, each with 256 FADD and 4 QGMMA, and no FADD's two sources share a
  bank (register parity). D-3's dflow loops are §17.3's counts.
- **Why `h1r_step` is untimed.** `pc90`'s launcher opts into more than 48 KB of shared memory only when the dynamic part
  exceeds 48 KB. `k_h1r` has 45,056 B static and 31,744 B dynamic, so the launch returns "invalid argument" (§18.2).
  Its shape, `pipe` n128 A = 1 U = 4, repeats Round 10's 56.31% within 0.3 points.
- **A = 5 against A = 4 for D-3.** A = 4 has the lower FADD, A = 5 the cheaper step:
  - at A = 4's 32.0076 these cells clear that fail at A = 5: D-3m M2q at 16,384³ (0.998%), (a) D-3m M2 (0.999%) and
    the target under (e) (0.994%);
  - at A = 5's 52.67 the target is under 5× at 16,384³ (4.979×), and at A = 4's 53.12 it is not (5.022×).
  - The lead is A = 5 (§18.3): the target clears γ under both, and 5× only under A = 5. No one loop is best for every
    cell, since D-3m M2q and the target under (e) need A = 4 for γ.
- **H-1T's f_a is timed** (§18.2). `h1t_form_xq` as compiled by 12.9 is 260.75 per real element (lf 251.16): a
  598-instruction loop, 5.155 instructions per element, 80 registers. That is 36.9 (12.4%) under Track H's 297.6, with
  the row's 16 IMAD.MOV per loop included. Y16 is 218.02.
  - Under 12.4 it is 360.15 (+38%) and 317.60 (+46%), from the PRMT (174 and 158 per loop), so H-1T must be a 12.9
    build too.
  - The 00:40Z high (309.1) and low (286.0) readings priced HFMA2.MMA and HADD2 as lone ops. The timed row is H-1T's own
    mix, so they are retired, and condition 7's γ takes f_a directly.
  - The forming on the pod is checked: the fixed LUT matches `h1t_ref` in all 131,072 codes (§18.6).

### G.9 A6: transcript hashing and the XOF at Round 11's h (the requester, 23:54Z and 04:00Z)

**Headline** (slowdown against plain FP8; γ at the design's FADD, W1; for D-3s at A = 5's 52.67, for H-1T at its step
shape's 57.11):

| Design, size | Without hashing | SHAKE256 | TurboSHAKE128 | SHA-256 tree digests, SHAKE256 XOF |
|---|---|---|---|---|
| NCP-FP8 (D-3s M2 X_q), 8,192³ | 5.021×, 1.676% | 1,722.9×, **0.0059%** | 624.7×, **0.0163%** | 1,069.6×, **0.0095%** |
| H-1T X_q, 8,192³ | 3.975×, 1.150% | 1,269.6×, **0.0040%** | 460.5×, **0.0111%** | 788.2×, **0.0065%** |
| NCP-FP8 (D-3s M2 X_q), 16,384³ | 4.979×, **0.976%** | 1,722.9×, **0.0034%** | 624.7×, **0.0094%** | 1,069.3×, **0.0055%** |
| H-1T X_q, 16,384³ | 3.953×, **0.708%** | 1,267.6×, **0.0025%** | 459.8×, **0.0068%** | 786.8×, **0.0040%** |

- Every hashed γ′ passes 1% by dilution only: it equals γ·C_h/(C_h + h·B). What decides it is how far an adversary's
  hash undercuts the reference h, and it reaches 1% at **e = 0.993–1.003%** in every hashed cell.
- **The SHAKE256 reference fails that test.** Round 11's build is 8.06% over its own prediction for the tile digest
  (Keccak-f is 7.9% over), so the prediction undercuts it by 8.06%, and γ′ is then 8.03% in every SHAKE256 cell.
- TurboSHAKE128's build is 0.28% over its prediction (γ′ 0.28–0.29% there), and SHA-256's is under its prediction.
- H-1T's additive W1 / k (4.450× and 4.429×) is in the rows table; the step-shape reading is the headline because
  `h1r_step` is untimed.

The rows come from `red-team-round9-frontier.py` (JSON key "A6: transcript hashing and the XOF"; `--md` prints the
tables).

**The model (the requester's):** both sides hash every checked word into the digests and squeeze the noise XOF.
- With h units per byte and B bytes per useful MAC:
  - slowdown′ = slowdown + h·B;
  - γ′ = 1 − ((1 − γ)·C_h + h·B)/(C_h + h·B), which equals γ·C_h/(C_h + h·B).
- C_h is W1's honest cost per MAC, γ's own denominator: 6.083 and 6.042 for D-3s at 8,192³ and 16,384³, and 4.450 and
  4.429 for H-1T.
- Real time adds h·B to the chain as serial work. That is an upper bound, within 0.3% at SHAKE256 and 0.9% at
  TurboSHAKE128, since the chain's 4–5 units could at best hide under the 450–1,720 units of hashing.
- The real-time bases are G.2's: D-3s at the timed dflow steps (52.67 and 53.12), H-1T at 57.11 and additive.
- An adversary who undercuts h by e pays (1 − e)·h·B. The break-even e is (1%·(C_h + h·B) − γ·C_h)/(h·B).

**h** (units per byte; §18.7, the mean over SMs):

| Row | Measured | Its build's prediction | Undercut to the prediction |
|---|---:|---:|---:|
| Keccak-f[1600] | 2,190.3 | 2,030.6 | 7.29% (measured 7.9% over) |
| SHAKE256 tile digest, from registers (the digest h) | **2,290.6** | 2,106 | **8.06%** |
| SHAKE256 tile digest, from L2 (sensitivity) | 2,476.5 | 2,218 | 10.44% |
| SHAKE256 noise, folded (the XOF h) | **2,199.2** | 2,039.5 | **7.26%** |
| SHAKE256 noise, stored | 2,288.3 | 2,106.6 | 7.94% |
| TurboSHAKE128, Keccak-p[1600, 12] (option 2; both h) | **826.3** | 824.0 | **0.28%** |
| SHA-256 compression | 1,356.5 | 1,404 | none (3.4% under) |
| SHA-256 node (verity's, 2 compressions) | 2,635.2 | 2,665 | none (1.1% under) |
| SHA-256 tree, 4 KiB leaves: (65 × compression + node) / 64 | **1,418.9** | 1,468 | none |

- Before Round 11 these were derived: SHAKE256 at 2,029.2 (4,312 × 64 / 136) and the SHA-256 tree at 1,443.8
  (counted). The JSON keeps the derivations.
- The SHA-256 option hashes the digests only; its XOF stays SHAKE256.
- **Why the SHAKE256 build is slow.** Keccak-f runs 7.9% over its loop at 64 per instruction, so SHF and LOP3 do not
  overlap in this build. *(inferred, §18.7)* The 4,315-instruction loop (69 KB) is past §16.3's instruction-fetch knee,
  and `perm12`'s 2,163 is not. That is why TurboSHAKE128 meets its prediction and SHAKE256 doesn't. So a Keccak-f loop
  under the knee (for instance rolled over rounds) plausibly reaches the prediction, and I take the prediction as
  reachable.
- **Not a reference: §17.8's 1,373-per-byte floor.** It assumed SHF and LOP3 overlap. They don't in this build, so the
  floor has no support, but it is not excluded either. Were it reachable, e would be about 37% against Keccak-f's
  2,190.3 and 40% against the digest's 2,290.6.

**B per design:**

| Design | Words hashed per output | Digest B per MAC (8,192 / 16,384) | XOF | XOF B per MAC (8,192 / 16,384) |
|---|---|---:|---|---:|
| NCP-FP8 (D-3s M2 X_q) | 2T − 1, every checked word (1,535 / 3,071) | 0.74951 / 0.74976 | E1 and F1: 2k B per activation row and per weight column, per unit | 0.000488 / 0.000244 |
| H-1T X_q | 4T − 1, every checked word (1,131 / 2,259) | 0.55225 / 0.55151 | 72 B per slice per activation row, per unit (r0 .. r17); B′ is fixed, so no weight XOF | 0.000304 / 0.000152 |

Two corrections to the requester's B for H-1T:
- **The digest binds 4T − 1 words, not 4T − 3.** The credit drops R_2T and R_(2T−1) because they are not forced at
  A = 0, but both are checked words (`h1_tagged.chain` returns 4T − 1). R_2T is the output, so both are hashed. At
  8,192³ B is 0.5522 against 0.5513, 0.16% more.
- **H-1T's XOF is 2.48 B per real element, not about 1 B.** The pinned layout (`h1_kernel.py` `sw = 72`,
  `hardness-shaped-matrices.md` §3.1) squeezes 18 raw words per slice for 41 salt bits (29 real-lane signs, and the
  sign and 3 mantissa bits of each of 3 tag lanes). A 6-byte packing would cut it 12×. That is a design choice for
  both sides, and the γ′ effect is negligible.

**Can an adversary skip or share any hashed byte?** No, for either design, provided the reference h is the adversary's
minimum.
- **Skip, digests.** Every checked position is bound, and SHAKE256's, TurboSHAKE128's and SHA-256's costs do not depend
  on content. A prover that does not compute a word still hashes whatever it puts in its place.
  - Leaving a tile unhashed is the same as leaving it undone: a sampled unit's opening fails, which the draw catches.
    That is δ, not γ.
  - No checked word is redundant for every input. D-3's R_1 = I_1 is already not a separate word, and H-1T's
    R_(2T−1) = I1_T holds only at A = 0.
- **Skip, XOF.** Every squeezed bit comes out of a whole permutation, so the used bits (bits 15 and 31 of r0 .. r15, a
  few bits of r16 and r17) cost the full block. All 18 H-1T words per slice carry used bits.
- **Share, digests.**
  - With a sponge per tile only a common prefix could be reused, and each tile begins with salted words under its own
    unit's domain.
  - With a tree, identical leaves would share digests. So the leaf layout must not let a leaf consist only of salt-free
    words, such as R_2T for all-zero rows. Per-thread leaves interleave salted I and R words and never do.
- **Share, XOF.**
  - D-3's E1 and F1 are keyed by (salt, unit index, root_A, weight id, row or column), so no stream repeats across
    units or rows. Within a unit each row's stream already serves all n columns in the honest count (hence 2k B per
    row, not per output).
  - π's seed is constant, so π is offline for both sides and not in B.
  - H-1T's salts are per (unit, row, slice).
- **Where it fails: h itself.** Since h·B is about 100–285 times C_h, any gap between the reference h and the cheapest
  implementation goes entirely to the adversary: γ′ ≈ γ·C_h/(h·B) + e.
  - **Against the build's own prediction** (the undercut column above): SHAKE256 gives γ′ = 8.03%, and 10.41% for the
    L2 variant, so it fails. TurboSHAKE128 gives 0.28–0.29%, and the SHA-256 tree 0.01–0.02%, which clear.
  - **Against the mixed-issue bound:** gpu-constants notes that mixed ALU + FMA streams issue at 84 per SM per clock
    against 64, and no FMA-offloaded build of these hashes was tried. That bounds e at 1 − 64/84 = 23.8%, where every
    hashed row is at γ′ 23.6–23.7%.
  - So the hashed rows hold only if the reference h is the fastest build anyone knows, including a mixed-pipe one.
    Round 11's SHAKE256 is not (by its own prediction). TurboSHAKE128's is, to its prediction.
- **Not in the rows: root_A.** It hashes 1 B per activation code per unit (1/n B per MAC): +0.280 units per MAC at
  8,192³ and +0.140 at 16,384³ at SHAKE256's digest h, for both designs. It is outside A6's scope, but it is the same
  kind of work.

**The rows** (γ at the design's FADD, W1; slowdown against plain FP8; for D-3s at 52.67 / 53.12, for H-1T at 57.11 /
additive):

| Design, size | Hashing | B | h·B | Slowdown | γ |
|---|---|---:|---:|---:|---:|
| NCP-FP8 (D-3s M2 X_q), 8,192³ | none | — | — | 5.0211× / 5.0633× | 1.6757% |
| | SHAKE256 | 0.7495 + 0.000488 | 1,717.91 | 1,722.9× / 1,723.0× | **0.0059%** |
| | SHAKE256, words from L2 (sensitivity) | 0.7495 + 0.000488 | 1,857.28 | 1,862.3× / 1,862.3× | **0.0055%** |
| | TurboSHAKE128 (option 2) | 0.7495 + 0.000488 | 619.73 | 624.7× / 624.8× | **0.0163%** |
| | SHA-256 tree digests, SHAKE256 XOF | 0.7495 + 0.000488 | 1,064.53 | 1,069.6× / 1,069.6× | **0.0095%** |
| | the SHAKE256 XOF only (digests unpriced, as under a fold) | 0.000488 | 1.07 | 6.095× / 6.137× | 1.4243% |
| | the TurboSHAKE128 XOF only | 0.000488 | 0.4 | 5.425× / 5.467× | 1.5715% |
| H-1T X_q, 8,192³ | none | — | — | 3.9746× / 4.4503× | 1.1501% |
| | SHAKE256 | 0.5522 + 0.000304 | 1,265.64 | 1,269.6× / 1,270.1× | **0.0040%** |
| | SHAKE256, words from L2 (sensitivity) | 0.5522 + 0.000304 | 1,368.33 | 1,372.3× / 1,372.8× | **0.0037%** |
| | TurboSHAKE128 (option 2) | 0.5522 + 0.000304 | 456.57 | 460.5× / 461.0× | **0.0111%** |
| | SHA-256 tree digests, SHAKE256 XOF | 0.5522 + 0.000304 | 784.23 | 788.2× / 788.7× | **0.0065%** |
| | the SHAKE256 XOF only (digests unpriced, as under a fold) | 0.000304 | 0.67 | 4.642× / 5.118× | 1.0001% |
| | the TurboSHAKE128 XOF only | 0.000304 | 0.25 | 4.225× / 4.701× | 1.0888% |
| NCP-FP8 (D-3s M2 X_q), 16,384³ | none | — | — | 4.9794× / 5.0216× | 0.9761% |
| | SHAKE256 | 0.7498 + 0.000244 | 1,717.93 | 1,722.9× / 1,722.9× | **0.0034%** |
| | SHAKE256, words from L2 (sensitivity) | 0.7498 + 0.000244 | 1,857.33 | 1,862.3× / 1,862.4× | **0.0032%** |
| | TurboSHAKE128 (option 2) | 0.7498 + 0.000244 | 619.73 | 624.7× / 624.7× | **0.0094%** |
| | SHA-256 tree digests, SHAKE256 XOF | 0.7498 + 0.000244 | 1,064.34 | 1,069.3× / 1,069.4× | **0.0055%** |
| | the SHAKE256 XOF only (digests unpriced, as under a fold) | 0.000244 | 0.54 | 5.516× / 5.558× | **0.8964%** |
| | the TurboSHAKE128 XOF only | 0.000244 | 0.2 | 5.181× / 5.223× | **0.9445%** |
| H-1T X_q, 16,384³ | none | — | — | 3.9532× / 4.4285× | 0.7081% |
| | SHAKE256 | 0.5515 + 0.000152 | 1,263.63 | 1,267.6× / 1,268.1× | **0.0025%** |
| | SHAKE256, words from L2 (sensitivity) | 0.5515 + 0.000152 | 1,366.17 | 1,370.1× / 1,370.6× | **0.0023%** |
| | TurboSHAKE128 (option 2) | 0.5515 + 0.000152 | 455.84 | 459.8× / 460.3× | **0.0068%** |
| | SHA-256 tree digests, SHAKE256 XOF | 0.5515 + 0.000152 | 782.86 | 786.8× / 787.3× | **0.0040%** |
| | the SHAKE256 XOF only (digests unpriced, as under a fold) | 0.000152 | 0.33 | 4.287× / 4.762× | **0.6585%** |
| | the TurboSHAKE128 XOF only | 0.000152 | 0.13 | 4.078× / 4.554× | **0.6886%** |

**γ′ when the adversary's hash undercuts the reference h by e** (e = the build's own gap: the row's digest and XOF each
at their build's undercut to its prediction, weighted by h·B; e = 23.8%: the mixed-issue bound):

| Design, size | Hashing | e = the build's own gap: γ′ | e = 23.8%: γ′ | Break-even e (γ′ = 1%) |
|---|---|---:|---:|---:|
| NCP-FP8 (D-3s M2 X_q), 8,192³ | SHAKE256 | 8.0360% (e = 8.06%) | 23.7314% | 0.9976% |
|  | SHAKE256, words from L2 (sensitivity) | 10.4080% (e = 10.44%) | 23.7373% | 0.9978% |
|  | TurboSHAKE128 (option 2) | 0.2919% (e = 0.28%) | 23.5944% | 0.9934% |
|  | SHA-256 tree digests, SHAKE256 XOF | 0.0168% (e = 0.01%) | 23.6838% | 0.9961% |
|  | the SHAKE256 XOF only (digests unpriced, as under a fold) | 2.5138% (e = 7.26%) | 4.9967% | none: over 1% at e = 0 |
|  | the TurboSHAKE128 XOF only | 1.5888% (e = 0.28%) | 3.0525% | none: over 1% at e = 0 |
| H-1T X_q, 8,192³ | SHAKE256 | 8.0344% (e = 8.06%) | 23.7301% | 0.9995% |
|  | SHAKE256, words from L2 (sensitivity) | 10.4067% (e = 10.44%) | 23.7361% | 0.9995% |
|  | TurboSHAKE128 (option 2) | 0.2868% (e = 0.28%) | 23.5908% | 0.9985% |
|  | SHA-256 tree digests, SHAKE256 XOF | 0.0126% (e = 0.01%) | 23.6817% | 0.9991% |
|  | the SHAKE256 XOF only (digests unpriced, as under a fold) | 1.9475% (e = 7.26%) | 4.1064% | none: over 1% at e = 0 |
|  | the TurboSHAKE128 XOF only | 1.1036% (e = 0.28%) | 2.3594% | none: over 1% at e = 0 |
| NCP-FP8 (D-3s M2 X_q), 16,384³ | SHAKE256 | 8.0340% (e = 8.06%) | 23.7295% | 1.0001% |
|  | SHAKE256, words from L2 (sensitivity) | 10.4067% (e = 10.44%) | 23.7355% | 1.0001% |
|  | TurboSHAKE128 (option 2) | 0.2851% (e = 0.28%) | 23.5891% | 1.0002% |
|  | SHA-256 tree digests, SHAKE256 XOF | 0.0092% (e = 0.00%) | 23.6806% | 1.0001% |
|  | the SHAKE256 XOF only (digests unpriced, as under a fold) | 1.4891% (e = 7.26%) | 2.8395% | 1.2693% |
|  | the TurboSHAKE128 XOF only | 0.9535% (e = 0.28%) | 1.7138% | 1.7167% |
| H-1T X_q, 16,384³ | SHAKE256 | 8.0331% (e = 8.06%) | 23.7288% | 1.0010% |
|  | SHAKE256, words from L2 (sensitivity) | 10.4060% (e = 10.44%) | 23.7349% | 1.0009% |
|  | TurboSHAKE128 (option 2) | 0.2825% (e = 0.28%) | 23.5873% | 1.0028% |
|  | SHA-256 tree digests, SHAKE256 XOF | 0.0071% (e = 0.00%) | 23.6796% | 1.0017% |
|  | the SHAKE256 XOF only (digests unpriced, as under a fold) | 1.1668% (e = 7.26%) | 2.3250% | 4.8787% |
|  | the TurboSHAKE128 XOF only | 0.6963% (e = 0.28%) | 1.3434% | 11.3232% |

**What this means:**
- **With the digests priced,** NCP-FP8 is about 1,723× plain FP8 and H-1T about 1,270× at SHAKE256.
  - TurboSHAKE128 cuts that 2.8×, to 625× and 460×. The SHA-256 tree gives 1,070× and 788×.
  - §18.7's audit ratio at Keccak-f's rate is 1,643×. These rows are higher because the tile digest is 2,290.6, not
    Keccak-f's 2,190.3, and they add the design's own 5×.
  - The 8,192³ and 16,384³ rows are within 0.2% of each other. The digest B per MAC is fixed by the words per output,
    not by the size: about 3k/16 words for D-3s (0.75 B per MAC) and 4k/29 for H-1T (0.55).
- **γ′ passes 1% by dilution only,** and the design's own γ enters it at the 0.005% level. The break-even undercut is
  1.0% at every cell, so the hash's reference build decides the verdict:
  - SHAKE256 at Round 11's build fails (8.03%);
  - TurboSHAKE128 at its build clears (0.29%), as does the SHA-256 tree, as long as no mixed-pipe build exists.
- **The XOF alone** (as under a fold) adds 0.3–1.1× at SHAKE256.
  - At 8,192³ neither design clears on it: NCP-FP8 1.424% and H-1T **1.0001%** (1.088% at 02:51Z, now on the edge).
    With TurboSHAKE128's XOF: 1.572% and 1.089%.
  - At 16,384³ both clear (0.896% and 0.659%). Against the SHAKE256 XOF's own 7.26% gap they fail again (1.489% and
    1.167%), and against TurboSHAKE128's 0.28% they clear (0.954% and 0.696%).
- A6's ask stands: Daniel's acceptance for FP8, now at Round 11's measured h, with SHAKE256's build known not to be the
  fastest (7.9% over its Keccak prediction).

### G.9.1 B's combined variant, re-priced

The scout's (bc-8e0cd393) "B's combined variant: the promoted tensor-core chain bound by the keyed integer mix"
([a6-binding-scout.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw-fp8/a6-binding-scout.md);
`a6-combined.py` and `.json` beside it, read-only). I re-run its `cost` at the worst credited ε per size from
`a6-combined.json`, with γ₀ = 1/400. The first row reproduces its published figures (checked).

**What enters:**
- **H-1T's f_a:** the chain is H-1T's, so f_a enters W1, the mix's ALU bound and the issue count. It is 260.75 as timed,
  against the published 297.6.
- **The tensor share** enters the capped time: 56.03% at `h1r_step`'s shape (§18.2), against the published 57.72%
  (Round 10's n128 A = 2).
- **Not HFMA2:** the chain has no f16 arithmetic.
- **Not routing:** σ is compiled in as a register order, so no SEL, SHFL or LDS is issued. Routing's measured prices
  (SEL 38.32, SHFL 97.94, LDS 95.89) would enter only a runtime σ.
- **LOP3's 64.14** is a sensitivity on every mix op (the mix's IADD3 is untimed).

| Variant | Size | W1 / k | Time, ideal | Time, share capped | γ not credited | γ credited | γ credited, H32 floor | Mix undercut to 1% | H-1T chain: γ, W1 / k, time at 57.11 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| as published (f_a 297.6, share 57.72%, FADD 32.00) | 8,192³ | 5.5612× | 2.7995× | 3.8305× | 50.6216% | **0.9350%** | 25.7783% | 0.1307% | 1.2385%, 4.4543×, 3.9791× |
|  | 16,384³ | 5.5342× | 2.7763× | 3.8237× | 50.3712% | **0.5320%** | 25.4516% | 0.9390% | 0.7469%, 4.4303×, 3.9555× |
| f_a 260.75 (timed), share 57.72% | 8,192³ | 5.5569× | 2.7950× | 3.8305× | 50.5828% | **0.8571%** | 25.7200% | 0.2873% | 1.1501%, 4.4503×, 3.9746× |
|  | 16,384³ | 5.5320× | 2.7741× | 3.8237× | 50.3522% | **0.4939%** | 25.4230% | 1.0151% | 0.7081%, 4.4285×, 3.9532× |
| f_a 260.75, share 56.03% (h1r_step's shape, 18.2) | 8,192³ | 5.5569× | 2.7950× | 3.9460× | 50.5828% | **0.8571%** | 25.7200% | 0.2873% | 1.1501%, 4.4503×, 3.9746× |
|  | 16,384³ | 5.5320× | 2.7741× | 3.9390× | 50.3522% | **0.4939%** | 25.4230% | 1.0151% | 0.7081%, 4.4285×, 3.9532× |
| f_a 260.75, share 56.03%, every mix op at LOP3's 64.14 | 8,192³ | 5.5629× | 2.8011× | 3.9460× | 50.6365% | **0.8562%** | 25.7463% | 0.2888% | 1.1501%, 4.4503×, 3.9746× |
|  | 16,384³ | 5.5381× | 2.7801× | 3.9390× | 50.4063% | **0.4934%** | 25.4498% | 1.0151% | 0.7081%, 4.4285×, 3.9532× |

- **Credited γ** falls, 0.935% → 0.857% at 8,192³ and 0.532% → 0.494% at 16,384³, because f_a is 36.9 lower. It
  clears at both sizes, as before, where H-1T alone fails at 8,192³ (1.150%).
- **Capped time** rises from 3.83× to 3.95× and 3.94× at the step shape's share, still under 5×. W1 / k stays over 5×
  (5.56× and 5.53×), as the scout found.
- **The mix undercut** (how far an adversary's mix may undercut its price before the credited γ reaches 1%) widens,
  from 0.13% to 0.29% at 8,192³ and from 0.94% to 1.02% at 16,384³. Against the 23.8% mixed-issue bound neither
  survives, as before.
- **No verdict flips.** The uncredited reading (50.6% and 50.4%) and the H32 floor (25.7% and 25.4%) fail, as before.

### G.10 §3 log lines

- 00:40Z strike (bc-79ab9271): frontier re-issue at `round10`, default weight side, with Track H's shared corrections
  and A6 (`genuine-fp8-red-team-round9.md` "Frontier restatement (Daniel 20:41Z)" G.2 and G.7–G.9;
  `red-team-round9-frontier.py` and `.json`; `red-team-round9-pair.py` and `.json`).
  - **Target:** D-3s M2 X_q at 16,384³ was 0.957% at 32.00, threshold 32.028‡, and 1.034% at the as-built 32.05.
  - **H-1T replaced posted H-1:** X_q 0.747% (32.164) at 16,384³ and 1.238% at 8,192³; γ₀ = 0 at 8,192³ 0.991%
    (32.006‡).
  - **Credit, 4T − 1 → 4T − 3:** H-1T X_q from 0.659% to 0.747% at 16,384³.
  - **A6 at 8,192³ (derived h):** NCP-FP8 from 5.277× to 1,527×, and H-1T from 4.454× to 1,126×; γ′ reaches 1% at a
    1.0% hash undercut.
- 04:45Z strike (bc-79ab9271): the Round 11 re-issue (`genuine-fp8-red-team-round9.md` "Frontier restatement (Daniel
  20:41Z)" G.1–G.9.1; `red-team-round9-frontier.py` and `.json`), at `round11`, γ at each design's FADD.
  - **Target:** D-3s M2 X_q at 16,384³ is **0.976% at 32.0118** (dflow A = 5 U = 2), threshold 32.027‡, so it clears as
    built; real time 4.979× at 52.67 (0.4% under 5×). The centre is settled as `imm`. Under the open sum-of-squares
    price (e) it is 1.0005% and fails, and 0.954% with the rms′ cache.
  - **H-1T at the timed f_a 260.75:** X_q 0.708% (32.197) at 16,384³ and 1.150% at 8,192³; γ₀ = 0 at 8,192³ 0.902%
    (32.071). Real time 3.953× and 3.975× at the step shape's 57.11.
  - **Flips:** the target, D-3m M4 at 32,768³ and the grid's 16,384 square now clear as built; D-3m M2q at 16,384³ now
    fails (1.004%). D-3s at 8,192³ is now over 5× (5.021×).
  - **A6 at 8,192³:** SHAKE256 1,722.9× (NCP-FP8) and 1,269.6× (H-1T); TurboSHAKE128 624.7× and 460.5×. The
    break-even e is 0.993–1.003%. SHAKE256's build is 8.06% over its own prediction, so γ′ = 8.03% against it;
    TurboSHAKE128's gives 0.29%.
  - **B's combined variant:** credited γ 0.857% / 0.494%, capped time 3.95× / 3.94×; no flips.

## Sampled proofs: the per-strip weight-noise caveat

Written 02:31Z to 02:50Z, CPU only, for the requester's 02:31Z item. It assesses §5 (the tile-local form, `ncp-v2`) and
§9's caveat of [sampled-proofs-circuit.md](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/sampled-proofs-circuit.md)
(bc-75d1b678's, read-only), against #295's keys (`docs/pouw-fp8/h100-scheme.md` §3.2: E₁ and F₁ both read root_A,
X-R9-2). The rows come from `red-team-round9-frontier.py`, JSON key "X-SPW: F1 per call against per strip": the target
(D-3s M2 X_q, default weight side, `round11`, the D-3 FADD 32.0118, W1), with the weight side formed once per strip of R
rows (m := R in f_b's term), and the XOF at Round 11's SHAKE256 noise h (2,199.2 units per byte, folded; G.9).
Re-issued 04:45Z at Round 11's prices, step prices and h; no verdict changed.

### SPW.1 Verdict

1. **Security: per-(strip, column) F₁ keeps what root_A bought, strip by strip, given the strip index in the key.**
   - In the ROM, strip s's F₁ is unknown until D_s is queried, so until its rows are fixed. Its rows meet only that
     strip's formed weights, so B̃ is post-commitment for every row it meets. B̃ is also fresh per strip, so X-17b-2's
     premise (formed weights fixed across the rows that meet them) fails. X-D3-3's three spike classes are then per-salt
     coincidences, which belong to the branching gap, as at r = 1 today (X-SPW-1).
   - It needs the strip index (or the call-global row index) in the key (X-SPW-2).
   - **A cheaper binding exists: a two-level key** (X-SPW-4). F₁ is keyed on D_A, a Merkle root over the call's D_s, and
     each tile checks its own D_s's path to D_A. That keeps F₁ per call.
   - "root_A per unit as today, plus D_s for E₁" can't be derived in a tile, because root_A isn't a Program value
     (§2.1). It is option (i) or (iii); D_A is its in-scope form.
2. **Cost: ruinous; Daniel's guess is confirmed** (X-SPW-3, SPW.2).
   - f_B/16 is 22.0 units per MAC. γ becomes 78.6% at R = 16 and 48.0–48.1% at R = 64, against 1.676% (8,192³) and
     0.976% (16,384³) today.
   - The slowdown becomes about 27.0× and 10.5×, against 5.02× and 4.98× at the timed dflow step. With F₁'s XOF, now
     2/R bytes per MAC, it is about 302× and 79×.
   - The steelman forms only the noise-reading items per strip: 15.7 units per MAC and γ 72.5% at R = 16.
   - At 16,384³ an F₁ key must cover at least 15,340 of the call's 16,384 rows for γ < 1%.
3. **H-1T: the tile-local form costs it nothing extra at serving.** It has no weight forming to move. Its salts are
   already per (unit, row, slice), so keying them on D_s changes no byte. It even drops A16's call-wide barrier. It
   needs X-SPW-2's index (X-SPW-5).
4. **Bottom line for Daniel: NCP-FP8 cannot meet the tile-local form with per-(strip, column) weight noise.**
   - It can meet the two-level key (X-SPW-4) at #295's serving cost. The one thing it keeps is A16's call-wide barrier
     for FP8. Option (i), the derived-input class with #295's root_A as is, also works, but changes two rules.
   - Committing F₁ in full is not viable (X-SPW-6).

### SPW.2 The rows

"Forming per MAC" is the weight side's f_B/R. The slowdown adds the change in forming to G.2's bases at the timed dflow
steps (52.67 / 53.12). The "+ XOF" columns add E₁ (2/n bytes per MAC) and F₁ (2/R) at 2,199.2 units per byte (Round
11's SHAKE256 noise, folded); the word digests are the same in every row (G.9). The steelman forms the noise-reading
items (noise field, centre, scale, s, block values, casts: 251 per element) per strip. It forms decode, statistic and
amplitude (100 per element) once per call, which needs a decoded-weight copy and the amplitude table, both excluded by
the 20:31Z and 20:58Z rulings.

| Size | F₁ keyed | Forming per MAC | γ (threshold) | C_h | Slowdown | + XOF: h·B | + XOF: slowdown | + XOF: γ′ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 8,192³ | per call (#295; the two-level key) | 0.043 | 1.676% (31.568) | 6.083 | 5.021× / 5.063× | 1.07 | 6.09× / 6.14× | 1.4243% |
|  | per strip of 64 rows | 5.494 | 48.143% (-26.572) | 11.534 | 10.472× / 10.514× | 69.26 | 79.73× / 79.78× | 6.8725% |
|  | per strip of 16 rows | 21.975 | 78.650% (-201.457) | 28.015 | 26.953× / 26.995× | 275.44 | 302.39× / 302.43× | 7.2611% |
|  | per strip of 64 rows, steelman | 3.939 | 40.065% (-10.045) | 9.979 | 8.917× / 8.959× | 69.26 | 78.18× / 78.22× | 5.0456% |
|  | per strip of 16 rows, steelman | 15.72 | 72.513% (-135.867) | 21.76 | 20.698× / 20.74× | 275.44 | 296.14× / 296.18× | 5.3092% |
| 16,384³ | per call (#295; the two-level key) | 0.021 | **0.976%** (32.027‡) | 6.042 | 4.979× / 5.022× | 0.54 | 5.52× / 5.56× | 0.8964% |
|  | per strip of 64 rows | 5.488 | 48.012% (-26.281) | 11.508 | 10.446× / 10.488× | 68.99 | 79.44× / 79.48× | 6.8637% |
|  | per strip of 16 rows | 21.951 | 78.611% (-201.436) | 27.972 | 26.909× / 26.952× | 275.17 | 302.08× / 302.12× | 7.2537% |
|  | per strip of 64 rows, steelman | 3.933 | 39.891% (-9.723) | 9.954 | 8.891× / 8.933× | 68.99 | 77.88× / 77.93× | 5.0294% |
|  | per strip of 16 rows, steelman | 15.714 | 72.472% (-135.466) | 21.734 | 20.672× / 20.714× | 275.17 | 295.84× / 295.88× | 5.3052% |

- **Rows per F₁ key for γ < 1%:** at least 15,340 at 16,384³. At 8,192³ it is at least 251,049, above m, so 8,192³
  fails at any keying, as it does today.
- **The XOF's γ′ falls only by dilution,** because both sides pay h·B. The slowdown decides the verdict. TurboSHAKE128
  (12 rounds, a 168-byte rate) would cut h to 0.38× (826.3 against 2,199.2), which still leaves about 103 units per MAC
  at R = 16.

### SPW.3 Named findings

- **X-SPW-1 (security, holds per strip).**
  - Per-(strip, column) F₁ = XOF(salt, call, D_s, s, weight id, j) keeps X-R9-2's property within each strip: the
    noise is unpredictable until the rows it meets are fixed, and there is no reuse.
  - Grinding moves to strip granularity: editing one strip's rows re-rolls that strip's E₁ and F₁, at about 2.2–4.4% of
    its work (h/n against C_h at 16,384 and 8,192). That is TT_NCP_U's ε, as for `ncp-v2`'s E₁ (§6.1), and it is not priced here.
- **X-SPW-2 (spec: the strip index in the key).**
  - Keyed on D_s without the strip index, and with a strip-local row index, two identical strips (repeated prompts,
    padding) get identical E₁ and F₁ (NCP-INT's F₁ is per run anyway). Their tiles' words are then identical, and the prover computes one strip
    and is credited for all of them.
  - This applies to §2.1's E₁[i] as written ("row i of strip s") unless i is call-global, and to a tile-local H-1T's
    salts. The fix is s, or the global row index, in every D_s-keyed stream.
- **X-SPW-3 (cost: ruinous).** See SPW.2. The weight side moves from f_B/m to f_B/R. That is 22.0 (R = 16) or 5.5
  (R = 64) units per MAC, against a 1% budget of about 0.06, plus F₁'s XOF at 69–275 units per MAC.
- **X-SPW-4 (the binding that works: a two-level key; recommended).**
  - The keys:
    - D_A = the Merkle root over the call's D_s, computed once per call by a tree unit;
    - F₁[:, j] = XOF(salt, call index, D_A, weight id, j);
    - E₁ stays on D_s, with the global row index.
  - Each tile recomputes its D_s, as in (a′), and checks the D_s's authentication path to D_A in gates. The path is 7–10
    compressions (448–640 bytes), at most 0.44% of D_s's own bytes.
  - **Why it binds.** Under the ROM and collision resistance, F₁ is unknown until D_A is queried. A right tile's rows
    hash to the only leaf its position can open, so every strip with right tiles was fixed before F₁.
  - **Harm stays local.** A wrong D_A, or a wrong tree unit, can pair with right tiles only through a collision. So
    it needs no harm-weighted size (unlike §5.2 3(a)), no public input and no evaluation by the verifier.
  - **Serving cost.** Serving is #295's with root_A := D_A: F₁ and forming per call (the "per call" rows).
  - **What it costs.**
    - FP8 keeps A16's call-wide barrier: the call's A is hashed before F₁. That is 1/n bytes per MAC, A6's root_A line.
      A23's shrink applies to NCP-INT and H-1T only. SPW.2's 15,340-row floor means no strip-granular key avoids it.
    - It needs an FP8 scheme version with new vectors, and X-R9-2's regression test re-keyed to D_A.
- **X-SPW-5 (H-1T: nothing extra).**
  - Serving is unchanged:
    - D_s hashing replaces root_A byte for byte (1/n bytes per MAC);
    - the salt XOF stays at 72 bytes per slice per row;
    - B′ is fixed, so no forming moves.
  - In the proof, a tile derives its rows' salts: 64 · 72 · T bytes, 2.6 MB per 64-row tile at 16,384 (T = 565). That
    is the tile-local form's in-tile noise, on the order of NCP-FP8's own, not an extra.
  - It needs X-SPW-2's index.
- **X-SPW-6 (committing F₁ in full: not viable for FP8).**
  - The size is 67 MB per call at 8,192² at §9's 1 byte per weight (134 MB at #295's 2), and 69 GB per 70B forward.
  - §5.3 prices proving NCP-INT's F₁, which is per run, at 63–82 T rows per run. NCP-FP8's F₁ is per call, so the
    same bytes recur every forward: 63–82 T rows per forward, against about 17 T for a whole window's tile proofs.

### SPW.4 §3 log line (the per-strip weight-noise caveat)

- 02:50Z strike (bc-79ab9271): the per-strip weight-noise caveat (`genuine-fp8-red-team-round9.md` "Sampled proofs:
  the per-strip weight-noise caveat"; `red-team-round9-frontier.py` and `.json`, key "X-SPW").
  - **Security:** per-(strip, column) F₁ holds per strip in the ROM, given the strip index (X-SPW-1, X-SPW-2).
  - **Cost:** ruinous. At 16,384³ γ is 78.6% (R = 16) or 48.0% (R = 64), and the slowdown is 27.1× or 10.7× (281× or
    74× with F₁'s XOF). A key needs at least 14,596 rows.
  - **H-1T:** nothing extra.
  - **For FP8:** the two-level key D_A (X-SPW-4) at #295's serving cost, with A16's barrier kept, or option (i).
    Committing F₁ in full would cost 63–82 T rows per forward (X-SPW-6).
- 04:45Z strike (bc-79ab9271): X-SPW re-issued at Round 11 (`round11`, FADD 32.0118, the timed dflow steps, the XOF
  at 2,199.2 units per byte). No verdict changed. At 16,384³ γ is 78.6% (R = 16) or 48.0% (R = 64), and the slowdown is
  26.9× or 10.4× (302× or 79× with F₁'s XOF), against 4.98× per call. A key needs at least 15,340 rows.
