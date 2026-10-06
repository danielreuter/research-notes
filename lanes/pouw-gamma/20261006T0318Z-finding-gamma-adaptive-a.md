---
id: pouw-gamma/20261006T0318Z-finding-gamma-adaptive-a
campaign: proofs
lane: pouw-gamma
kind: finding
status: final
repo: verity
origin: bc-7f347b4b-6175-4b6e-84c6-731add2f8589 (pouw-gamma, for the proofs coordinator), at main c305471c5
---

# Pearl-C's γ with A chosen after the coins (option (a)): it does not hold; seed E_A per row (`-h3`) instead

Written 8:18 PM PDT, 5 Oct, for the proofs coordinator's interface draft (11 PM PDT) and Daniel's morning ruling.

## Answer

**No.** Under option (a), E_A comes from the epoch coins and the matmul index alone, so the prover knows every row's
noise before it chooses the row. It can then choose each row of A so that the formed row A′ lands exactly on one of a
few shared target rows. The noisy product C̃ = A′·B̃ᵀ is then the same few rows over and over: the prover computes them
once per weight per epoch and copies them. On the exact Python reference at 8192³, 256 of 256 rows (8 calls × 32 rows,
each row with its own E_A) formed bit for bit onto 16 shared A′ rows, and every row passed every rule Pearl-C v1 applies.
The prover's work becomes about 2–4% of W_ref, so the best γ the game can give under (a) is about 96–98%, which is no
bound at all. 0.36949% is not merely loosened.

**The cheapest fix is already designed and proved: per-row seeds, the `-h3` hash format.** Row i of call u draws E_A
from H_"pearl-c/v0/seed-A"(coins ‖ leaf_i ‖ root_B ‖ u·2³² + i), where leaf_i is the GPU's own unsalted digest of that
row. The seed binds the row, the coins can stay public before serving, and neither the gateway nor any round trip sits
on the critical path. `ttOutRowSeed_of_ttOut` (pinned on main) reduces the row-seeded TT_OUT to the per-unit TT_OUT
already granted, with no new named assumption. γ is unchanged, and the error becomes (q + R)/2¹²⁸ over the R declared
rows. On the panel, `-h3` is cheaper than `-h2`: 1.340× against 1.464× at decode and 1.205× against 1.223× at prefill, on
GPU 1's real call. What's missing is Lean only: a row-seeded twin of the served line's theorem (the `K` variant at
LoopCast8p72, cap 1/1000), which is a mechanical port, plus the statement review of the deployed seed's conditions.

## 1. The game already lets the prover choose A after the salt

`Definitions/Pouw/Game/Defs.lean` fixes the workload (layout and weights) and the preprocessing before the salt s. The
online program then runs with s and the oracle, "reads the workload and its activation input A.act; it may commit other
activations" (line 19). So the existing statement is already adaptive in A. What option (a) changes is the semantics,
not the game. Every γ theorem quantifies over `sem : PearlCSem` and takes TT_OUT at that `sem` as its hypothesis `hTT`,
for example `pearlCHiddenSm120v1LoopCast8p72Rev1Cap1000_8192 … (hTT : TTOutTilePearlCDevRev1 CM (devSm120v1
Prices.sm120Loop) sem (1/1000))`. `PearlCSem.noise H s U u act` is abstract, and TT_OUT's rationale (`εPearlC = (q +
N)/2¹²⁸`) counts one fresh ROM draw of E_A per unit and per oracle query. That counting needs the noise to be read at an
oracle point that determines the unit's activations. Today it is: seed_A = H(salt ‖ root_A ‖ root_B ‖ index), so each
candidate A costs a query, and grinding over candidates is what the union bound pays for. Under (a), `sem_a.noise` does
not read `act`, so the theorems still type-check, but their hypothesis TT_OUT(sem_a) is false. The attack below is a
counterexample to it, so no γ follows. A new statement for (a) would not rescue this, because the attack wins the game
as stated.

## 2. The attack under (a)

**Freedom.** The prover chooses every FP32 word of every activation row after the coins. Nothing in Pearl-C's rules ties
a unit's A to the previous layer: TT_OUT puts the quantizer and glue outside the unit (`TTOut.lean`, lines 55–57), and
the game lets the program commit other activations.

**Construction.** Each row has 32 noise codes E, known before the row is chosen. Forming v1 computes
A′ = e4m3(atom(α·x, E′, F_A)), with E′ = e4m3(β·E). Here α = 448/max(s + 4ρ, 2⁻³²) and β ∝ ρα, where s is the row's
max and ρ its RMS over every 8th position. The prover fixes one target row T, shared by every row: 7/8 of its positions
are fixed generic small codes, with one spike, and its stride-8 positions are either 0 or a multiple of one column of
F_A. That gives 193 possible targets, and 16 were used.

For each row, the prover:

1. Guesses the stride-8 RMS t. That fixes β, then E′, then the noise vector n = E′·F_Aᵀ.
2. Sets x = (T − n)/α, with a spike at one position that pins α.
3. Accepts when the RMS of that x at the stride-8 positions gives back t (a fixed point).

E′ is constant on pieces of t: there are 131 pieces per row on average over the scan's [1, 4], and 46 over the observed
range [1, 1.6] (64 rows measured). Every accepted row is verified with the reference's own `pearl_c.form_v1`.

**Measured on the reference** (`verity/protocols/accounting/work/pouw/schemes/pearl_c.py` at c305471c5, device
`pearl_c_device.SM120`, E_A per call = H(coins ‖ call index) as (a) proposes):

| k | rows | formed onto a shared target | distinct A′ rows | floor and `live_row` |
|---|---|---|---|---|
| 1,024 | 16 (1 call) | 16 | 7 | 16/16 |
| 8,192 | 64 (2 calls) | 64 | 7 (56 rows on one) | 64/64 |
| 8,192 | 256 (8 calls) | 256 | 16 (216 rows on one) | 256/256 |

Every committed x row is distinct, and t ranged over [1.0001, 1.5092]. Within each class, the C̃ words of the first and
last row against test columns are equal.

**What doesn't stop it:**

- **Per-row rules.** v1's `admissible` (`pearl_c.py`, lines 516–523) and the work module's `row_passes` are exactly the
  noise floor ρ·α ≥ 1 and `live_row`, and every attack row passes both. R1 is Pearl-C4's per-row credit rule, not
  Pearl-C's.
- **The cap.** I replayed the debit (`pearl_c_debit.word_debit`) against 16 honestly formed Gaussian B̃ rows at
  k = 8,192. Honest rows flag 0 atom-words. The main class flags 2 of 4,096 (0.05% of atoms, about half the 1/1000 cap),
  and the two other classes tested flag 0. No row has a later +0 promotion. The cap reads within-word skippable atoms,
  not repetition across rows.
- **The audits.** The hidden audit (`TileProofSoundAll`) and the work law's K = 27,713 draws check that drawn tiles are
  computed correctly. Every attack tile is correct, since each C̃ word is the chain of the true A′ with B̃, so no number
  of draws sees anything.

**The prover's cost**, per row at k = n = 8,192 (my estimate, in W_ref's units):

- The search: about 46 pieces × k/8 for the stride-8 RMS (updated one code at a time), plus one k × 32 product for n and
  one forming check, so about 0.6M.
- P_A: r·k, about 0.26M.
- The peel: 2r BF16 per word at price 2 = 128 per word, so about 1.05M.

Copying the class rows' C̃, and computing them (at most 193 rows per weight per epoch), comes on top. The total is about
1.9M per row, against W_ref ≈ 8,921 × 8,192 ≈ 73M per row: about 2.6%. My script's naive search (a full product per
piece) would cost about 47%. A real attacker uses the incremental search, which is ordinary linear algebra.

## 3. Options

- **(a) as proposed: no bound** (sections 1–2).
- **`-h3` per-row seeds: recommended.**
  - **Definition.** `hash.cuh`'s `b3_seeds` (mode i2 = 1) and `serving.py`'s `"h3"` format (`seed_a="row"`,
    `row_cap=True`) exist on main. The Python reference has no `row_seed` yet (`hash.cuh` cites `pearl_c.row_seed`), and
    `PROTOCOL.md` doesn't document `-h3`. Under the service, s is the epoch coins, which is exactly the game's salt, and
    seed_B = H(coins ‖ root_B) stays as it is. Coin-keyed seeds are sound for operands registered before the coins (the
    weights) and never for operands chosen after them.
  - **Proof, pinned on main.** `ttOutRowSeed_of_ttOut`, `ttOutTileRowSeed_of_ttOutTile` and `ttOutRowSeedCode_of_ttOut`
    (owner @compute-accounting) read four conditions, all definitions or W1 properties, no cryptographic assumption:
    - (C0) `RowLocal`, which holds for every `devAt` device by `rfl`;
    - (C1) `RowSeedNoise`, the deployed seed's definition;
    - (C2) the per-row cap, which is what `-h3`'s `row_cap` is;
    - (C3) and (C5) `CM.SplitClosed` and `RelabelClosed`, both hypotheses on W1.

    Pinned instances: `pearlCSampledSm120v1RowSeed_8192` (cap 1/400) and `pearlCSampledSm120v2RowSeedCap1000_8192`.
  - **Missing for the served line.** The served theorem uses `pearlCProtocolDevRev1K`, which is rev1 with W_ref plus c
    per activation element. That term is row-additive, so a row-cap `K` twin of the reduction is a port of
    `RowSeedGamma.lean` (1,296 lines; better generalized once over any row-additive W_ref). `gammaHidden_of_sampled_all`
    is generic, so γ = 1648180439/446072750000 (0.36949%) follows at error (q + R)/2¹²⁸ on the domain R ≤ 2⁶⁴. I didn't
    build it. `server.md` records that `-h3` waited on M3's statement review, and I didn't confirm whether that review
    closed.
  - **GPU cost (measured, `internal/pouw/rtx-pro/server.md`).** `-h3` is 1.340× at decode and 1.205× at prefill on GPU
    1's real call, against `-h2`'s 1.464× and 1.223×. `-h3`'s fused A path is 11.0 µs per call (#537), against the
    service draft's 17.9 µs per call for `-h2`'s A commitment. Option (a) would save at most that A path; that saving is
    unmeasured.
  - **Hidden-audit cost (estimate, not built).** If the row digest is unsalted, E_A must stay private: an unsalted digest
    of a low-entropy row allows a dictionary check. So the circuit derives the seed and the noise line in gates for each
    drawn A row:
    - about 4 BLAKE3 compressions (two for the 104-byte seed, two for the line);
    - the line's normalization (an isqrt, a BF16 divide, 32 BF16 multiplies and casts);
    - E′ with E as a witness rather than a constant.

    My estimate is 0.1–0.2M ANDs per drawn A row, about 1% of the ≈14.9M ANDs that row's hm96-sha512 read already costs
    at k = 8,192. The seed should be keyed on the digest the gadget already computes, hm96's inner SHA-512 row digest.
    Keying it on `-h3`'s BLAKE3 leaf would add a second full-row hash, about 5.7M ANDs per row. Whether the
    SHA-512-keyed seed is a `CodeSeedNoise` relabel of the granted per-unit `sem`, or TT_OUT at a different `sem` citing
    `cr/sha-512`, is for the statement reviewer. Pearl's lottery tickets are keyed by seed_A, so in served mode they
    should be dropped or keyed by a public per-call value.
  - **Variant with no new gates.** The GPU publishes salted per-row commitments and the seed reads them, so the seed is
    public. That moves salting from the gateway to the GPU, which is the service design's call.
- **(b) as briefed** (ncp-v2's pattern: a per-call digest of A in gates feeding the seed). It works, but forming waits
  for the whole call's digest (a per-call barrier like `-h2`'s A root). In gates it adds a per-call tree, a key, and a
  separate row hash over the FP32 row (about 15M ANDs per row if not shared with hm96's read). `-h3` dominates it.
- **Revealing coins after A's roots reach the gateway, in batches: doesn't fit decode.** Forming needs E_A inside the
  call, and the next layer needs this call's U, so a reveal per batch is either a per-call round trip, which is (c), or
  a second noisy pass that doubles the work.
- **(c) the gateway in the critical path:** rejected in the brief, and not needed.

## 4. Confidence and what was checked

- **High that (a) breaks γ.** The attack is constructive, runs on the exact reference, and passes every rule
  Pearl-C v1 applies (`admissible`, the cap's replayed debit). Its success rate over E_A was 336 of 336 rows across the
  runs.
- **Medium-high that `-h3` restores 0.36949% on the served line.** That rests on the pinned reduction, a `K` twin not
  yet written, and the statement review of (C1) and (C2) for the deployed seed.
- **Not checked:**
  - No Lean was built. I read the definitions, the theorems' signatures and `lean-audit.json`, and wrote no scratch
    lemma.
  - The attack ran on the Python reference, not on GPU kernels.
  - The attacker's cost in W1 units and the gate costs are estimates; only the piece counts and the debit flags were
    measured.
  - Pearl-C4 was not tried. It has the same seed_A shape (`pearl_c4.noise`), so the same question applies, but its
    forming and R1 rule differ.

The attack scripts and their logs are private material, in the Project store under `private/pouw-gamma/`: `attack_a.py`,
`attack_a2.py`, `check_debit.py`, `pieces.py`, `run-8192.log`, `run-8192-8calls.log`, `debit-8192.log`, `pieces.log`.
They are run from a checkout with `PYTHONPATH=.:catalog`.
