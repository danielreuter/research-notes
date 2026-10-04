"""Writes Pouw/PearlC/DeviceSm120KernelGamma.lean: γ at sm_120's records against the honest kernel's W_ref.

python3 gen_kernel_gamma.py   (from this folder; exact arithmetic, stdlib only)
"""
from fractions import Fraction as F
from pathlib import Path

# The honest kernel's E4M3 cast, in W1 units per code (internal/pouw/rtx-pro/server.md, 10:05Z).
CASTS = {"Cast32": F(32), "Cast32p06": F(3206, 100), "Cast16": F(16), "Cast8p72": F(872, 100), "Cast8": F(8)}  # add here
CHAIN_ONLY = {"Cast8p72", "Cast32p06", "Cast16"}  # casts that also get the chain-only reading (the panel publishes these)
# The statement's own cast: at 8.00 it is the statement's W_ref, already pinned; at 8.38 it is the exact in-loop value
# (A-only forming 1.047) that the rounded twins (qa = 2) bound.
LOOP_ONLY = {"Cast8"}

R = 32
SIZES = (8192, 16384)
# name, Lean prices, (add, bf16, fs, qa), c as a Lean term given the cast h: W_ref's forming beyond the record's.
RECORDS = {
    "": ("Prices.sm120", (F(8), F(2), F(40), F(1)), lambda h: (h - 8, f"{h} - 8")),
    "Loop": ("Prices.sm120Loop", (F(1047, 125), F(2), F(40), F(2)), lambda h: (h - F(8953, 1000), f"{h} - 8953 / 1000")),
}


def credit(p, G, n):
    add, bf, fs, _ = p
    n = F(n)
    return n**3 + (0 if G == 0 else n**3 * add / (32 * G)) + n * n * R + 2 * bf * R * n * n + fs * n * n


def omega(p, law, n, c, chain_only=False):
    mk = F(n) ** 2
    cr = credit(p, 4, n) - p[0] * mk if law == "v1" else credit(p, 0, n)
    rho = F(1, 400) if law == "v1" else F(1, 1000)
    den = cr - p[2] * mk - rho * cr if chain_only else (1 - rho) * cr
    return (cr + p[3] * mk + c * mk) / den


def lit(q):
    return f"{q.numerator} / {q.denominator}"


def pct(q):
    return f"{float(q) * 100:.5f}%"


def rows():
    for rec, (pr, p, cof) in RECORDS.items():
        for cast, h in CASTS.items():
            if cast in LOOP_ONLY and not rec:
                continue
            c, cterm = cof(h if h.denominator > 1 else int(h))
            for co in (False, True) if cast in CHAIN_ONLY else (False,):
                for law in ("v1", "v2"):
                    for n in SIZES:
                        om = omega(p, law, n, c, co)
                        yield rec, pr, cast, h, c, cterm, law, n, om, 1 - F(399, 400) / om, co


LAW = {
    "v1": dict(dev="devSm120v1", G=4, rho="1 / 400", tag="Rev1", what="v1 under rev1", tt="TTOutPearlCDevRev1",
               ttt="TTOutTilePearlCDevRev1", proto="pearlCProtocolDevRev1K", tiles="pearlCTilesDevRev1K",
               gen="pearlCGammaDevRev1KAt", sgen="pearlCSampledDevRev1KAt",
               unf="wrefDevRev1K, wrefDevRev1, creditDevRev1, firstAddDev, creditDev"),
    "v2": dict(dev="devSm120v2", G=0, rho="1 / 1000", tag="Cap1000", what="v2 at the cap 1/1,000", tt="TTOutPearlCDev",
               ttt="TTOutTilePearlCDev", proto="pearlCProtocolDevK", tiles="pearlCTilesDevK", gen="pearlCGammaDevKAt",
               sgen="pearlCSampledDevKAt", unf="wrefDevK, wrefDev, creditDev"),
}


def theorem(rec, pr, cast, h, cterm, law, n, om, g, tile, co):
    L = LAW[law]
    d = f"({L['dev']} {pr})"
    unf = L["unf"].replace("wrefDevRev1, ", "wrefDevRev1, creditDevRev1ChainOnly, ").replace(
        "wrefDev, ", "wrefDev, creditDevChainOnly, ") if co else L["unf"]
    def proof(u):
        return (f"(by rw [{u},\n          show {d}.G = {L['G']} from rfl,\n          show {d}.prices = {pr} from rfl]\n"
                f"        norm_num [{pr}, Params.pi, sh{n}])")
    pf, pf0 = proof(unf), proof(L["unf"])
    price = "8.376" if rec else "8.00"
    kind = "per audit tile, " if tile else ""
    name = f"pearlC{'Sampled' if tile else 'Gamma'}Sm120{law}{rec}{cast}{'ChainOnly' if co else ''}{L['tag']}_{n}"
    reading = ", chain-only" if co else ""
    doc = (f"/-- **{L['what']}{reading}, {kind}{n}³**, FP32 at {price}, the honest cast at {float(h):g}: "
           f"`γ = {lit(g).replace(' ', '')}` ({pct(g)}). -/")
    if cast in LOOP_ONLY:
        twin = f"pearlC{'Sampled' if tile else 'Gamma'}Sm120{law}Loop{L['tag']}_{n}"
        doc = (f"/-- **{L['what']}, {kind}{n}³, the exact in-loop value**: FP32 at 8.376, the statement's cast at 8.0 and "
               f"the A-only forming at its measured 1.047, `γ = {lit(g).replace(' ', '')}` ({pct(g)}). `{twin}` "
               f"bounds it from above (`qa` rounded up to 2). -/")
    lines, rest = [], doc
    while len(rest) > 120:
        cut = rest.rindex(" ", 0, 120)
        lines.append(rest[:cut])
        rest = rest[cut + 1:]
    doc = "\n".join(lines + [rest])
    head = (f"{doc}\n"
            f"theorem {name}\n"
            f"    (hTT : {L['ttt'] if tile else L['tt']}{'ChainOnly' if co else ''} CM {d} sem ({L['rho']})) :\n")
    sgen = L["sgen"].replace("KAt", "KChainOnlyAt") if co else L["sgen"]
    gen = L["gen"].replace("KAt", "KChainOnlyAt") if co else L["gen"]
    if tile:
        body = (f"    GγSampled CM ({L['proto']} {d} sem ({L['rho']}) ({cterm}))\n"
                f"      ({L['tiles']} {d} sem ({L['rho']}) ({cterm}))\n"
                f"      (pearlCDomainDevAt {d} sh{n}) (({lit(g)} : ℚ) : ℝ) εPearlC :=\n"
                f"  {sgen} CM _ sem _ _ _ ({lit(om)}) _ (by norm_num)\n    {pf0}\n    {pf}\n    (by norm_num) hTT\n")
    else:
        body = (f"    Gγ CM ({L['proto']} {d} sem ({L['rho']}) ({cterm}))\n"
                f"      (pearlCDomainDevAt {d} sh{n}) (({lit(g)} : ℚ) : ℝ) εPearlC :=\n"
                f"  {gen} CM _ sem _ _ _ ({lit(om)}) _ (by norm_num)\n    {pf}\n    (by norm_num) hTT\n")
    return name, head + body


HEADER = '''import Pouw.PearlC.ChainOnlyGamma
import Pouw.PearlC.DevicePricesLoop
import Pouw.PearlC.DevicePrices

/-!
# γ at the RTX PRO 6000 (sm_120) records against the kernel as it runs (the price-twins lane's file; staged)

Generated by `gen_kernel_gamma.py` in `internal/pouw/price-twins-lean/`; to add a cast price, add it to `CASTS` there
and regenerate.

The statement's `W_ref` prices the E4M3 cast at the credited 8.0 per code. The sm_120 port casts at 32.06 as written,
16.00 packed four per word, and 8.72 packed with wide stores, the kernel's target (`internal/pouw/rtx-pro/server.md`,
10:05Z and 10:25Z). Each theorem here is γ for v1 under rev1 (cap 1/400) or v2 at the cap 1/1,000, per unit or per
audit tile, at `devSm120v1` or `devSm120v2`, against `W_ref` with the honest cast at 32, 32.06, 16 or 8.72, at the
issue-bound FP32 add (`Prices.sm120`) or the in-loop one (`Prices.sm120Loop`). At 8.72 the chain-only reading is
stated too. At the statement's own cast (8) only the in-loop row is here: it is the exact in-loop value of the twins,
which `Prices.sm120Loop` bounds from above by rounding the A-only forming up to 2.

The forming-credited theorems take the record's own TT_OUT (TT_OUT does not read `W_ref`: `ttOut_wref`); the chain-only
ones take its weaker chain-only form (`ttOutPearlCDevChainOnly_of_ttOut`, with the forms in `TTOutChainOnly`).

Both records credit the cast at its cheapest implementation, 8.0 (the coordinator's ruling, 30 Sep 10:49Z). `W_ref`
gains `c` per activation element over the record's: the honest cast `h` less the credited 8, plus, in the loop, the
A-only forming's measured 1.047 less the record's rounded 2. So `c = h − 8` at `Prices.sm120` and `c = h − 8.953` at
`Prices.sm120Loop`, and `W_ref` is the kernel's at each price exactly.
-/

namespace Pouw.PearlC

open Pouw.Fp8Atom Pouw.PearlC.Assumptions

section Gamma

variable {Q R S : Type} [Fintype Q] [DecidableEq Q] [Fintype R] [Fintype S] (CM : CostModel Q R S)
  (sem : PearlCSem Q R S)
'''


def main():
    out, table = [HEADER], []
    for rec, pr, cast, h, c, cterm, law, n, om, g, co in rows():
        for tile in (False, True):
            name, text = theorem(rec, pr, cast, h, cterm, law, n, om, g, tile, co)
            out.append("\n" + text)
            table.append((name, lit(g), pct(g), lit(om)))
    out.append("\nend Gamma\n\nend Pouw.PearlC\n")
    here = Path(__file__).resolve().parent
    (here / "Pouw/PearlC/DeviceSm120KernelGamma.lean").write_text("".join(out))
    for row in table:
        print(*row, sep="\t")


if __name__ == "__main__":
    main()
