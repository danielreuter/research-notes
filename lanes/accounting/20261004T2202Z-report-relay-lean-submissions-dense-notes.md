---
id: 20261004T2202Z-report-relay-lean-submissions-dense-notes
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/lean/submissions/dense/NOTES.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/lean/submissions/dense/NOTES.md`, sha256 `a75f04d9a0f499d84b2ff99707c7e25ba9b80212a2fee9ff0e0ab83299281b0e`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# The dense single-layer scheme (S1) meets the requirement

Status: **proved.** `DenseMeets.lean` proves `PousDense.dense_meets`, the first end-to-end `Meets` with no named
assumption, on `[propext, Classical.choice, Quot.sound]`.
- **Checks.** The module passes a kernel replay (`leanchecker`), and a replay from an empty environment
  (`leanchecker --fresh`, which rechecks Mathlib and `Pous` too). See `AXIOMS.txt`.
- **Grading.** It is not a pinned target, so `grade.sh` cannot grade it yet.
- **The statement for review** is `DenseMeetsDraft.lean` (a `sorry`). `DenseMeets.lean` repeats its definitions
  and statement byte for byte and proves it.
- **Scope.** It certifies security only, not decode cost. In the positive direction, it shows `Meets` is
  satisfiable.

| File | Content |
|---|---|
| `DenseMeetsDraft.lean` | the scheme and the statement, `sorry` (for review) |
| `DenseMeets.lean` | the same, proved; standalone (imports `Pous` and `Mathlib`) |
| `AXIOMS.txt` | `#print axioms`, kernel replays, hashes |

## The statement

~~~lean
/-- The complete DAG on `Fin B`: every earlier node is a parent. -/
def completeDAG (B : ℕ) : TopoDAG B where
  par i := Finset.univ.filter fun j => j < i
  par_lt _ _ hj := (Finset.mem_filter.1 hj).2

abbrev denseModel (B ℓ : ℕ) : IdealModel := IdealModel.randomOracle (LabelQry B ℓ) (Bits ℓ)

def blocks (B ℓ : ℕ) (W : Bits (B * ℓ)) : Fin B → Bits ℓ := (codeEquiv B ℓ).symm W

def denseScheme (B ℓ : ℕ) [NeZero B] : Scheme (denseModel B ℓ) where
  n := B * ℓ
  t := 0
  B := B
  ℓ := ℓ
  B_pos := Nat.pos_of_ne_zero (NeZero.ne B)
  Coins := Unit
  enc W H _ := (fun i => i.elim0, fun i => label (completeDAG B) (blocks B ℓ W) H i)
  dec _ C f := codeEquiv B ℓ fun i =>
    bxor (C i) (f (i, fun j => if j ∈ (completeDAG B).par i then some (C j) else none))

theorem PousDense.dense_meets :
    Pous.Meets (PousDense.denseScheme (2 ^ 16) 8192) .sequential 64 (2 ^ 20) 107 ((2⁻¹ : ENNReal) ^ 128)
~~~

`TopoDAG`, `LabelQry`, `label` and `bxor` are the trusted `Pous.Labelling` ones (B5's), and `codeEquiv` is the
trusted `Pous.codeEquiv`. `Meets` unfolds to five clauses:
- `ε ≤ 2^-128` (here equal);
- `Correct`, bit-exact public decoding;
- `CodeHoldsW`, `|C| ≥ |W|` (here equal);
- the space bound `|C| + |pp| ≤ 1.05·|W|` (here `|C| = |W|`, `|pp| = 0`);
- `AuditSecure .sequential ⌊ρ|C|⌋ 64 2^20 107 1% 2^-128`.

## Points for review

- **Model.** It is B5's random oracle on label-shaped queries `(i, partial assignment of labels)`, as in B5's
  modelling choice. A real hash's other inputs are independent of every label and are not modelled. Decoding
  makes one such query per block.
- **Data before the oracle.** `W` is fixed before `H` (the trusted layer's choice 1). So `d = W` is B5's
  fixed-before-the-oracle data, and no salt or commitment term appears. A deployment needs a salt drawn after `W`.
- **Parameters.**
  - `B = 2^16` blocks of `ℓ = 8192` bits, so `|C| = |W| = 2^29` bits.
  - The state is `S = ⌊(18/19)·2^29⌋ = 508614548` bits.
  - `D = 64` rounds and `Q = 2^20` queries per answer, with sequential reveal, `k = 107` challenges and
    `ε = 2^-128`.
  - The deadline is essential: the bound fails once `D ≥ B − s`.
- **Not certified: decode cost.** Each block hashes all earlier labels of its segment, `Θ(B)` absorptions per
  byte.
- **Reveal mode.** The statement uses `.sequential` (per-answer `(D, Q)`), the demanding one (F5).

## Proof (as planned; the Lean names in `DenseMeets.lean`)

1. **Reach on the complete DAG** (`card_reach_le`, `complete_hard`). From `s` pebbles, greedy pebbling covers at most `s + D` nodes in `D` rounds:
   each round adds at most the least unpebbled node. So the DAG is `PebblingHard` at
   `(B − D − 1, D, B)`, with every block a challenge.
2. **B5 gives `TimedINC`** (`dense_timedINC`). Rebuilding every block means all `B` challenges are right, so
   `TimedINC (denseScheme B ℓ) D Q β π` holds with `π = B·2^β·((B(Q+2))²/2^ℓ)^(B−D)`. The compressor and
   expander of `TimedINC` are B5's `A₁`, `A₂` with `W` fixed.
3. **`Pous.Pinned.Theorem1iiSeq`** (`PousTargets.theorem1_ii_seq`, the `thm1-family` proof) gives
   `Pr[pass] ≤ |Hist|·π + p₀^k`, with `p₀ = 1 − (β − S − B)/(B·ℓ)`.
4. **Rate 1:** `Correct` (`denseScheme_correct`: `C_i ⊕ H(i, C_{<i}) = W_i`), `CodeHoldsW`, `SpaceBound`.
5. **Certificate at `β = 531499840`** (`dense_union_term`, `dense_sampling_term`, `stateBound_dense`).
   - `|Hist|·π ≤ 2^1712 · 2^16 · 2^β · 2^(−8118·65472) = 2^-128` exactly.
   - `p₀ = 1 − 22819756/536870912 ≈ 0.957495`, and `p₀^107 ≈ 0.00959 ≤ 1%`, while `p₀^106 ≈ 0.01001`.

The certificate's union term is handled in exponents of 2. `two_pow_combine` and `sq_div_two_pow_le` keep
numerals like `2^531499840` away from `norm_num` and `ring`, which would try to evaluate them. `norm_num` checks
only the exponent arithmetic and the rational `p₀^107`.

