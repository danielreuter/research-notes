"""fused-phases: does a ``--tile 64x64`` bench-vu result (the committed column, ``--auth included-hash-shared``) prove the set its
``instances`` ref names?  The ref (relchain.instances_ref with tile) vs the frozen ref, and the canonical x / W / y digests of the
VUs it proves (relchain.tile_instances) vs the frozen set's (relchain.instances), per registered v1 relation."""
import os

from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS
from verity_numerical.bench.instance_equiv import _sha, arrays, same_ref
from verity_numerical.bench.tables import FROZEN_INSTANCES

procs = int(os.environ.get("VY_CPU_THREADS", "8"))
for name in ("fp8-ada", "bf16-hopper", "fp8-hopper", "bf16-ampere"):
    rel = RELATIONS[name]
    want = FROZEN_INSTANCES[rel.target.name]
    ref = relchain.instances_ref(rel, 4096, tile=(64, 64))
    tile_vus, _, _ = relchain.tile_instances(rel, 64, 64, procs=procs)
    t = arrays(tile_vus, rel.word_dtype)
    try:
        f = arrays(relchain.instances(rel, 4096, procs=procs), rel.word_dtype)
        same = {k: _sha(t[k]) == _sha(f[k]) for k in ("x", "W", "y")}
    except FileNotFoundError as e:
        same = f"frozen set not built: {e}"
    print(f"{name}: tile64x64 ref {'== FROZEN ref' if same_ref(ref, want) else '!= frozen ref'} "
          f"(tier {ref['tier']}, manifest {ref['manifest_sha256'][:12]}); numbers equal to the frozen set: {same}")
