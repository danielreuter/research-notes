"""flock-glue: AND-depth profile of an exported unit netlist (rows in order; self-references dropped).
usage: python3 levels.py NETLIST"""
import sys
from collections import Counter

f = open(sys.argv[1])
useful, const, n_in = map(int, f.readline().split()[:3])
lvl = [0] * useful
fwd = selfref = 0
for i in range(useful):
    v = list(map(int, f.readline().split()))
    na = v[0]
    a, b = v[1:1 + na], v[2 + na:]
    if i < n_in or i == const:
        continue
    m = 0
    for c in a + b:
        if c == i:
            selfref += 1
            continue
        if c > i and c != const:
            fwd += 1
        m = max(m, lvl[c])
    lvl[i] = m + 1
h = Counter(lvl[n_in:const])
D = max(h)
print(f"useful={useful} n_in={n_in} depth={D} selfrefs={selfref} forward_refs={fwd}")
w = [h[d] for d in range(1, D + 1)]
print("width min/median/max", min(w), sorted(w)[len(w) // 2], max(w))
print("levels with width<32:", sum(1 for x in w if x < 32), " <8:", sum(1 for x in w if x < 8))
