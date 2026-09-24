#!/usr/bin/env bash
# agkr-table: gpu/fs_cuda.DeviceTranscript (the Fiat-Shamir sponge on the device) and the LogUp graphs that use it.
#  A. kernel vs gpu/transcript.Transcript: 300 random absorb (1/4/5 extension elements) + 1-2 challenge steps, eager and
#     replayed from a captured CUDA graph; same challenges, same final state / counter.
#  B. the exported 4096-VU instance proved with the host sponge (VERITY_GPU_HOST_FS=1, the per-round graphs) and with
#     the device sponge (one graph per level): identical proof bytes; min-of-3 prove / t_lookup for both.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
$PY - <<'EOF'
import gc, hashlib, os, random, time
from pathlib import Path

import numpy as np
import torch

from gpu.field import P
from gpu.fs_cuda import DeviceTranscript
from gpu.transcript import Transcript

dev = torch.device("cuda")
rng = random.Random(7)
tr = Transcript()
tr.absorb(b"warm")
dt = DeviceTranscript(dev)
dt.load(tr)
ok = True
o = torch.zeros((2, 6), dtype=torch.int32, device=dev)
for it in range(300):
    m = rng.choice([1, 4, 5])
    msg = [tuple(rng.randrange(P) for _ in range(6)) for _ in range(m)]
    nch = rng.choice([1, 2])
    dt.step(torch.tensor(msg, dtype=torch.int32, device=dev), o[0], o[1] if nch == 2 else None)
    tr.absorb_exts(msg)
    want = [tr.challenge() for _ in range(nch)]
    got = [tuple(int(v) for v in r) for r in o[:nch].cpu().tolist()]
    if got != want:
        ok = False
        print("MISMATCH at step", it, got, want, flush=True)
        break
t2 = Transcript()
t2.slots = 0
DeviceTranscript.store(t2, dt.buf.cpu().numpy(), 0)
ok &= t2.state == tr.state and t2.ctr == tr.ctr
print(f"A eager: {'ok' if ok else 'FAIL'} (ctr {tr.ctr})", flush=True)

# graph capture: three steps on static buffers, replayed twice from host-loaded states
msgs = torch.zeros((3, 4, 6), dtype=torch.int32, device=dev)
outs = torch.zeros((4, 6), dtype=torch.int32, device=dev)
side = torch.cuda.Stream()
side.wait_stream(torch.cuda.current_stream())
with torch.cuda.stream(side):
    dt.step(msgs[0], outs[0]); dt.step(msgs[1], outs[1], outs[2]); dt.step(msgs[2], outs[3])
torch.cuda.current_stream().wait_stream(side)
torch.cuda.synchronize()
g = torch.cuda.CUDAGraph()
with torch.cuda.graph(g):
    dt.step(msgs[0], outs[0]); dt.step(msgs[1], outs[1], outs[2]); dt.step(msgs[2], outs[3])
gok = True
for rep in range(2):
    ms = [[tuple(rng.randrange(P) for _ in range(6)) for _ in range(4)] for _ in range(3)]
    msgs.copy_(torch.tensor(ms, dtype=torch.int32))
    dt.load(tr)
    g.replay()
    want = []
    tr.absorb_exts(ms[0]); want.append(tr.challenge())
    tr.absorb_exts(ms[1]); want += [tr.challenge(), tr.challenge()]
    tr.absorb_exts(ms[2]); want.append(tr.challenge())
    got = [tuple(int(v) for v in r) for r in outs.cpu().tolist()]
    t3 = Transcript(); t3.slots = 0
    DeviceTranscript.store(t3, dt.buf.cpu().numpy(), 0)
    gok &= got == want and t3.state == tr.state and t3.ctr == tr.ctr
print(f"A graph: {'ok' if gok else 'FAIL'}", flush=True)
if not (ok and gok):
    raise SystemExit(1)

# B. end to end
from gpu import prover
from gpu.run import load_instance

inst = load_instance(Path("/workspace/agkr-table/bb/pos4096"), dev)
res = {}
for mode in ("host", "device"):
    if mode == "host":
        os.environ["VERITY_GPU_HOST_FS"] = "1"
    else:
        os.environ.pop("VERITY_GPU_HOST_FS", None)
    t = time.perf_counter()
    proof, st = prover.prove(inst, True)
    torch.cuda.synchronize()
    print(f"B {mode}: warm prove {time.perf_counter() - t:.1f}s", flush=True)
    gc.collect()
    tt, tl = [], []
    for _ in range(3):
        torch.cuda.synchronize()
        t = time.perf_counter()
        proof, st = prover.prove(inst, True)
        torch.cuda.synchronize()
        tt.append(time.perf_counter() - t)
        tl.append(st.t_lookup)
    b = proof.to_bytes()
    res[mode] = hashlib.sha256(b).hexdigest()
    print(f"B {mode}: prove min {min(tt):.3f}s  t_lookup min {min(tl):.3f}s  proof {len(b)} B sha256 {res[mode][:16]}", flush=True)
    del proof, st
print("B:", "IDENTICAL proofs" if res["host"] == res["device"] else "PROOFS DIFFER", flush=True)
EOF
