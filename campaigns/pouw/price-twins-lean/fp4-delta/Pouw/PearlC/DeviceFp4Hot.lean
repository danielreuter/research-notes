import Pouw.PearlC.DeviceFp4ChainOnly

/-!
# Pearl-C4 v2's accounting at an FP4 record (the price-twins lane's file; definitions only, staged)

Pearl-C4 v2 is T1: the hot word's H is removed before the clean-up by one exact FP32 add per word, credited as forced
clean-up (`pearlc4-domain-gamma.py`'s `hot = "credited"`; `theory-pearl-c4-domain.md`). The v2 protocol isn't staged, so
these definitions fix only what its price twins read:
* **The credit** (`creditFp4Hot d a s`): `creditFp4` plus the removal, `a` per word in FP4 units (`a = 2·FADD`). The
  cap is on this credit.
* **`W_ref`** (`wrefFp4Hot`): the credit plus the A-only forming `qa`.
* **γ** (`gammaFp4Hot`), and the chain-only reading (`creditFp4HotChainOnly`, `gammaFp4HotChainOnly`: the credit less
  `fs·m·k`, the removal kept, the cap on the full credit).
* **The accounting a v2 protocol and its tiles must meet** to give them: `Fp4HotUnitAccounting`, `Fp4HotTileAccounting`
  and their chain-only forms.
-/

namespace Pouw.PearlC

variable {Q R S : Type}

/-- **Pearl-C4 v2's credit at an FP4 record**: `creditFp4` plus the H removal, `a` per word (FP4 units). -/
def creditFp4Hot (d : Fp4Device) (a : ℚ) (s : Shape) : ℚ := creditFp4 d s + a * s.m * s.n

/-- **Pearl-C4 v2's `W_ref`**: the credit plus the A-only forming. -/
def wrefFp4Hot (d : Fp4Device) (a : ℚ) (s : Shape) : ℚ := creditFp4Hot d a s + d.prices.qa * s.m * s.k

/-- **Pearl-C4 v2's chain-only credit**: `creditFp4Hot` less the credited forming `fs·m·k`. -/
def creditFp4HotChainOnly (d : Fp4Device) (a : ℚ) (s : Shape) : ℚ := creditFp4Hot d a s - d.prices.fs * s.m * s.k

/-- **Pearl-C4 v2's γ** at the cap `ρ`: `1 − (399/400)/ω` with `ω = wrefFp4Hot/((1 − ρ)·creditFp4Hot)`. -/
def gammaFp4Hot (d : Fp4Device) (a ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefFp4Hot d a s / ((1 - ρ) * creditFp4Hot d a s))

/-- **Pearl-C4 v2's chain-only γ** at the cap `ρ`, on the full credit: `ω = wrefFp4Hot/(creditFp4HotChainOnly −
ρ·creditFp4Hot)`. -/
def gammaFp4HotChainOnly (d : Fp4Device) (a ρ : ℚ) (s : Shape) : ℚ :=
  1 - (1 - 1 / 400) / (wrefFp4Hot d a s / (creditFp4HotChainOnly d a s - ρ * creditFp4Hot d a s))

/-- **The per-unit accounting a Pearl-C4 v2 protocol meets** on the one-shape domain at `s`, with the credited bound
`K`: a unit within the cap has `W_ref = wrefFp4Hot` and is credited at least `K`. The forming-credited reading takes
`K = (1 − ρ)·creditFp4Hot` and the chain-only one `K = creditFp4HotChainOnly − ρ·creditFp4Hot`. Either holds once the
protocol's credit is that credit less the debit, with the cap `debit ≤ ρ·creditFp4Hot`. -/
def Fp4HotUnitAccounting (P : Protocol Q R S) (D : Layout → Prop) (d : Fp4Device) (a K : ℚ) (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
    P.actOK (U.layout.shape u) act → P.capOK H s' U u act →
      P.Wref U.layout u = (wrefFp4Hot d a s : ℝ) ∧ (K : ℝ) ≤ P.credit H s' U u act

/-- **The per-tile accounting a Pearl-C4 v2 protocol's audit tiles meet**, with the credited bound `K`: each tile has a
share `t ≥ 0`, with `Wcred = wrefFp4Hot·t ≤ Wref`, and a tile within the cap is credited at least `K·t`. -/
def Fp4HotTileAccounting (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : Fp4Device) (a K : ℚ)
    (s : Shape) : Prop :=
  ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes, ∃ t : ℚ, 0 ≤ t ∧
    TR.Wcred U.layout g act = ((wrefFp4Hot d a s * t : ℚ) : ℝ) ∧ TR.Wcred U.layout g act ≤ TR.Wref U.layout g ∧
    ∀ (H : Q → R) (s' : S), TR.capOK H s' U g act → ((K * t : ℚ) : ℝ) ≤ TR.credit H s' U g act

end Pouw.PearlC
