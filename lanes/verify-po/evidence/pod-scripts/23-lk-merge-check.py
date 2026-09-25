"""verify-po: check a merged-LK circuit (lane/agkr-fp8 d5d80e0b `merge_tables`) against the unmerged one it claims to rewrite,
with MY tree's parser (main: backends/gkr/gpu/circuit.parse_circuit), not the producer's merge code.

    python 23-lk-merge-check.py UNMERGED/circuit.txt MERGED/circuit.txt     (cwd /workspace/src/backends/gkr)

1. Every line that is not table / itable / row / query is identical, in order (columns, wires, products, asserts).
2. The merged circuit has exactly one table, and every query goes to it. Queries pair up in order; for the pair
   (U: table t, n linear forms; M) the tag c = M.cols[1] is a bare constant, t <-> c is one bijection over all queries,
   M.cols[0] = U.cols[0] + c 2^20, M.cols[2:n+1] = U.cols[1:], and the rest are the zero form.
3. The merged rows, as a multiset, equal the union over source tables t of (c_t 2^20 + key, c_t, outputs, 0...), where
   (key, outputs) are t's rows as MY parser materialises them; source keys are unique and in [0, 2^20), and the merged
   first column is unique and below P (so no two tables' tuples can coincide and no key wraps mod P)."""
import json
import sys
from pathlib import Path

import numpy as np

from gpu.circuit import P, parse_circuit

SHIFT = 2**20
up, mp = Path(sys.argv[1]), Path(sys.argv[2])
ut, mt = up.read_text(), mp.read_text()
res = {"unmerged": str(up), "merged": str(mp), "P": P}


def head(text):
    return [ln for ln in text.splitlines() if ln.split() and ln.split()[0] not in ("table", "itable", "row", "query")]


res["head_identical"] = head(ut) == head(mt)
U, M = parse_circuit(ut), parse_circuit(mt)
res["merged_tables"] = [(t.name, t.cols, t.nrows) for t in M.tables]
res["unmerged_tables_queried"] = sorted({q.table for q in U.queries})
ok_one = len(M.tables) == 1 and all(q.table == M.tables[0].name for q in M.queries)
res["one_table"] = ok_one
LK = M.tables[0]
W = LK.cols
res["queries"] = [len(U.queries), len(M.queries)]
bad, tag_of, table_of = [], {}, {}
for j, (uq, mq) in enumerate(zip(U.queries, M.queries)):
    n = len(uq.cols)
    c = mq.cols[1]
    if len(mq.cols) != W or c.terms or not (1 <= c.konst < 2**16):
        bad.append((j, "shape/tag"))
        continue
    t, tg = uq.table, c.konst
    if tag_of.setdefault(t, tg) != tg or table_of.setdefault(tg, t) != t:
        bad.append((j, f"tag map {t}->{tg}"))
    k0u, k0m = uq.cols[0], mq.cols[0]
    if k0m.terms != k0u.terms or k0m.konst != (k0u.konst + tg * SHIFT) % P:
        bad.append((j, "key form"))
    if [(l.terms, l.konst) for l in mq.cols[2:n + 1]] != [(l.terms, l.konst) for l in uq.cols[1:]]:
        bad.append((j, "output forms"))
    if any(l.terms or l.konst for l in mq.cols[n + 1:]):
        bad.append((j, "padding"))
res["query_problems"] = bad[:10]
res["query_problem_count"] = len(bad)
res["tag_map"] = tag_of
exp, src_problems = [], []
for t, tg in sorted(tag_of.items(), key=lambda kv: kv[1]):
    r = U.table(t).device_rows("cpu").numpy() % P
    if r[:, 0].min() < 0 or r[:, 0].max() >= SHIFT or len(np.unique(r[:, 0])) != len(r):
        src_problems.append(f"{t}: keys not unique in [0, 2^20)")
    if 1 + r.shape[1] > W:
        src_problems.append(f"{t}: {r.shape[1]} columns do not fit width {W}")
        continue
    b = np.zeros((len(r), W), dtype=np.int64)
    b[:, 0] = r[:, 0] + tg * SHIFT
    b[:, 1] = tg
    b[:, 2:1 + r.shape[1]] = r[:, 1:]
    exp.append(b)
    res.setdefault("source_rows", {})[t] = int(len(r))
E = np.concatenate(exp)
G = LK.device_rows("cpu").numpy() % P


def srt(a):
    return a[np.lexsort(a.T[::-1])]


res["rows"] = {"merged": int(len(G)), "expected": int(len(E))}
res["rows_equal_multiset"] = bool(G.shape == E.shape and np.array_equal(srt(G), srt(E)))
res["merged_first_col_unique"] = bool(len(np.unique(G[:, 0])) == len(G))
res["merged_first_col_max"] = int(G[:, 0].max())
res["below_P"] = bool(G[:, 0].max() < P)
res["source_problems"] = src_problems
res["ok"] = bool(res["head_identical"] and ok_one and len(U.queries) == len(M.queries) and not bad and not src_problems
                 and res["rows_equal_multiset"] and res["merged_first_col_unique"] and res["below_P"])
print(json.dumps(res, indent=1, default=str))
sys.exit(0 if res["ok"] else 1)
