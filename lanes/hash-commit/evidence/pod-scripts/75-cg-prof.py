# commit-gpu: per-piece wall times of the GPU committer at the fp8-ada+blake3 shape (4096 x 1536 u8 rows x 2, 4096 y words)
import os, statistics as st, sys, time
sys.path.insert(0, "/workspace/src/backends/shared"); sys.path.insert(0, "/workspace/src")
import numpy as np, torch, cupy as cp
from hash_gpu import frame_v3 as fv3
from backends.direct.ligero import frame_gpu

N, NB, R = 4096, 1536, 30
sync = torch.cuda.synchronize


def t(name, fn, reps=R):
    fn(); sync()
    xs = []
    for _ in range(reps):
        t0 = time.perf_counter(); fn(); sync(); xs.append(time.perf_counter() - t0)
    print(f"{name:40s} med {st.median(xs)*1e3:8.3f} ms  min {min(xs)*1e3:8.3f}", flush=True)


rng = np.random.default_rng(0)
a = rng.integers(0, 256, (N, NB), dtype=np.uint8)
t("h2d pageable 6MiB", lambda: torch.from_numpy(a).to("cuda"))
t("h2d pageable 6MiB + widen", lambda: torch.from_numpy(a).to("cuda").to(torch.int64))
pin = torch.empty((N, NB), dtype=torch.uint8, pin_memory=True)
t("memcpy into pinned", lambda: pin.numpy().__setitem__(slice(None), a))
t("h2d pinned 6MiB", lambda: pin.to("cuda", non_blocking=True))
dev = torch.from_numpy(a).to("cuda")
t("widen to int64 on device", lambda: dev.to(torch.int64))
w = torch.from_numpy(rng.integers(0, 1 << 16, N, dtype=np.int64)).cuda()
with frame_gpu._torch_stream():
    t("blake3_keyed_rows", lambda: fv3.blake3_keyed_rows(cp.asarray(dev), b"k" * 32))
    cvs, roots = fv3.blake3_keyed_rows(cp.asarray(dev), b"k" * 32)
    lv = roots.view(cp.uint8).reshape(N, 32)
    did = b"d" * 32
    t("build_tree 4096 x 32B (cached heads)", lambda: fv3.build_tree(did, N, "blake3-keyed/row/v2", lv, vlen=32))
    t("build_tree 4096 x 32B (fresh heads)", lambda: (fv3._Head._cache.clear(), fv3.build_tree(did, N, "blake3-keyed/row/v2", lv, vlen=32)))
    t("build_tree 4096 u16 (cached heads)", lambda: fv3.build_tree(did, N, "u16", w.to(torch.int16), vmode=fv3.VALUE_U16))
    t("blake3_digests", lambda: frame_gpu.blake3_digests(cvs, 1))
    t("blake3_digests .get()", lambda: frame_gpu.blake3_digests(cvs, 1).get())
    t("_Head() one fresh", lambda: fv3._Head(os.urandom(90)))
    t("midstate() one", lambda: fv3.midstate(os.urandom(90)))
    k = cp.ElementwiseKernel("int32 x", "int32 y", "y = x", "noop")
    z = cp.zeros(1, dtype=cp.int32)
    t("cupy tiny kernel launch", lambda: k(z, z))
    t("cp.asarray small", lambda: cp.asarray(np.zeros(40, dtype=np.uint8)))
from backends.direct.ligero import hashauth
from backends.direct.ligero.leaf import registry
leaf = registry.get("blake3")
t("frame_gpu.row_tree (device rows)", lambda: frame_gpu.row_tree("a", b"\1" * 32, dev, word_bits=8, role=1, scheme=leaf))
t("frame_gpu.word_tree y u16", lambda: frame_gpu.word_tree("y", b"\2" * 32, w, nbytes=2, schema="u16"))
