"""agkr-nvf4: microbenchmark of open_w_qc_eval's SIMT encode (6 rows per committed row, cosets only) and row_code_dot
at the fp4-nvf4 4096-VU shapes (rows 11672, k 4096); encoder variants must match the default output bit for bit.
python 15_enc.py"""
import time

import cupy as cp
import torch

from backends.direct.encode.encode_ntt_simt import RSEncoderSIMT
from gpu import kernels
from gpu.field import P

ROWS, K = 11672, 4096
N = 4 * K
dev = torch.device("cuda")
g = torch.Generator(device=dev).manual_seed(1)
at = torch.randint(0, P, (ROWS * 6, K), dtype=torch.int32, device=dev, generator=g)
code = torch.randint(0, P, (ROWS, N), dtype=torch.int32, device=dev, generator=g)


def bench(f, reps=10):
    f()
    torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        f()
        torch.cuda.synchronize()
        ts.append(time.perf_counter() - t)
    ts.sort()
    return ts[len(ts) // 2] * 1e3


ref = cp.empty((ROWS * 6, 3 * K), dtype=cp.int32)
base = RSEncoderSIMT(K, N)
base(cp.asarray(at).view(cp.uint32), ref.view(cp.uint32), write_systematic=False)
out = cp.empty_like(ref)
variants = {
    "default": {},
    "t512_r4_mb2": {"radix4": True, "min_blocks_per_sm": 2},
    "t256_r4_mb2": {"threads": 256, "radix4": True, "min_blocks_per_sm": 2},
    "t256_r4_mb3": {"threads": 256, "radix4": True, "min_blocks_per_sm": 3},
    "t256_r4_mb4": {"threads": 256, "radix4": True, "min_blocks_per_sm": 4},
    "t1024_r4": {"threads": 1024, "radix4": True},
    "t512_r4_mb2_b340": {"radix4": True, "min_blocks_per_sm": 2, "blocks": 340},
}
for name, kw in variants.items():
    try:
        enc = RSEncoderSIMT(K, N, **kw)
        ms = bench(lambda: enc(cp.asarray(at).view(cp.uint32), out.view(cp.uint32), write_systematic=False))
        same = bool((out == ref).all())
        print(f"enc {name}: {ms:.2f} ms same={same}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"enc {name}: error {type(e).__name__}: {e}", flush=True)

ev = torch.as_tensor(ref, device=dev)
r0 = kernels.row_code_dot(at, ev, code)
for split in (32, 64, 128, 256):
    ms = bench(lambda: kernels.row_code_dot(at, ev, code, split=split))
    print(f"row_code_dot split={split}: {ms:.2f} ms same={bool((kernels.row_code_dot(at, ev, code, split=split) == r0).all())}", flush=True)
