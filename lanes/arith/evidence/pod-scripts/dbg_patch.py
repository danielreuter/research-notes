"""arith (diagnostic, never committed): log every tests-graph capture, static-set creation and eviction to stderr.

    python dbg_patch.py TREE      # edits TREE/backends/direct/ligero/protocol.py in place
"""
import sys
from pathlib import Path

p = Path(sys.argv[1]) / "backends/direct/ligero/protocol.py"
s = p.read_text()
s = s.replace(
    "        st = _TestsStatic(key, cfg, sys, tb, m, Mrows, width, chain, device, steps)\n",
    "        st = _TestsStatic(key, cfg, sys, tb, m, Mrows, width, chain, device, steps)\n"
    "        import time as _t, sys as _s; print(f'DBG {_t.perf_counter():.3f} static-new stream={skey[1]} key={key} n_sets={len(sets)}', file=_s.stderr)\n",
    1)
s = s.replace(
    "            old = sets.pop()\n",
    "            old = sets.pop()\n"
    "            import time as _t, sys as _s; print(f'DBG {_t.perf_counter():.3f} static-evict stream={skey[1]} key={old.key}', file=_s.stderr)\n",
    1)
s = s.replace(
    "    if hit is not None and hit[1] != mbuf.data_ptr():              # the pinned buffer moved (grown): re-capture\n",
    "    if hit is not None and hit[1] != mbuf.data_ptr():              # the pinned buffer moved (grown): re-capture\n"
    "        import time as _t, sys as _s; print(f'DBG {_t.perf_counter():.3f} mbuf-moved lkey={lkey}', file=_s.stderr)\n",
    1)
s = s.replace(
    "    if hit is None:\n        try:\n            cur = torch.cuda.current_stream(device)\n",
    "    if hit is None:\n"
    "        import time as _t, sys as _s; _t0 = _t.perf_counter()\n"
    "        try:\n            cur = torch.cuda.current_stream(device)\n",
    1)
s = s.replace(
    "        hit = (g, mbuf.data_ptr())\n        st.graphs[lkey] = hit\n",
    "        hit = (g, mbuf.data_ptr())\n        st.graphs[lkey] = hit\n"
    "        print(f'DBG {_t.perf_counter():.3f} tests-capture stream={torch.cuda.current_stream(device).cuda_stream} lkey={lkey} ms={1e3 * (_t.perf_counter() - _t0):.1f}', file=_s.stderr)\n",
    1)
s = s.replace(
    "    g = getattr(holder, attr)\n    if g is None:\n        try:\n",
    "    g = getattr(holder, attr)\n    if g is None:\n"
    "        import time as _t, sys as _s; _t0 = _t.perf_counter()\n        try:\n",
    1)
s = s.replace(
    "        setattr(holder, attr, g)\n",
    "        setattr(holder, attr, g)\n"
    "        print(f'DBG {_t.perf_counter():.3f} {attr}-capture stream={torch.cuda.current_stream(device).cuda_stream} ms={1e3 * (_t.perf_counter() - _t0):.1f}', file=_s.stderr)\n",
    1)
s = s.replace(
    "        print(f'rep {",
    "        import time as _t, sys as _s; print(f'DBG {_t.perf_counter():.3f} rep-end', file=_s.stderr)\n        print(f'rep {",
    1)
print("DBG markers:", [m for m in ("static-new", "static-evict", "mbuf-moved", "tests-capture", "-capture stream") if m in s])
p.write_text(s)
print("patched", p)
