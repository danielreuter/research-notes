"""NumPy mirror of int8_route_replay.cu's breadth-first Strassen: A (m x k) and B (n x k) row-major, C = A·Bᵀ.
Checks the coefficient tables (stored-quadrant order s00, s01, s10, s11) and the merge table against A @ B.T."""
import numpy as np

TA = [(1, 0, 0, 1), (0, 0, 1, 1), (1, 0, 0, 0), (0, 0, 0, 1), (1, 1, 0, 0), (-1, 0, 1, 0), (0, 1, 0, -1)]
TB = [(1, 0, 0, 1), (1, 0, 0, 0), (0, 0, 1, -1), (-1, 1, 0, 0), (0, 0, 0, 1), (1, 0, 1, 0), (0, 1, 0, 1)]
TC = [(1, 0, 0, 1, -1, 0, 1), (0, 0, 1, 0, 1, 0, 0), (0, 1, 0, 1, 0, 0, 0), (1, -1, 1, 0, 0, 1, 0)]


def split(x, table):
    r, c = x.shape[1] // 2, x.shape[2] // 2
    q = [x[:, :r, :c], x[:, :r, c:], x[:, r:, :c], x[:, r:, c:]]
    out = np.empty((x.shape[0] * 7, r, c), dtype=np.int64)
    for p in range(x.shape[0]):
        for t, co in enumerate(table):
            out[p * 7 + t] = sum(w * qq[p] for w, qq in zip(co, q))
    return out


def merge(cl):
    P = cl.shape[0] // 7
    r, c = cl.shape[1], cl.shape[2]
    out = np.empty((P, 2 * r, 2 * c), dtype=np.int64)
    for p in range(P):
        ms = cl[p * 7:(p + 1) * 7]
        quads = [sum(w * ms[t] for t, w in enumerate(co)) for co in TC]
        out[p, :r, :c], out[p, :r, c:], out[p, r:, :c], out[p, r:, c:] = quads
    return out


rng = np.random.default_rng(1)
for n, L in ((16, 1), (32, 2), (64, 3), (64, 4)):
    A = rng.integers(-12, 13, (n, n))
    B = rng.integers(-12, 13, (n, n))
    a, b = A[None], B[None]
    for _ in range(L):
        a, b = split(a, TA), split(b, TB)
    c = np.einsum("pik,pjk->pij", a, b)
    for _ in range(L):
        c = merge(c)
    ok = np.array_equal(c[0], A @ B.T)
    print(n, L, "exact" if ok else "MISMATCH", "leaf max", int(np.abs(a).max()), int(np.abs(b).max()))
