"""Exact GF(2) circuit of one tensor-core transition unit (verity.ml.tc GroupSum.step) in Flock's model.

Exponents are carried in "S-units" (E + 254), so every exponent is a small unsigned integer; the floor is F + 254.
The group sum follows verity.ml.tc.models.group_sum literally, with the normalisation folded into one shift:
    m = floor(|t| * 2^(min(W - L, 126 + M) - rescale))      (rescale >= 0)
    m = floor(|t| * 2^min(W - L, 126 + M)) << -rescale       (rescale < 0)
    e = max(M + L - W, -126)
which is the composition of the reference's truncating shifts (nested floors by powers of two compose).
"""
from __future__ import annotations

import math

from gf2 import (ONE, ZERO, Circuit, L, NOT, OR, add, and_reduce, compress_columns, const, const_bits, lzc,
                 multiply, mux, or_reduce, shl_window, shr, sub)

S_BIAS = 254


class Fmt:
    def __init__(self, name, exp_bits, man_bits, nan_rule):
        self.name, self.exp_bits, self.man_bits, self.nan_rule = name, exp_bits, man_bits, nan_rule
        self.bits = 1 + exp_bits + man_bits
        self.bias = (1 << (exp_bits - 1)) - 1
        self.sig_bits = man_bits + 1
        self.product_shift = 25 - 2 * self.sig_bits
        # exponent of a product = (ea or 1) + (eb or 1) + offset
        self.offset = 23 - self.product_shift - 2 * self.bias - 2 * man_bits


BF16 = Fmt("bf16", 8, 7, "ieee")
E4M3 = Fmt("e4m3", 4, 3, "e4m3")


def decode_operand(C, fmt, word):
    m = word[: fmt.man_bits]
    e = word[fmt.man_bits: fmt.man_bits + fmt.exp_bits]
    s = word[fmt.bits - 1]
    h = or_reduce(C, e)
    if fmt.nan_rule == "ieee":
        C.assert_zero(f"{fmt.name} operand not finite", and_reduce(C, e))
    elif fmt.nan_rule == "e4m3":
        C.assert_zero("e4m3 operand NaN", and_reduce(C, e + m))
    e_eff = [e[0] ^ C.AND(NOT(e[0]), NOT(h))] + e[1:]  # (e or 1)
    nz = OR(C, h, or_reduce(C, m))
    sig = m + [h]
    return s, e_eff, sig, nz


def max_tree(C, vals, width):
    vals = [v + [ZERO] * (width - len(v)) for v in vals]
    while len(vals) > 1:
        nxt = []
        for i in range(0, len(vals) - 1, 2):
            a, b = vals[i], vals[i + 1]
            _, a_lt_b = sub(C, a, b, width)
            nxt.append(mux(C, a_lt_b, b, a))
        if len(vals) % 2:
            nxt.append(vals[-1])
        vals = nxt
    return vals[0]


def group_sum(C, terms, W, F):
    """terms: list of (sign, S (bit list), nz, scaled magnitude bit list). Returns (sign, S_out (10 bits), nz, m24)."""
    rescale = W - 24
    FS = F + S_BIAS
    EW = 10  # exponent width in S-units (max 513)
    # --- max exponent over nonzero terms, with the floor
    C.phase = "max exponent"
    masked = [[C.AND(nz, b) for b in S] for (_, S, nz, _) in terms]
    M = max_tree(C, masked + [const_bits(FS, EW)], EW)
    # --- align
    C.phase = "align (9 or 17 shifters)"
    n = max(len(t[3]) for t in terms)
    aligned = []
    for (s, S, nz, mag) in terms:
        d, _ = sub(C, M, S, EW)
        big = or_reduce(C, d[5:])
        a = shr(C, mag, d[:5], big)
        aligned.append((s, a + [ZERO] * (n - len(a))))
    # --- signed sum (two's complement, sign-extension trick)
    C.phase = "signed sum (CSA tree) + abs"
    k = len(terms)
    max_mag = sum((1 << len(t[3])) - 1 for t in terms)
    TB = max_mag.bit_length()  # bits of |t|
    TW = TB + 1  # two's complement width
    cols = [[] for _ in range(TW + 2)]
    for (s, a) in aligned:
        for j in range(n):
            cols[j].append(a[j] ^ s)
        cols[0].append(s)
        cols[n].append(NOT(s))
    neg = (-(k << n)) % (1 << TW)
    for j in range(TW):
        if neg >> j & 1:
            cols[j].append(ONE)
    t = compress_columns(C, cols)[:TW]
    tsign = t[TW - 1]
    absv = add(C, [b ^ tsign for b in t[:TB]], [tsign], width=TB)
    # --- normalise
    C.phase = "normalise (lzc, shift, exponent)"
    P = 1 << math.ceil(math.log2(TB))
    padded = absv + [ZERO] * (P - TB)
    _, lz = lzc(C, padded)  # L = P - lz for nonzero |t|
    lzb = len(lz)
    # sh = min(W - L, 126 + M) - max(rescale, 0);  M = S_M - 254;  L = P - lz
    #    = min(W - P + lz, S_M - 128) - max(rescale, 0)
    r = max(rescale, 0)
    sh_min = min(W - TB, 126 + F) - r
    U0 = -sh_min
    # u = sh + U0 = min(lz + (W - P - r + U0), S_M + (-128 - r + U0))
    ca = W - P - r + U0
    cb = -128 - r + U0
    A = add(C, lz + [ZERO] * (EW - lzb), const_bits(ca % (1 << EW), EW), width=EW)
    B = add(C, M, const_bits(cb % (1 << EW), EW), width=EW)
    _, a_lt_b = sub(C, A, B, EW)
    u = mux(C, a_lt_b, A, B)
    ub = (P + ca).bit_length()  # u = min(A, B) <= A <= P + ca
    u = u[:ub]
    m = shl_window(C, absv, u, U0, U0 + 24 + min(rescale, 0))
    if rescale < 0:
        m = [ZERO] * (-rescale) + m
    m = m[:24]
    # e = max(M + L - W, -126) -> S_out = max(S_M + P - lz - W, 128)
    e_raw, _ = sub(C, add(C, M, const_bits((P - W) % (1 << EW), EW), width=EW), lz, EW)
    _, lt128 = sub(C, e_raw, const_bits(128, EW), EW)
    S_out = mux(C, lt128, const_bits(128, EW), e_raw)
    nz_out = or_reduce(C, m)
    return tsign, S_out, nz_out, m


def saturated(C, S_out, nz):
    C.phase = "pack + saturation"
    # exponent > 127  <=>  S > 381
    _, lt382 = sub(C, S_out, const_bits(382, len(S_out)), len(S_out))
    return C.AND(nz, NOT(lt382))


def unit(fmt, groups, W, F, epilogue=False):
    C = Circuit()
    k = sum(groups)
    x = C.input("x", k * fmt.bits)
    w = C.input("w", k * fmt.bits)
    c = C.input("c", 32)
    rescale = W - 24
    prods = []
    for i in range(k):
        C.phase = "operand decode + finiteness"
        sa, ea, siga, nza = decode_operand(C, fmt, x[i * fmt.bits:(i + 1) * fmt.bits])
        sb, eb, sigb, nzb = decode_operand(C, fmt, w[i * fmt.bits:(i + 1) * fmt.bits])
        C.phase = "product exponent"
        S = add(C, ea, eb, width=fmt.exp_bits + 1)
        S = add(C, S, const_bits((fmt.offset + S_BIAS) % 1024, 10), width=10) if fmt.offset + S_BIAS else S
        nz = C.AND(nza, nzb)
        C.phase = "significand multipliers"
        mag = multiply(C, siga, sigb)[: 2 * fmt.sig_bits]
        sh = fmt.product_shift + rescale
        scaled = ([ZERO] * sh + mag) if sh >= 0 else mag[-sh:]
        prods.append((sa ^ sb, S, nz, scaled))
    # accumulator
    C.phase = "accumulator decode"
    cm, cf, cs = c[:23], c[23:31], c[31]
    hc = or_reduce(C, cf)
    C.assert_zero("accumulator not finite", and_reduce(C, cf))
    nzc = OR(C, hc, or_reduce(C, cm))
    cf_eff = [cf[0] ^ C.AND(NOT(cf[0]), NOT(hc))] + cf[1:]
    Sc = add(C, cf_eff, const_bits(127, 10), width=10)
    mag24 = cm + [hc]
    scaled_c = ([ZERO] * rescale + mag24) if rescale >= 0 else mag24[-rescale:]
    acc = (cs, Sc, nzc, scaled_c)
    sats = []
    start = 0
    for gi, size in enumerate(groups):
        s_o, S_o, nz_o, m24 = group_sum(C, [acc] + prods[start:start + size], W, F)
        sats.append((saturated(C, S_o, nz_o), s_o))
        scaled_o = ([ZERO] * rescale + m24) if rescale >= 0 else m24[-rescale:]
        acc = (s_o, S_o, nz_o, scaled_o)
        start += size
    s_o, S_o, nz_o, m24 = acc[0], acc[1], acc[2], m24
    C.phase = "pack + saturation"
    # pack
    # FP32 field = (e + 127) for normals, 0 for subnormals: S - 128 + m23 (S = e + 254; subnormal <=> S = 128, m23 = 0)
    field = add(C, S_o[:8], const_bits((-128) % 256, 8), cin=m24[23], width=8)
    sign_n = C.AND(s_o, nz_o)
    field_n = [C.AND(nz_o, b) for b in field]
    # first saturating group wins (sticky)
    sat_any, sat_sign = sats[-1]
    for sat_g, sgn in reversed(sats[:-1]):
        sat_sign = mux(C, sat_g, [sgn], [sat_sign])[0]
        sat_any = OR(C, sat_g, sat_any)
    out_m = [C.AND(NOT(sat_any), b) for b in m24[:23]]
    out_f = [OR(C, sat_any, b) for b in field_n]
    out_s = mux(C, sat_any, [sat_sign], [sign_n])[0]
    word = out_m + out_f + [out_s]
    C.output("c_out", word)
    if epilogue:
        C.output("y16", f32_to_bf16(C, word))
    return C


def f32_to_bf16(C, u):
    low, lsb = u[:16], u[16]
    carry = add(C, low, const_bits(0x7FFF, 16), cin=lsb, width=16, carry_out=True)[16]
    return add(C, u[16:32], [carry], width=16)


def epilogue_only():
    C = Circuit()
    u = C.input("u", 32)
    C.output("y16", f32_to_bf16(C, u))
    return C
