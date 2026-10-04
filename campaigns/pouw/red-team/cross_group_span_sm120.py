"""Red-team for `cross-group-knowledge-wide/pearl-c`: which share of the cross-group joint skips span only two promotion groups?

The wide row carries only sets spanning three or more groups; the verifier debits the narrow ones (a pair replay, like P1's
within-group flags). Per word of a family (census s5 forming, bit-exact sm_120 atom, G = 4), from the honest state:
  - N, the atoms a narrow debit flags: lone skips, P1's within-group joint flags (`pearlc_census.debit`), and every atom of a
    jointly skippable pair spanning two groups (neither atom skippable alone). The pair test replays two group sums and the
    FP32 promotion fold, vectorized over the partner;
  - S, the census's greedy joint set (`greedy_set`: two-group pairs packed greedily, then singles given the set);
  - the wide residue S \\ N (what the narrower conjecture still carries), and N's size (what the extra debit costs the credit).
"""
import argparse, importlib.util, json, os, sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

TREE = Path(os.environ.get("CENSUS_TREE") or f"/workspace/research/src/{os.environ.get('RESEARCH_SOURCE_SHA', '')}")
_spec = importlib.util.spec_from_file_location("pearlc_census", TREE / "benchmarks/pouw/pearlc_census.py")
C = importlib.util.module_from_spec(_spec)
sys.modules["pearlc_census"] = C
_spec.loader.exec_module(C)
C.set_atom("sm120-e4m3-k32")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt_result  # noqa: E402

G = 4


def fold(S):
    """The FP32 promotion fold over group sums, rows of S (…, groups) → the ticket word per row."""
    tot = np.zeros(S.shape[:-1], np.float32)
    for g in range(S.shape[-1]):
        tot = (tot + S[..., g].astype(np.float32)).astype(np.float32)
    return tot


def word(job):
    fam, k, w = job
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, 64, 16, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-A"))[0]
    b = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-B"))[0]
    A, B = np.repeat(a, 16, 0)[w:w + 1], np.tile(b, (64, 1))[w:w + 1]
    T = k // 32
    ng = T // G
    groups = [list(range(g * G, (g + 1) * G)) for g in range(ng)]
    Sg = np.array([C.group_run(A, B, ts)[0][0] for ts in groups], np.float32)
    Sm = np.array([[C.group_run(A, B, ts, frozenset({t}))[0][0] for t in ts] for ts in groups], np.float32)  # (ng, G)
    final = fold(Sg[None])[0]
    lone = np.zeros(T, bool)
    for g in range(ng):
        X = np.repeat(Sg[None], G, 0)
        X[:, g] = Sm[g]
        lone[g * G:(g + 1) * G] = fold(X) == final
    p1 = C.debit(A, B, G)[0][0]
    pair = np.zeros(T, bool)
    for g1 in range(ng):
        for i1 in range(G):
            t1 = g1 * G + i1
            if lone[t1]:
                continue
            rest = [(g2, i2) for g2 in range(g1 + 1, ng) for i2 in range(G) if not lone[g2 * G + i2]]
            if not rest:
                continue
            X = np.repeat(Sg[None], len(rest), 0)
            X[:, g1] = Sm[g1, i1]
            for r, (g2, i2) in enumerate(rest):
                X[r, g2] = Sm[g2, i2]
            hit = fold(X) == final
            if hit.any():
                pair[t1] = True
                for r in np.flatnonzero(hit):
                    g2, i2 = rest[r]
                    pair[g2 * G + i2] = True
    N = lone | p1 | pair
    S = C.greedy_set(A, B, G)
    Sarr = np.zeros(T, bool)
    Sarr[list(S)] = True
    wide = Sarr & ~N
    return {"family": fam, "k": k, "word": w, "atoms": T, "greedy_share": float(Sarr.mean()),
            "narrow_debit_share": float(N.mean()), "lone_share": float(lone.mean()), "p1_share": float(p1.mean()),
            "pair_only_share": float((pair & ~lone & ~p1).mean()),
            "wide_residue_share": float(wide.mean()), "wide_of_greedy": float(wide.sum() / max(1, Sarr.sum()))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="gaussian,outliers-first,spikes-first,aligned-spikes-r32,aligned-spikes-r48,"
                                          "aligned-spikes-pm1-r48")
    ap.add_argument("--k", type=int, default=8192)
    ap.add_argument("--words", type=int, default=16)
    ap.add_argument("--procs", type=int, default=48)
    args = ap.parse_args()
    jobs = [(f, args.k, w) for f in args.families.split(",") for w in range(args.words)]
    with Pool(min(args.procs, len(jobs))) as pool:
        rows = pool.map(word, jobs)
    summary = {}
    for f in args.families.split(","):
        r = [x for x in rows if x["family"] == f]
        summary[f] = {key: float(np.mean([x[key] for x in r])) for key in
                      ("greedy_share", "narrow_debit_share", "pair_only_share", "wide_residue_share", "wide_of_greedy")}
        summary[f]["wide_residue_share_max"] = float(max(x["wide_residue_share"] for x in r))
        print(json.dumps({"family": f, **summary[f]}), flush=True)
    meas = [(f"{f}.{m}", round(v[m], 6), "fraction") for f, v in summary.items()
            for m in ("greedy_share", "narrow_debit_share", "wide_residue_share")]
    rt_result.write("cross-group-span-sm120", meas, {"k": args.k, "G": G, "summary": summary, "words": rows},
                    detail="greedy cross-group sets vs a narrow (two-group) debit; wide residue per word")


if __name__ == "__main__":
    main()
