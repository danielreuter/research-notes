import sys, numpy as np
from verity.ir.defs import bind
from verity_vllm.program.registry import sampling as SM
from verity_vllm.query import word as Wd
V = int(sys.argv[1]) if len(sys.argv) > 1 else 16
fn = bind(SM.GumbelTopPTokenSelect, V=V)
G = Wd.Graph(fn)
u = Wd.units(G, 16, 32)
print("gates", G.total, "free", G.free, "computing", G.n, "units", len(u["kinds"]), u["kinds"][:8])
print("recomputed", len(G.recomputed))
for a, b in G.recomputed[:10]:
    print(" ", G.prim_names[int(G.prim[a])], G.scope_names[int(G.scope[a])], "owner", int(u["owner"][a]), "<-", G.prim_names[int(G.prim[b])], G.scope_names[int(G.scope[b])], "owner", int(u["owner"][b]))
print("cut", u["cut"].ok, u["cut"].codes)
