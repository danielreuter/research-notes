"""Lane enc-hopper: standalone timing of the two GPU-bound prover phases at the prover's shapes.

    python microbench.py [--l 16384] [--rows 3328] [--tpad 256] [--reps 5] [--json out.json] [--no-merkle] [--only encode|merkle]
"""
import argparse, json, sys, time
import torch

from backends.direct.ligero import merkle as lmerkle
from backends.direct.ligero.encode_simt import LigeroEncoderSIMT
from backends.direct.ligero.field import P

ap = argparse.ArgumentParser()
ap.add_argument("--l", type=int, default=16384)
ap.add_argument("--rows", type=int, default=3328)
ap.add_argument("--tpad", type=int, default=256)
ap.add_argument("--reps", type=int, default=5)
ap.add_argument("--json", default=None)
ap.add_argument("--only", default=None)
ap.add_argument("--seed", type=int, default=1)
args = ap.parse_args()
dev = torch.device("cuda")
l, n, R = args.l, 4 * args.l, args.rows
g = torch.Generator().manual_seed(args.seed)
W = torch.randint(0, P, (R, l), generator=g, dtype=torch.int64).to(torch.int32).to(dev)
S = torch.randint(0, P, (R, args.tpad), generator=g, dtype=torch.int64).to(torch.int32).to(dev)


def timeit(fn, reps):
    fn(); torch.cuda.synchronize()
    ts = []
    for _ in range(reps):
        torch.cuda.synchronize(); t = time.perf_counter(); fn(); torch.cuda.synchronize(); ts.append(time.perf_counter() - t)
    ts.sort()
    return ts[len(ts) // 2]


res = {"l": l, "n": n, "rows": R, "codeword_GB": R * n * 4 / 1e9, "gpu": torch.cuda.get_device_name(0)}
U = torch.empty((R, n), dtype=torch.int32, device=dev)
if args.only in (None, "encode"):
    enc = LigeroEncoderSIMT(l, n, 0, dev)
    encz = LigeroEncoderSIMT(l, n, args.tpad, dev)
    t_plain = timeit(lambda: enc.encode(W, out=U), args.reps)
    t_zk = timeit(lambda: encz.encode(W, S, want_coefs=True, out=U), args.reps)
    res.update(encode_plain_ms=t_plain * 1e3, encode_zk_coefs_ms=t_zk * 1e3,
               encode_plain_GBps=res["codeword_GB"] / t_plain, encode_zk_GBps=res["codeword_GB"] / t_zk)
    print(f"encode plain {t_plain*1e3:.3f} ms ({res['encode_plain_GBps']:.0f} GB/s codeword) | zk+coefs {t_zk*1e3:.3f} ms", flush=True)
else:
    U.random_(0, P)
if args.only in (None, "merkle"):
    from hash_gpu import merkle as gm
    from hash_gpu import blake3_cuda as b3
    U32 = U.contiguous()
    t_commit = timeit(lambda: lmerkle.commit_device(U32), args.reps)
    t_leaves = timeit(lambda: gm.leaves(U32, "blake3"), args.reps)
    lv = gm.leaves(U32, "blake3")
    def tree():
        cur = lv
        while cur.shape[0] > 1:
            cur = gm.node_level(cur, "blake3")
        return cur
    t_tree = timeit(tree, args.reps)
    # chunk kernel alone (no parents over the chunk CVs)
    import cupy as cp
    m = cp.asarray(U32).view(cp.uint32)
    nchunks = (R + 255) // 256
    ws = cp.empty((nchunks, n, 8), dtype=cp.uint32)
    def chunks_only():
        b3.module().get_function("blake3_chunks")(((n + 127) // 128, nchunks), (128,),
            (m, __import__("numpy").int64(1), __import__("numpy").int64(256 * n), __import__("numpy").int64(n),
             __import__("numpy").int32(R), __import__("numpy").int32(n), __import__("numpy").int32(nchunks), ws))
    t_chunks = timeit(chunks_only, args.reps)
    res.update(merkle_commit_ms=t_commit * 1e3, merkle_leaves_ms=t_leaves * 1e3, merkle_tree_ms=t_tree * 1e3,
               blake3_chunks_ms=t_chunks * 1e3, merkle_GBps=res["codeword_GB"] / t_commit,
               compressions=n * (R // 16 + (1 if R % 16 else 0) + nchunks - 1), nchunks=nchunks)
    print(f"merkle commit {t_commit*1e3:.3f} ms ({res['merkle_GBps']:.0f} GB/s) | leaves {t_leaves*1e3:.3f} | chunks-kernel {t_chunks*1e3:.3f} | tree {t_tree*1e3:.3f}", flush=True)
if "encode_plain_ms" in res and "merkle_commit_ms" in res:
    res["encode_plus_merkle_ms"] = res["encode_zk_coefs_ms"] + res["merkle_commit_ms"]
    print(f"encode(zk)+merkle {res['encode_plus_merkle_ms']:.3f} ms per sub-batch; x25 = {25*res['encode_plus_merkle_ms']/1e3:.3f} s")
if args.json:
    json.dump(res, open(args.json, "w"), indent=1)
