"""Lane enc-hopper: static attribution without performance counters (ERR_NVGPUCTRPERM in the container):
registers / spills / smem of the cupy kernels, SASS opcode histogram (nvcc -cubin -arch=sm_90 + cuobjdump), occupancy.
"""
import collections, os, re, subprocess, sys, tempfile
import cupy as cp
import numpy as np
import torch

from backends.direct.ligero import encode_simt
from hash_gpu import blake3_cuda as b3

sm = cp.cuda.runtime.getDeviceProperties(0)
print("device", sm["name"].decode() if isinstance(sm["name"], bytes) else sm["name"], "SMs", sm["multiProcessorCount"],
      "smem/SM", sm["sharedMemPerMultiprocessor"], "regs/SM", sm["regsPerMultiprocessor"], "clock kHz", sm["clockRate"],
      "memclock kHz", sm["memoryClockRate"], "bus bits", sm["memoryBusWidth"], "L2", sm["l2CacheSize"])


def attrs(k, name):
    print(f"[{name}] regs={k.num_regs} local(spill)={k.local_size_bytes}B smem_static={k.shared_size_bytes}B "
          f"max_threads={k.max_threads_per_block} max_dyn_smem={k.max_dynamic_shared_size_bytes}")


def sass_hist(src: str, name: str, defines: dict | None = None):
    with tempfile.TemporaryDirectory() as d:
        cu = os.path.join(d, "k.cu"); cubin = os.path.join(d, "k.cubin")
        open(cu, "w").write(src)
        cmd = ["nvcc", "-cubin", "-arch=sm_90", "-std=c++17", "-O3", "-Xptxas", "-v", "-o", cubin, cu]
        r = subprocess.run(cmd, capture_output=True, text=True)
        for line in r.stderr.splitlines():
            if "registers" in line or "spill" in line or "Function properties" in line or "error" in line.lower():
                print("   ptxas:", line.strip())
        if r.returncode != 0:
            print(r.stderr[-2000:]); return
        sass = subprocess.run(["cuobjdump", "-sass", cubin], capture_output=True, text=True).stdout
    funcs = re.split(r"\n\s*Function : ", sass)
    for f in funcs[1:]:
        fname = f.split("\n", 1)[0].strip()
        ops = re.findall(r"/\*[0-9a-f]{4}\*/\s+(?:@!?U?P\d\s+)?([A-Z0-9_.]+)", f)
        h = collections.Counter(o.split(".")[0] for o in ops)
        full = collections.Counter(ops)
        print(f"   SASS {fname[:60]}: {len(ops)} static instrs;", ", ".join(f"{k}={v}" for k, v in h.most_common(18)))
        print("      top full opcodes:", ", ".join(f"{k}={v}" for k, v in full.most_common(14)))


l = int(sys.argv[1]) if len(sys.argv) > 1 else 16384
enc = encode_simt.LigeroEncoderSIMT(l, 4 * l, 256, "cuda")
attrs(enc.kernel, f"rs_encode_ligero l={l} threads={enc.threads} dyn_smem={enc.smem}")
occ = cp.cuda.runtime.getDeviceProperties(0)["regsPerMultiprocessor"] // (enc.kernel.num_regs * enc.threads) if enc.kernel.num_regs else 0
print(f"   blocks/SM by registers: {occ}; by smem: {sm['sharedMemPerMultiprocessor'] // (enc.smem + 1024)}; by threads: {2048 // enc.threads}")
params = {"pinv": encode_simt._P_INV_MOD_R, "k": l, "logk": l.bit_length() - 1, "threads": enc.threads,
          "logt": enc.threads.bit_length() - 1, "tp": 256, "kinv_mont": 1}
sass_hist(encode_simt._SRC % params, "rs_encode_ligero")
mod = b3.module()
for kn in ("blake3_chunks", "blake3_parents"):
    attrs(mod.get_function(kn), kn)
sass_hist(b3.SRC, "blake3")
