"""agkr-nvf4: host cost of add_lookup_claim's per-query term loop (Python ext arithmetic) on the exported unit circuit.
python 09_terms.py STMT_DIR"""
import sys
import time

from gpu import prover
from gpu.circuit import load_circuit
from gpu.field import ZERO, e_scale, e_sub

circ = load_circuit(sys.argv[1] + "/circuit.txt")
z = (5, 6, 7, 8, 9, 10)
bs_all = [(1, 0, 0, 0, 0, 0), (11, 2, 3, 4, 5, 6), (13, 1, 1, 1, 1, 1), (17, 9, 8, 7, 6, 5), (19, 3, 3, 3, 3, 3)]
for name in sorted({q.table for q in circ.queries}):
    qs = prover.table_queries(circ, name)
    t0 = time.perf_counter()
    for _ in range(5):
        csts, terms = [], {}
        for j, qu in enumerate(qs):
            cst = z
            for kk, lin in enumerate(qu.cols):
                cst = e_sub(cst, e_scale(bs_all[kk], lin.konst))
                for idx, coef in lin.terms:
                    terms[(j, idx)] = e_sub(terms.get((j, idx), ZERO), e_scale(bs_all[kk], coef))
            csts.append(cst)
        keys = sorted(terms, key=lambda k: (k[1], k[0]))
    dt = (time.perf_counter() - t0) / 5
    print(f"{name}: {len(qs)} queries, {len(terms)} terms, loop {dt * 1e3:.2f} ms")
