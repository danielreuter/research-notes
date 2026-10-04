import Pouw.PearlC.DeviceHot
import Pouw.PearlC.DeviceRev1

/-!
# v1-hot's accounting at a device record (the price-twins lane's file; definitions only, staged)

`pearl-c-sm120 v1-hot` is v1 (G = 4, cap 1/400, rev1's credit) with each group's word started at a salted `H_{i,g}`
instead of +0 (`internal/pouw/ttout-restatements.md` §9, bc-b58c6093). `H_{i,g}`'s sign and mantissa come from row i's
`E_A` sub-domain and its exponent from v2-hot's sizing rule (`HotSizing`, `DeviceHot.lean`), the same for every group of
the row. The total still starts at +0, and U = fl(T − Σ_g H_{i,g}), with the sum folded in FP32 per row. The record
(`devSm120v1hot`) is the rev lane's and isn't staged. These definitions fix only what the price twins read:
* **The credit** (`creditDevRev1Hot`): rev1's `creditDevRev1` plus U's removal, one FP32 add per word, credited as
  forced clean-up, as v2-hot's is. The first promotion stays excluded: the total starts at +0, so `T_1 = S_1` exactly
  and it stays skippable (`firstAddDev` as written). The cap is on this credit.
* **The fold** (`hotFoldDev`): Σ_g H_{i,g} per row, `k/(32·G) − 1` FP32 adds for each of the m rows, in `W_ref` only.
  It is honest work outside the tensor-core chain, and it scales with m, not m·n.
* **`W_ref`** (`wrefDevRev1Hot`): the credit, the A-only forming `qa`, `c` per activation element (the kernel's cast
  and the in-loop A-only forming beyond the record's, as in `DeviceKernelWref`), the fold, and the sizing rule's cost.
* **γ** (`gammaHotRev1`) at `ω = W_ref/((1 − ρ)·credit)`, and the accounting a v1-hot protocol and its tiles must meet
  to give it (`HotRev1UnitAccounting`, `HotRev1TileAccounting`).
* **The chain-only reading** (`creditDevRev1HotChainOnly`, `gammaHotRev1ChainOnly` and the two `…ChainOnly` accounting
  forms): the credit less the forming `fs·m·k`, with the cap on the full credit.
-/

namespace Pouw.PearlC

open Pouw.Fp8Atom

variable {Q R S : Type}

/-- **v1-hot's credit at a record**: `creditDevRev1` plus U's removal `fl(T − Σ_g H_{i,g})`, one FP32 add per word. -/
def creditDevRev1Hot (d : PearlCDevice) (s : Shape) : ℚ := creditDevRev1 d s + d.prices.add * s.m * s.n

/-- **The fold of a row's group starts**, Σ_g H_{i,g}: `k/(32·G) − 1` FP32 adds for each of the m rows (`k/128 − 1` at
G = 4), ascending in g. -/
def hotFoldDev (d : PearlCDevice) (s : Shape) : ℚ := d.prices.add * s.m * ((s.k : ℚ) / (32 * d.G) - 1)

/-- **v1-hot's `W_ref` at a record**, under the sizing rule `h`: the credit, the A-only forming, `c` per activation
element, the fold, and the sizing rule's cost. -/
def wrefDevRev1Hot (d : PearlCDevice) (h : HotSizing) (c : ℚ) (s : Shape) : ℚ :=
  creditDevRev1Hot d s + (d.prices.costs.qa : ℚ) * s.m * s.k + c * s.m * s.k + hotFoldDev d s + h.cost d.prices s

/-- **v1-hot's γ** at the cap `ρ`: `1 − (399/400)/ω` with `ω = wrefDevRev1Hot/((1 − ρ)·creditDevRev1Hot)`. -/
def gammaHotRev1 (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefDevRev1Hot d h c s / ((1 - ρ) * creditDevRev1Hot d s))

/-- **The per-unit accounting a v1-hot protocol meets** on the one-shape domain at `s`: a unit within the cap has
`W_ref = wrefDevRev1Hot` and is credited at least `(1 − ρ)·creditDevRev1Hot`. It holds once the protocol's credit is
`creditDevRev1Hot − debit` with the cap `debit ≤ ρ·creditDevRev1Hot`, and its `W_ref` is `wrefDevRev1Hot` under `h`. -/
def HotRev1UnitAccounting (P : Protocol Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ)
    (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
    P.actOK (U.layout.shape u) act → P.capOK H s' U u act →
      P.Wref U.layout u = (wrefDevRev1Hot d h c s : ℝ) ∧
        (((1 - ρ) * creditDevRev1Hot d s : ℚ) : ℝ) ≤ P.credit H s' U u act

/-- **The per-tile accounting a v1-hot protocol's audit tiles meet** on the one-shape domain at `s`: each tile has a
share `t ≥ 0` (its credited rows' share of the unit), with `Wcred = wrefDevRev1Hot·t ≤ Wref`, and a tile within the cap
is credited at least `(1 − ρ)·creditDevRev1Hot·t`. -/
def HotRev1TileAccounting (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : PearlCDevice)
    (h : HotSizing) (c ρ : ℚ) (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes, ∃ t : ℚ, 0 ≤ t ∧
    TR.Wcred U.layout g act = ((wrefDevRev1Hot d h c s * t : ℚ) : ℝ) ∧ TR.Wcred U.layout g act ≤ TR.Wref U.layout g ∧
    ∀ (H : Q → R) (s' : S), TR.capOK H s' U g act →
      (((1 - ρ) * creditDevRev1Hot d s * t : ℚ) : ℝ) ≤ TR.credit H s' U g act

/-- **v1-hot's chain-only credit**: `creditDevRev1Hot` less the credited forming `fs·m·k`. U's removal stays credited:
it is clean-up, not forming. -/
def creditDevRev1HotChainOnly (d : PearlCDevice) (s : Shape) : ℚ :=
  creditDevRev1Hot d s - (d.prices.costs.fs : ℚ) * s.m * s.k

/-- **v1-hot's chain-only γ** at the cap `ρ`, which stays on the full credit: `1 − (399/400)/ω` with
`ω = wrefDevRev1Hot/(creditDevRev1HotChainOnly − ρ·creditDevRev1Hot)`. -/
def gammaHotRev1ChainOnly (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefDevRev1Hot d h c s / (creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s))

/-- **The per-unit accounting a chain-only v1-hot protocol meets**: a unit within the cap has `W_ref = wrefDevRev1Hot`
and is credited at least `creditDevRev1HotChainOnly − ρ·creditDevRev1Hot`. -/
def HotRev1UnitAccountingChainOnly (P : Protocol Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing)
    (c ρ : ℚ) (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
    P.actOK (U.layout.shape u) act → P.capOK H s' U u act →
      P.Wref U.layout u = (wrefDevRev1Hot d h c s : ℝ) ∧
        ((creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s : ℚ) : ℝ) ≤ P.credit H s' U u act

/-- **The per-tile accounting a chain-only v1-hot protocol's audit tiles meet**: as `HotRev1TileAccounting`, with the
fixed credit `(creditDevRev1HotChainOnly − ρ·creditDevRev1Hot)·t`. -/
def HotRev1TileAccountingChainOnly (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : PearlCDevice)
    (h : HotSizing) (c ρ : ℚ) (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes, ∃ t : ℚ, 0 ≤ t ∧
    TR.Wcred U.layout g act = ((wrefDevRev1Hot d h c s * t : ℚ) : ℝ) ∧ TR.Wcred U.layout g act ≤ TR.Wref U.layout g ∧
    ∀ (H : Q → R) (s' : S), TR.capOK H s' U g act →
      (((creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) * t : ℚ) : ℝ) ≤ TR.credit H s' U g act

end Pouw.PearlC
