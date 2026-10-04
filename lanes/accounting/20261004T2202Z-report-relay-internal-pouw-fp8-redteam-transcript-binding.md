---
id: 20261004T2202Z-report-relay-internal-pouw-fp8-redteam-transcript-binding
campaign: pouw
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/internal/pouw-fp8/redteam-transcript-binding.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/internal/pouw-fp8/redteam-transcript-binding.md`, sha256 `f776ec5cd068834085f9f7b6cfcf2b6c2dd59183972c7f9a4ef03cc31485c0a4`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# Red team A6: what a cheaper transcript binding costs in security

Audit item A6 of `docs/deployment-requirements-audit.md`. CPU only. The evidence is `redteam-transcript-binding-exact-fadd.py` and
its `.json`, beside this file; they use the store's bit-exact `HOPPER_E4M3_K32` atom and H-1T forming.

**Verdict.**
- The per-word hash is what makes the H100 bound count words at all.
- No fold or compressed transcript keeps that count. Linear folds lose the running words outright: about half the credited set.
- A cheap binding needs a new hardware-semantics hardness Prop, with the fold's own work credited.
- The only change that keeps the proof is a leaner random-oracle instance, worth about 2.5×.

**X-A6-1. The per-word hash buys the random-oracle extraction, not audit soundness.**
- **The audit never opens a single word.**
  - The MVP draws tiles after the transcript root. The prover opens A's rows, B's rows and the leaf, and the verifier replays the whole tile and compares the leaf (`protocols/pouw/PROTOCOL.md` on `cursor/pouw-mvp-4f91`, Lifecycle steps 4–6).
  - Any collision-resistant digest the verifier can recompute would make that check sound.
- **The lower bound needs more than binding the words as a function.**
  - `distinctWritesMH100On` assumes every target is a *register* of the program on S.
  - The game supplies this as "the adversary outputs the committed values". SHAKE256 as a random oracle realizes it: a correct digest means H was queried on the exact word string, so every credited word was written.
  - That is H-1T's §5.3 model gap "the hash as a random oracle".
  - A digest that fixes the words but can be computed without writing them discharges nothing. So every credited word must be a random-oracle input, verbatim.

**X-A6-2. Linear folds lose the running words (measured).**
- **Almost every FADD is exact.** In H-1T, 99.3–100% of the FADDs R_τ = RN(R_(τ−1) + I_τ) are exact at k = 8,192, 16,384 and 32,768:
  - on three rows: a Gaussian row with outliers, the zero row, and a 416 row sign-aligned to one column;
  - over 64 synthetic Student-t(4) weight columns and 3 salts.
  - So R_τ = I_1 + … + I_τ exactly.
- **Any fold linear in the words' values** (mod p, or over Z) then satisfies Σ r_τ·R_τ = Σ_σ (Σ_(τ≥σ) r_τ)·I_σ.
  - The prover absorbs only the I words, with suffix-sum keys, and never writes an R word.
  - That skips 2T − 3 of the 4T − 3 credited words: ε ≈ 50%, so γ(H-1T) goes from 0.75% to about 50%.
  - D-3s has the same split-K plus FADD chain. I did not measure it.
- **Over bit patterns mod p, the collapse is partial.** 73–88% of steps keep R's sign and binade, and on those steps bits(R_τ) − bits(R_(τ−1)) = I_τ/ulp(R).
- **GF(2)-linear folds (XOR/rotate, Pearl's mix)** avoid the collapse because of carries. But a duplicate pair cancels (w ⊕ w = 0), and so do the shared high bits of neighbouring R words.

**X-A6-3. The key can't come after the transcript commitment, so 1/|field| isn't the soundness error.**
- **The prover knows the key while it computes.** Keying after the commitment would mean keeping every word until the draw (12.3 KB per output, on top of A7) or replaying the unit. So the key comes with the noise, after the activation commitment.
- **1/|K| per fold only bounds blind guessing.** It assumes the words are fixed before the key, which they aren't here. Use at least 64 bits.
- **Equal-fold collisions and wrong words cancelling each other both need the correct fold value first.** A prover that knows r can do either. So everything reduces to one question: is F_r(ts) cheaper to compute than ts? For value-linear folds, X-A6-2 says yes.
- **Keys must be per tile, chained over positions.** Per-word keys cost XOF bytes per word, which is as much as hashing.

**X-A6-4. `DistinctLive`'s per-word count survives no fold, even a nonlinear one. This is the key answer.**
- **In the model, the proof collapses.**
  - Under a fold, the targets are just the fold words: 32 per fold word per tile.
  - `MH100w` can't restore the count, because a priced instruction there computes any function.
  - An MMA fed R_(τ−1) as its accumulator may write RN(C + atom(0, a, b)) directly, and put the slice's fold partial into a spare register.
  - That is one write per output per slice instead of two, so at most about half the honest cost, whatever the fold function g is.
- **On hardware, that fusion is impossible**: the accumulator path truncates C.
- **So restoring the count needs a Prop over hardware semantics.** That is a representation-exploiting, TT-type conjecture, the kind the H100 route avoided. It is false in `MH100w`.

**X-A6-5. Option (a), a compressed transcript, certifies nothing provable.**
- Words sampled after the commitment are vacuous: the prover just replays the drawn tile.
- Sample positions known in advance shrink the targets to the sample. Even a sampled R_τ needs only a sum of I words (X-A6-2).
- R_2T is the useful output plus the atoms' truncation residues, and it is already uncredited.
- Any credit beyond the sample needs a chain-forcing conjecture. That conjecture has known counterexamples: freezing, exact designs, and the structural pair.

**X-A6-6. A fold is W1 work, and nowhere near 1×.**
- **Only hash calls are free.** The §0 rule puts every other piece of online PoUW work in W_ref.
- **The cheapest absorption is broken.** A 3-input IADD3 or LOP3 tree costs 16 units per word, or 2.2 units per useful MAC for H-1T (0.138 words per MAC) and 3.0 for D-3s (0.1875). It is linear, so X-A6-2 applies.
- **A keyed nonlinear chain costs 2–5 writes per word**, 96–300 units: 13–41 units per MAC for H-1T and 18–56 for D-3s.
  - That is 25–100× below SHAKE256's 1,000–1,500, but 3–9× the word's own 32.
- **Every way of accounting for it fails:**
  - uncredited, it adds tens of points to γ (the integer lane's D2 figure is 35–67%);
  - declared free like a hash call, it hands over `MH100`'s free linear algebra, under which the exact R words count zero;
  - credited, most of the certified work is fold, which is against decision 1.
- **Pearl is near 1× only because it folds final output cells**, O(1/k) per MAC.
- **Untimed:** INT-pipe work kept `wgmma` at 98–100% in Round 8, so the slowdown in time may be smaller than the W1 price.

**X-A6-7. The minimum I'd accept.**
- **Keep the proof (recommended): random-oracle absorption of every credited word, with a leaner instance.**
  - TurboSHAKE128 or KangarooTwelve (Keccak-p with 12 rounds at a 168 B rate), or a BLAKE3-style ARX compression, takes about 2.5× fewer instructions per byte than SHAKE256.
  - That is about 400–600× per useful MAC.
  - The claim moves from `random-oracle/shake-256` to the new instance. The error stays q²·2^−256 plus salt guessing.
  - 0.55 and 0.75 B per MAC are already the floor for these designs (X-A6-1).
- **Cheap, with a new assumption:**
  - The fold: two chains per tile, acc ← (acc ⊕ w)·r mod 2^32, with odd r and seeds taken per tile from the noise derivation, then one SHAKE256 per tile.
  - Cost: about 190 units per word, which is 26 units per MAC for H-1T and 36 for D-3s.
  - Error: 2^−64 per audited tile against guessing, plus ε_f.
  - It rests on a named Prop in `H100Assumptions`, stated over hardware semantics, not `MH100w` (X-A6-4). **`FoldForcesWrites(g, ε_f, ρ)`**: any program right on a salt set of probability ≥ ρ that outputs the tile folds also writes all but an ε_f fraction of the credited words. With it, `distinctLiveMH100` gives 32·(1 − ε − ε_f)·n.
  - The fold's work must also be credited, which is Daniel's ruling under decision 1.
  - Before adoption it needs a red-team pass on exact R sums, shared high bits, the low bits (the low j bits of acc depend only on the low j bits of the words), and duplicates.

## `FoldForcesWrites` for the integer mix (second pass, authorized by Daniel)

The mix is the scout's #4 as `a6-binding-scout.md` §Test 3 defines it:
- a ternary tree over each tile's credited words (1 row × 8 columns, N = 8(4T − 3) words);
- levels alternating IADD3 and LOP3 0x96 (XOR3), each zero-padded to a multiple of 3;
- leaves in a keyed order, then one 32-bit root per tile, then SHAKE256 over the roots.

The evidence is `redteam-transcript-binding-intmix.py` and its `.json`, beside this file. They cover the scout's 27 cases per size at k = 2,048, 8,192 and 32,768, over 3 salts, with the bit-exact atom.

**Verdict: BROKEN as stated; PLAUSIBLE after a sign repair, in a hardware-semantic model.**
- **As X-A6-7 stated it, it fails for every ε_f below 25%.**
  - The mix sees the FP sign only through one parity bit per tile.
  - H-1T's two blocks give exactly opposite atoms on every all-zero slice, so a prover copies block 1's atom instead of computing block 2's.
- **Other readings fail too.** It is false in `MH100w` for every g, and reading "forces a write" as register equality is false even with hardware semantics.
- **Once repaired** (X-A6-11), in `MH100sem` and in cost form, no attack was found. It is falsifiable, but provable only at the leaves. The open content is that every R word costs a write.

**X-A6-8. The statement.**
- **The machine, `MH100sem`.** It is `MH100w` (prices `h100LoopFree` under `h32LoopFree`, free set F, free moves and operands), with one change: every priced op outputs its bit-exact sm_90 function of its inputs.
  - The pinned classes are IADD3, LOP3, IMAD, SHF, PRMT, FADD/FFMA/FMUL (RN), DADD/DFMA, HADD2/HFMA2, F2FP, and E4M3 k32 `wgmma`/`mma` via `HOPPER_E4M3_K32`, including C ≠ 0.
  - The C ≠ 0 semantics are the model's; the H100 validated C = 0 only.
  - Unpinned classes are outside the model.
- **Key timing.** κ comes from its own `derive` domain, after the activation commitment and the weight registration. The prover knows it while computing, so P may depend on κ.
  - x is fixed before κ, so the statement is required for all keys except a set of probability ρ_κ.
- **"Forces a write"** means that some register of P equals ±t on S: equal up to the FP sign. Plain equality is false (X-A6-10).
  - Suppose no two credited words are equal up to sign on S, and none equals a free value up to sign. Then the targets ±t are pairwise distinct and non-free, and `distinctWritesMH100On` charges 32 for each.
  - `DistinctLivePMAt` is `DistinctLiveAt` with "equal" and "free" taken up to sign.
- **Sketch** (a named hypothesis in `Pouw.Dimension.H100Assumptions`, not an axiom). `Sm90Sem`, `mixRoot` and `DistinctLivePMAt` enter its reads record:

  ~~~lean
  def MixGood (pr : Prices100) (εf ρ : ℚ) (x : LegalH1T) (κ : Key) : Prop :=
    ∀ S : Set Salt, ρ ≤ μ S → ∀ ε, DistinctLivePMAt ε S (F x) (ts x) →
    ∀ P : List Op100, (∀ o ∈ P, o.WFw pr (F x) ∧ Sm90Sem o) →
      (∀ s ∈ S, ∀ j, rootOut P s j = mixRoot κ (tileWords x s j)) →
      ∃ T' ⊆ ts x, (1 - ε - εf) * (ts x).card ≤ T'.card ∧
        ∀ t ∈ T', ∃ r ∈ regs100 sm90 P (L x), ∀ s ∈ S, r s = t s ∨ r s = -t s
  def FoldForcesWritesMix (pr : Prices100) (εf ρ ρκ : ℚ) : Prop :=
    ∀ x : LegalH1T, keyLaw {κ | ¬ MixGood pr εf ρ x κ} ≤ ρκ
  ~~~

  - **Theorem, `foldMixCost`:** with `distinctWritesMH100On`, cost ≥ 32(1 − ε − ε_f)·n.
  - Crediting the mix needs a cost form with the extra term c_mix·Σ_j (N_j − 1) (X-A6-15).
- **ε_f can't be 0.** A prover can skip ⌈log₂(1/ρ)/32⌉ whole tiles and guess their roots, which makes it right on a salt set of probability at least ρ.
  - So ε_f ≥ ⌈log₂(1/ρ)/32⌉·N/n. State it per unit, with n much larger than N, never per tile.
  - The roots' min-entropy on legal inputs needs its own census.
  - Conjecture: ε_f is exactly this term, and ρ_κ ≤ 2^−64.

**X-A6-9. `MH100w` refutes it for every g.**
- A priced instruction there computes any function.
  - A few `wgmma`s read a row's X_q slices and salt words, with the weights as free operands, and write the row's tile roots directly.
  - That costs about 15 per word read, spread over all the row's tiles, against 48 per credited word honestly.
- **No counting argument closes the gap.**
  - Given x and B, a tile's words are fixed by the row's salt: about 41 bits per slice, or 1.3 registers, against 16 credited words per slice per tile.
  - So any information argument forces at most about 8% of the writes. The rest must come from the instructions' semantics.

**X-A6-10. The mix is a T-function, injective in each word, and blind to sign up to parity.**
- **T-function.** It has no rotations, so the root mod 2^j depends only on the words mod 2^j.
  - The lowest bit to change in the root is the lowest bit to change in the word: 100% over 4 trials per tile, at all sizes.
  - So one wrong word always changes the root. The scout's 0% single-substitution rows are a theorem.
- **Sign.** Bit 31 has no carry out.
  - The root mod 2^31 ignores every sign.
  - Root bit 31 is the parity of the signs XOR a carry from below.
  - Flipping any two words' signs leaves the root unchanged in 100% of tiles.
- **Register equality fails.** The chain run on negated laid-out weights (free pre-salt data, the same instructions) flips the sign of every nonzero word, so no register equals an honest word.
  - Its root is exactly the honest root (offset 0) on every tile without a zero word, in every case and size.
  - Hence "up to sign" in X-A6-8.
- **Carries are the only nonlinearity, and they run upward.** A "cheap correction" to a mix of the I words alone is the R words' contribution itself.

**X-A6-11. The break: H-1T's blocks pair up to sign on all-zero slices.**
- **Where the pairs come from.** `h1t_ref` forms block 1 as (x + sμ, tags v) and block 2 as (−sμ, −v).
  - On a slice where every product x_i·b_i is 0, block 2's atom is exactly −1 times block 1's, on every salt.
  - Measured on 3 salts, I_τ = −I_(τ+T) on 100% of slices of the zero row, 98.6–99.6% for "first slice then 0" and 49.3–49.8% for "aligned first half". These are exactly their zero-slice shares.
- **Attack.** On those slices, skip block 2's atom and feed block 1's word to the mix unchanged.
  - The FADD's negate modifier keeps R exact.
  - The sign errors are invisible when their count in the tile is even. That count is fixed by x, so at most one atom per tile is computed to fix the parity.
  - It saves 32 per atom: T·z of the 4T − 3 credited words, where z is the share of zero-product slices.
  - Under the per-word hash the same move costs a negation (32) and saves nothing.
- **Census, exact (ε) against up to sign (ε±), at all three sizes:**

  | Rows | ε | ε± |
  |---|---:|---:|
  | Zero row | 0–0.11% | 25.0–25.3% |
  | First slice, then 0 | about 0% | 24.9–25.0% |
  | Half zero | 0–0.07% | 12.5–12.6% |
  | Quarter zero | 0–0.13% | 6.2–6.4% |
  | Real, S1, twins, aligned | unchanged | = ε |

  - Activations that are 90% ReLU-sparse have z ≈ 0.9^29 ≈ 5%, so ε_f ≈ 1.2%. Padding rows lose 25%.
- **Repairs:**
  1. **Cheapest, a verifier rule.** Block-2 atoms of zero-product slices are neither credited nor computed.
     - z is public, since the verifier knows x and B.
     - The honest reference uses the same sign trick, so c and W drop together and γ is unchanged.
  2. **Track H.** Make block 2's tags independent (not −v) and correct the tag residue in the output. This re-opens the tag separation and the error bound.
  3. **In the mix.** Rotate each level-0 output by a keyed amount (SHF.W, +1/3 op per word).
     - Only pairs in the same level-0 group stay invisible, about z/2 per tile.
     - It costs 10.7 per word, and no merge floor credits that: γ ≈ 19% at 8,192³.
  - Every repair still needs the census counted up to sign.

**X-A6-12. Exact FADDs, fusion and the keyed order.**
- **Every rewrite I found writes the R words.**
  - A level-0 IADD3 needs its members' bit patterns. An R word's bit pattern is its exact prefix sum renormalized to its binade.
  - The scout's integer emulation matches 100% of real steps, but at 3 or more INT ops per word.
  - The in-binade shortcut takes at least 2 ops per word, and it holds on only 73–88% of steps.
  - No instruction writes two R words, or their bit-pattern sum, into one register (X-A6-13).
- **Fusion saves nothing.** Test 1's tensor-core fusion forms R_τ directly, but the mix needs I_τ too (an FSUB or a second MMA), so the net is zero.
- **Keyed order, with the key known.** The tree depends only on the partition into groups.
  - Related pairs of one output share a level-0 group 1–2 times per tile under the keyed random order, and none has a shortcut.
  - In a second test, each duplicated value is replaced by a fresh value everywhere it occurs. The root stays unchanged (XOR siblings cancel) for 0 of 14,948 duplicated values under the keyed order, and 3 of 14,948 under each of two structured orders, all on built inputs.
- **Implementability is open.** A random partition over the whole tile needs the tile buffered: 4.5 KB per output at 8,192, or about 74 MB for a 128 × 128 CTA tile.
  - So the honest mix needs a streaming order: a per-output chain, or step-major groups with keyed local choices.
  - That order is the g the Prop must name. All the evidence here and the scout's is for the random order, apart from the duplicate test.

**X-A6-13. Tensor-core routes and partial writes save nothing.**
- **MMA reads cost more than the ALU.** Any MMA pays 32 or more per word read at n8, or 144 at the measured rate, against IADD3's 16.
  - IGMMA sums bytes, which serves level 0 only after recombination.
  - b1 MMA gives popcounts, not XOR.
  - FP16 accumulation packs two outputs per register, but I has 14 significant bits against FP16's 11, and unpacking costs a write.
- **The low bits of I.** I's low 10 bits are always zero (measured minimum 10, median 11, 12–13 on tag-only rows).
  - The root's low 10 bits ignore the I words in 100% of tiles.
  - So against a prover holding the R words, the root checks 22 bits.
- **Packing.** No sm_90 instruction puts two atom outputs or two FP32 R words into one register exactly. f16x2 is too narrow, and two chains in one DADD need 74 bits against 53.

**X-A6-14. Falsifiable, yes. Provable only at the leaves.**
- X-A6-11 falsifies the unrepaired statement.
- **A general proof is beyond reach.**
  - LOP3 is Boolean-complete, so a bound in any model containing it is a superlinear circuit lower bound for an explicit function.
  - A depth bound d doesn't help, because the honest chain has depth about 2T.
  - Information arguments stop at about 8% (X-A6-9).
- **Provable in Lean now:**
  - injectivity in each word, with the lowest-changed-bit lemma;
  - the T-function and sign-parity lemmas;
  - the `MH100w` refutation;
  - **the phased connectivity floor.** A program computing `mixRoot` from N word registers, taken as independent inputs, costs at least φ·(N − 1). Here φ = 32·min over instruction classes of (registers written)/(registers read − 1). Under H32:

    | Instructions allowed | φ |
    |---|---:|
    | 3-input ALU only | 16 |
    | Adding `wgmma` m64n8k32 with C | 15.07 |
    | Adding DFMA | 12.8 |
    | Adding `mma.sp` m16n8k64 E4M3 | 9.87 |

- **Left open:**
  - the word half, which is the conjecture: no `MH100sem` program gets the level-0 sums of R bit patterns without one register per R word;
  - C ≠ 0;
  - unpinned classes;
  - branching on κ and the salt;
  - the streaming order;
  - a floor outside the phased model, where the chain already connects each output's words.

**X-A6-15. Crediting the mix.**
- **Uncredited,** it is honest W1 with no credit: +32.7 points of γ.
- **Credited** at c_mix per merge, it is sound only if the Prop carries c_mix·Σ_j (N_j − 1).
  - That term is proved only in the phased model, and only at φ. The conjectured 16 rests on `MH100sem`.
  - A third of the certified work is then binding, not useful work. That is decision 1, Daniel's call.
- **In time,** the mix rides idle issue slots (about 5 per word, per the scout), so a W1 credit of 16 certifies work the clock barely sees.

| γ(H-1T) | 8,192³ | 16,384³ |
|---|---:|---:|
| No mix (today's per-word hash) | 1.24% | 0.75% |
| Mix uncredited | 33.96% | 33.73% |
| Mix credited at 16 per merge (conjectured) | 0.95% | 0.60% |
| Credited at φ = 15.07 / 12.8 / 9.87 (proved, phased) | 2.87 / 7.55 / 13.60% | 2.52 / 7.22 / 13.29% |

- **Path B** credits the promoted tensor-core chain's words instead.
  - The statement and X-A6-11's census must be redone on them; the FADD analysis doesn't carry over.
  - C ≠ 0 must be validated on an H100 first.
