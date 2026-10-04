"""Red-team supplement to fragment_joint_sm120.py: how aligned are the per-word joint sets inside one MMA fragment?

For every one of a 16 x 8 fragment's 128 words it computes the census's greedy joint set (`greedy_pure` for the pure chain,
v2; `greedy_set` for G = 4, v1), then counts, per atom, the words whose set contains it. A fragment-wide skip of any set
containing atom t needs t in the joint skip of every word (at most PATCH_MAX = 5 words patched), so the largest count bounds
what a pair or larger set could still give the fragment greedy missed. It also tests the most shared pairs fragment-wide.
"""
import argparse, importlib.util, itertools, json, os, sys
from collections import Counter
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
from fragment_joint_sm120 import run_from  # noqa: E402


def operands(fam, k):
    XA, XB, _, _ = C.family_rows(fam, k, 1.0, 16, 8, 1)
    FcA, FcB = C.s5_lines(k, 1, 16.0)
    a = C.form_s5(XA, FcA, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-A"))[0]
    b = C.form_s5(XB, FcB, 1.0, 16.0, C._rng(1, fam, k, 1.0, "unit-B"))[0]
    return np.repeat(a, 8, 0), np.tile(b, (16, 1))


def word_set(job):
    fam, k, G, w = job
    A, B = operands(fam, k)
    s = C.greedy_pure(A[w:w + 1], B[w:w + 1]) if G == 0 else C.greedy_set(A[w:w + 1], B[w:w + 1], G)
    return w, sorted(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", default="aligned-spikes-r56,8192,0;aligned-spikes-r48,8192,4")
    ap.add_argument("--procs", type=int, default=64)
    args = ap.parse_args()
    out, meas = [], []
    for spec in args.cells.split(";"):
        fam, k, G = spec.split(",")
        k, G = int(k), int(G)
        with Pool(args.procs) as pool:
            sets = dict(pool.map(word_set, [(fam, k, G, w) for w in range(128)]))
        T = k // 32
        count = Counter(t for s in sets.values() for t in s)
        pairs = Counter(p for s in sets.values() for p in itertools.combinations(s, 2))
        A, B = operands(fam, k)
        start = (np.zeros(128), np.zeros(128, np.float32) if G else None)
        final = run_from(A, B, 0, *start, G)
        tested = []
        for (t1, t2), n in pairs.most_common(20):
            same = int((run_from(A, B, 0, *start, G, frozenset((t1, t2))) == final).sum())
            tested.append({"pair": [t1, t2], "words_with_pair_in_set": n, "words_unchanged_fragment_wide": same})
        r = {"family": fam, "k": k, "layout": "pure" if G == 0 else f"G{G}", "atoms": T,
             "per_word_set_share_mean": float(np.mean([len(s) / T for s in sets.values()])),
             "per_word_set_share_max": float(max(len(s) / T for s in sets.values())),
             "max_words_sharing_an_atom": max(count.values(), default=0),
             "max_words_sharing_a_pair": max(pairs.values(), default=0),
             "top_pairs_tested": tested,
             "best_pair_words_unchanged": max((x["words_unchanged_fragment_wide"] for x in tested), default=0)}
        out.append(r)
        print(json.dumps(r), flush=True)
        tag = f"{fam}.k{k}.{r['layout']}"
        meas += [(f"{tag}.max_words_sharing_an_atom", r["max_words_sharing_an_atom"], "words"),
                 (f"{tag}.best_pair_words_unchanged", r["best_pair_words_unchanged"], "words")]
    rt_result.write("fragment-alignment-sm120", meas, {"cells": out},
                    detail="per-word greedy joint sets of all 128 words of one 16x8 fragment; atom and pair sharing")


if __name__ == "__main__":
    main()
