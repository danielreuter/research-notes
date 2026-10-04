import Pouw.PearlC.DevicePrices
import Pouw.PearlC.DevicePricesLoop

/-!
# v2-hot's accounting at a device record (the price-twins lane's file; definitions only, staged)

`pearl-c-sm120 v2-hot` is v2 with a salted hot start (`internal/pouw/rtx-pro/theory-pearl-c-sm120.md` §14,
`internal/pouw/ttout-restatements.md` §8). Each word's accumulator starts at a per-row `H_i` instead of +0. `H_i` has
its sign and mantissa from a sub-domain of row i's `E_A` seed and its exponent from a public sizing rule, and
U = fl(C̃ − H_i). The record (`devSm120v2hot`: the hot chain, U's removal step and the debit's replay on the hot chain)
is the rev lane's and isn't staged. These definitions fix only what the price twins read:
* **The credit** (`creditDevHot`): v2's `creditDev` plus U's removal, one FP32 add per word, credited as forced
  clean-up (Pearl-C4 T1's precedent). The cap is on this credit. H_i itself replaces the accumulator's zero fill and
  costs nothing; its keyed-hash block per row is priced with the hashing format (`docs/pouw/hashing-accounting.md`), as
  `E_A`'s own seeds are.
* **The sizing rule** (`HotSizing`): H_i's column scale, which the record reads, and its cost, in `W_ref` only. One `h`
  fixes both, so a protocol cited with `h` pays for the rule it uses. `publicConst c₀` costs nothing beyond forming's
  α_i and ρ_i. `colRms`, the job's largest column code RMS, needs a pass over B̃: one FP32 FMA per element, `n·k` per
  unit, at the measured 8.46.
* **`W_ref`** (`wrefDevHot`): the credit, the A-only forming `qa`, `c` per activation element (the kernel's cast and the
  in-loop A-only forming beyond the record's, as in `DeviceKernelWref`), and the sizing rule's cost.
* **γ** (`gammaHot`) at `ω = W_ref/((1 − ρ)·credit)`, and the accounting a v2-hot protocol and its tiles must meet to
  give it (`HotUnitAccounting`, `HotTileAccounting`).
* **The chain-only reading** (`creditDevHotChainOnly`, `gammaHotChainOnly`, `HotUnitAccountingChainOnly`,
  `HotTileAccountingChainOnly`): the credit less the forming `fs·m·k`, with the cap on the full credit, so
  `ω = W_ref/(creditDevHotChainOnly − ρ·creditDevHot)`.
-/

namespace Pouw.PearlC

open Pouw.Fp8Atom

variable {Q R S : Type}

/-- **An H_i sizing rule**, one object for both of its uses:
* `colMeanSq`, the square of the column scale `c` in H_i's exponent `e_i = ⌊log₂(√(32·16)·α_i·ρ_i·c)⌋`
  (`ttout-restatements.md` §8), as a function of the job's formed B̃. The v2-hot record reads it to form H_i;
* `cost`, the honest reference's cost of computing it, per unit, at the FP32 prices `pr`, which `W_ref` reads.
A v2-hot protocol cited with `h` must build H_i from `h.colMeanSq`, so that `W_ref` carries that same rule's cost. -/
structure HotSizing where
  colMeanSq : ∀ {n k : ℕ}, Matrix (Fin n) (Fin k) Code → ℚ
  cost : Prices → Shape → ℚ
  cost_nonneg : ∀ pr s, 0 ≤ pr.add → 0 ≤ cost pr s

/-- H_i's column scale is a public constant `c₀`, and the row factor α_i·ρ_i is forming's own: no extra cost. -/
def HotSizing.publicConst (c₀ : ℚ) : HotSizing := ⟨fun _ => c₀ ^ 2, fun _ _ => 0, fun _ _ _ => le_rfl⟩

/-- H_i's column scale is the job's largest column code RMS, `max_j (1/k)·Σ_t val(B̃_jt)²` squared: a pass over B̃, one
FP32 FMA per element at GPU 0's measured 8.46 (`ttout-restatements.md` §8), which is above both FP32 prices. -/
def HotSizing.colRms : HotSizing :=
  ⟨fun {_ k} B => Finset.univ.fold max 0 fun j => (∑ t, codeVal (B j t) ^ 2) / k,
    fun _ s => 423 / 50 * s.n * s.k, fun _ s _ => by positivity⟩

/-- **v2-hot's credit at a record**: `creditDev` plus U's removal `fl(C̃ − H_i)`, one FP32 add per word. -/
def creditDevHot (d : PearlCDevice) (s : Shape) : ℚ := creditDev d s + d.prices.add * s.m * s.n

/-- **v2-hot's `W_ref` at a record**, under the sizing rule `h`: the credit, the A-only forming, `c` per activation
element, and the sizing rule's cost. -/
def wrefDevHot (d : PearlCDevice) (h : HotSizing) (c : ℚ) (s : Shape) : ℚ :=
  creditDevHot d s + (d.prices.costs.qa : ℚ) * s.m * s.k + c * s.m * s.k + h.cost d.prices s

/-- **v2-hot's γ** at the cap `ρ`: `1 − (399/400)/ω` with `ω = wrefDevHot/((1 − ρ)·creditDevHot)`. -/
def gammaHot (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefDevHot d h c s / ((1 - ρ) * creditDevHot d s))

/-- **The per-unit accounting a v2-hot protocol meets** on the one-shape domain at `s`: a unit within the cap has
`W_ref = wrefDevHot` and is credited at least `(1 − ρ)·creditDevHot`. It holds once the protocol's credit is
`creditDevHot − debit` with the cap `debit ≤ ρ·creditDevHot`, and its `W_ref` is `wrefDevHot` under `h`. -/
def HotUnitAccounting (P : Protocol Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ)
    (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
    P.actOK (U.layout.shape u) act → P.capOK H s' U u act →
      P.Wref U.layout u = (wrefDevHot d h c s : ℝ) ∧ (((1 - ρ) * creditDevHot d s : ℚ) : ℝ) ≤ P.credit H s' U u act

/-- **The per-tile accounting a v2-hot protocol's audit tiles meet** on the one-shape domain at `s`: each tile has a
share `t ≥ 0` (its credited rows' share of the unit), with `Wcred = wrefDevHot·t ≤ Wref`, and a tile within the cap is
credited at least `(1 − ρ)·creditDevHot·t`. -/
def HotTileAccounting (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : PearlCDevice)
    (h : HotSizing) (c ρ : ℚ) (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes, ∃ t : ℚ, 0 ≤ t ∧
    TR.Wcred U.layout g act = ((wrefDevHot d h c s * t : ℚ) : ℝ) ∧ TR.Wcred U.layout g act ≤ TR.Wref U.layout g ∧
    ∀ (H : Q → R) (s' : S), TR.capOK H s' U g act →
      (((1 - ρ) * creditDevHot d s * t : ℚ) : ℝ) ≤ TR.credit H s' U g act

/-- **v2-hot's chain-only credit**: `creditDevHot` less the credited forming `fs·m·k`, as `creditChainOnly` is at the
H100. U's removal stays credited: it is clean-up, not forming. -/
def creditDevHotChainOnly (d : PearlCDevice) (s : Shape) : ℚ :=
  creditDevHot d s - (d.prices.costs.fs : ℚ) * s.m * s.k

/-- **v2-hot's chain-only γ** at the cap `ρ`, which stays on the full credit: `1 − (399/400)/ω` with
`ω = wrefDevHot/(creditDevHotChainOnly − ρ·creditDevHot)`. -/
def gammaHotChainOnly (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefDevHot d h c s / (creditDevHotChainOnly d s - ρ * creditDevHot d s))

/-- **The per-unit accounting a chain-only v2-hot protocol meets**: a unit within the cap has `W_ref = wrefDevHot` and
is credited at least `creditDevHotChainOnly − ρ·creditDevHot`. It holds once the credit is
`creditDevHotChainOnly − debit` with the cap `debit ≤ ρ·creditDevHot`. -/
def HotUnitAccountingChainOnly (P : Protocol Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ)
    (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
    P.actOK (U.layout.shape u) act → P.capOK H s' U u act →
      P.Wref U.layout u = (wrefDevHot d h c s : ℝ) ∧
        ((creditDevHotChainOnly d s - ρ * creditDevHot d s : ℚ) : ℝ) ≤ P.credit H s' U u act

/-- **The per-tile accounting a chain-only v2-hot protocol's audit tiles meet**: as `HotTileAccounting`, with the fixed
credit `(creditDevHotChainOnly − ρ·creditDevHot)·t`. -/
def HotTileAccountingChainOnly (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : PearlCDevice)
    (h : HotSizing) (c ρ : ℚ) (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes, ∃ t : ℚ, 0 ≤ t ∧
    TR.Wcred U.layout g act = ((wrefDevHot d h c s * t : ℚ) : ℝ) ∧ TR.Wcred U.layout g act ≤ TR.Wref U.layout g ∧
    ∀ (H : Q → R) (s' : S), TR.capOK H s' U g act →
      (((creditDevHotChainOnly d s - ρ * creditDevHot d s) * t : ℚ) : ℝ) ≤ TR.credit H s' U g act

end Pouw.PearlC
