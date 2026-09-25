"""verify-po: does a BOOL_QUADRATIC + PAIRED NVFP4 unit circuit (lane/agkr-nvf4 b7cec878) enforce exactly the lookups of the
circuit it rewrites (the 2b25df7f circuit verified for art:5adf62eb)? MY tree's parser (main gpu/circuit.parse_circuit) only.

    python 27-nvf4-rewrite-check.py OLD/circuit.txt NEW/circuit.txt       (cwd /workspace/src/backends/gkr)

Both circuits have one merged table LK: rows (tag 2^20 + key, tag, outputs..., 0...), queries (key + tag 2^20, tag, outputs...).
1. LK blocks by tag, classified by content: R<w> (keys 0..2^w-1, no outputs), PR<b> (rows (x + 2^b y, x, y) for x, y < 2^b),
   else listed (matched between OLD and NEW by exact content).
2. Every lookup fact as (block, column forms): OLD's R1/R<b>/listed queries; NEW's queries with a PR<b> query split into
   R<b>(x) and R<b>(y) (and its key form checked to be x + 2^b y), plus one R1(e) per BOOL product wire w = e e that has an
   assert w - e = 0. The two multisets must be equal.
3. OLD's column / prod / assert lines are a subset of NEW's; NEW's extra prods and asserts are exactly those bool pairs."""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from gpu.circuit import P, parse_circuit

SHIFT = 2**20
old_t, new_t = Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text()
O, N = parse_circuit(old_t), parse_circuit(new_t)
res = {}


def lin_key(l):
    return (tuple(sorted((i, c % P) for i, c in l.terms if c % P)), l.konst % P)


def blocks(C):
    (t,) = C.tables
    G = t.device_rows("cpu").numpy() % P
    out = {}
    for tag in np.unique(G[:, 1]):
        b = G[G[:, 1] == tag].copy()
        b[:, 0] -= int(tag) * SHIFT
        b = b[np.lexsort(b.T[::-1])]
        keys, rest = b[:, 0], b[:, 2:]
        kind = ("L", hash(b.tobytes()))
        n = len(b)
        w = n.bit_length() - 1
        if not rest.any() and n == 2**w and np.array_equal(keys, np.arange(n)):
            kind = ("R", w)
        elif rest.shape[1] >= 2 and not rest[:, 2:].any():
            h = int(round(np.log2(n) / 2)) if n else 0
            x, y = rest[:, 0], rest[:, 1]
            if n == 4**h and x.max() < 2**h and y.max() < 2**h and np.array_equal(keys, x + y * 2**h) \
                    and len({(int(a), int(c)) for a, c in zip(x, y)}) == n:
                kind = ("PR", h)
        out[int(tag)] = kind
    return out


def colform(C, l):
    """a Lin over wires -> the same form over columns (input wires only)."""
    terms = []
    for i, c in l.terms:
        wv = C.wires[i]
        if wv[0] != "in":
            return None
        terms.append((wv[1], c))
    return lin_key(type(l)(terms, l.konst))


def facts(C, bl, bool_facts):
    f, probs = Counter(), []
    for q in C.queries:
        tag = q.cols[1]
        if tag.terms or tag.konst not in bl:
            probs.append("tag")
            continue
        kind = bl[tag.konst]
        k = q.cols[0]
        key = lin_key(type(k)(k.terms, (k.konst - tag.konst * SHIFT) % P))
        if kind[0] == "R":
            f[(kind, key)] += 1
            if any(lin_key(l) != ((), 0) for l in q.cols[2:]):
                probs.append("range outputs")
        elif kind[0] == "PR":
            x, y = q.cols[2], q.cols[3]
            s = Counter()
            for i, c in x.terms:
                s[i] += c
            for i, c in y.terms:
                s[i] += c * 2 ** kind[1]
            if key != lin_key(type(k)(list(s.items()), x.konst + y.konst * 2 ** kind[1])):
                probs.append("PR key != x + 2^b y")
            f[(("R", kind[1]), lin_key(x))] += 1
            f[(("R", kind[1]), lin_key(y))] += 1
        else:
            f[(kind, key, tuple(lin_key(l) for l in q.cols[2:]))] += 1
    for e in bool_facts:
        f[(("R", 1), e)] += 1
    return f, probs


bo, bn = blocks(O), blocks(N)
res["old_blocks"] = sorted(str(v) for v in bo.values())
res["new_blocks"] = sorted(str(v) for v in bn.values())
res["listed_blocks_equal"] = sorted(v for v in bo.values() if v[0] == "L") == sorted(v for v in bn.values() if v[0] == "L")
old_lines, new_lines = set(), Counter(ln for ln in new_t.splitlines() if ln.split() and ln.split()[0] in ("col", "prod", "assert"))
missing = [ln for ln in old_t.splitlines() if ln.split() and ln.split()[0] in ("col", "prod", "assert") and new_lines[ln] == 0]
res["old_col_prod_assert_missing_in_new"] = len(missing)
old_prod_w = {int(ln.split()[1]) for ln in old_t.splitlines() if ln.startswith("prod ")}
asserts = Counter(lin_key(l) for _, l in N.asserts)
bools, bool_probs = [], []
extra_prods = [(i, w) for i, w in enumerate(N.wires) if w[0] == "prod" and i not in old_prod_w]
for i, (_, depth, a, b) in extra_prods:
    if lin_key(a) != lin_key(b):
        bool_probs.append(f"prod {i}: a != b")
        continue
    e = colform(N, a)
    neg = type(a)([(j, -c) for j, c in a.terms] + [(i, 1)], -a.konst)
    pos = type(a)([(j, c) for j, c in a.terms] + [(i, -1)], a.konst)
    if e is None or not (asserts[lin_key(neg)] or asserts[lin_key(pos)]):
        bool_probs.append(f"prod {i}: no assert w - e = 0 or e not over columns")
        continue
    bools.append(e)
res["bool_prods"] = len(bools)
res["extra_prods"] = len(extra_prods)
res["extra_asserts"] = len(N.asserts) - len(O.asserts)
res["bool_problems"] = bool_probs[:5]
fo, po = facts(O, bo, [])
fn, pn = facts(N, bn, bools)
res["queries"] = [len(O.queries), len(N.queries)]
res["facts"] = [sum(fo.values()), sum(fn.values())]
res["facts_by_kind_old"] = {str(k): v for k, v in sorted(Counter(k[0] for k in fo.elements()).items())}
res["facts_by_kind_new"] = {str(k): v for k, v in sorted(Counter(k[0] for k in fn.elements()).items())}
res["query_problems"] = (po + pn)[:5]
res["facts_equal"] = fo == fn
res["ok"] = bool(res["facts_equal"] and res["listed_blocks_equal"] and not missing and not bool_probs and not po and not pn
                 and res["extra_prods"] == len(bools) == res["extra_asserts"])
print(json.dumps(res, indent=1, default=str))
sys.exit(0 if res["ok"] else 1)
