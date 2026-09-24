"""arith: census + micro-benchmark of the prover's tests kernels on a registered relation's real system (pod only).

    python kbench.py --relation fp8-ada-v3x4 --l 4096 [--reps 20]

Random canonical residues for the codeword U (Mrows, n) and the challenge rows; every candidate kernel is checked
bit-exact against the current one before it is timed (CUDA events, median of --reps).
"""
import argparse
import json
import statistics

import torch

from backends.direct.ligero import protocol, relations, tests_fused, witness
from backends.direct.ligero.field import P
from backends.direct.ligero.relchain import RelationChainRunner


def timeit(fn, reps):
    fn()
    torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        a, b = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        a.record()
        fn()
        b.record()
        b.synchronize()
        ts.append(a.elapsed_time(b))
    return statistics.median(ts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--relation", default="fp8-ada-v3x4")
    ap.add_argument("--l", type=int, default=4096)
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--n-proofs", type=int, default=13)
    a = ap.parse_args()
    dev = torch.device("cuda")
    rel = relations.RELATIONS[a.relation]
    R = RelationChainRunner(rel, "cuda", -128.0, n_proofs=a.n_proofs, zk=True)
    sys_, tb = R.sys, R.tb
    cfg = R.cfg(a.l)
    m, n, k, D = sys_.m, cfg.n, cfg.k, cfg.D
    Mrows = protocol.n_rows(cfg, m, True)
    sp = tb.quad["split"]
    census = {"m": m, "Mrows": Mrows, "l": cfg.l, "n": n, "k": k, "D": D, "L": tb.L, "Q": tb.Q,
              "Q_bool": int(sp["bool_q"].numel()), "Q_gen": int(sp["Q_gen"]),
              "bool_rows_distinct": int(torch.unique(sp["bool_j"]).numel())}
    csr = tests_fused.csr_tables(sp["gen"], sp["Q_gen"], dev)
    sp["csr"] = csr
    for side in ("a", "b", "c"):
        ptr = csr[side]["ptr"].to(torch.int64)
        cnt = ptr[1:] - ptr[:-1]
        census[f"terms_{side}"] = int(cnt.sum())
        census[f"terms_{side}_max"] = int(cnt.max()) if cnt.numel() else 0
        census[f"terms_{side}_hist"] = {int(v): int(c) for v, c in zip(*torch.unique(cnt, return_counts=True))}
        census[f"const_{side}_nonzero"] = int((csr[side]["const"] != 0).sum())
    alljs = torch.cat([csr[s]["j"] for s in "abc"]).to(torch.int64)
    census["gen_rows_distinct"] = int(torch.unique(alljs).numel())
    print(json.dumps(census))

    g = torch.Generator(device="cpu").manual_seed(1)
    U = torch.randint(0, P, (Mrows, n), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
    coefs = torch.randint(0, P, (Mrows, k), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
    rho_q = torch.randint(0, P, (D, tb.Q), generator=g, dtype=torch.int64).to(dev)
    r = torch.randint(0, P, (D, Mrows), generator=g, dtype=torch.int64).to(dev)
    f = tests_fused.fused_for(D, dev)
    rg = rho_q.index_select(1, sp["gen_q"])
    rb = rho_q.index_select(1, sp["bool_q"])
    bj = sp["bool_j"].to(torch.int32).contiguous()
    res = {}
    ref_gen = f.quad_general(rg, U[:m], csr)
    res["quad_general"] = timeit(lambda: f.quad_general(rg, U[:m], csr), a.reps)
    if hasattr(f, "quad_general_v4"):
        got = f.quad_general_v4(rg, U[:m], csr)
        res["quad_general_v4_exact"] = bool(torch.equal(got, ref_gen))
        res["quad_general_v4"] = timeit(lambda: f.quad_general_v4(rg, U[:m], csr), a.reps)
    res["boolcomb_rows"] = timeit(lambda: f.lincomb(rb, U[:m], square_minus=True, rows=bj), a.reps)
    res["quad_p0"] = timeit(lambda: witness.quad_p0(tb, rho_q, U[:m]), a.reps)
    res["lincomb_w"] = timeit(lambda: f.lincomb(r, coefs), a.reps)
    res["lincomb_v"] = timeit(lambda: f.lincomb(r[:, :m], coefs[:m]), a.reps)
    print(json.dumps({k_: (round(v, 4) if isinstance(v, float) else v) for k_, v in res.items()}))


if __name__ == "__main__":
    main()
