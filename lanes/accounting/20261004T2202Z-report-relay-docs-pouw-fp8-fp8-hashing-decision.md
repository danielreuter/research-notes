---
id: 20261004T2202Z-report-relay-docs-pouw-fp8-fp8-hashing-decision
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/docs/pouw-fp8/fp8-hashing-decision.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/pouw-fp8/fp8-hashing-decision.md`, sha256 `e14e3ee96a47b9e46b36c1f95f282cf52b00429aebff06b1f47d3397bc349551`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# A6: how FP8 PoUW binds its checked words (decision note for Daniel)

**Status: DECIDED by Daniel at 01:37Z: choice C, no FP8 binding for now.**
- **Path B is CLOSED (Daniel deferred to the default, 2026-09-29, 17:32Z): the integer mix's work is NOT credited, which stops B.** Why:
  - uncredited, the mix raises γ by about 50 points;
  - credited, about half the certified work would be binding rather than useful matmul;
  - crediting also rests on the unproven `FoldForcesWrites` over all H100 programs;
  - at 8,192³ it has a 0.17% margin before γ reaches 1%.

  FP8 PoUW stays unbound (choice C). If FP8 must ship with a binding, the fallback is per-word TurboSHAKE128 (option A), which is provable but far outside 5×. The B results remain below as the record.
- **The history:** a heads-up since 00:30Z, updated 01:35Z with the scout's first three CPU tests, and at 02:40Z with
  the combined-variant test and the red team's `FoldForcesWrites` pass.

**Round 11 (04:56Z): options 1 and 2 are now at measured H100 hash rates.**
- **No-binding row:** NCP-FP8 uses Track C's measured short loop (52.67 per add word). H-1T's slowdown was measured in Round 12 (05:02Z): `h1r_step` runs at 57.30 per add word, which is 55.84% of the tensor-core rate.
- **SHAKE256:** Round 11's build runs 8.1% slower than the instruction-count prediction. A faster build would put γ′ at about 8%, so **option 1 fails the hash-optimality condition.**
- **TurboSHAKE128:** it is within 0.3% of its prediction (γ′ about 0.3%), so **option 2 passes it.** Both still assume no mixed ALU + FMA build exists; at that bound (23.8%) γ′ is about 24%.

Coordinator, 29 Sep 2026, 00:35Z. The numbers below were first derived; Round 11 measured the hash rates on an H100 and
re-issues every row (`red-team-round9-frontier.py --hash-units-per-byte`).
- **Sources:**
  - the red team on bindings: `internal/pouw-fp8/redteam-transcript-binding.md`, X-A6-1 to X-A6-7;
  - the frontier rows: `internal/pouw-fp8/genuine-fp8-red-team-round9.md` §G.9;
  - the audit item: `docs/deployment-requirements-audit.md` §A6.
- **NCP-FP8** is D-3s (#295): f16 sums, X_q, decoded weights. **H-1T** is Track H's tagged hardness route.
- **One unit** is the time of one dense FP8 multiply-add on the tensor cores at full rate. So "u units per MAC" means u
  times the time of the plain FP8 matmul being certified.

## The options

| Option | NCP-FP8 8,192³ | NCP-FP8 16,384³ | H-1T 8,192³ | H-1T 16,384³ |
|---|---|---|---|---|
| **No binding** (reference only; the proof does not hold without one, so no γ) | 5.02×, γ — | 4.98×, γ — | 3.99× (measured), γ — | 3.97× (measured), γ — |
| **1. SHAKE256 per word** (measured 2,291 units per byte) | 1,723×, γ′ 0.0059% | 1,723×, γ′ 0.0034% | 1,270×, γ′ 0.0040% | 1,268×, γ′ 0.0025% |
| **2. Cheaper hash per word** (TurboSHAKE128, measured 826 units per byte) | 625×, γ′ 0.016% | 625×, γ′ 0.009% | 461×, γ′ 0.011% | 460×, γ′ 0.007% |
| **3. Fold under `FoldForcesWrites`**, fold work credited (not re-priced) | 42.3× (42.0×), γ′ 0.23% | 41.7× (41.4×), γ′ 0.14% | 31.1×, γ′ 0.18% | 30.7×, γ′ 0.11% |

Slowdown is against plain FP8.

- **Corrected 29 Sep** ([hashing accounting](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/hashing-accounting.md)): with any per-word binding, and hashing free in γ, γ is 1.68%, 0.98%, 1.15% and 0.71% across the four columns. The γ′ figures in options 1–3 credit the hashing, which that note recommends against.

- **Where the costs come from:**
  - Option 1: the digests bind every checked word, at 0.75 B per MAC for NCP-FP8 and 0.55 for H-1T, and the noise XOF
    is under 0.001 B per MAC.
  - Option 3: the red team's cheapest sound fold costs 36 units per MAC for NCP-FP8 and 26 for H-1T. That is two keyed
    multiply-xor chains per tile and one SHAKE256 per tile. On top of that comes the SHAKE256 noise XOF: 0.3–1.0 units
    per MAC.
  - If the fold's work is not credited, γ is about 86%.
- **What "26–36 units per MAC" means:** the fold alone takes 26–36 times as long as the plain FP8 matmul it certifies.
  It runs on the CUDA cores, and it can't hide under the tensor-core work, which is only 4–5 units per MAC. So the fold
  sets the pace, and the end-to-end slowdown is about 31–42×.
- **The small γ′ values come from dilution, not strength.** In every option the binding is most of the work. So γ′ is
  decided by whether an adversary can do the binding more cheaply than the reference price. In every cell, a 0.9–1.0%
  faster hash or fold is enough to reach γ′ = 1%.
  - nvcc's own Keccak build is already 7.2% slower than the explicit one.
  - An untried mixed-pipe Keccak could be up to 24% faster.
  - So Round 11 has to measure the fastest build anyone knows.
  - This also runs against the plan's goal that security comes from the matmul work, not from hashing.

**Is any option inside 5×? None of these three.** The closest is the fold, at about 31× (H-1T) and 42× (NCP-FP8).
The one path that might reach 5× is a combination from the scout's tests, untested as a whole: choice B below.

## In plain words

**What the per-word hash is for.** The proof counts how many distinct 32-bit results the prover must have written into
registers, since each costs 32 units on an H100. Hashing every checked word forces the prover to hold each one, because a
hash can't be fed a word that was never computed, so the count applies. The audit alone would need only one
collision-resistant digest per tile, because the verifier replays whole tiles. The per-word part exists for the lower
bound.

**What `FoldForcesWrites` would assume about the hardware.** It assumes that on a real H100, no program can compute a
tile's keyed fold without first writing each of the tile's words, not even by a shortcut through the tensor cores or the
FP32 rounding.

**Why it isn't provable today.** It is a claim about every possible program on the real hardware's arithmetic, which is
the kind of conjecture the H100 route was built to avoid; the route rests only on measured per-instruction prices and
counting. The only concrete test so far went against it. H-1T's running-sum adds are exact in 99.3–100% of steps, so a
linear fold can be computed from the atom words alone, which loses half the credited words. A nonlinear fold blocks that
shortcut, but nothing rules out others.

## Recommendation

**Hold. Don't adopt a binding for FP8 yet.** No option is both provable and inside 5×.

**Settled: sampled proofs' own commitment is not the binding** (`docs/pouw/sampled-proofs-circuit.md` §5). Since your
00:15Z ruling, sampled proofs is PoUW's verifier. But its commitment forces each credited word to be written only if
every word is committed verbatim under a random oracle. That is per-word hashing paid elsewhere: about 3,300 units per
word by the design's count, or about 5,500 with the scout's SHA-256 leaf, against H-1T's budget of 4–8. Anything
cheaper binds only a function of the words, and fails for the same reason the fold does.

**What you'd be choosing between:**
- **A. A provable binding now, well outside 5×:** the cheaper per-word hash (option 2), at about 460–620× plain FP8.
  - It keeps the proof as it is.
  - It needs one named extra assumption: the reference hash price is within 0.5% of the fastest implementation.
  - It is priced at Round 11's measured rate.
  - SHAKE256 (option 1) does the same job at 2.5× the cost, and the fold (option 3) is about 31–42× on an unproven
    assumption. Neither is worth choosing over A.
- **B. Research the one path that might reach 5×, for H-1T only.** It has two parts, and the scout tested each
  separately (the last section):
  1. **Accumulate in the tensor cores, with one FP32 add every 4 steps.** H-1T drops from 4.45× to about 2.8×.
  2. **Bind with the integer mix:** half an instruction per word in idle slots.

  Together they fit 5× in time, but not by instruction count. The test results are in the section below. B needs:
  - a new H-1T variant, with Track H's distinctness census and the Lean proof redone;
  - the tensor core's add into a nonzero accumulator confirmed on an H100 (Round 11's capture C2 tests that);
  - `FoldForcesWrites`, the unproven assumption above;
  - your ruling to credit the mix's own work, without which γ rises by about 50 points;
  - a red-team pass.

  NCP-FP8 has no such path.
- **C. Neither, for now.** FP8 PoUW stays unbound research, and A6 stays open.

**Recommended, and decided by Daniel at 01:37Z: C now, with B's next steps authorized.** They are CPU only, plus capture C2 in Round 11, which is within
its cap:
- test the combined variant, meaning the census, the output error and the mix's shortcut test together;
- a red-team pass on `FoldForcesWrites` for the integer mix.

Choose A only if FP8 PoUW has to ship with a binding before B reports.

## B's results (02:40Z): what you'd be deciding next

Both of B's next steps ran on CPU:
- **the combined variant:** H-1T with tensor-core accumulation, an FP32 add every 4 steps, and the integer mix;
- **a red-team pass on `FoldForcesWrites`** for the mix.

The full accounts are `internal/pouw-fp8/a6-binding-scout.md` (the combined variant) and
`internal/pouw-fp8/redteam-transcript-binding.md` X-A6-8 to X-A6-15.

**What the combined variant does on the model:**
- **Distinctness:** at most 0.07% of credited words fail to count, and 0 on real weights.
- **Output error:** 0.007–0.037% median against today's FP32 chain. Against the exact result it is within 0.01 point of
  the FP32 chain's own error.
- **Shortcuts:** no cheap shortcut reproduces a tile's mix, in 0 of 3,840 real tiles. Only recomputing the same words
  works, and that saves nothing.
- **Speed:**

  | Size | In time | At the measured tensor-core share | By instruction count |
  |---|---:|---:|---:|
  | 8,192³ | 2.8× | 3.8× | 5.56× |
  | 16,384³ | 2.8× | 3.8× | 5.53× |

  **So it is inside 5× in time.** The mix runs in instruction slots the matmul leaves idle.
- **All of this except cost and γ assumes** the tensor core adds correctly into a nonzero accumulator. An H100 has
  confirmed that only from zero, and Round 11's capture C2 tests it.

**What the red team found about the assumption:**
- **Broken as first stated, and cheap to repair.** The mix sees each word's sign only through one parity bit per tile,
  and on all-zero slices H-1T's second block is exactly the negative of its first. The repair is a verifier rule: those
  atoms are neither credited nor computed. γ doesn't change.
- **After the repair, no attack worked,** but it is provable only at the leaf level. A general proof would need circuit
  lower bounds beyond known techniques. So `FoldForcesWrites` would stay a named, unproven assumption about all H100
  programs.
- **Two gaps remain:**
  - the assumption must name a word order the GPU can stream, and none has been tested;
  - each tile's mix checks only 22 of 32 bits against a prover who has the running sums. The scout adds that on
    zero-activation inputs a wrong tile can keep the right mix far more often than 2^−32.

**The question for you: credit the mix's own work, or not?** (**Decided 17:32Z: not credited; B closed.**) It decides γ:

| γ (combined variant) | 8,192³ | 16,384³ |
|---|---:|---:|
| Mix credited at its reference price (Round 11 prices) | **0.86%** | **0.49%** |
| Mix credited only at the provable floor | 25.8% | 25.5% |
| Mix not credited | 50.6% | 50.4% |

- **Crediting it means about half of the certified work is the binding, not the useful matmul.** The mix costs about 32
  units per word (the scout corrected its earlier 16), which is about half of the 5.56× instruction count.
- **It also means trusting that no one can compute the mix more cheaply than its reference price.** At 8,192³ a mix just
  0.17% cheaper lifts γ to 1%, so there is almost no margin.

**My recommendation: keep C.**
- Run capture C2 in Round 11 regardless. It is cheap, it is already in the cap, and it also settles the Lean model's
  open silicon question.
- Go further with B only if you're willing to credit the mix at its reference price. The next steps would be:
  - the sign repair written into the scheme;
  - a streaming word order, tested;
  - `FoldForcesWrites` restated on the combined chain's words;
  - Track H's distinctness census and the Lean statement redone for that chain.
- If you aren't willing to credit it, B stops, and FP8 PoUW's binding stays per-word hashing (option A) whenever FP8
  has to ship.

## What fitting 5× would take

At 8,192³, the binding would have to cost:
- **H-1T:** at most **0.55 units per MAC**, from its instruction-count slowdown of 4.45×. If its untimed checked step
  overlaps like D-3s's, it could be about 1.1. That is about 4–8 units per credited word, or 1/8–1/4 of one 32-unit
  register write.
- **NCP-FP8:** nothing at the measured 5.28×, and about 0.02 units per MAC at the staged 4.98×.

**The scout's CPU tests** (29 Sep; bit-exact model and Track H's code, k = 2,048–32,768; full account, scripts and JSON
in [`internal/pouw-fp8/a6-binding-scout.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw-fp8/a6-binding-scout.md)).
Everything below except the costs rests on the tensor core's add into a nonzero accumulator, which Round 11's C2 tests.
- **Dead:** the running-sum digest, because the tensor core forms up to 20% of the sums (93–100% on inputs built for
  it) without writing their atom words. Also dead: tensor-core accumulation without FP32 adds, where up to 80% of the
  words can't be counted.
- **Promising:** tensor-core accumulation with one FP32 add every 4 steps (4.45× → 2.8×), and the integer mix, a tree of
  3-input integer adds and XORs over the words. **Correction:** the mix costs about 32 units per word, not 16. So it
  doesn't fit the variant outright, and leaving it uncredited raises γ by about 50 points, not 30.

**Combined variant** (29 Sep, 02:30Z; same file). B's two parts were run together, with the integer mix in a keyed order,
and the census, output error and shortcut test were measured on the same runs: all five sizes, real weights from four
models, Track H's four attack families and the scout's own inputs.
- **It holds on the model.** At most 0.07% of the credited words can't be counted. The output is within 0.01–0.04%
  (median) of the FP32 chain's, about a tenth of that chain's own error. No shortcut that saves work gave the right mix on
  any tile. Only exact emulations matched, and they redo the same words at a higher cost.
- **For the red team:** 3 tiles on built inputs kept the right mix under aligned changes, though none of those changes
  saved work. The keyed order must be known before computing, so it only stops weights prepared for a known tree. In
  the runs it changed nothing measurable.
- **Cost:** 5.56× by instruction count and 2.8–3.8× in time at 8,192³ (5.53× and 2.8–3.8× at 16,384³). **It fits 5× in
  time, not by count,** because the mix alone costs more than the tensor-core work.
- **γ:** 0.94% at 8,192³ and 0.53% at 16,384³ if you credit the mix's work at its reference price. It is about 25% if
  the mix is credited only at the floor, and about 50% if it isn't credited. So γ under 1% needs `FoldForcesWrites` and
  your ruling to credit the mix. At 8,192³ it also needs the reference price to be within 0.17% of the fastest mix.

**Ranking:** first the combined variant, which fits 5× in time but not by count; then the tensor-core digest, at 32 per
word, which no variant leaves. The other candidates stay out. None is provable today, and NCP-FP8 still has room for none.
