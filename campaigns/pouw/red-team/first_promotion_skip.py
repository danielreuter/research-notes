"""Red-team: TT_OUT credits a promotion add that no program has to execute (the first one, +0 + S_1).

Pearl-C's ticket word is T_last with T_0 = +0 and T_g = RNE(T_{g-1} + S_g), S_g the g-th window's accumulator; a zero
total is +0.  `creditOf` (Lean `Pouw.PearlC.Game.creditOf`, `pearl_c.PearlC.credit_of`) credits k/(32 G) promotion adds
per word at the device's FADD price, but T_1 = RNE(+0 + S_1) is S_1 itself (−0 read as +0), so the program "honest chain,
first promotion skipped" outputs every checked word bit for bit and spends fadd·m·n less.  Neither the debit (P1's
jointFlags: atoms) nor the promotion identities (promFlags: adds that leave the total unchanged) removes it.

This script (1) checks the equality on the scheme's own `chain` for the H100 and sm_120 records on census-formed operands,
and exhaustively on the FP32 add over sampled words; (2) prices the skip against γ₀ = 1/400 of `credit_of` over the domain's
k (Lean `pearlCDomain`: 128 | k <= 2^16), at the record's prices and at the FADD price measured on the RTX PRO 6000.
"""
import argparse, importlib.util, json, os, random, sys
from pathlib import Path

import numpy as np

BR = Path(os.environ.get("SM120_TREE", "/tmp/wt/pearl-c-sm120-b44b"))
AT = Path(os.environ.get("ATTACKS_TREE", "/tmp/wt/pearl-c-sm120-attacks-cb92"))
sys.path[:0] = [str(BR / "packages/verity/src"), str(BR / "protocols/pouw")]
from verity.ml.tc import fp32  # noqa: E402
from verity_pouw.protocol import Shape  # noqa: E402
from verity_pouw.schemes import pearl_c as PC  # noqa: E402
from verity_pouw.schemes.pearl_c_device import H100, SM120  # noqa: E402

_spec = importlib.util.spec_from_file_location("pearlc_census", AT / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt_result  # noqa: E402


def chain_skip_first(a, b, device):
    """`pearl_c.chain` with the first promotion not executed: the first window's accumulator is the total."""
    total, atom, window = None, device.atom, device.window
    for ws in range(0, len(a), window):
        local = 0
        for s in range(ws, min(ws + window, len(a)), PC.SLICE):
            local = PC._check_finite(atom.step(local, a[s:s + PC.SLICE], b[s:s + PC.SLICE]))
        total = local if total is None else PC._check_finite(fp32.add(total, local))
        if total == 0x80000000:
            total = 0
    return total


def words_equal(device, atom_name, fam, k, rows, cols):
    C.set_atom(atom_name)
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, rows, cols, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a, _, _, fa, la = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-A"))
    b, _, _, fb, lb = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-B"))
    same = total = 0
    for i in range(rows):
        ai = [int(x) for x in a[i]]
        for j in range(cols):
            bj = [int(x) for x in b[j]]
            same += PC.chain(ai, bj, device) == chain_skip_first(ai, bj, device)
            total += 1
    return {"device": device.name, "family": fam, "k": k, "in_domain": bool(fa and la and fb and lb),
            "words": total, "equal": same}


def add_zero_identity(samples, seed=1):
    """RNE(+0 + w) == w for every finite FP32 word w but −0 (read as +0): sampled words plus every exponent's boundaries."""
    rng = random.Random(seed)
    ws = [rng.getrandbits(32) for _ in range(samples)]
    ws += [(s << 31) | (e << 23) | m for s in (0, 1) for e in range(255) for m in (0, 1, 0x3FFFFF, 0x400000, 0x7FFFFF)]
    bad = 0
    for w in ws:
        if (w >> 23) & 0xFF == 0xFF:
            continue
        want = 0 if w == 0x80000000 else w
        got = fp32.add(0, w)
        bad += (0 if got == 0x80000000 else got) != want
    return len(ws), bad


def price(device_name, fadd, ks, mn):
    """Per shape: creditOf, the skip's saving fadd·m·n, and whether TT_OUT(1/400)'s event fires for the adversary that runs
    the whole honest reference W_ref (ρ included) minus the first promotion."""
    dev = {"h100": H100, "sm120": SM120}[device_name]
    out = []
    for k in ks:
        for m, n in mn(k):
            s = Shape(m, k, n)
            sch = PC.PearlC(k_min=128, forming="v1", device=dev)
            credit, wref = sch.credit_of(s), sch.wref(s)
            f_rec = dev.prices.fadd
            credit = credit + (fadd - f_rec) * m * n * dev.promotions(k)   # re-price the promotions at `fadd`
            wref = wref + (fadd - f_rec) * m * n * dev.promotions(k)
            saving = fadd * m * n
            adv = wref - saving
            fires = credit > adv / (1 - 1 / 400)
            out.append({"device": device_name, "fadd": fadd, "m": m, "n": n, "k": k, "credit_per_word": credit / (m * n),
                        "saving_share_of_credit": saving / credit, "gamma0": 1 / 400, "tt_out_event_fires": bool(fires)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fadd-measured", type=float, default=8.456, help="FADD in FP8-MAC units (r20260930-060338-26b9)")
    ap.add_argument("--add-samples", type=int, default=200000)
    args = ap.parse_args()
    eq = []
    for device, atom in ((H100, "hopper-e4m3-k32"), (SM120, "sm120-e4m3-k32")):
        for fam in ("gaussian", "constant", "zero-slices", "aligned-spikes-pm1-r444", "spikes-first"):
            for k, rows, cols in ((128, 16, 16), (1024, 8, 8), (8192, 4, 4)):
                r = words_equal(device, atom, fam, k, rows, cols)
                eq.append(r)
                print(json.dumps(r), flush=True)
    n_add, bad_add = add_zero_identity(args.add_samples)
    print(json.dumps({"fp32_add_zero_identity_words": n_add, "mismatches": bad_add}), flush=True)
    ks = [128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
    square = lambda k: [(8192, 8192), (k, k)]  # noqa: E731
    priced = (price("h100", 32, ks, square) + price("sm120", 32, ks, square)
              + price("sm120", args.fadd_measured, ks, square))
    for p in priced:
        print(json.dumps(p))
    all_equal = all(r["equal"] == r["words"] for r in eq)
    fires = [p for p in priced if p["tt_out_event_fires"]]
    meas = [("words_checked", sum(r["words"] for r in eq), "words"), ("words_equal", sum(r["equal"] for r in eq), "words"),
            ("fp32_add_zero_identity_mismatches", bad_add, "words")]
    for p in priced:
        if p["m"] == 8192:
            meas.append((f"{p['device']}.fadd{p['fadd']:g}.k{p['k']}.saving_share", round(p["saving_share_of_credit"], 6),
                         "fraction"))
    rt_result.write("first-promotion-skip", meas,
                    {"equalities": eq, "fp32_add_zero_identity": {"words": n_add, "mismatches": bad_add}, "priced": priced,
                     "violations": fires},
                    status="passed" if all_equal and bad_add == 0 else "failed",
                    detail="the first promotion is RNE(+0 + S_1) = S_1; creditOf credits it; TT_OUT(1/400) event per shape")


if __name__ == "__main__":
    main()
