"""Lane hp2-host step 1: where do the ~8 ms/sub-batch of tests_w go?  Times, on one bf16-hopper (or fp8-hopper) sub-batch's
actual challenge sizes: the SHAKE-256 squeeze (hashlib), the bytes -> BabyBear conversion + H2D (numpy vs device), the
_challenge2 loop, statement_digest (blake2b), and the per-phase host/GPU split of the prover (CUDA events around
the tests).  cwd = a source tree."""
import argparse, hashlib, os, sys, time, ctypes, ctypes.util
import numpy as np
import torch
from backends.direct.ligero import protocol as pm
from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import RelationChainRunner, instances
from backends.direct.ligero.chain import N_FAMILIES
from backends.direct.ligero.compile import P

ap = argparse.ArgumentParser()
ap.add_argument("--relation", default="bf16-hopper")
ap.add_argument("--zk", action="store_true")
ap.add_argument("--cache", default="/workspace/instances-cache")
args = ap.parse_args()
rel = relation(args.relation)
per_proof = 16384 // rel.steps
n_proofs = -(-4096 // per_proof)
R = RelationChainRunner(rel, "cuda", -128.0, 2, n_proofs=n_proofs, zk=args.zk, mode="interactive")
lay = R.layout(per_proof); cfg = R.cfg(lay.l)
m, l, D = R.sys.m, cfg.l, cfg.D
M = pm.n_rows(cfg, m, True)
count = D * (M + R.tb.L + R.tb.Q + N_FAMILIES * l)
print(f"{rel.name}: m={m} M={M} L={R.tb.L} Q={R.tb.Q} l={l} n={cfg.n} D={D} t={cfg.t}; challenge-1 symbols {count} = {4*count/1e6:.2f} MB")

def bench(fn, reps=7):
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter(); fn(); ts.append(time.perf_counter() - t0)
    ts.sort(); return ts[len(ts)//2] * 1e3

seed = hashlib.blake2b(b"seed", digest_size=32).digest()
raw = hashlib.shake_256(seed).digest(4 * count)
print(f"shake_256 squeeze {4*count/1e6:.2f} MB (hashlib):        {bench(lambda: hashlib.shake_256(seed).digest(4*count)):.2f} ms")
# libcrypto via ctypes (GIL released during the call)
lib = None
for name in ("libcrypto.so.3", "libcrypto.so", ctypes.util.find_library("crypto")):
    try:
        if name: lib = ctypes.CDLL(name); break
    except OSError: pass
if lib is not None:
    lib.EVP_MD_CTX_new.restype = ctypes.c_void_p
    lib.EVP_shake256.restype = ctypes.c_void_p
    lib.EVP_DigestInit_ex.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    lib.EVP_DigestUpdate.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
    lib.EVP_DigestFinalXOF.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
    lib.EVP_MD_CTX_free.argtypes = [ctypes.c_void_p]
    buf = np.empty(4 * count, dtype=np.uint8)
    def xof():
        ctx = lib.EVP_MD_CTX_new()
        lib.EVP_DigestInit_ex(ctx, lib.EVP_shake256(), None)
        lib.EVP_DigestUpdate(ctx, seed, len(seed))
        lib.EVP_DigestFinalXOF(ctx, buf.ctypes.data, buf.nbytes)
        lib.EVP_MD_CTX_free(ctx)
    xof()
    print(f"  libcrypto EVP_DigestFinalXOF (ctypes) same bytes: {bytes(buf) == raw};  {bench(xof):.2f} ms  [{name}]")
    pinned = torch.empty(4 * count, dtype=torch.uint8, pin_memory=True)
    pbuf = pinned.numpy()
    def xof_pinned():
        ctx = lib.EVP_MD_CTX_new(); lib.EVP_DigestInit_ex(ctx, lib.EVP_shake256(), None)
        lib.EVP_DigestUpdate(ctx, seed, len(seed)); lib.EVP_DigestFinalXOF(ctx, pbuf.ctypes.data, pbuf.nbytes); lib.EVP_MD_CTX_free(ctx)
    print(f"  ... into pinned memory: {bench(xof_pinned):.2f} ms")
    # in a thread while the main thread spins in Python (does the GIL get released?)
    import threading
    def spin(n=2_000_000):
        s = 0
        for i in range(n): s += i
        return s
    t_spin = bench(lambda: spin())
    def both():
        th = threading.Thread(target=xof_pinned); th.start(); spin(); th.join()
    print(f"  python spin alone {t_spin:.2f} ms; spin || ctypes-XOF in a thread: {bench(both):.2f} ms (overlap if ~max)")
    def both_hashlib():
        th = threading.Thread(target=lambda: hashlib.shake_256(seed).digest(4*count)); th.start(); spin(); th.join()
    print(f"  spin || hashlib.shake_256 in a thread: {bench(both_hashlib):.2f} ms")
else:
    print("  libcrypto not found")
print(f"numpy frombuffer.astype(int64) % P:               {bench(lambda: np.frombuffer(raw, dtype='<u4').astype(np.int64) % P):.2f} ms")
def dev_conv():
    u = torch.from_numpy(np.frombuffer(raw, dtype='<u4').view(np.int32).copy()).to('cuda')
    x = (u.to(torch.int64) & 0xFFFFFFFF) % P
    torch.cuda.synchronize(); return x
print(f"main's device conversion (copy + H2D pageable + mod): {bench(dev_conv):.2f} ms")
pin = torch.empty(count, dtype=torch.int32, pin_memory=True)
def dev_conv_pinned():
    pin.numpy().view(np.uint8)[:] = np.frombuffer(raw, dtype=np.uint8)
    u = pin.to('cuda', non_blocking=True)
    x = (u.to(torch.int64) & 0xFFFFFFFF) % P
    torch.cuda.synchronize(); return x
print(f"pinned H2D + device mod:                          {bench(dev_conv_pinned):.2f} ms")
print(f"_expand end to end (main):                        {bench(lambda: (pm._expand(seed, count, 'cuda'), torch.cuda.synchronize())):.2f} ms")
print(f"merkle.hash_bytes(seed1 preimage ~100 B):         {bench(lambda: pm.merkle.hash_bytes(b'x'*120)):.3f} ms")
print(f"_challenge2 (t={cfg.t}, n={cfg.n}):                 {bench(lambda: pm._challenge2(b'x'*32, b'r'*32, None, None, cfg.t, cfg.n, cc=(b'a'*32, b'b'*32), r2=b'c'*32)):.2f} ms")
data = instances(rel, 4096, cache=args.cache)
vus = data[:per_proof]
V = pm.Coins.sample()
proof, pubs, lay_i = R.prove_vus(vus, check=False, min_l=lay.l, coins=V)   # warm-up
a, b, ypub = pubs
print(f"statement_digest (blake2b over a,b,y16):          {bench(lambda: pm.statement_digest(R.sys, cfg, a, b, layout=lay_i, y16=ypub, rel=R.hooks)):.2f} ms")
print(f"  of which _u_bytes(a)+_u_bytes(b):               {bench(lambda: (pm._u_bytes(a, R.hooks.word_dtype), pm._u_bytes(b, R.hooks.word_dtype))):.2f} ms")
# marshalling: list-of-lists -> numpy, public_vectors, hints
import time as _t
t0 = _t.perf_counter(); units = []
for v, (aa, bb, accs, y) in enumerate(vus):
    from backends.direct.ligero.relchain import vu_units
    units += vu_units(rel, aa, bb, accs)
while len(units) < lay.l: units.append(R._pad_unit())
an = np.asarray([u[1] for u in units], dtype=np.int64); bn = np.asarray([u[2] for u in units], dtype=np.int64)
cn = np.asarray([u[0] for u in units], dtype=np.int64); yn = np.asarray([u[3] for u in units], dtype=np.int64)
print(f"host marshalling lists -> numpy (untimed by bench): {(_t.perf_counter()-t0)*1e3:.2f} ms")
def pv():
    pub = rel.public_vectors(R.p, None, an, bn, None, device="cuda"); torch.cuda.synchronize(); return pub
print(f"public_vectors (numpy in, {len(pv())} tensors out):     {bench(pv):.2f} ms")
def hints():
    h = rel.hints(R.p, R.sys, cn, an, bn, yn, "cuda"); torch.cuda.synchronize(); return h
print(f"hints (graph replay + uploads):                  {bench(hints):.2f} ms")
ad, bd, cd, yd = (torch.as_tensor(x, device="cuda") for x in (an, bn, cn, yn))
def pv_dev():
    pub = rel.public_vectors(R.p, None, ad, bd, None, device="cuda"); torch.cuda.synchronize(); return pub
print(f"public_vectors from device tensors:              {bench(pv_dev):.2f} ms")
def hints_dev():
    h = rel.hints(R.p, R.sys, cd, ad, bd, yd, "cuda"); torch.cuda.synchronize(); return h
print(f"hints from device tensors:                       {bench(hints_dev):.2f} ms")
# a sub-batch, un-profiled, phase laps
for _ in range(2):
    V = pm.Coins.sample(); proof, pubs, lay_i = R.prove_vus(vus, check=False, min_l=lay.l, coins=V)
print("prove_vus timings (ms):", {k: round(v * 1e3, 2) for k, v in proof.timings.items()})
print("proof bytes:", proof.n_bytes()["total"] / 1e6, "MB")
from backends.direct.ligero.serialize import proof_bytes
print(f"proof_bytes (Python struct writer):              {bench(lambda: proof_bytes(proof), 3):.2f} ms")
