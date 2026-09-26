#!/usr/bin/env python3
"""red-team-flock-2: the Rust tail interpreter's primitives (`ir_tail::apply`, through the `rtf2-tail` harness) against the IR
primitives (verity_vllm F32Add/F32Mul/F32Div/F32Fma/RsqrtApprox/MufuSqrtFtz/DivFullRcp/DivFullScaleA `.evaluate`), bit for
bit, on the same host. Unary MUFU ops: every exponent x both signs x mantissa samples (plus 0, 1, max); binary/ternary ops:
special classes, NaN payloads (both operands NaN included), exact cancellation, subnormals, the 2^126 / 2^-126 thresholds.

  tail_diff.py RTF2_TAIL_BIN TABLES_DIR [per_exponent] [seed]
"""
import random, subprocess, sys, time

B = sys.argv[1]; TD = sys.argv[2]
PER = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
rng = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 20260926)


def word(fam):
    s = rng.getrandbits(1) << 31
    m = rng.getrandbits(23)
    if fam == "zero":
        return s
    if fam == "sub":
        return s | rng.randrange(1, 1 << 23)
    if fam == "inf":
        return s | 0x7F800000
    if fam == "qnan":
        return s | 0x7FC00000 | rng.getrandbits(22)
    if fam == "snan":
        return s | 0x7F800000 | rng.randrange(1, 1 << 22)
    if fam == "big":
        return s | (rng.randrange(0xFC, 0xFF) << 23) | m          # around |x| = 2^126
    if fam == "tiny":
        return s | (rng.randrange(1, 3) << 23) | m                 # around |x| = 2^-126
    if fam == "one":
        return s | (127 << 23) | rng.choice([0, 1, m])
    return s | (rng.randrange(1, 0xFF) << 23) | m


FAMS = ["norm", "norm", "norm", "zero", "sub", "inf", "qnan", "snan", "big", "tiny", "one"]


def cases():
    out = []
    for prim in ("rsq", "sqrt", "rcp"):
        for s in (0, 1):
            for e in range(256):
                for m in [0, 1, (1 << 23) - 1] + [rng.getrandbits(23) for _ in range(PER)]:
                    out.append((prim, ((s << 31) | (e << 23) | m,)))
    for prim, ar in (("add", 2), ("mul", 2), ("div", 2), ("fma", 3), ("scale", 2)):
        for _ in range(60 * PER):
            args = [word(rng.choice(FAMS)) for _ in range(ar)]
            k = rng.randrange(6)
            if k == 0 and prim in ("add", "fma"):              # exact cancellation
                args[-1] = args[0] ^ 0x80000000 if prim == "add" else args[-1]
            if k == 1:
                args = [word("qnan") if i < 2 else a for i, a in enumerate(args)]   # two NaN operands (payload choice)
            if k == 2:
                args = [word("snan") if i == 0 else word("qnan") if i == 1 else a for i, a in enumerate(args)]
            out.append((prim, tuple(args)))
    return out


def main():
    from verity_vllm.program.registry import prims as P
    fn = {"add": P.F32Add, "mul": P.F32Mul, "div": P.F32Div, "fma": P.F32Fma, "rsq": P.RsqrtApprox, "sqrt": P.MufuSqrtFtz,
          "rcp": P.DivFullRcp, "scale": P.DivFullScaleA}
    cs = cases()
    t0 = time.time()
    want = [fn[p].evaluate(*a) & 0xFFFFFFFF for p, a in cs]
    t1 = time.time()
    inp = "\n".join(p + " " + " ".join(f"{x:08x}" for x in a) for p, a in cs) + "\n"
    got = subprocess.run([B, TD], input=inp, capture_output=True, text=True, check=True).stdout.split()
    t2 = time.time()
    assert len(got) == len(cs)
    per, first = {}, {}
    for (p, a), w, g in zip(cs, want, got):
        n, bad = per.get(p, (0, 0))
        g = int(g, 16)
        per[p] = (n + 1, bad + (g != w))
        if g != w and len(first.setdefault(p, [])) < 4:
            first[p].append(([f"{x:08x}" for x in a], f"ir {w:08x}", f"rust {g:08x}"))
    print(f"TAIL_DIFF {len(cs)} cases (IR {t1 - t0:.0f} s, Rust {t2 - t1:.0f} s)")
    for p, (n, bad) in per.items():
        print(f"  {p:6s} {n:9d} cases {bad:6d} mismatches", first.get(p, ""))


if __name__ == "__main__":
    main()
