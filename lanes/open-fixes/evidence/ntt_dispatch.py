"""ntt_dispatch.py REL VUS: run from a tree root; prove one --zk interactive sub-batch of VUS VUs and count field.ntt calls by
path (ntt_cuda four-step vs the torch chain) and shape, so a byte-identity A/B is known to have exercised the CUDA NTT."""
import collections
import sys

import torch

from backends.direct.ligero import field
from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import RelationChainRunner, instances

rel_name, vus = sys.argv[1], int(sys.argv[2])
counts: collections.Counter = collections.Counter()
try:
    from backends.direct.ligero import ntt_cuda
    _orig = ntt_cuda.ntt

    def _counted(x, inverse=False):
        counts[("cuda4step", tuple(x.shape), inverse)] += 1
        return _orig(x, inverse)
    ntt_cuda.ntt = _counted
except ImportError:
    ntt_cuda = None
_dom_get = field.Domain.get.__func__ if hasattr(field.Domain.get, "__func__") else None


def _torch_counter(n, device):
    counts[("torch-chain", n)] += 1
    return _dom_get(field.Domain, n, device)


if _dom_get is not None:
    field.Domain.get = classmethod(lambda cls, n, device: _torch_counter(n, device))
R = RelationChainRunner(relation(rel_name), "cuda", -128.0, 2, n_proofs=1, zk=True, mode=protocol_mod.MODE_INTERACTIVE)
data = instances(relation(rel_name), 4096, procs=8, cache="/workspace/instances-cache")
lay = R.layout(vus)
# the first prove runs the Python of every stage once (eager or under graph capture); later ones replay the graphs unseen
R.prove_vus(data[:vus], check=False, min_l=lay.l, coins=protocol_mod.Coins.sample())
torch.cuda.synchronize()
print(f"{rel_name} l={lay.l} CUDA_NTT={getattr(field, 'CUDA_NTT', None)} ntt_cuda={'yes' if ntt_cuda else 'absent'}")
for k, v in sorted(counts.items(), key=str):
    print("  ", k, v)
print("NTT_DISPATCH cuda4step", sum(v for k, v in counts.items() if k[0] == "cuda4step"),
      "Domain.get (torch-chain NTTs and other domain users)", sum(v for k, v in counts.items() if k[0] == "torch-chain"))
