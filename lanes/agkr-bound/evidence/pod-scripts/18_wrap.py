"""agkr-bound: bench_result.py with tools/link_stub.py's circuit appended as a third segment of every Instance (LINK_DIR
set), tiled to the unit segment's row count: the marginal A100 cost of the bit link's prime side inside the real BF16
proof.  The Rust verifier does not know the segment, so only the Python verifier's verdict counts.  cwd backends/gkr.
    [LINK_DIR=D] python 18_wrap.py <bench_result.py args>
"""
import os
import runpy
import sys

sys.path.insert(0, ".")
import torch                                            # noqa: E402

from gpu import prover                                  # noqa: E402
from gpu.bb_export import read_rows                     # noqa: E402
from gpu.circuit import layers, load_circuit            # noqa: E402
from gpu.field import P                                 # noqa: E402

LD = os.environ.get("LINK_DIR")
if LD:
    circ = load_circuit(os.path.join(LD, "circuit.txt"))
    lay = layers(circ)
    base = torch.from_numpy(read_rows(os.path.join(LD, "witness.bin")).astype("int64"))
    cache = {}
    Orig = prover.Instance

    class WithLink(Orig):
        def __init__(self, segs, chain=None, *a, **k):
            Orig.__init__(self, segs, chain, *a, **k)
            u, dev = self.segs[0].units, self.segs[0].cols.device
            if u not in cache:
                cache[u] = base.repeat(-(-u // base.shape[0]), 1)[:u].to(dev) % P
            self.segs = list(self.segs) + [prover.Segment("link", circ, lay, cache[u], circ.hash)]

    prover.Instance = WithLink
    print(f"18_wrap: link segment {circ.ncols} columns, {circ.nwires} wires appended to every Instance", flush=True)
sys.argv = ["bench_result.py"] + sys.argv[1:]
runpy.run_path("bench_result.py", run_name="__main__")
