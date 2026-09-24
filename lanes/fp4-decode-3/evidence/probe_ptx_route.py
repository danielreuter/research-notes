"""lane fp4-decode-3: NVRTC -> compute_89 PTX -> RawModule(path=...) (driver JIT) works on the 5090, and how long it takes for the hashed
fused witness kernel (/tmp/wit.cu from probe_nvrtc.sh)."""
import sys
import time

import cupy as cp
from cupy_backends.cuda.libs import nvrtc

print("nvrtc", nvrtc.getVersion(), "cc", cp.cuda.Device().compute_capability)


def ptx_of(src: str, arch: str) -> str:
    p = nvrtc.createProgram(src, "k.cu", (), ())
    try:
        nvrtc.compileProgram(p, ("-std=c++17", f"-arch=compute_{arch}"))
        return nvrtc.getPTX(p)
    finally:
        nvrtc.destroyProgram(p)


src = 'extern "C" __global__ void f(unsigned* x){ x[threadIdx.x] += 1; }'
ptx = ptx_of(src, "89")
print(type(ptx), len(ptx))
open("/tmp/t.ptx", "w" if isinstance(ptx, str) else "wb").write(ptx)
k = cp.RawModule(path="/tmp/t.ptx").get_function("f")
z = cp.zeros(8, dtype=cp.uint32)
k((1,), (8,), (z,))
print("tiny ptx route ok", int(z.sum()) == 8, type(k))
if len(sys.argv) > 1:
    t = time.perf_counter()
    ptx = ptx_of(open("/tmp/wit.cu").read(), "89")
    t1 = time.perf_counter()
    open("/tmp/wit_nvrtc89.ptx", "w" if isinstance(ptx, str) else "wb").write(ptx)
    k = cp.RawModule(path="/tmp/wit_nvrtc89.ptx").get_function("witness_program")
    print(f"witness kernel: nvrtc compute_89 {t1 - t:.1f}s, load+JIT sm_120 {time.perf_counter() - t1:.1f}s", flush=True)
