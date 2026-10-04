---
id: 20261004T2202Z-report-relay-internal-pouw-fp8-a6-binding-scout
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw-fp8/a6-binding-scout.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw-fp8/a6-binding-scout.md`, sha256 `b48b9e62ab89c12a17d5305df7e48d8fa2d6d886c773197fc825697a646336dd`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# A6 scout: cheaper ways to bind H-1T's credited words

CPU only. This is a list of candidates, not a design. The budget is about 4 units per credited word under additive W1, or
about 8 if H-1T's step overlaps like D-3s's. NCP-FP8 (D-3s) has about 0.02 units per MAC, and nothing below fits it.

**29 Sep, the three CPU tests are run** (§"The three CPU tests"). The running-sum digest (#2) is dead. So is the
tensor-core chain (#7) without promotion. With an FP32 add every 4 slices #7 is sound, and it leaves 25 units per word,
too few for the digest. The integer mix (#4) survived every shortcut tried. The new ranking is at the end.

**29 Sep, 02:30Z: B's combined test is run** (the next section). #7 promoted every 4 slices, bound by #4 with a keyed
order, measured on the same runs: a clean census, an output error at a tenth of the FP32 chain's own, and no
work-saving shortcut that matches a tile. It fits 5× in time but not in W1, and γ < 1% only if the mix is credited at its
reference price. **Correction:** the mix costs about 32 units per word (0.5 INT32 op at 64), not 16; 16 is the
issue-slot floor. Rows #4 and the verdicts below are corrected in place.

## B's combined variant: the promoted tensor-core chain bound by the keyed integer mix

**Every number in this section except cost and γ comes from the nonzero-accumulator model.** Steps 2–4 of each group
run `HOPPER_E4M3_K32.step` with C ≠ 0, which an H100 has confirmed only from C = 0. Round 11's capture C2 tests it. The
cost and γ formulas don't depend on it, except through ε.

### The definition (v0), for the red team

Per output (row r, column j): T = ⌈k/29⌉ slices per block and S = 2T slices, block 1's from x1 and block 2's from x2,
each against the laid-out weight slice W_(t mod T) (H-1T's `h1t_ref` and `layout_weights`, unchanged). G = ⌈S/4⌉
groups of 4 consecutive slices; the last may be short.

- **Chain.** C_t = TC(+0, slice t) at a group's first slice (t = 1, 5, 9, …), and C_t = TC(C_(t−1), slice t)
  otherwise. TC is one wgmma k32 step with scale-d = 1, `verity.ml.tc`'s `HOPPER_E4M3_K32.step` (GroupSum with C,
  14-bit window, floor −139). F_1 = the last C of group 1, and F_h = RN_f32(F_(h−1) + the last C of group h), one FADD.
  The output is F_G.
- **Checked words:** C_1 … C_S and F_2 … F_G, m = S + G − 1 per output (707 at 8,192, 1,412 at 16,384). This is the
  analogue of H-1T's 4T − 1 (1,131 and 2,259).
- **Credited words:** all but F_(G−1) and F_G, S + G − 3 per output (705 and 1,410), the analogue of 4T − 3 (1,129 and
  2,257). Track H's `census` drops the last two words, unchanged: F_G is the output, and F_(G−1) is determined by it and
  the last group's word.
- **Mix v0, per tile.** A tile is Q = 32 outputs, one thread's FP32 accumulators in an m64n64 wgmma (on the GPU they
  span 2 rows × 16 columns; the test's tile is 32 columns of one row). Q = n when n < 32.
  1. **Stream:** the tile's m·Q words as uint32 bit patterns, event-major in write order (C_1, C_2, C_3, C_4, C_5, …,
     C_8, F_2, C_9, …, each F_h right after its group's last C). Within each event the Q words go in the keyed order σ:
     position p holds output σ(p).
  2. **Tree:** each level pads with zero words to a multiple of 3 and replaces each consecutive triple (a, b, c) by
     IADD3 = a + b + c mod 2^32 at even levels and LOP3 0x96 = a ⊕ b ⊕ c at odd levels, starting with IADD3, until one
     word is left: the tile's root. That is Σ_l ⌈N_l/3⌉ ops, 0.5003 per word at 8,192.
  3. **Check:** the root is committed with the tile's outputs. The verifier replays drawn tiles bit-exactly and compares
     roots.
  4. **Key:** σ is a Fisher–Yates shuffle of the Q positions from
     K = `verity.randomness.derive(beacon, "verity/pouw-fp8/mix-order/v0", context)`: for i = 0 … Q − 2, swap positions
     i and i + K.uniform(Q − i, ("order", i)). There is one σ per run, applied to every event and tile, and the prover
     knows it before computing, because it is compiled into the kernel as a register permutation. σ = identity is the
     fixed order. The test's keys use beacons `a6-test-beacon-A` and `-B` with context {run, k, Q}.

### What was run

- **Script:** `a6-combined.py`, beside this note, with subcommands `selfcheck`, `run --k K --part trackh|cases|all`,
  `cost`, `summary DIR`, `tables`, `structure` and `cancellations`. `a6-combined.json` holds every case, order and
  substitution, plus `cost` at ε = 0 and at the worst ε. `tables` prints the tables below from the JSON.
- **Code:** it loads Test 2's `tc_chain(…, 4)` and Test 3's tree from `a6-binding-tests.py`. It swaps Track H's
  `h1_tagged.chain` for the promoted chain and wraps `census` to record each salt's words; nothing in Track H is edited.
  `selfcheck` confirms the mix equals Test 3's tree, the event order is a permutation, and the skip variant with no skip
  equals the chain. The census reproduces Test 2's promoted-chain census bit for bit at 2,048.
- **Inputs, per size (all five, 2,048 to 32,768; the real matrices are those of Tests 1–3):**
  - **Track H's four families,** its own `run_s1`, `run_f19`, `run_neg` and `run_absorb` at 16 salts. That covers S1
    and its real-column baseline over 1,024 columns, F19-2 twins, b/−b, and absorption.
  - **This scout's 28 cases** at 8 salts: Tests 1–3's 27 plus a Student-t (ν = 3) row. Real columns, S1 and the
    inputs built for fusion use 1,024 columns; F19-2, b/−b and absorption use 256.
  - **The mix, the shortcuts and the output error** use each census's first 4 salts, on the same words. That is 3,436
    tiles per order per size, 768 of them from real columns, under three orders (fixed, and keyed with beacons A and B).
- **Time:** 16.5 minutes on 4 CPU cores (four single-threaded runs), with no GPU.

### 1. Census

ε on the credited words, the worst case per family (16 salts for Track H's families, 8 for the cases):

| Family | 2,048 | 4,096 | 8,192 | 16,384 | 32,768 |
|---|---|---|---|---|---|
| Real columns (Qwen2.5-3B, Qwen3-8B, Qwen2.5-72B, Hermes-405B ×2) | 0 | 0 | 0 | 0 | 0 |
| S1 | 0 | 0.0039% | 0.0001% | 0.0008% | 0.0003% |
| F19-2 twins | 0 | 0 | 0 | 0 | 0 |
| b/−b | 0 | 0 | 0 | 0 | 0 |
| Absorption (synthetic) | 0.0022% | 0.071% | 0.035% | 0.018% | 0.015% |
| Absorption, real columns aligned | 0 | 0 | 0 | 0 | 0 |
| Built for fusion (11 cases) | 0 | 0 | 0 | 0 | 0 |

- **Other census measures:** tensor-core words equal to their predecessor on every salt ≤ 0.071%, and F words equal to
  their predecessor on every salt 0.
- **Caveat, as in Test 2:** Track H's per-salt coincidence (a word equal to another of its row on that salt, what a
  branching prover reads) is 31–40% under S1, absorption and the built inputs. On real columns, F19-2 and b/−b it is
  about 1%.

### 2. Output error

Against the FP32 chain (H-1T's honest output) and against the exact X_q·B′, over 1,024 real columns and 4 salts:

| Row | Against FP32, median / worst relative | Worst ÷ output RMS | Median / worst ulps | Against exact, median (FP32 chain's own) |
|---|---|---|---|---|
| Gaussian, 8,192 | 0.014% / 9.6% | 0.091% | 1.7e3 / 1.3e6 | 0.124% (0.122%) |
| Gaussian, 16,384 | 0.018% / 12% | 0.092% | 2.1e3 / 1.8e6 | 0.133% (0.132%) |
| 8 outliers ×30, 8,192 | 0.026% / 72% | 0.22% | 3.1e3 / 8.6e6 | 0.191% (0.186%) |
| 8 outliers ×30, 16,384 | 0.032% / 23% | 0.30% | 3.9e3 / 3.0e6 | 0.245% (0.246%) |
| Student-t, 8,192 | 0.021% / 20% | 0.13% | 2.5e3 / 2.5e6 | 0.260% (0.258%) |
| Student-t, 16,384 | 0.026% / 14% | 0.21% | 3.0e3 / 2.3e6 | 0.291% (0.285%) |
| `s1_row`, 8,192 | 0.010% / 10% | 0.046% | 1.2e3 / 1.1e6 | 0.010% (0.004%) |
| `s1_row`, 16,384 | 0.007% / 7.2% | 0.026% | 7.9e2 / 8.7e5 | 0.007% (0.003%) |

- **Across all five sizes:**
  - the median relative error against FP32 is 0.007–0.037%;
  - the worst output is at most 0.35% of the output RMS;
  - against exact, the promoted chain is within 0.01 point of the FP32 chain's own error on every row (on `s1_row` both
    are ≤ 0.010%).
- **Why "worst relative" and ulps are large:** the worst relative errors and the ulp counts sit on outputs near zero.
  H-1T's salts make the partial sums far larger than the output.

### 3. The mix's shortcut test on the combined chain

Each substitution is a set of words the adversary holds without doing the honest computation. The table gives:
- the share of tiles whose mix equals the honest one, the worst over all cases, sizes and the three orders, with real
  columns in brackets;
- the share of outputs where the substitution happens to leave every word right (the worst case; real columns in
  brackets). A prover who substitutes in one output of a tile matches that tile at this rate.

| Id | Substitution | Route | Against honest | Tiles matched | Outputs left right |
|---|---|---|---|---|---|
| A1 | the group kept in the tensor core: C_(h,1..3) taken as the group's last word | tensor-core-internal | saves 3 waits per group (time only) | 0% (0%) | 0% |
| A2 | every C_(h,s>1) read one step late | tensor-core-internal | saves nothing | 0% (0%) | 0% |
| A3 | one C_(h,s>1) per output read one step late | tensor-core-internal | saves one read | 0% (0%) | ≤ 6.3% (0.05%) |
| A4 | one C_(h,s>1) per output → its atom TC(+0, slice) | tensor-core-internal | same cost | 0% (0%) | ≤ 3.1% (0.02%) |
| B1 | one slice skipped per output, the rest recomputed | skipped work | saves 32 | 0% (0%) | ≤ 3.1% (0.02%) |
| B2 | one promotion FADD skipped per output | skipped work | saves 32 | 0% (0%) | ≤ 6.3% (0%) |
| C1 | every F_h by integer increments of F_(h−1)'s bits | exact adds (X-A6-2) | ≥ 6× the FADD | 0% (0%) | ≤ 66% (0.02%) |
| C2 | every F_h by an exact-add emulation (RZ) | exact adds (X-A6-2) | ≥ 6× the FADD | 100% (100%) | 100% |
| C3 | every C_t as exact sums (RZ) of the group's atoms | exact emulation | 2× (atom + FADD per word) | 100% on zero-row built inputs (0%) | 100% (0%) |
| C4 | every C_(h,s>1) by integer increments from the atoms | exact emulation | ≥ 7× | 0% (0%) | 0% |
| D1 | fused: one TC chain accumulating onto the FP32 word, no restarts and no FADDs | fused accumulate | saves G − 1 FADDs (10% of W1) | 0% (0%) | 0% |
| E1 | the same slice skipped in every output of the row | skipped work, aligned | saves 32 per output | 0% (0%) | ≤ 1.7% (0.05%) |
| E2 | the same C_(h,s>1) read one step late in every output of the row | tensor-core-internal, aligned | saves one read | ≤ 3.1% (0%) | ≤ 7.6% (0.02%) |

The 3–7% "outputs left right" cells are Track H's absorption cases with 8 columns: 1–2 outputs of 32.

- **No route cheaper than honest matched a real-column tile:** 0 of 3,840 per order across the sizes, under 0.08% at
  95% confidence.
  - The routes that skip work (A1, B1, B2, D1, E1) matched no tile in any case.
  - A single changed word always shows, because each word enters one IADD3 or XOR3 that is one-to-one in it. A match
    needs several changes that cancel.
- **Only the exact emulations match, by recomputing the same words at a higher cost:**
  - Every promotion FADD is exact on real columns (100.0% at every size), so C2 reproduces every F word. X-A6-2 found
    the same exactness in H-1T's running adds.
  - The mix still needs each F word bit-exactly, and nothing cheaper than one FADD produces it. X-A6-2's collapse was
    for a fold that is linear in the values and so can be computed from the atoms alone. The mix works on bit patterns,
    so the collapse does not carry over.
  - The tensor-core steps are exact sums in only 42–57% of steps on real columns, so C3 matches only on zero-row inputs,
    where every step is exact, and it costs 2×.
- **Structured cancellations: 3 changed tiles kept the honest root, all on built inputs, and none of them saves work.**
  - E2 cancelled once at 2,048 (fixed order, absorption with tiny = 0) and once at 4,096 (keyed order B, loud first
    slice then zeros). C3 cancelled once at 2,048 (fixed order).
  - The cause is the words' structure:
    - every C word has at least 10 trailing zero bits from the 14-bit window (median 11 at 2,048);
    - IADD3's carries run upward only, so the root's low 10 bits come from the F words alone. At 2,048, 0–2 of the
      root's bits are always zero on real columns, and up to 10 on built zero-row inputs;
    - in tags-only regions (zero activations), the 32 words of an event form a regular progression across columns, set
      by 3 salted tag lanes. In both E2 cases one event's 32 related differences vanished at the tree's fourth level.
      In the C3 case, 2 changed words in consecutive events cancelled at the fourth level.
  - `a6-combined.py structure --k K` prints the zero-bit counts, and `cancellations --k K --case … --order … --sub …`
    locates each case's unchanged tile and the level where the difference vanishes.
  - So for structured substitutions on such regions, the chance that a wrong tile keeps the honest root is not 2^−32.
    The red team should know this.
  - A per-word rotation (a funnel shift) would bring the zero bits into play, but at one more op per word it doubles
    the mix. Untested.

**The keyed order (X-A6-3 and precomputation).**
- **The prover must know the key.** The mix consumes words while they are live in registers. A tile's 707 × 32 words
  (90 KB at 8,192) can't wait for a key drawn after the commitment. Applying it then means storing every word or
  replaying the tile, which is X-A6-3's objection (12.3 KB per output for H-1T).
  - So σ is a per-run register permutation compiled into the kernel, at no cost.
  - Test 3's full-tile random order can't be implemented, because registers can't be indexed dynamically.
  - IADD3 and XOR3 are symmetric, so only the grouping into triples matters.
- **Does the order stop precomputation?** Only precomputation that depends on the tree's alignment, done before the key
  is drawn: weights or inputs placed so that related words become siblings.
  - Measured, the fixed order and both keys gave the same match shares in every case at every size. The only exceptions
    are the 3 structured cancellations above, which moved between orders rather than disappearing.
  - Value-dependent precomputation is already impossible: the salts make every word's value unknown before the run, and
    ε = 0 means no word is fixed across salts.
  - So the key is harmless and free, but on this evidence it buys nothing measurable.

### 4. Cost and γ

Per output, in units. W1 adds everything up. Time is derived, not measured: the maximum of the tensor core, the ALU pipe
(the mix plus X_q forming), the FMA pipe (the promotion FADDs) and issue (32 per thread-instruction).

| | 8,192³ | 16,384³ |
|---|---|---|
| Slices 2T; groups G | 566; 142 | 1,130; 283 |
| Tensor core / promotion FADDs / X_q forming / mix | 18,112 / 4,512 / 298 / 22,636 | 36,160 / 9,024 / 298 / 45,190 |
| Mix INT32 ops per output (per checked word) | 353.7 (0.5003) | 706.1 (0.5001) |
| **W1, slowdown** | **45,558, 5.56×** | **90,672, 5.53×** |
| **Time, ideal overlap** | **2.80×** (the mix's ALU pipe) | **2.78×** |
| **Time, tensor share at D-3s's measured 57.72%** | **3.83×** (the tensor core) | **3.82×** |
| **γ, mix not credited** | **50.6%** | **50.4%** |
| **γ, mix credited at its reference price** (64 per op, with `FoldForcesWrites`) | **0.94%** | **0.53%** |
| γ, mix credited at the H32 floor (16 per word) | 25.8% | 25.5% |
| A mix this much cheaper than the reference lifts γ to 1% | 0.17% | 0.96% |
| For reference: the promoted chain alone (no binding) | 2.80×, γ 1.82% | 2.78×, γ 1.04% |
| For reference: H-1T (FADD chain) | 4.45×, γ 1.24% | 4.43×, γ 0.75% |

- **How γ is computed:** g0 = 1/400 and the worst ε (0.035% and 0.018%), with 32 units per credited word.
  - Not credited: γ = 1 − (1 − g0)·credit / W1.
  - Credited: γ = 1 − ((1 − g0)·credit + M′) / W1, where M′ is the mix at its reference price, or at half of it for the
    floor. This is G.9's treatment of forced work.
  - The other sizes are in the JSON: W1 5.52–5.68×, time 2.77–2.91× (3.82–3.84× capped), and γ credited 0.32–3.2%
    (under 1% from 8,192 up).
- **Does it fit 5×?**
  - **In time, yes.** The tensor core and the mix run on different pipes.
  - **In W1, no: 4,598 units per output over at 8,192.** The mix alone costs more than the tensor-core work (32 per
    word × 1.25 words per k32 step).
  - Fitting W1 would need a mix at ≤ 25.5 units per word, or binding only about 80% of the words.
- **Is γ < 1%?** Only with the mix credited at its reference price. That needs `FoldForcesWrites` plus a price
  assumption: at 8,192, a mix 0.17% cheaper than the reference crosses 1%. Uncredited, γ is about 50%; at the floor,
  about 25%.

### Verdict

- **Measured, on the model:** the combined variant holds.
  - The census is clean (≤ 0.071%).
  - The output error is a tenth of the FP32 chain's own.
  - No work-saving shortcut matched a tile under any order.
- **Against 5×:** it fits in time (2.8–3.8×) but not in W1 (5.5–5.6×). γ is under 1% at 8,192 and 16,384 only if
  Daniel credits the mix's work at its reference price.
- **Open:**
  - the red team's verdict on `FoldForcesWrites`, including the structured cancellations above;
  - the crediting ruling;
  - Round 11's C2 for C ≠ 0;
  - Track H's census and proofs redone for a truncating accumulator.

## Candidates (the first scout)

**The floor decides most rows.**
- **Tensor core:** reading a 32-bit word costs at least 32 units. At n8, every format takes in one A-operand register per
  32 units (u8 k32, e4m3 k32, tf32 k8 and b1 k256 alike). At n8's measured SS rate, 22% of peak, it is 144.
- **CUDA cores:** at least 16 units at the issue rate (32 per instruction), because a 3-source instruction cuts the
  word count by at most two. IADD3 and LOP3 run on the INT32 pipe at 64 per instruction, so they pay 32.
- **Memory side:** 950 units or more.
- **So nothing that reads every credited word fits in W1.** A candidate fits only in time, or by reading fewer words.
- **Idle time in the honest step** (§14.4): about 42% of the tensor core (≈ 12 units per word) and about 0.33 issue slot
  per word (2.5 of 4 warp instructions issued at ~144 words per SM-clock).

**Probe** (`a6-binding-scout-probe.py` → `.json`, bit-exact model, X-A6-2's three rows, k = 2,048 / 8,192 / 32,768):
- **The tensor core's accumulate-into-C path equals the FADD's R_τ in only 0.8–19% of steps.** The path is
  `HOPPER_E4M3_K32.step(R_(τ−1), a, b)`. The zero row is worst: 19% at k = 2,048 and 12% at 8,192. This path is
  validated on the H100 for C = 0 only. Test 1 below extends this probe.
- **R's bytes churn:** 3–4 of R's four bytes change in 52–74% of steps. R's top byte is unchanged in 66–96% of steps.
- **I's low byte is always 0:** the atom keeps 14 bits, and the median I word has 11 trailing zero bits.

Costs are per credited word: W1 first, then time where it differs.

| # | Candidate | Cost | Might work because | Fails because |
|---|---|---|---|---|
| 1 | **Tensor-core limb digest of every word.** u8 IGMMA m64n8k32 reads the FP32 registers as A fragments; the layout map to check is a fixed k-permutation, which the key absorbs. Keyed s8 B, int32 wrap, then one SHAKE per tile | 32 (144 at n8's measured rate); +20 in time | Exact integers with no NaN, and every bit is read. R's bytes churn, so X-A6-2's value-linear shortcut misses. Re-encoding to e4m3 instead would cost 128 | 4–8× over budget. It is linear over limbs with the key known during compute (X-A6-3), so X-A6-4's collapse stands and it needs a `DigestForcesWrites` Prop. Test 2: it misses the promoted TC chain's 25 per word too |
| 2 | **#1 on the R words only**, plus a Prop `RForcesI` | 16 (32 per R word); about +4 in time if IGMMA fills the idle tensor time, ≈ 0.55 per MAC | The C path rarely reproduces R_τ, so R_τ needs I_τ written | **Dead (Test 1).** The C path forms R_τ in 2–7% of steps on real columns, up to 20% on the b/−b zero row and 93–100% on inputs built for it. No exponent-only rule names the fused steps, so `RForcesI` has no clause that holds |
| 3 | **X-A6-7's keyed multiply-xor chains** | ≈ 190; in time, 4–7× the INT pipe's rate | Nonlinear, with one SHAKE per tile | 25–50× over, and it needs `FoldForcesWrites`. **New:** a chain's low j bits see only the words' low j bits, and I's low 11 bits are zero, so for a wrong I word its 2^−64 is about 2^−42 |
| 4 | **ALU-only 3-input tree** (IADD3 alternating with LOP3 0x96 = XOR3, 0.5 op per word) in idle issue slots. IMAD would share the FADDs' datapath | ≈ 32 (0.5 op at the INT32 pipe's 64; 16 is the issue floor); ≈ +5 in time | Inside the time budget. **Test 3:** on the words' bit patterns the value-linear collapse does not carry over. No cheap substitute and no shortcut from the I words reproduced a real tile's mix (0 of 384 tiles at each size), and the worst built input reaches 8.6% | It needs `FoldForcesWrites`, and its uncredited W1 adds about 50 points of γ. The chi (0xD2) and MAJ (0xE8) LUTs lose information (MAJ collapses at 2,048), so use IADD3 and XOR3 only |
| 5 | **FP nonlinearity as the fold:** FFMA rounding (acc·k + w), or words as e4m3/bf16/tf32 operands into the 14-bit accumulator | ≥ 32. FFMA can't hide: the FP32 pipe carries the FADDs | A bit-exact hardware nonlinearity | Absorption and the 14-bit window drop most bits, so only high bits are bound. Raw bit patterns hit NaN/Inf codes. X-A6-4 |
| 6 | **Credit fewer words:** I only, R only, or a salted fraction f fixed before the commitment | Scales with f; hashing fits only at f ≲ 1/1,000 | Trivial | γ ≈ the uncredited honest share (≈ 50%, or 1 − f). A secret subset needs the key after the commitment (X-A6-3). Known positions shrink the targets (X-A6-5) |
| 7 | **Chain inside the tensor core:** scale-d = 1, so R_τ = TC(R_(τ−1), a, b), with no FADD and no separate I; optionally an FP32 add of the chain every 4 slices | Test 2: 2.2–2.4× instead of 4.4–4.6×, leaving 39–40 per word; with the FP32 add every 4 slices 2.8–2.9×, leaving 24–26 | There are no parallel I words for X-A6-2. **Test 2, promoted every 4 slices:** the census's ε ≤ 0.07%, and the error against the FP32 chain is 0.013–0.029% median | **Without promotion, dead (Test 2):** ε reaches 63% (S1) and 80% (absorption), and the error against FP32 grows to 0.74–1.0% median at 32,768. Promoted, it is a scheme change: C ≠ 0 accumulation must be validated on an H100, and DistinctLive and the tag separation re-proved under truncation. Reading accumulators every k32 costs a wait per atom (46–56% tensor share measured) |
| 8 | **Downstream layers consume the words** | 0 | Free | They read only R_2T, which is already uncredited, at 8 bits. The credited words are intermediates |
| 9 | **Fixed-function engines:** copy engines' AES-GCM in Confidential Computing mode, TMA and memory-side reduces, L2 compression, NVLink/PCIe CRC, GSP crypto | ≥ 950. The words would first have to reach HBM: ≈ 300 GB per 8,192³ GEMM, about 40× the run | Off the SMs | Bandwidth. GHASH is GF(2)-linear. The link CRCs and GSP crypto aren't programmable |
| 10 | **Post-commitment keys, samples or deadlines** | Small | A true 1/\|K\| | X-A6-3: hold 12.3 KB per output, or replay. X-A6-5: drawn tiles are just replayed. A tile replays in microseconds, so a deadline can't separate |
| 11 | **Provable instances:** K12, TurboSHAKE or BLAKE3 per word, or an SIS lattice hash on IGMMA | 2,900–4,400; SIS ≈ 1,000 | The random oracle keeps the proof (X-A6-7). SIS is collision-resistant under a standard assumption | 125–1,100× over. SIS binds as a function but gives no RO extraction (X-A6-1). It is the fallback |
| 12 | **Sampled proofs' own commitment to values.** Sampled proofs is PoUW's verifier (Daniel, 00:15Z); see `docs/pouw/sampled-proofs-circuit.md` §5.4 | It forces writes only if every word goes verbatim under a random-oracle leaf: options 1–2, 3,300–8,000. Its SHA-256 leaf is ≈ 5,500, derived from ≈ 1,400 INT instructions per 64-byte block (48 schedule words at about 10 each, 64 rounds at about 14) at 64 units each | One absorption serves both protocols, and the leaf hash is changed in one place. The leaf could carry #1's or #4's result | Anything smaller binds only a function of the words. The output and folds fall to X-A6-2 and X-A6-4, and a sample or words committed after the draw fall to X-A6-5. The circuit design and the decision note's Recommendation agree |

## The three CPU tests

**Common to all three.**
- **Script:** `a6-binding-tests.py` (`selfcheck | fusion | tcchain | intmix --k K --nsalt N --out F`).
  `a6-binding-tests-summary.py DIR` folds the per-size runs into `a6-test1-fusion.json`, `a6-test2-tcchain.json` and
  `a6-test3-intmix.json`, and prints the tables below. All of these sit beside this note. CPU only, on this VM.
- **Model:**
  - The tensor core's accumulate-into-C step is `gs_acc`, `verity.ml.tc`'s `HOPPER_E4M3_K32.step` vectorized: Hawkeye's
    GroupSum with C, width 14, floor −139.
  - `selfcheck` compared 40,000 samples against `HOPPER_E4M3_K32.step` and found 0 mismatches, and at C = 0 `gs_acc`
    equals every I word (`a6-binding-tests-selfcheck.json`).
  - **The step is validated on the H100 for C = 0 only, so every number here with C ≠ 0 is the model's.** That covers
    all of Test 1 and all of Test 2's TC chains.
- **Track H's code, not new models:** `h1_tagged.h1t_ref`, `layout_weights(..., "h1t")`, `chain` and `census`. Test 2
  replaces `h1_tagged.chain` with the TC chain and wraps `census`. Nothing in Track H was edited.
- **Sizes:** all five frontier sizes (2,048, 4,096, 8,192, 16,384 and 32,768) for every test. Salts: 4 for Tests 1 and
  3, 16 for Test 2's census, and 2 for its output error.
- **Real matrices:** `h1_fetch.py --rows 1024` exports in `/tmp/h1w_big` (`h1_tagged.real_matrix`), 1,024 columns each,
  not kept in the store.
  - 2,048: Qwen2.5-3B, layer 18 q_proj.
  - 4,096: Qwen3-8B, layer 18 q_proj.
  - 8,192: Qwen2.5-72B, layer 40 q_proj.
  - 16,384 and 32,768: Hermes-3-Llama-3.1-405B, layer 63 q_proj and mlp.down_proj. Meta's own checkpoint is gated, so
    this public fine-tune of it stands in.
- **Cases (Tests 1 and 3), 27 per size:**
  - **Real columns:** three rows (Gaussian, Gaussian with 8 outliers ×30, and Track H's `s1_row`) over 256 real columns.
  - **The four attack families, built with Track H's constructions:**
    - S1 at x_tag F, 32 and 0;
    - F19-2 twins of 32 real columns;
    - b/−b on a zero row and on a Gaussian row;
    - absorption, six synthetic cases plus real columns aligned in the first half.
  - **Eleven inputs built to maximize fusion** (`cases()`): the zero row over real, tags-only, ±448 or ±256 weights;
    aligned 416 or 256 with signs alternating per slice or per 4 slices; one lane per slice; and a loud first slice
    followed by zeros.

### Test 1: the running-sum digest (#2). Dead.

**The question:** how often does one wgmma with scale-d = 1, TC(R_(τ−1), slice τ), equal the FADD's
R_τ = RN_f32(R_(τ−1) + I_τ)? At such a step R_τ is formed without I_τ being written. Below is the fused share of steps,
the worst case per family, mean over 4 salts:

| Family | 2,048 | 4,096 | 8,192 | 16,384 | 32,768 |
|---|---|---|---|---|---|
| Real columns (worst of the three rows) | 6.8% | 5.0% | 3.9% | 3.4% | 2.0% |
| S1 | 1.2% | 0.6% | 0.3% | 0.2% | 0.1% |
| F19-2 twins | 10.3% | 8.0% | 5.2% | 3.8% | 3.0% |
| b/−b (zero row; Gaussian row 6.7% → 1.5%) | 20.1% | 16.4% | 10.9% | 9.1% | 6.9% |
| Absorption (real columns aligned; synthetic cases ≤ 1.3%) | 4.6% | 3.8% | 2.3% | 1.6% | 1.2% |
| Built: zero row, tags-only or ±448 / ±256 weights | 99.9–100% | 99.2% | 97.8–97.9% | 97.1–97.3% | 93.2–93.6% |
| Built: 256 aligned, signs alternating per slice or per 4 | 68–70% | 58–61% | 48–51% | 42–45% | 33–34% |
| Built: loud first slice then zeros, ±448 weights | 14.3% | 12.8% | 13.5% | 14.5% | 13.0% |

- **What this costs the digest:** a fused step skips the write of one I word. So `RForcesI`'s ε is about half the fused
  share, fused × (2T − 1)/(4T − 3). That reaches 3.4% on real columns, 10% on b/−b and 47–50% on the built inputs.
- **Why steps fuse:** the running sums are short. In 69–82% of fused steps on real columns, F19-2 and b/−b, both
  R_(τ−1) and R_τ have at most 14 significant bits, the accumulator's width, so its truncation loses nothing.
  - The built inputs keep R short: on the zero row only the small tags accumulate, and alternating signs cancel.
  - In S1, short sums make up under 1% of steps, and fusion is just as rare.
- **Exponent-only rules:** each rule is fitted per case on salts 0–1 and scored on salts 2–3. A "strict" cell predicts
  fusion at ≥ 99% over ≥ 20 steps; that is what a prover who must not miss can use.
  - **Before the step,** from e(R_(τ−1)) minus the largest product's exponent, the rule names **0% of the fused steps**
    on real columns and in every family, at every size. The majority rule's precision is only 27–70%.
  - **With every exponent,** including I_τ's and R_τ's, it names 16–21% on b/−b and at most 0.3% elsewhere.
  - It works only on the built inputs, naming 37–61% of their fused steps. There, fusing every step already succeeds
    93–100% of the time.
- **Verdict:** the pass mark was about 2%.
  - Fusion runs 2–20% on real and family inputs and nearly 100% on inputs built for it, and no exponent rule tells the
    fused steps apart. So `RForcesI` has no clause that holds, and #2 is dead.
  - #1, which digests every word, doesn't depend on `RForcesI`.
  - Any binding over the FADD chain has to bind the I words as well as the R words.

### Test 2: tensor-core accumulation (#7). Dead unpromoted; sound promoted, but the digest doesn't fit.

**The chains:**
- **TC:** R_1 = TC(+0, slice 1) and R_τ = TC(R_(τ−1), slice τ) over both blocks, with no FADD and no I words. It
  credits 2T − 2 words.
- **TC + promote 4:** the TC chain restarts from +0 every 4 slices, and an FADD adds each group's last word into an FP32
  accumulator. The first group's word is the accumulator. It credits 2T + G − 3 words, with G = ⌈2T/4⌉.
- **Cost model:** `gamma_h1t`'s W = 64T + 32 per FADD + 297.6 (X_q forming).

**Slowdown, and the units per credited word left under 5×:**

| Chain | 2,048 | 4,096 | 8,192 | 16,384 | 32,768 |
|---|---|---|---|---|---|
| FADD (H-1T) | 4.57×, 3.2 | 4.50×, 3.6 | 4.45×, 4.0 | 4.43×, 4.1 | 4.42×, 4.2 |
| TC | 2.36×, 38.6 | 2.29×, 39.3 | 2.25×, 40.0 | 2.23×, 40.3 | 2.22×, 40.4 |
| TC + promote 4 | 2.91×, 24.4 | 2.84×, 25.2 | 2.80×, 25.6 | 2.78×, 25.8 | 2.77×, 25.9 |

**Census ε_credited, the worst case per family** (Track H's `census` with its chain replaced, 16 salts, 2,048 → 32,768):

| Chain | S1 | Absorption | Absorption, real columns aligned | Real columns, F19-2, b/−b |
|---|---|---|---|---|
| FADD | 0 | 0 | 0 | 0 |
| TC | 1.0 / 13.8 / 33.5 / 52.1 / 63.2% | 62.1 / 74.8 / 74.8 / 75.0 / 79.5% | 6.1 / 6.2 / 9.4 / 15.6 / 9.4% | 0 |
| TC + promote 4 | 0 | ≤ 0.07% | 0 | 0 |

- **Why the TC chain fails:** the 14-bit accumulator absorbs on its own.
  - Under S1, 93–98% of the TC chain's words equal another word of their row on the same salt. This is Track H's
    per-salt coincidence, the measure a branching prover reads.
  - The FADD chain's is 22–25% and the promoted chain's 36–40%.
  - Many of the TC chain's words stay equal on every salt, which gives the ε above. The promoted chain's higher
    coincidence is a caveat for the red team, although its ε is ≤ 0.07%.

**Output error.** The comparisons are against the FP32 chain (H-1T's honest output) and against the exact X_q·B′, over
all 1,024 real columns and 2 salts. Each cell gives the median relative error, then the p99 relative to the output's RMS,
then the median in ulps.

| Gaussian row | 2,048 | 8,192 | 32,768 |
|---|---|---|---|
| FP32 vs exact | 0.12% / 0.33% / 1.4e4 | 0.13% / 0.36% / 1.5e4 | 0.13% / 0.34% / 1.6e4 |
| TC vs FP32 | 0.13% / 0.71% / 1.5e4 | 0.35% / 1.8% / 4.2e4 | 0.74% / 3.3% / 8.9e4 |
| TC + promote 4 vs FP32 | 0.013% / 0.041% / 1.5e3 | 0.015% / 0.046% / 1.7e3 | 0.015% / 0.044% / 1.7e3 |
| TC + promote 4 vs exact | 0.12% / 0.33% / 1.5e4 | 0.13% / 0.36% / 1.5e4 | 0.13% / 0.35% / 1.6e4 |

- **Rows with outliers and Student-t rows:** TC vs FP32 reaches 1.0% and 0.94% median, with p99 at 5.1% and 4.8%, at
  32,768. The promoted chain stays at 0.019–0.029% median against FP32, and against exact it matches FP32's own error.
  The 4,096 and 16,384 columns are in `a6-test2-tcchain.json`.
- **Does the digest then fit?** The TC chains have no I words, so digesting the running sums means digesting every
  credited word. That is #1, and it needs no `RForcesI`.
  - The TC chain leaves 39–40 per word. That is ≥ 32 at peak rate but < 144 at n8's measured rate.
  - The promoted chain leaves 24–26 per word, less than 32, so the digest doesn't fit.
- **Verdict:**
  - **Without promotion, dead:** ε reaches 80%, and the error grows with k to 0.7–1.0% median.
  - **With an FP32 add every 4 slices, promising as a scheme:**
    - its census is clean;
    - its error against FP32 is about a tenth of FP32's own error against exact;
    - its slowdown is 2.8× instead of 4.45×.
  - At #4's price of 32 per word it leaves no room for #4 additively, nor for the digest. The combined test puts the
    pair at 5.56× in W1 and 2.8–3.8× in time.
  - Adopting it means validating C ≠ 0 accumulation on an H100 and redoing Track H's census and proofs for a truncating
    accumulator.

### Test 3: the integer mix (#4). Survives every shortcut tried.

**The tree:**
- **Structure:** a ternary tree over each tile's credited words, with levels alternating IADD3 and LOP3 0x96 (XOR3).
  That is 0.502 op per word.
- **Tile:** 1 row × 8 columns, holding 8(4T − 3) words: 2,248 at 2,048 and 36,136 at 32,768.
- **Order:** the words go in a fixed random order, standing in for a salt-keyed one.
- **Variants:** XOR3 / IADD3, IADD3 / chi (0xD2) and IADD3 / MAJ (0xE8).
- **Scale:** 2,496 tiles per size, 384 of them from real columns.

**The substitutions,** each a word the adversary holds without writing R_τ:
- every R_τ replaced by I_τ;
- every R_τ replaced by the **integer shortcut**, which computes the mix from the I words alone. It advances R's bit
  pattern by I_τ / ulp(R_(τ−1)) inside R's binade;
- every R_τ replaced by **exact adds truncated to FP32**. This emulates the FADD, and it takes at least three integer
  instructions per word, more than the FADD it avoids;
- one random R_τ per output replaced by R_(τ−1), a skipped FADD;
- one random R_τ per output replaced by I_τ.

**Results for IADD3 / XOR3, the share of tiles whose mix equals the honest one** (worst case over the 27 cases):

| Substitution | 2,048 | 4,096 | 8,192 | 16,384 | 32,768 | Real columns |
|---|---|---|---|---|---|---|
| Every R_τ → I_τ | 0% | 0% | 0% | 0% | 0% | 0% |
| Every R_τ → integer shortcut from the I words | 6.2% | 8.6% | 2.3% | 1.6% | 0.8% | 0% |
| Every R_τ → exact adds (emulates the FADD) | 100% | 100% | 100% | 100% | 100% | 100% |
| One R_τ → R_(τ−1) | 0% | 0% | 0% | 0% | 3.1% | 0% |
| One R_τ → I_τ | 0% | 0% | 0% | 0% | 0% | 0% |

- **Integer shortcut:** its worst case is the built input with a loud first slice then zeros (small I against large R).
  It reproduces 43–72% of the R words there at 8,192 (up to 81% at 2,048), against about 0.1% on real columns. A tile
  holds thousands of words, so a single miss changes its mix.
- **Exact adds:** they reproduce every R word on real columns, because those adds are exact, as X-A6-2 found. But
  emulating the add costs more than the FADD, so this is the FADD, not a shortcut.
- **One R_τ → R_(τ−1) at 32,768:** 1 of 32 tiles, in an absorption case with identical columns. There, equal changes in
  two columns cancel under XOR.
- **The other trees:**
  - XOR3 / IADD3 behaves the same, with 0% everywhere for one R_τ → R_(τ−1).
  - chi lets one R_τ → R_(τ−1) through in up to 6.2% of tiles and one R_τ → I_τ in up to 1.6%.
  - MAJ collapses at 2,048: 192 distinct roots in 2,496 tiles, and every substitution is invisible. At other sizes up to
    12.5% of tiles are unchanged.
  - Use IADD3 and XOR3 only.
- **The mix binds the I words too, so Test 1's fusion buys nothing against it.** A prover who forms R_τ in the tensor
  core must still produce I_τ for the mix, with a second tensor-core step or R_τ − R_(τ−1). Either is another write.
- **Verdict: promising, and the only survivor.**
  - The value-linear collapse that broke the linear fold (X-A6-2, 73–88%) does not carry over to the words' bit patterns.
    No cheap substitute reproduced a real tile's mix: 0 of 384 tiles at each size, under 1% at 95% confidence. The worst
    built input reaches 8.6%.
  - This is evidence, not a proof. It still needs `FoldForcesWrites`, and the mix's own 32 units per word are not
    credited, which adds about 50 points to γ.
  - Against the FADD chain it fits only in time, at about +5 per word. On the promoted TC chain (24–26 per word left)
    it doesn't fit additively either; the combined test measures the pair.

## Ranking after the tests

1. **#4, the integer mix (IADD3 / XOR3 over the credited words), keyed per run. Promising, the only survivor.** It
   needs `FoldForcesWrites` and a red-team pass. Uncredited, γ rises by about 50 points.
2. **#7 with an FP32 add every 4 slices. Promising as a scheme change:** 2.8× instead of 4.45×, a clean census, and an
   error a tenth of FP32's own.
   - Combined with #4 (the combined test at the top), it fits 5× in time but not in W1 (5.56×).
   - It needs C ≠ 0 accumulation validated on an H100.
3. **#1, the tensor-core digest of every word. Unchanged:** 32 per word fits no live variant.

**Dead:** #2, the running-sum digest (Test 1), and #7 without promotion (Test 2).

**Done on CPU:** the combined test (the top section). **Next, not run here:** C ≠ 0 accumulation on an H100 against
`HOPPER_E4M3_K32` (Round 11's C2), and the red team's `FoldForcesWrites` pass.
