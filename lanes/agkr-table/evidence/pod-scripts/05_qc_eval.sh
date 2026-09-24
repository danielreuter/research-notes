#!/usr/bin/env bash
# agkr-table: ligero.open_w_qc_eval (encode a's rows with the SIMT encoder + split-row row·code reduction + one INTT_n)
# against open_w_qc (the aᵀX INT8 GEMM route of v6) and, on the small case, open_w_qc_reference (v1: torch NTT
# encode-multiply-INTT): identical (w, qc) on random commitments; min-of-3 timings of both at the prover's full shape
# (26644 rows of k = 4096).
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - <<'EOF'
import time, torch
from gpu import ligero as L
from gpu.field import P, DEG

dev = torch.device("cuda")
g = torch.Generator(device=dev)
g.manual_seed(7)


def rnd(*shape):
    return torch.randint(0, P, shape, dtype=torch.int64, device=dev, generator=g)


def case(l, reps, with_ref):
    x = rnd(l)
    cm = L.commit(x, L.DEFAULT)
    a = rnd(l, L.DEG)
    r = rnd(cm.rows, L.DEG)
    fs = [("gemm", L.open_w_qc), ("eval", L.open_w_qc_eval)] + ([("ref", L.open_w_qc_reference)] if with_ref else [])
    out = {}
    for name, f in fs:
        f(cm, a, r)
        torch.cuda.synchronize()
        ts = []
        for _ in range(reps):
            t0 = time.perf_counter()
            w, qc = f(cm, a, r)
            torch.cuda.synchronize()
            ts.append(time.perf_counter() - t0)
        out[name] = (w, qc % P, min(ts))
    same = all(torch.equal(out["gemm"][0], out[n][0]) and torch.equal(out["gemm"][1], out[n][1]) for n, _ in fs)
    print(f"l={l} rows={cm.rows} same={same} " + " ".join(f"{n}={out[n][2]:.4f}s" for n, _ in fs), flush=True)
    return same


ok = case(4096 * 37 + 1234, 1, True)
ok &= case(4096 * 26644 - 777, 3, False)
print("OK" if ok else "MISMATCH", flush=True)
EOF
