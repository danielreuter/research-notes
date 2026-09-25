"""verify-po: does a BOOL_QUADRATIC + PAIRED NVFP4 unit circuit (lane/agkr-nvf4 b7cec878) enforce exactly the lookups of the
circuit it rewrites (the 2b25df7f circuit verified for art:5adf62eb)? MY tree's parser (main gpu/circuit.parse_circuit) only.

    python 27-nvf4-rewrite-check.py OLD/circuit.txt NEW/circuit.txt       (cwd /workspace/src/backends/gkr)

Forms are canonical: a term on the constant-one column / wire is folded into the constant, and a product wire is named by its
content (depth, {a, b}), not its index (the new bool wires are interleaved, so indices shift).
1. The one table LK, split into blocks by the tag column and classified by content (tag column zeroed): R<w> (keys 0..2^w-1,
   no outputs), PR<b> (rows (x + 2^b y, x, y), every x, y < 2^b), else listed; listed blocks must match OLD <-> NEW exactly.
2. Every lookup fact as (block, column forms): OLD's queries; NEW's queries with a PR<b> query split into R<b>(x), R<b>(y) (its
   key form checked to be x + 2^b y); plus one R1(e) per NEW product wire w = e e (not in OLD) with a NEW assert +-(w - e) = 0.
   The two multisets must be equal.
3. OLD's products and asserts (canonical) are a sub-multiset of NEW's; NEW's extras are exactly those bool pairs; columns equal."""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from gpu.circuit import P, parse_circuit

SHIFT = 2**20
old_t, new_t = Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text()
O, N = parse_circuit(old_t), parse_circuit(new_t)
res = {"columns_equal": O.col_names == N.col_names and O.one_col == N.one_col}


def canon_cols(C, l, dk=0):
    k, t = (l.konst + dk) % P, Counter()
    for i, c in l.terms:
        if i == C.one_col:
            k = (k + c) % P
        else:
            t[i] = (t[i] + c) % P
    return tuple(sorted((i, c) for i, c in t.items() if c)), k


def canon_wires(C, l, memo):
    k, t = l.konst % P, Counter()
    for i, c in l.terms:
        w = C.wires[i]
        if w[0] == "in" and w[1] == C.one_col:
            k = (k + c) % P
        else:
            t[("c", w[1]) if w[0] == "in" else ("p", prod_canon(C, i, memo))] += c
    return tuple(sorted((tok, c % P) for tok, c in t.items() if c % P)), k


def prod_canon(C, i, memo):
    if i not in memo:
        _, depth, a, b = C.wires[i]
        memo[i] = (depth,) + tuple(sorted([canon_wires(C, a, memo), canon_wires(C, b, memo)]))
    return memo[i]


def blocks(C):
    (t,) = C.tables
    G = t.device_rows("cpu").numpy() % P
    out = {}
    for tag in np.unique(G[:, 1]):
        b = G[G[:, 1] == tag].copy()
        b[:, 0] -= int(tag) * SHIFT
        b[:, 1] = 0
        b = b[np.lexsort(b.T[::-1])]
        keys, rest = b[:, 0], b[:, 2:]
        n = len(b)
        kind = ("L", n, hash(b.tobytes()))
        w = n.bit_length() - 1
        if not rest.any() and n == 2**w and np.array_equal(keys, np.arange(n)):
            kind = ("R", w)
        elif not rest[:, 2:].any() and n == 4 ** (h := (w // 2)) and rest[:, 0].max() < 2**h and rest[:, 1].max() < 2**h \
                and np.array_equal(keys, rest[:, 0] + rest[:, 1] * 2**h) and len(np.unique(keys)) == n:
            kind = ("PR", h)
        out[int(tag)] = kind
    return out


def facts(C, bl):
    f, probs = Counter(), []
    for q in C.queries:
        tag = canon_cols(C, q.cols[1])
        if tag[0] or tag[1] not in bl:
            probs.append(f"tag {tag}")
            continue
        kind = bl[tag[1]]
        key = canon_cols(C, q.cols[0], -tag[1] * SHIFT)
        outs = [canon_cols(C, l) for l in q.cols[2:]]
        if kind[0] == "R":
            f[(kind, key)] += 1
            if any(o != ((), 0) for o in outs):
                probs.append("range outputs")
        elif kind[0] == "PR":
            x, y = outs[0], outs[1]
            s = Counter(dict(x[0]))
            for i, c in y[0]:
                s[i] = (s[i] + c * 2 ** kind[1]) % P
            if key != (tuple(sorted((i, c) for i, c in s.items() if c)), (x[1] + y[1] * 2 ** kind[1]) % P):
                probs.append("PR key != x + 2^b y")
            if any(o != ((), 0) for o in outs[2:]):
                probs.append("PR padding")
            f[(("R", kind[1]), x)] += 1
            f[(("R", kind[1]), y)] += 1
        else:
            f[(kind, key, tuple(outs))] += 1
    return f, probs


bo, bn = blocks(O), blocks(N)
res["old_blocks"] = sorted(str(v[:2]) for v in bo.values())
res["new_blocks"] = sorted(str(v[:2]) for v in bn.values())
res["listed_blocks_equal"] = sorted(v for v in bo.values() if v[0] == "L") == sorted(v for v in bn.values() if v[0] == "L")
mo, mn = {}, {}
po_ = Counter(prod_canon(O, i, mo) for i, w in enumerate(O.wires) if w[0] == "prod")
pn_ = Counter(prod_canon(N, i, mn) for i, w in enumerate(N.wires) if w[0] == "prod")
ao = Counter(canon_wires(O, l, mo) for _, l in O.asserts)
an = Counter(canon_wires(N, l, mn) for _, l in N.asserts)
res["old_prods_subset"] = not (po_ - pn_)
res["old_asserts_subset"] = not (ao - an)
extra_p, extra_a = pn_ - po_, an - ao
res["extra_prods"], res["extra_asserts"] = sum(extra_p.values()), sum(extra_a.values())
bools, bool_probs, used = Counter(), [], Counter()
for pc, n in extra_p.items():
    depth, a, b = pc
    if a != b or any(tok[0] != "c" for tok, _ in a[0]):
        bool_probs.append(f"extra prod not e*e over columns: {str(pc)[:120]}")
        continue
    wt = (("p", pc), 1)
    neg = (tuple(sorted([wt] + [(tok, (-c) % P) for tok, c in a[0]])), (-a[1]) % P)
    pos = (tuple(sorted([(("p", pc), P - 1)] + list(a[0]))), a[1])
    hit = neg if extra_a[neg] else pos if extra_a[pos] else None
    if hit is None or extra_a[hit] - used[hit] < n:
        bool_probs.append(f"no assert w - e = 0 for {str(pc)[:120]}")
        continue
    used[hit] += n
    bools[(tuple(sorted((tok[1], c) for tok, c in a[0])), a[1])] += n
res["unmatched_extra_asserts"] = sum((extra_a - used).values())
res["bool_pairs"] = sum(bools.values())
res["bool_problems"] = bool_probs[:5]
fo, pro = facts(O, bo)
fn, prn = facts(N, bn)
for e, n in bools.items():
    fn[(("R", 1), e)] += n
res["queries"] = [len(O.queries), len(N.queries)]
res["facts"] = [sum(fo.values()), sum(fn.values())]
res["facts_by_kind_old"] = {str(k): v for k, v in sorted(Counter(str(k[0]) for k in fo.elements()).items())}
res["facts_by_kind_new"] = {str(k): v for k, v in sorted(Counter(str(k[0]) for k in fn.elements()).items())}
res["query_problems"] = (pro + prn)[:5]
res["facts_equal"] = fo == fn
if not res["facts_equal"]:
    res["facts_only_old"] = [str(k)[:160] for k in list((fo - fn).elements())[:5]]
    res["facts_only_new"] = [str(k)[:160] for k in list((fn - fo).elements())[:5]]
res["ok"] = bool(res["columns_equal"] and res["facts_equal"] and res["listed_blocks_equal"] and res["old_prods_subset"]
                 and res["old_asserts_subset"] and not bool_probs and not pro and not prn and res["unmatched_extra_asserts"] == 0
                 and res["extra_prods"] == res["bool_pairs"] == res["extra_asserts"])
print(json.dumps(res, indent=1, default=str))
sys.exit(0 if res["ok"] else 1)
