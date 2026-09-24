"""share-logup-3: the pipelined pair's proofs verify (Python verifier), both INTERLEAVE_PAIR settings, and a tampered
fingerprint statement is rejected.  usage: check_pair.py [rel=fp8-ada] [mode=interactive|fiat-shamir] [depth=4]"""
import sys

import numpy as np

from backends.direct.ligero import protocol as protocol_mod
from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.relchain import SharedHashedRunner, instances_digest, tile_digest, tile_instances

relname = sys.argv[1] if len(sys.argv) > 1 else "fp8-ada"
mode = sys.argv[2] if len(sys.argv) > 2 else protocol_mod.MODE_INTERACTIVE
depth = int(sys.argv[3]) if len(sys.argv) > 3 else 4
rel = RELATIONS[relname]
batch, total = 16384, 4096
per = batch // rel.steps
n_proofs = -(-total // per)
R = SharedHashedRunner(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=False, mode=mode)
data, xr, wc = tile_instances(rel, 64, 64, cache="/workspace/instances-cache")
dig = tile_digest(rel, 64, 64) if rel.frozen_tier else instances_digest(rel, total)
R.commit_vus(data, manifest_sha256=dig, cache=f"/workspace/auth-cache-shared-{relname}-{mode}", tile=(64, 64), x_rows=xr, w_cols=wc)
subs = [(lo, min(lo + per, total)) for lo in range(0, total, per)]
l = R.layout(per).l
fac = (lambda i: protocol_mod.Coins.sample()) if R.interactive else (lambda i: None)
bad = 0
for inter in (True, False):
    relchain.INTERLEAVE_PAIR = inter
    many, wall = R.prove_vus_many([data[lo:hi] for lo, hi in subs], fac, depth=depth, min_l=l,
                                  vu_ids_list=[range(lo, hi) for lo, hi in subs])
    oks = []
    for coins, pf, pubs, lay in many:
        ok, why = R.verify_vus(pf, pubs, lay, coins=(coins, pf.h.coins) if R.interactive else None)
        oks.append(ok)
        if not ok:
            print("  REJECT", why)
    bad += len(oks) - sum(oks)
    print(f"interleave={inter}: {sum(oks)}/{len(oks)} accepted, wall {wall:.3f}", flush=True)
# a tampered F_G on the last pair: rejected
coins, pf, pubs, lay = many[-1]
pf.g.fp = pf.g.fp.copy()
pf.g.fp[0, 0, 0] = (int(pf.g.fp[0, 0, 0]) + 1) % protocol_mod.P
ok, why = R.verify_vus(pf, pubs, lay, coins=(coins, pf.h.coins) if R.interactive else None)
print("tampered F_G:", "ACCEPTED (BAD)" if ok else f"rejected ({why})")
bad += int(ok)
print("CHECK", "PASS" if bad == 0 else f"FAIL {bad}")
