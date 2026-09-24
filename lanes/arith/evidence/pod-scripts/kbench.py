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
    ap.add_argument("--sweep", action="store_true")
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
    for side in ("a", "b", "c"):
        ptr = csr[side]["ptr"].cpu().tolist()
        js, cs, ks = csr[side]["j"].cpu().tolist(), csr[side]["coef"].cpu().tolist(), csr[side]["const"].cpu().tolist()
        exprs = [tuple(zip(js[ptr[q]:ptr[q + 1]], cs[ptr[q]:ptr[q + 1]])) + (("k", ks[q]),) for q in range(len(ptr) - 1)]
        uniq = set(exprs)
        census[f"uniq_{side}"] = len(uniq)
        census[f"uniq_{side}_terms"] = sum(len(e) - 1 for e in uniq)
        lin = set(e[:-1] for e in exprs)
        census[f"uniq_{side}_noconst_terms"] = sum(len(e) for e in lin)
    ftmp = tests_fused.fused_for(D, dev)
    for kn in ("quad_u32", "quad_v4_u32", "boolcomb_rows_v4_u32", "lincomb_v4_u32"):
        if kn in ftmp.k:
            kk = ftmp.k[kn]
            census[f"regs_{kn}"] = kk.num_regs
            census[f"lmem_{kn}"] = kk.local_size_bytes
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
    if a.sweep:
        tests_fused.QUAD_V4 = False
        ref_q = f.quad_general(rg, U[:m], csr)
        tests_fused.QUAD_V4 = True
        for thr in (128, 256):
            for qf in (False, True):
                for S in (16, 32, 64, 128, 256):
                    tests_fused.QUAD_THREADS, tests_fused.QUAD_QFAST, tests_fused.QUAD_SPLITS = thr, qf, S
                    ok = bool(torch.equal(f.quad_general(rg, U[:m], csr), ref_q))
                    t = timeit(lambda: f.quad_general(rg, U[:m], csr), a.reps)
                    print(f"sweep thr={thr} qfast={int(qf)} S={S} exact={ok} ms={t:.4f}", flush=True)
        return
    flags = [("old", False, False), ("reduce", False, True), ("new", True, True)]
    if not hasattr(tests_fused, "QUAD_V4"):
        flags = flags[:1]
    ref = {}
    for tag, qv4, rk in flags:
        if len(flags) > 1:
            tests_fused.QUAD_V4, tests_fused.REDUCE_KERNEL = qv4, rk
        outs = {"quad_general": lambda: f.quad_general(rg, U[:m], csr),
                "boolcomb_rows": lambda: f.lincomb(rb, U[:m], square_minus=True, rows=bj),
                "quad_p0": lambda: witness.quad_p0(tb, rho_q, U[:m]),
                "lincomb_w": lambda: f.lincomb(r, coefs),
                "lincomb_v": lambda: f.lincomb(r[:, :m], coefs[:m])}
        for name, fn in outs.items():
            got = fn()
            if tag == "old":
                ref[name] = got
            else:
                res[f"{name}_{tag}_exact"] = bool(torch.equal(got, ref[name]))
            res[f"{name}_{tag}"] = timeit(fn, a.reps)
    print(json.dumps({k_: (round(v, 4) if isinstance(v, float) else v) for k_, v in res.items()}))


if __name__ == "__main__":
    main()
