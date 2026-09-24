"""sp1-table (pod): how often a group of the frozen vu-k1536 set is all-normal (every x and W word has exponent field
1..254), per VU group of 8 products (16 words), and the zero / subnormal word fractions."""

import numpy as np

F = "/workspace/src/fixtures/bench-instances/v1/vu-k1536"
K = 1536
x = np.fromfile(F + ".x.u16", dtype="<u2").reshape(-1, K)
w = np.fromfile(F + ".w.u16", dtype="<u2").reshape(-1, K)
n = x.shape[0]


def stats(a, name):
    e = (a >> 7) & 0xFF
    m = a & 0x7F
    zero = (e == 0) & (m == 0)
    sub = (e == 0) & (m != 0)
    print(f"{name}: zero {zero.mean():.4%}  subnormal {sub.mean():.4%}  non-finite {(e == 0xFF).mean():.4%}")
    return (e >= 1) & (e <= 254)


nx, nw = stats(x, "x"), stats(w, "w")
normal = (nx & nw).reshape(n, K // 8, 8).all(axis=2)
print(f"all-normal groups: {normal.mean():.4%} of {normal.size:,}; VUs with every group all-normal: {normal.all(axis=1).mean():.4%}")
prod_zero = ((x & 0x7FFF) == 0) | ((w & 0x7FFF) == 0)
print(f"groups with a zero product: {prod_zero.reshape(n, K // 8, 8).any(axis=2).mean():.4%}")
per_vu = normal.mean(axis=1)
print("per-VU all-normal fraction quantiles:", np.quantile(per_vu, [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1]).round(4))
