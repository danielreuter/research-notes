"""VM check of ScaledMmFp8BlockSharedScale_v1 against ScaledMmFp8Block_v1: signature, circuit identity after merging duplicates,
and the Q_word_v1 unit rule (with #98's members check when the tree has it)."""
import sys
import time

from verity.ir.defs import bind
from verity.ir.layout import resolve
from verity_vllm.program.registry import fp8
from verity_vllm.query import word as W


def canon(fn, table):
    c, call = W._call_scope(fn)
    lo, n = call.offset, fn.gates
    ids = [0] * n
    for j in range(n):
        g = c.gate(lo + j)
        ops = tuple(ids[o - lo] if lo <= o < lo + n else table.setdefault(("in", o), len(table)) for o in g.operands)
        ids[j] = table.setdefault((g.prim.id, ops), len(table))
    return tuple(ids[resolve(call, r) - lo] for r in fn.body.ret)


shapes = [(256, 256), (384, 128), (128, 512)]
for K, N in shapes:
    old, new = bind(fp8.ScaledMmFp8Block, K=K, N=N, G=128), bind(fp8.ScaledMmFp8BlockSharedScale, K=K, N=N, G=128)
    assert old.signature() == new.signature()
    t = {}
    same = canon(old, t) == canon(new, t)
    nb, kb = N // 128, K // 128
    print(f"K={K} N={N}: gates old {old.gates} new {new.gates} (saved {old.gates - new.gates} = {(128 - 1) * nb * kb} expected), same circuit {same}")
    t0 = time.time()
    r_old, r_new = W.unit_rule(old), W.unit_rule(new)
    print(f"  old violations {[(v['class'], v.get('codes')) for v in r_old['violations']]}")
    print(f"  new violations {r_new['violations']}; committed_interior_words {r_new['committed_interior_words']} (want {nb * kb}); "
          f"units {r_new['units_per_call']} by_kind {r_new['by_kind']} {time.time() - t0:.1f}s")
    print(f"  new interior {r_new['committed_interior']}")
