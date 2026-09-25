"""agkr-bound: tools/link_stub.py's circuit (the A-GKR side of the survey's bit link) through the CUDA prover as a
single-segment instance, tiled to B units; 1 warm-up + reps timed proofs, each verified.  cwd backends/gkr.
    python 15_link_gpu.py DIR B [REPS]
"""
import json
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, ".")
from gpu import prover                                  # noqa: E402
from gpu.bb_export import read_rows                     # noqa: E402
from gpu.circuit import layers, load_circuit            # noqa: E402
from gpu.field import P                                 # noqa: E402
from gpu.gkr import VerifyError                         # noqa: E402

d, B = Path(sys.argv[1]), int(sys.argv[2])
reps = int(sys.argv[3]) if len(sys.argv) > 3 else 2
dev = torch.device("cuda")
circ = load_circuit(d / "circuit.txt")
rows = read_rows(d / "witness.bin").astype("int64")
t = torch.from_numpy(rows).repeat(-(-B // rows.shape[0]), 1)[:B].to(dev) % P
inst = prover.Instance([prover.Segment("unit", circ, layers(circ), t, circ.hash)], None)
for rep in range(-1, reps):
    torch.cuda.synchronize(dev)
    t0 = time.perf_counter()
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize(dev)
    tp = time.perf_counter() - t0
    t1 = time.perf_counter()
    err = None
    try:
        prover.verify(inst, proof, True)
    except VerifyError as e:
        err = str(e)
    tv = time.perf_counter() - t1
    print(json.dumps({"rep": rep, "warmup": rep < 0, "units": B, "ncols": circ.ncols, "nwires": circ.nwires, "prover_s": round(tp, 4),
                      "python_verifier_s": round(tv, 3), "verified": err is None, "error": err, "proof_bytes": proof.nbytes(),
                      "t_commit": st.t_commit, "t_arith": st.t_arith, "t_open": st.t_open, "t_witness_wires": st.t_witness_wires,
                      "committed_elements": st.committed_elements, "ligero_rows": st.ligero_rows,
                      "sequential_depth": st.sequential_depth(True), "peak_mem_bytes": st.peak_mem}), flush=True)
