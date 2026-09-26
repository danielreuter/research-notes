import sys
sys.path.insert(0, "/workspace/backends/flock/python")
from verity_flock import unit as U, fp
from verity_flock.gf2 import ZERO, NOT, OR, add, and_reduce, const_bits, multiply, mux, or_reduce


def classify(C, w, man, exp):
    m, e = w[:man], w[man:man + exp]
    e_any, e_all, m_any = or_reduce(C, e), and_reduce(C, e), or_reduce(C, m)
    return e_any, m_any, C.AND(e_all, m_any), C.AND(e_all, NOT(m_any))   # e_any, m_any, nan, inf


def tc_total(C, acc, a, b, groups=(8, 8), W=25, F=-132):
    fmt = U.BF16
    rescale = W - 24
    ops = []
    for x, y in zip(a, b):
        cx, cy = classify(C, x, 7, 8), classify(C, y, 7, 8)
        ops.append((x, y, cx, cy))
    p_nan, p_inf, prods = [], [], []
    for x, y, cx, cy in ops:
        zx, zy = NOT(OR(C, cx[0], cx[1])), NOT(OR(C, cy[0], cy[1]))
        n = OR(C, OR(C, cx[2], cy[2]), OR(C, C.AND(cx[3], zy), C.AND(cy[3], zx)))
        p_nan.append(n)
        p_inf.append(C.AND(OR(C, cx[3], cy[3]), NOT(n)))
        dec = []
        for w, c in ((x, cx), (y, cy)):
            m, e = w[:7], w[7:15]
            dec.append((w[15], [e[0] ^ C.AND(NOT(e[0]), NOT(c[0]))] + e[1:], m + [c[0]], OR(C, c[0], c[1])))
        (sa, ea, siga, nza), (sb, eb, sigb, nzb) = dec
        S = add(C, ea, eb, width=fmt.exp_bits + 1)
        S = add(C, S, const_bits((fmt.offset + U.S_BIAS) % 1024, 10), width=10)
        mag = multiply(C, siga, sigb)[: 2 * fmt.sig_bits]
        sh = fmt.product_shift + rescale
        prods.append((sa ^ sb, S, C.AND(nza, nzb), ([ZERO] * sh + mag) if sh >= 0 else mag[-sh:]))
    cm, cf, cs = acc[:23], acc[23:31], acc[31]
    hc, c_all, cm_any = or_reduce(C, cf), and_reduce(C, cf), or_reduce(C, cm)
    c_nan, c_inf = C.AND(c_all, cm_any), C.AND(c_all, NOT(cm_any))
    cf_eff = [cf[0] ^ C.AND(NOT(cf[0]), NOT(hc))] + cf[1:]
    mag24 = cm + [hc]
    state = (cs, add(C, cf_eff, const_bits(127, 10), width=10), OR(C, hc, cm_any),
             ([ZERO] * rescale + mag24) if rescale >= 0 else mag24[-rescale:])
    nan, pos, neg = c_nan, C.AND(c_inf, NOT(cs)), C.AND(c_inf, cs)
    sats, start, m24 = [], 0, None
    for size in groups:
        for i in range(start, start + size):
            sgn = prods[i][0]
            nan = OR(C, nan, p_nan[i])
            pos = OR(C, pos, C.AND(p_inf[i], NOT(sgn)))
            neg = OR(C, neg, C.AND(p_inf[i], sgn))
        nan = OR(C, nan, C.AND(pos, neg))
        s_o, S_o, nz_o, m24 = U.group_sum(C, [state] + prods[start:start + size], W, F)
        sat = U.saturated(C, S_o, nz_o)
        sats.append((sat, s_o))
        fin_sat = C.AND(sat, NOT(OR(C, pos, neg)))
        pos, neg = OR(C, pos, C.AND(fin_sat, NOT(s_o))), OR(C, neg, C.AND(fin_sat, s_o))
        state = (s_o, S_o, nz_o, ([ZERO] * rescale + m24) if rescale >= 0 else m24[-rescale:])
        start += size
    s_o, S_o, nz_o = state[0], state[1], state[2]
    field = add(C, S_o[:8], const_bits((-128) % 256, 8), cin=m24[23], width=8)
    sign_n = C.AND(s_o, nz_o)
    field_n = [C.AND(nz_o, x) for x in field]
    sat_any, sat_sign = sats[-1]
    for sat_g, sg in reversed(sats[:-1]):
        sat_sign = mux(C, sat_g, [sg], [sat_sign])[0]
        sat_any = OR(C, sat_g, sat_any)
    finite = [C.AND(NOT(sat_any), x) for x in m24[:23]] + [OR(C, sat_any, x) for x in field_n] + [mux(C, sat_any, [sat_sign], [sign_n])[0]]
    inf = OR(C, pos, neg)
    special = fp.select(C, nan, const_bits(fp.TC_NAN, 32), const_bits(fp.F32_INF, 31) + [neg])
    return fp.select(C, OR(C, nan, inf), special, finite)


def build(fn):
    C = U.Circuit()
    x = C.input("x", 256); w = C.input("w", 256); c = C.input("c", 32)
    out = fn(C, c, [x[i * 16:(i + 1) * 16] for i in range(16)], [w[i * 16:(i + 1) * 16] for i in range(16)])
    C.output("c_out", out); C.output("y16", fp.f32_to_bf16(C, out, 0x7FFF))
    return C


if __name__ == "__main__":
    C = build(tc_total)
    live = C.live()
    print("ands", sum(1 for v in range(len(C.kind)) if v in live and C.kind[v] == "and"), "budget", 8192 - 640 - 256 - 1)
