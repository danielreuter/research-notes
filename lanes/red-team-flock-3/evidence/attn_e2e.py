"""red-team-flock-3: end-to-end exactness of the attention lowering from its pinned netlist text alone.

For each instance, the verifier accepts a cut-word assignment W iff every unit's output = netlist(its leaves, its cut inputs from W)
and every tail-computed word and output = the pinned tail on (unit outputs + public words). This solves that system by fixpoint
(public words -> tail ops whose operands are known -> units whose inputs are known -> ...), with MY netlist evaluator (netlist.py)
and the tail ops evaluated by the IR's own primitives (verity_vllm prims, by id). If every cut word is determined, the assignment
is unique (the unit/tail dependency graph is acyclic). The outputs are then compared with the IR reference (`verity.evaluation.
evaluate` of AttentionHead_v3{T}) and, for captured sets, with the captured outputs; every cut word is compared with the IR's
gate values (`verity_flock.ir_lower.cut_words`, the IR evaluator at the producer's cut gates).

  attn_e2e.py captured SET_DIR [T,T,..] [limit]
  attn_e2e.py adversarial T[,T..] N SEED
"""
import hashlib
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import netlist as NL  # noqa: E402

from verity.evaluation import evaluate  # noqa: E402
from verity_numerical.bench import templates as TM  # noqa: E402
from verity_vllm.program.registry import prims as P  # noqa: E402

SUB = TM.subcircuit("attention-head", D=64, BN=128)
D = 64
_NETS = {}


def net_for(T):
    if T not in _NETS:
        from verity_flock.templates import attention_head as AH
        low = AH.lowering(SUB, T)
        _NETS[T] = (NL.Net(low.text), low)
    return _NETS[T]


def prim(pid):
    name, ver = pid.rsplit("_v", 1)
    p = getattr(P, name)
    assert p.id == pid, (p.id, pid)
    return p.evaluate


class Solver:
    def __init__(self, net: NL.Net):
        self.net, self.tc = net, NL.TcUnit(net)
        c, lv = net.cut, net.leaves
        self.words = c["words"]
        self.unit_in, self.unit_out = c["in"], c["out"]
        self.public, self.outputs = c["public"], c["outputs"]
        self.tail = c["tail"]
        self.leaf_in = lv["in"]
        self.U = len(self.unit_in)
        assert len(self.leaf_in) == self.U and all(len(x) == 16 for x in self.leaf_in)
        a_cols = self.tc.ac_cols
        for u in range(self.U):
            assert [p[0] for p in self.unit_in[u]] == a_cols, f"unit {u} cut input columns"
            assert len(self.unit_out[u]) == 1 and self.unit_out[u][0][0] == 0, f"unit {u} cut output"
        self.fns = {}
        for op in self.tail:
            if op[1] != "Const":
                self.fns.setdefault(op[1], prim(op[1]))
        self.n_slots = 1 + max([op[0] for op in self.tail] + [self.words - 1])

    def solve(self, flat):
        """flat: (n, 64 + 128 T) u16 instance leaves -> (slots (n, n_slots) u64, outputs (n, 64), stats)."""
        n = flat.shape[0]
        known = np.zeros(self.n_slots, dtype=bool)
        slots = np.zeros((n, self.n_slots), dtype=np.uint64)
        for k, leaf in self.public:
            slots[:, k] = flat[:, leaf]; known[k] = True
        tail_done = [False] * len(self.tail)
        unit_done = [False] * self.U
        rounds = unit_evals = 0
        sat_all = True
        while True:
            progress = False
            for j, op in enumerate(self.tail):
                if tail_done[j]:
                    continue
                out, pid, args = op[0], op[1], op[2:]
                if pid == "Const":
                    slots[:, out] = args[0] & 0xFFFFFFFF
                elif all(known[a] for a in args):
                    fn = self.fns[pid]
                    cols = [slots[:, a] for a in args]
                    slots[:, out] = [fn(*[int(c[i]) for c in cols]) & 0xFFFFFFFF for i in range(n)]
                else:
                    continue
                assert not known[out], f"slot {out} written twice"
                known[out] = True; tail_done[j] = True; progress = True
            ready = [u for u in range(self.U) if not unit_done[u] and all(known[k] for _, k in self.unit_in[u])]
            if ready:
                L = n * len(ready)
                acc = np.empty(L, dtype=np.uint64); a = np.empty((L, 16), dtype=np.uint64); b = np.empty((L, 16), dtype=np.uint64)
                for r, u in enumerate(ready):
                    ks = [k for _, k in self.unit_in[u]]
                    sl = slice(r * n, (r + 1) * n)
                    a[sl] = slots[:, ks[:16]]; acc[sl] = slots[:, ks[16]]
                    b[sl] = np.stack([flat[:, lf] if lf >= 0 else np.zeros(n, dtype=np.uint64) for lf in self.leaf_in[u]], axis=1)
                res, sat = self.tc(acc, a, b)
                sat_all &= bool(sat.all())
                for r, u in enumerate(ready):
                    k = self.unit_out[u][0][1]
                    assert not known[k], f"cut word {k} computed twice"
                    slots[:, k] = res[r * n:(r + 1) * n]; known[k] = True; unit_done[u] = True
                unit_evals += L; progress = True
            rounds += 1
            if not progress:
                break
        undetermined = int((~known[:self.words]).sum())
        outs = slots[:, self.outputs] if undetermined == 0 else None
        return slots, outs, {"rounds": rounds, "unit_evals": unit_evals, "undetermined_cut_words": undetermined,
                             "units_unsolved": self.U - sum(unit_done), "tail_unsolved": len(self.tail) - sum(tail_done), "sat": sat_all}


def ir_outputs(T, flat):
    defn = SUB.definition(T)
    return np.array([evaluate(defn, [int(x) for x in r[:D]], [int(x) for x in r[D:D + T * D]], [int(x) for x in r[D + T * D:]])
                     for r in flat], dtype=np.uint64)


def check(T, flat, captured_out=None, cut_check=True):
    net, low = net_for(T)
    s = Solver(net)
    t0 = time.time()
    slots, outs, st = s.solve(flat.astype(np.uint64))
    t1 = time.time()
    ir = ir_outputs(T, flat)
    t2 = time.time()
    r = dict(T=T, n=len(flat), pin=net.sha256[:16], units=s.U, tail_ops=len(s.tail), cut_words=s.words, **st)
    r["out_mismatch_heads"] = None if outs is None else int((outs != ir).any(axis=1).sum())
    r["out_mismatch_words"] = None if outs is None else int((outs != ir).sum())
    if captured_out is not None:
        r["ir_vs_captured_heads"] = int((ir != captured_out).any(axis=1).sum())
    if cut_check and outs is not None:
        from verity_flock import ir_lower as IL
        cw = IL.cut_words(low, flat.astype(np.uint64))
        r["cut_mismatch_heads"] = int((slots[:, :s.words] != cw).any(axis=1).sum())
        r["cut_mismatch_words"] = int((slots[:, :s.words] != cw).sum())
    r["solve_s"], r["ir_s"] = round(t1 - t0, 1), round(t2 - t1, 1)
    if outs is not None and r["out_mismatch_heads"]:
        i = int(np.nonzero((outs != ir).any(axis=1))[0][0])
        r["first_bad"] = {"i": i, "got": [hex(int(x)) for x in outs[i][:8]], "ir": [hex(int(x)) for x in ir[i][:8]]}
    return r


def main():
    mode = sys.argv[1]
    summary = {}
    if mode == "captured":
        from verity_numerical.bench.input_sets import InputSet
        s = InputSet.open(sys.argv[2])
        only = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 and sys.argv[3] else None
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
        q, k, v, out = s.port("q"), s.port("k"), s.port("v"), s.port("out")
        byT = defaultdict(list)
        for i in range(s.n):
            byT[len(k[i]) // D].append(i)
        for T in sorted(byT):
            if only and T not in only:
                continue
            ids = byT[T][:limit] if limit else byT[T]
            flat = np.stack([np.concatenate([q[i], k[i], v[i]]).astype(np.uint64) for i in ids])
            cap = np.stack([np.asarray(out[i], dtype=np.uint64) for i in ids])
            r = check(T, flat, cap)
            summary[T] = r
            print("E2E", json.dumps(r), flush=True)
    else:
        import gen_attn as G
        Ts = [int(x) for x in sys.argv[2].split(",")]
        n, seed = int(sys.argv[3]), int(sys.argv[4])
        for T in Ts:
            for cat in G.CATEGORIES:
                flat = G.instances(T, n, seed, cat)
                r = check(T, flat, None, cut_check=len(sys.argv) <= 5)
                r["category"] = cat
                summary[f"{T}/{cat}"] = r
                print("E2E", json.dumps(r), flush=True)
    bad = {k: v for k, v in summary.items() if v.get("out_mismatch_heads") != 0 or v.get("undetermined_cut_words") != 0
           or v.get("cut_mismatch_heads", 0) != 0 or v.get("ir_vs_captured_heads", 0) != 0 or not v.get("sat")}
    print("SUMMARY", json.dumps({"cases": len(summary), "bad": list(bad), "heads": sum(v["n"] for v in summary.values())}))


if __name__ == "__main__":
    main()
