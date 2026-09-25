"""b-ligero-sha256: cProfile of the hashed prover's per-proof host cost (fp8-ada-x4+sha256, 2 VUs, l=256, the second of two proofs).
research run --on vy-b-ligero-sha256 --project verity --cwd /workspace/src --send 12-prof.py -- \
    bash -c 'source /workspace/env.sh; exec $PY -u "$RESEARCH_RUN_DIR/inputs/12-prof.py"'"""
import cProfile
import io
import os
import pstats
import time

os.environ.setdefault("LIGERO_GPU_STRICT", "1")
os.environ.setdefault("LIGERO_GRAPH_STRICT", "1")
from backends.direct.ligero.relations import relation  # noqa: E402
from backends.direct.ligero.relchain import HashedRelationRunner, instances  # noqa: E402

REL = os.environ.get("REL", "fp8-ada-x4")
rel = relation(REL)
t = time.perf_counter()
R = HashedRelationRunner(rel, "cuda", -128.0, zk=True, mode="interactive", leaf=os.environ.get("LEAF", "sha256"))
print(f"runner {time.perf_counter() - t:.1f}s")
data = instances(rel, 4)
R.commit_vus(data)
for i in range(2):
    t = time.perf_counter()
    R.prove_vus(data[:2], check=False, vu_ids=[0, 1])
    print(f"warm prove {i}: {time.perf_counter() - t:.2f}s")
pr = cProfile.Profile()
pr.enable()
t = time.perf_counter()
proof, pubs, lay = R.prove_vus(data[:2], check=False, vu_ids=[0, 1])
print(f"profiled prove: {time.perf_counter() - t:.2f}s timings {({k: round(v, 3) for k, v in proof.timings.items() if isinstance(v, float)})}")
t = time.perf_counter()
ok, why = R.verify_vus(proof, pubs, lay)
print(f"verify {time.perf_counter() - t:.2f}s {ok} {why}")
pr.disable()
s = io.StringIO()
pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(35)
print(s.getvalue())
s = io.StringIO()
pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(20)
print(s.getvalue())
