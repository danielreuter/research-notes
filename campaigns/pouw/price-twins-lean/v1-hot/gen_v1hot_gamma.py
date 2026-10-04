"""Writes Pouw/PearlC/HotRev1Gamma.lean: v1-hot's price twins, generic over the H_{i,g} sizing rule, and their values at
the fixed rule `HotSizing.publicConst 64`.

python3 gen_v1hot_gamma.py   (from this folder; exact arithmetic, stdlib only)
"""
from fractions import Fraction as F
from pathlib import Path

R, RHO, G = 32, F(1, 400), 4
SIZES = (8192, 16384)
# the statement's cast, GPU 0's 64-bit-store cast (server.md 10:25Z), and the kernel's as-written and packed casts
CASTS = {"Cast8": F(8), "Cast8p72": F(872, 100), "Cast32p06": F(3206, 100), "Cast16": F(16)}
# name, Lean prices, (add, bf16, fs, qa), c as a Lean term given the cast h
RECORDS = {
    "": ("Prices.sm120", (F(8), F(2), F(40), F(1)), lambda h: (h - 8, f"{lean(h)} - 8")),
    "Loop": ("Prices.sm120Loop", (F(1047, 125), F(2), F(40), F(2)),
             lambda h: (h - F(8953, 1000), f"{lean(h)} - 8953 / 1000")),
}
C0 = 64  # the sizing rule, HotSizing.publicConst 64, as v2-hot's (ttout-restatements.md §8 and §9)


def lean(q):
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator} / {q.denominator}"


def gamma(p, c, n, co=False):
    """v1-hot at the cap 1/400: rev1's credit plus U's removal, W_ref plus the fold of the group starts (§9)."""
    add, bf, fs, qa = p
    n = F(n)
    mk = n * n
    credit = n ** 3 + n ** 3 * add / (32 * G) + mk * R + 2 * bf * R * mk + fs * mk - add * mk + add * mk
    wref = credit + (qa + c) * mk + add * n * (n / (32 * G) - 1)
    den = credit - fs * mk - RHO * credit if co else (1 - RHO) * credit
    return 1 - F(399, 400) / (wref / den)


def pct(q):
    return f"{float(q) * 100:.5f}%"


# The four general theorems: v2-hot's (`../v2-hot/gen_hot_gamma.py`) with the v1-hot definitions.
GENERAL = '''namespace Pouw.PearlC

open Pouw.PearlC.Assumptions

/-- TT_OUT at a protocol meeting v1-hot's per-unit accounting gives `G_γ` at `gammaHotRev1 d h c ρ s`. -/
theorem pearlCGammaHotRev1At {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (P : Protocol Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ) (s : Shape) (hρ : ρ < 1)
    (hC : 0 < creditDevRev1Hot d s) (hW0 : 0 < wrefDevRev1Hot d h c s) (hacc : HotRev1UnitAccounting P D d h c ρ s)
    (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D (gammaHotRev1 d h c ρ s : ℝ) εPearlC := by
  have hden : 0 < (1 - ρ) * creditDevRev1Hot d s := mul_pos (by linarith) hC
  set ω := wrefDevRev1Hot d h c s / ((1 - ρ) * creditDevRev1Hot d s) with hωdef
  have hω0 : 0 < ω := div_pos hW0 hden
  have hid : wrefDevRev1Hot d h c s = ω * ((1 - ρ) * creditDevRev1Hot d s) := by
    rw [hωdef, div_mul_cancel₀ _ hden.ne']
  have hW : ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
      P.actOK (U.layout.shape u) act → P.capOK H s' U u act → P.Wref U.layout u ≤ (ω : ℝ) * P.credit H s' U u act := by
    intro U hU H s' u hu act ha hcap
    obtain ⟨hw, hcr⟩ := hacc U hU H s' u hu act ha hcap
    rw [hw, hid]
    push_cast
    exact mul_le_mul_of_nonneg_left (by exact_mod_cast hcr) (by exact_mod_cast hω0.le)
  have key := gammaFromTTOut CM P D (1 / 400) (ω : ℝ) εPearlC (by exact_mod_cast hω0) hW hTT
  have e : ((gammaHotRev1 d h c ρ s : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by
    rw [gammaHotRev1, ← hωdef]; push_cast; ring
  rw [e]
  exact key

/-- TT_OUT per tile at a protocol and tiles meeting v1-hot's per-tile accounting gives `GγSampled` at
`gammaHotRev1 d h c ρ s`. -/
theorem pearlCSampledHotRev1At {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
    (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ)
    (s : Shape) (hρ : ρ < 1) (hC : 0 < creditDevRev1Hot d s) (hW0 : 0 < wrefDevRev1Hot d h c s)
    (hacc : HotRev1TileAccounting P TR D d h c ρ s) (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D (gammaHotRev1 d h c ρ s : ℝ) εPearlC := by
  have hden : 0 < (1 - ρ) * creditDevRev1Hot d s := mul_pos (by linarith) hC
  set ω := wrefDevRev1Hot d h c s / ((1 - ρ) * creditDevRev1Hot d s) with hωdef
  have hω0 : 0 < ω := div_pos hW0 hden
  have hid : wrefDevRev1Hot d h c s = ω * ((1 - ρ) * creditDevRev1Hot d s) := by
    rw [hωdef, div_mul_cancel₀ _ hden.ne']
  have hW : ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes,
      TR.capOK H s' U g act → TR.Wcred U.layout g act ≤ (ω : ℝ) * TR.credit H s' U g act := by
    intro U hU H s' g hg act hcap
    obtain ⟨t, ht, hw, _, hcr⟩ := hacc U hU g hg act
    rw [hw, hid]
    have := hcr H s' hcap
    have e2 : ((ω * ((1 - ρ) * creditDevRev1Hot d s) * t : ℚ) : ℝ) =
        (ω : ℝ) * (((1 - ρ) * creditDevRev1Hot d s * t : ℚ) : ℝ) := by
      push_cast; ring
    rw [e2]
    exact mul_le_mul_of_nonneg_left this (by exact_mod_cast hω0.le)
  have hWc : ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes,
      TR.Wcred U.layout g act ≤ TR.Wref U.layout g := by
    intro U hU g hg act
    obtain ⟨t, _, _, hle, _⟩ := hacc U hU g hg act
    exact hle
  have key := gammaSampled CM P TR D (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc hTT
  have e : ((gammaHotRev1 d h c ρ s : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by
    rw [gammaHotRev1, ← hωdef]; push_cast; ring
  rw [e]
  exact key

/-- TT_OUT at a protocol meeting v1-hot's chain-only per-unit accounting gives `G_γ` at
`gammaHotRev1ChainOnly d h c ρ s`. -/
theorem pearlCGammaHotRev1ChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (P : Protocol Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing) (c ρ : ℚ)
    (s : Shape) (hK : 0 < creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) (hW0 : 0 < wrefDevRev1Hot d h c s)
    (hacc : HotRev1UnitAccountingChainOnly P D d h c ρ s) (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D (gammaHotRev1ChainOnly d h c ρ s : ℝ) εPearlC := by
  set ω := wrefDevRev1Hot d h c s / (creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) with hωdef
  have hω0 : 0 < ω := div_pos hW0 hK
  have hid : wrefDevRev1Hot d h c s = ω * (creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) := by
    rw [hωdef, div_mul_cancel₀ _ hK.ne']
  have hW : ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ u < U.layout.N, ∀ act : Codes,
      P.actOK (U.layout.shape u) act → P.capOK H s' U u act → P.Wref U.layout u ≤ (ω : ℝ) * P.credit H s' U u act := by
    intro U hU H s' u hu act ha hcap
    obtain ⟨hw, hcr⟩ := hacc U hU H s' u hu act ha hcap
    rw [hw, hid]
    push_cast
    exact mul_le_mul_of_nonneg_left (by exact_mod_cast hcr) (by exact_mod_cast hω0.le)
  have key := gammaFromTTOut CM P D (1 / 400) (ω : ℝ) εPearlC (by exact_mod_cast hω0) hW hTT
  have e : ((gammaHotRev1ChainOnly d h c ρ s : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by
    rw [gammaHotRev1ChainOnly, ← hωdef]; push_cast; ring
  rw [e]
  exact key

/-- TT_OUT per tile at a protocol and tiles meeting v1-hot's chain-only per-tile accounting gives `GγSampled` at
`gammaHotRev1ChainOnly d h c ρ s`. -/
theorem pearlCSampledHotRev1ChainOnlyAt {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S]
    (CM : CostModel Q R S) (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : PearlCDevice)
    (h : HotSizing) (c ρ : ℚ) (s : Shape) (hK : 0 < creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s)
    (hW0 : 0 < wrefDevRev1Hot d h c s) (hacc : HotRev1TileAccountingChainOnly P TR D d h c ρ s)
    (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D (gammaHotRev1ChainOnly d h c ρ s : ℝ) εPearlC := by
  set ω := wrefDevRev1Hot d h c s / (creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) with hωdef
  have hω0 : 0 < ω := div_pos hW0 hK
  have hid : wrefDevRev1Hot d h c s = ω * (creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) := by
    rw [hωdef, div_mul_cancel₀ _ hK.ne']
  have hW : ∀ U : Workload, U.InDomain P D → ∀ (H : Q → R) (s' : S), ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes,
      TR.capOK H s' U g act → TR.Wcred U.layout g act ≤ (ω : ℝ) * TR.credit H s' U g act := by
    intro U hU H s' g hg act hcap
    obtain ⟨t, ht, hw, _, hcr⟩ := hacc U hU g hg act
    rw [hw, hid]
    have := hcr H s' hcap
    have e2 : ((ω * (creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) * t : ℚ) : ℝ) =
        (ω : ℝ) * (((creditDevRev1HotChainOnly d s - ρ * creditDevRev1Hot d s) * t : ℚ) : ℝ) := by
      push_cast; ring
    rw [e2]
    exact mul_le_mul_of_nonneg_left this (by exact_mod_cast hω0.le)
  have hWc : ∀ U : Workload, U.InDomain P D → ∀ g < (TR.tiling U.layout).NT, ∀ act : Codes,
      TR.Wcred U.layout g act ≤ TR.Wref U.layout g := by
    intro U hU g hg act
    obtain ⟨t, _, _, hle, _⟩ := hacc U hU g hg act
    exact hle
  have key := gammaSampled CM P TR D (1 / 400) (ω : ℝ) εPearlC (by norm_num) (by exact_mod_cast hω0) hW hWc hTT
  have e : ((gammaHotRev1ChainOnly d h c ρ s : ℚ) : ℝ) = 1 - (1 - 1 / 400) / (ω : ℝ) := by
    rw [gammaHotRev1ChainOnly, ← hωdef]; push_cast; ring
  rw [e]
  exact key

section Twins

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
'''


HEADER = """import Pouw.PearlC.TileGamma
import Pouw.PearlC.DeviceHotRev1

/-!
# v1-hot's price twins, generic over the H_{i,g} sizing rule (the price-twins lane's file; staged)

Generated by `v1-hot/gen_v1hot_gamma.py` in `internal/pouw/price-twins-lean/`.

* **γ from TT_OUT at any v1-hot protocol** (`pearlCGammaHotRev1At`, `pearlCSampledHotRev1At`): if the protocol meets
  v1-hot's accounting at a record (`HotRev1UnitAccounting`, `HotRev1TileAccounting`), TT_OUT at it gives `G_γ` (per
  tile, `GγSampled`) at `gammaHotRev1 d h c ρ s`.
* **The twins** (`pearlC{Gamma,Sampled}Sm120v1Hot{,Loop}{Cast8,Cast8p72,Cast32p06,Cast16}{,ChainOnly}_{8192,16384}`): v1
  under rev1 at the cap 1/400, at a record with `G = 4` and the issue-bound (`Prices.sm120`) or in-loop
  (`Prices.sm120Loop`) prices, against `W_ref` with the honest cast at the statement's 8, at 8.72, or at the kernel's
  as-written 32.06 and packed 16, for **every** sizing rule `h`. `c` is the honest cast less the credited 8, plus, in
  the loop, the measured A-only forming 1.047 less the record's 2, so `W_ref` is exact at both prices.
* **The values** (`gammaHotRev1_…`, `gammaHotRev1ChainOnly_…`): γ at each twin's record, cast and shape at the fixed
  rule `HotSizing.publicConst 64`, by `norm_num`.
* **The chain-only reading**, the same way: the credit less the forming, with the cap on the full credit. A chain-only
  protocol has the forming-credited one's game (neither `G_γ` nor `GγSampled` reads the credit).
-/

""" + GENERAL





def wrap(doc):
    lines, rest = [], doc
    while len(rest) > 120:
        cut = rest.rindex(" ", 0, 120)
        lines.append(rest[:cut])
        rest = rest[cut + 1:]
    return "\n".join(lines + [rest])


UNF_C = "creditDevRev1Hot, creditDevRev1, creditDev, firstAddDev"


def twin(rec, pr, cast, h, cterm, n, tile, co=False):
    CO = "ChainOnly" if co else ""
    name = f"pearlC{'Sampled' if tile else 'Gamma'}Sm120v1Hot{rec}{cast}{CO}_{n}"
    price = "1047/125 = 8.376" if rec else "8.00"
    what = "per audit tile, " if tile else ""
    reading = "chain-only, " if co else ""
    doc = wrap(f"/-- **v1-hot under rev1 at the cap 1/400, {reading}{what}{n}³**, FP32 at {price}, the honest cast at "
               f"{float(h):g}, under any H_{{i,g}} sizing rule `h`: "
               f"γ = `gammaHotRev1{CO} d h ({cterm}) (1 / 400) sh{n}` "
               f"(`gammaHotRev1{CO}_…` give its values). -/")
    pos = (f"(by rw [creditDevRev1HotChainOnly, {UNF_C}, hG, hp]\n        norm_num [{pr}, Params.pi, sh{n}])" if co
           else f"(by rw [{UNF_C}, hG, hp]\n        norm_num [{pr}, Params.pi, sh{n}])")
    posw = (f"(by have h0 := h.cost_nonneg {pr} sh{n} (by norm_num [{pr}])\n"
            f"        rw [wrefDevRev1Hot, {UNF_C}, hotFoldDev, hG, hp]\n"
            f"        generalize h.cost {pr} sh{n} = x at h0 ⊢\n"
            f"        norm_num [{pr}, Params.pi, sh{n}]\n"
            f"        linarith)")
    if tile:
        return name, f"""
{doc}
theorem {name}
    (P : Protocol Q R S) (TR : TileRules Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing)
    (hG : d.G = 4) (hp : d.prices = {pr})
    (hacc : HotRev1TileAccounting{CO} P TR D d h ({cterm}) (1 / 400) sh{n})
    (hTT : TTOutTile CM P TR D (1 / 400) εPearlC) :
    GγSampled CM P TR D (gammaHotRev1{CO} d h ({cterm}) (1 / 400) sh{n} : ℝ) εPearlC :=
  pearlCSampledHotRev1{CO}At CM P TR D d h _ _ _{"" if co else " (by norm_num)"}
    {pos}
    {posw}
    hacc hTT
"""
    return name, f"""
{doc}
theorem {name}
    (P : Protocol Q R S) (D : Layout → Prop) (d : PearlCDevice) (h : HotSizing) (hG : d.G = 4)
    (hp : d.prices = {pr})
    (hacc : HotRev1UnitAccounting{CO} P D d h ({cterm}) (1 / 400) sh{n})
    (hTT : TTOut CM P D (1 / 400) εPearlC) :
    Gγ CM P D (gammaHotRev1{CO} d h ({cterm}) (1 / 400) sh{n} : ℝ) εPearlC :=
  pearlCGammaHotRev1{CO}At CM P D d h _ _ _{"" if co else " (by norm_num)"}
    {pos}
    {posw}
    hacc hTT
"""


def value(rec, pr, p, cast, h, c, cterm, n, co=False):
    CO = "ChainOnly" if co else ""
    g = gamma(p, c, n, co)
    name = f"gammaHotRev1{CO}_sm120v1Hot{rec}{cast}_publicConst{C0}_{n}"
    price = "1047/125 = 8.376" if rec else "8.00"
    reading = ", chain-only" if co else ""
    unf = (f"gammaHotRev1ChainOnly, wrefDevRev1Hot, creditDevRev1HotChainOnly, creditDevRev1Hot, creditDevRev1,\n"
           f"    creditDev, firstAddDev, hotFoldDev" if co
           else f"gammaHotRev1, wrefDevRev1Hot, {UNF_C}, hotFoldDev")
    doc = wrap(f"/-- v1-hot's γ under rev1 at the cap 1/400{reading}, {n}³, FP32 at {price}, the honest cast at "
               f"{float(h):g}, at the sizing rule `HotSizing.publicConst {C0}`: `{lean(g).replace(' ', '')}` "
               f"({pct(g)}). -/")
    return name, g, f"""
{doc}
theorem {name}
    (d : PearlCDevice) (hG : d.G = 4) (hp : d.prices = {pr}) :
    gammaHotRev1{CO} d (HotSizing.publicConst {C0}) ({cterm}) (1 / 400) sh{n} =
      {lean(g)} := by
  rw [{unf}, hG, hp]
  norm_num [HotSizing.publicConst, {pr}, Params.pi, sh{n}]
"""


def rewrap_docs(text):
    """Refill each `/-- … -/` docstring longer than 120 columns."""
    import re

    def fill(m):
        block = m.group(0)
        if all(len(line) <= 120 for line in block.splitlines()):
            return block
        words, lines, line = block[4:-3].split(), [], "/--"
        for w in words:
            if len(line) + 1 + len(w) > 120:
                lines.append(line)
                line = w
            else:
                line += " " + w
        lines.append(line + " -/" if len(line) + 3 <= 120 else line + "\n-/")
        return "\n".join(lines)
    return re.sub(r"/-- .*? -/", fill, text, flags=re.S)


def main():
    out, vals, table = [HEADER], ["\nend Twins\n\n/-! ## The values, at `HotSizing.publicConst 64` -/\n"], []
    for rec, (pr, p, cof) in RECORDS.items():
        for cast, h in CASTS.items():
            c, cterm = cof(h)
            for co in (False, True):
                for n in SIZES:
                    for tile in (False, True):
                        out.append(twin(rec, pr, cast, h, cterm, n, tile, co)[1])
                    name, g, text = value(rec, pr, p, cast, h, c, cterm, n, co)
                    vals.append(text)
                    table.append((name, lean(g), pct(g)))
    here = Path(__file__).resolve().parent
    text = "".join(out + vals) + "\nend Pouw.PearlC\n"
    (here / "Pouw/PearlC/HotRev1Gamma.lean").write_text(rewrap_docs(text))
    for row in table:
        print(*row, sep="\t")


if __name__ == "__main__":
    main()
