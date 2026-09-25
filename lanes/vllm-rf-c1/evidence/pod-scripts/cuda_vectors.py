"""vllm-v1 conformance vectors against vLLM's four CUDA SHA-256 copies, byte for byte.

Run from the shipped tree root (`research run --cwd source`) with /workspace/venv312/bin/python after pod_bootstrap.sh:

  A native_tree.cu              (native collector's GPU tree)     chunk leaves, node/lift levels
  B hidden_gpu_tree.cu          (CMT-2 hidden_gpu extension)      chunk leaves, node/lift levels
  C native_leafhash.cu          (device weights hashing)          position leaves, node/lift fold
  D fa2_tap_src/verity_tap.h    (FA2 H1 tap, VERITY_TAP=4)        in-kernel thread leaf (header + SHA-256 + store)

A is exercised twice: the production-built `verity_native_collect` .so (ctypes on its extern "C" launchers) and a standalone
nvcc build of the same file with the same CUDA flags.  B and C are the production JIT extensions (hidden_gpu.ext(), leafhash.ext()).
D is compiled into a one-thread harness kernel (one TU per src_mask, the macro VERITY_SHA_SRC) against the bootstrap's tap8 tree.

Every vector a copy's leaf kind or node rule covers is compared; vectors outside a copy's rule are listed with the reason.
Writes $RESEARCH_RUN_DIR/cuda_vectors.json; exit 1 on any mismatch in a covered vector.
"""
from __future__ import annotations

import ctypes
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

TREE = os.getcwd()
INT = os.path.join(TREE, "integrations", "vllm")
ACQ = os.path.join(INT, "verity_vllm", "acquire")
VEC_PATH = os.path.join(TREE, "packages", "verity", "src", "verity", "commitments", "vllm_v1", "vectors.json")
OUT = os.environ.get("RESEARCH_RUN_DIR") or "/tmp/c1-cuda"
WORK = os.path.join(OUT, "build")
os.makedirs(WORK, exist_ok=True)
sys.path.insert(0, INT)

import numpy as np  # noqa: E402
import torch  # noqa: E402

V = json.load(open(VEC_PATH))
H = bytes.fromhex
results: dict = {"vectors_sha256": hashlib.sha256(open(VEC_PATH, "rb").read()).hexdigest(), "copies": {}, "env": {}}
bad: list[str] = []


def sha_file(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rec(copy: str, kind: str, name: str, got: bytes | None, want: str, note: str = "") -> None:
    ok = got is not None and got.hex() == want
    results["copies"][copy]["checks"].append({"kind": kind, "vector": name, "want": want, "got": got.hex() if got is not None else None,
                                              "equal": ok, **({"note": note} if note else {})})
    if not ok:
        bad.append(f"{copy} {kind} {name}: want {want[:16]} got {(got.hex() if got is not None else None) and got.hex()[:16]}")


def skip(copy: str, kind: str, name: str, why: str) -> None:
    results["copies"][copy]["not_covered"].append({"kind": kind, "vector": name, "why": why})


def new_copy(copy: str, source: str, how: str) -> None:
    results["copies"][copy] = {"source": os.path.relpath(source, TREE), "source_sha256": sha_file(source), "how": how, "checks": [],
                               "not_covered": []}


def words_le(b: bytes) -> np.ndarray:
    return np.frombuffer(b, dtype="<u4").copy()


def dig_rows(ds: list[bytes]) -> np.ndarray:
    return np.frombuffer(b"".join(ds), dtype=np.uint32).reshape(-1, 8).copy()


def paths_from_levels(levels: list[list[bytes]], n: int) -> list[list[str | None]]:
    out = []
    for i in range(n):
        p, idx = [], i
        for lv in levels[:-1]:
            w = len(lv)
            if idx == w - 1 and w % 2 == 1:
                p.append(None)
            else:
                p.append(lv[idx ^ 1].hex())
            idx //= 2
        out.append(p)
    return out


results["env"] = {"torch": torch.__version__, "cuda": torch.version.cuda, "device": torch.cuda.get_device_name(0),
                  "capability": list(torch.cuda.get_device_capability(0)), "python": sys.version.split()[0]}
try:
    import vllm  # noqa: F401
    results["env"]["vllm"] = vllm.__version__
except Exception as e:  # noqa: BLE001
    results["env"]["vllm"] = repr(e)[:80]
nvcc = os.path.join(os.environ.get("CUDA_HOME", "/usr/local/cuda-12.9"), "bin", "nvcc")
if not os.path.exists(nvcc):
    nvcc = next((c for c in ("/usr/local/cuda-12.9/bin/nvcc", "/usr/local/cuda/bin/nvcc") if os.path.exists(c)), "nvcc")
results["env"]["nvcc"] = subprocess.run([nvcc, "--version"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
cc = torch.cuda.get_device_capability(0)
ARCH = f"sm_{cc[0]}{cc[1]}"


# ----------------------------------------------------------------------------------------------------------------- A: native_tree.cu
class NativeTree:
    """ctypes over the extern "C" launchers (device pointers from torch tensors, the default stream)."""

    def __init__(self, lib: ctypes.CDLL):
        self.base = lib.verity_chunk_leaves_launch_base
        self.base.restype = ctypes.c_int
        self.base.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                              ctypes.c_uint32, ctypes.c_uint32, ctypes.c_long, ctypes.c_void_p]
        self.whole = lib.verity_chunk_leaves_launch
        self.whole.restype = ctypes.c_int
        self.whole.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                               ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
        self.level = lib.verity_tree_level_launch
        self.level.restype = ctypes.c_int
        self.level.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long, ctypes.c_void_p]

    def chunk_leaves(self, stream_words: np.ndarray, cw: int, f: dict, ci_base: int | None) -> list[bytes]:
        s = torch.from_numpy(stream_words.view(np.int32)).cuda()
        n = stream_words.size // cw
        out = torch.zeros((n, 8), dtype=torch.int32, device="cuda")
        if ci_base is None:
            rc = self.whole(s.data_ptr(), out.data_ptr(), n, cw, f["launch_tag"], f["src_mask"], f["HB"], f["M"], f["NB"], None)
        else:
            rc = self.base(s.data_ptr(), out.data_ptr(), n, cw, f["launch_tag"], f["src_mask"], f["HB"], f["M"], f["NB"], ci_base, None)
        torch.cuda.synchronize()
        assert rc == 0, rc
        b = out.cpu().numpy().astype(np.uint32).tobytes()
        return [b[32 * i:32 * i + 32] for i in range(n)]

    def levels(self, leaves: list[bytes]) -> list[list[bytes]]:
        cur = torch.from_numpy(dig_rows(leaves).view(np.int32)).cuda()
        lv = [leaves]
        n = len(leaves)
        while n > 1:
            m = (n + 1) // 2
            nxt = torch.zeros((m, 8), dtype=torch.int32, device="cuda")
            rc = self.level(cur.data_ptr(), nxt.data_ptr(), n, None)
            torch.cuda.synchronize()
            assert rc == 0, rc
            b = nxt.cpu().numpy().astype(np.uint32).tobytes()
            lv.append([b[32 * i:32 * i + 32] for i in range(m)])
            cur, n = nxt, m
        return lv

    def one_level(self, ds: list[bytes]) -> list[bytes]:
        cur = torch.from_numpy(dig_rows(ds).view(np.int32)).cuda()
        m = (len(ds) + 1) // 2
        nxt = torch.zeros((m, 8), dtype=torch.int32, device="cuda")
        rc = self.level(cur.data_ptr(), nxt.data_ptr(), len(ds), None)
        torch.cuda.synchronize()
        assert rc == 0, rc
        b = nxt.cpu().numpy().astype(np.uint32).tobytes()
        return [b[32 * i:32 * i + 32] for i in range(m)]


def legacy(f: dict) -> bool:
    return f.get("BN", 0) == 0 and f.get("D", 0) == 0


def run_chunk_and_tree(copy: str, chunk_leaves, levels_fn, one_level_fn, with_base: bool) -> None:
    for i, c in enumerate(V["chunk_leaf"]):
        f, cw = c["fields"], c["fields"]["chunk_words"]
        name = f"chunk_leaf[{i}]"
        if not legacy(f):
            skip(copy, "chunk_leaf", name, f"header words 8/9 are hard-wired to 0 in this kernel; the vector's tile is (BN, D) = ({f['BN']}, {f['D']})")
            continue
        chunk = words_le(H(c["chunk"]))
        ci = f["chunk_index"]
        stream = np.concatenate([np.zeros(ci * cw, dtype=np.uint32), chunk]) if ci else chunk
        rec(copy, "chunk_leaf", name + " whole-step", chunk_leaves(stream, cw, f, None)[ci], c["leaf"], f"chunk at index {ci} of a {ci + 1}-chunk stream")
        if with_base:
            rec(copy, "chunk_leaf", name + " window", chunk_leaves(chunk, cw, f, ci)[0], c["leaf"], f"one-chunk window, ci_base {ci}")
    for t in V["trees"]:
        n = t["leaf_count"]
        name = f"trees[N={n}]"
        if n == 0:
            skip(copy, "tree", name, "no zero-leaf tree on the device; the empty root H(empty/v1) is computed on the host")
            continue
        lv = levels_fn([H(x) for x in t["leaves"]])
        rec(copy, "tree_root", name, lv[-1][0], t["root"])
        if lv is not None and len(lv) and isinstance(lv[0], list):
            got_paths = paths_from_levels(lv, n)
            ok = got_paths == t["paths"]
            results["copies"][copy]["checks"].append({"kind": "tree_paths", "vector": name, "equal": ok, "n_paths": n})
            if not ok:
                bad.append(f"{copy} tree_paths {name}")
    for i, hv in enumerate(V["hash"]):
        name = f"hash[{i}] {hv['tag']}"
        if hv["tag"] == "verity-vllm/node/v1":
            rec(copy, "node", name, one_level_fn([H(p) for p in hv["parts"]])[0], hv["digest"])
        elif hv["tag"] == "verity-vllm/lift/v1":
            rec(copy, "lift", name, one_level_fn([H(p) for p in hv["parts"]])[0], hv["digest"])
        else:
            skip(copy, "hash", name, "tag not computed by this copy")
    for i, r in enumerate(V["roots"]):
        inp, name = r["inputs"], f"roots[{i}] {r['kind']}"
        if r["kind"] == "run" and inp["step_roots"]:
            fr = levels_fn([H(x) for x in inp["step_roots"]])[-1][0]
            got = hashlib.sha256(b"verity/cmt-integ/run-root/v0" + H(inp["program_digest"]) + H(inp["geo_digest"])
                                 + len(inp["step_roots"]).to_bytes(8, "big") + fr).digest()
            rec(copy, "run_root_fold", name, got, r["root"], "device fold of the step roots; binding hashed on the host")
        elif r["kind"] == "weights":
            fr = levels_fn([H(x) for x in inp["tensor_roots"]])[-1][0]
            got = hashlib.sha256(b"verity/cmt-integ/weights-root/v0" + H(inp["geo_digest"]) + H(inp["names_digest"])
                                 + len(inp["tensor_roots"]).to_bytes(8, "big") + fr).digest()
            rec(copy, "weights_root_fold", name, got, r["root"], "device fold of the tensor roots; binding hashed on the host")
        else:
            skip(copy, "root", name, "root bindings are host code; only the fold under a run/weights root with >= 1 child is on the device")
    for k in ("pos_leaf", "thread_leaf", "id_leaf"):
        skip(copy, k, f"{k}[*]", "leaf rule not implemented by this copy")


def build_standalone_native_tree() -> str:
    src = os.path.join(ACQ, "native_tree.cu")
    so = os.path.join(WORK, "native_tree_standalone.so")
    cmd = [nvcc, "-O3", "--use_fast_math", f"-arch={ARCH}", "-Xcompiler", "-fPIC", "-shared", src, "-o", so]
    p = subprocess.run(cmd, capture_output=True, text=True)
    open(os.path.join(WORK, "native_tree_standalone.log"), "w").write(" ".join(cmd) + "\n" + p.stdout + p.stderr)
    if p.returncode != 0:
        raise RuntimeError(f"nvcc native_tree.cu failed: {p.stderr[-2000:]}")
    return so


t0 = time.time()
src_a = os.path.join(ACQ, "native_tree.cu")
try:
    from verity_vllm.acquire import native_collect as NC
    m = NC.ext()
    new_copy("A_native_tree.prod_so", src_a, f"production verity_native_collect extension {m.__file__} (ctypes on its extern C launchers)")
    results["copies"]["A_native_tree.prod_so"]["so"] = m.__file__
    results["copies"]["A_native_tree.prod_so"]["so_sha256"] = sha_file(m.__file__)
    nt = NativeTree(ctypes.CDLL(m.__file__))
    run_chunk_and_tree("A_native_tree.prod_so", nt.chunk_leaves, nt.levels, nt.one_level, True)
except Exception as e:  # noqa: BLE001
    results["copies"].setdefault("A_native_tree.prod_so", {"checks": [], "not_covered": []})["error"] = repr(e)[:600]
    bad.append(f"A_native_tree.prod_so error {e!r}"[:300])
try:
    so = build_standalone_native_tree()
    new_copy("A_native_tree.nvcc", src_a, f"nvcc -O3 --use_fast_math -arch={ARCH} -shared (the collector's CUDA_CFLAGS)")
    nt2 = NativeTree(ctypes.CDLL(so))
    run_chunk_and_tree("A_native_tree.nvcc", nt2.chunk_leaves, nt2.levels, nt2.one_level, True)
except Exception as e:  # noqa: BLE001
    results["copies"].setdefault("A_native_tree.nvcc", {"checks": [], "not_covered": []})["error"] = repr(e)[:600]
    bad.append(f"A_native_tree.nvcc error {e!r}"[:300])
results["timing_a_s"] = round(time.time() - t0, 1)

# ----------------------------------------------------------------------------------------------------------------- B: hidden_gpu_tree.cu
try:
    sys.path.insert(0, os.path.join(ACQ, "hidden_gpu_src"))
    import hidden_gpu as HG
    e = HG.ext()
    new_copy("B_hidden_gpu_tree", os.path.join(ACQ, "hidden_gpu_src", "hidden_gpu_tree.cu"), f"production hidden_gpu.ext() JIT extension {e.__file__}")
    results["copies"]["B_hidden_gpu_tree"]["so"] = e.__file__

    def b_chunks(stream_words, cw, f, ci_base):
        out = e.chunk_leaves(torch.from_numpy(stream_words.view(np.int32)).cuda(), cw, f["launch_tag"], f["src_mask"], f["HB"], f["M"], f["NB"])
        b = out.cpu().numpy().astype(np.uint32).tobytes()
        return [b[32 * i:32 * i + 32] for i in range(out.shape[0])]

    def b_levels(leaves):
        lv = e.tree_levels(torch.from_numpy(dig_rows(leaves).view(np.int32)).cuda())
        res = []
        for t in lv:
            b = t.cpu().numpy().astype(np.uint32).tobytes()
            res.append([b[32 * i:32 * i + 32] for i in range(t.shape[0])])
        return res

    def b_one_level(ds):
        if len(ds) == 1:
            # tree_level refuses n < 2: the lift of a lone child is level 1's odd tail of a 3-leaf tree [x, y, child]
            x = hashlib.sha256(b"x").digest()
            return [b_levels([x, x, ds[0]])[1][1]]
        t = e.tree_level(torch.from_numpy(dig_rows(ds).view(np.int32)).cuda())
        b = t.cpu().numpy().astype(np.uint32).tobytes()
        return [b[32 * i:32 * i + 32] for i in range(t.shape[0])]

    run_chunk_and_tree("B_hidden_gpu_tree", b_chunks, b_levels, b_one_level, False)
except Exception as ex:  # noqa: BLE001
    results["copies"].setdefault("B_hidden_gpu_tree", {"checks": [], "not_covered": []})["error"] = repr(ex)[:600]
    bad.append(f"B_hidden_gpu_tree error {ex!r}"[:300])

# ----------------------------------------------------------------------------------------------------------------- C: native_leafhash.cu
try:
    from verity_vllm.acquire import leafhash as LH
    le = LH.ext()
    C = "C_native_leafhash"
    new_copy(C, os.path.join(ACQ, "native_leafhash.cu"), f"production leafhash.ext() JIT extension {le.__file__}")
    results["copies"][C]["so"] = le.__file__

    def pos_leaves(buf: bytes, chunk: int) -> list[bytes]:
        t = torch.frombuffer(bytearray(buf), dtype=torch.uint8).cuda()
        o = le.pos_leaves(t, int(chunk)).cpu().numpy().tobytes()
        return [o[32 * i:32 * i + 32] for i in range(len(o) // 32)]

    def root(leaves: list[bytes]) -> bytes:
        t = torch.frombuffer(bytearray(b"".join(leaves)), dtype=torch.uint8).reshape(-1, 32).cuda()
        return le.tree_root(t).cpu().numpy().tobytes()

    rng = np.random.default_rng(20260925)
    for i, pv in enumerate(V["pos_leaf"]):
        v = H(pv["value"])
        name = f"pos_leaf[{i}] len={len(v)}"
        if not v:
            skip(C, "pos_leaf", name, "pos_leaves refuses an empty buffer (the host path skips numel()==0 tensors)")
            continue
        rec(C, "pos_leaf", name + " single", pos_leaves(v, len(v))[0], pv["leaf"], f"one leaf, chunk {len(v)}")
        for chunk in (256, 4096):
            if len(v) <= chunk:
                head = rng.integers(0, 256, size=chunk, dtype=np.uint8).tobytes()
                rec(C, "pos_leaf", name + f" tail@{chunk}", pos_leaves(head + v, chunk)[1], pv["leaf"], f"tail leaf after one {chunk}-byte leaf")
    for t in V["trees"]:
        n, name = t["leaf_count"], f"trees[N={t['leaf_count']}]"
        if n == 0:
            skip(C, "tree", name, "tree_root refuses zero leaves")
            continue
        rec(C, "tree_root", name, root([H(x) for x in t["leaves"]]), t["root"])
    for i, hv in enumerate(V["hash"]):
        name = f"hash[{i}] {hv['tag']}"
        if hv["tag"] == "verity-vllm/node/v1":
            rec(C, "node", name, root([H(p) for p in hv["parts"]]), hv["digest"])
        elif hv["tag"] == "verity-vllm/lift/v1":
            skip(C, "lift", name, "tree_root exposes only the root; lift is exercised inside every odd-width tree vector (N = 3, 5, 6, 7, 9, 17)")
        else:
            skip(C, "hash", name, "tag not computed by this copy")
    for i, r in enumerate(V["roots"]):
        inp, name = r["inputs"], f"roots[{i}] {r['kind']}"
        if r["kind"] == "weights":
            fr = root([H(x) for x in inp["tensor_roots"]])
            got = hashlib.sha256(b"verity/cmt-integ/weights-root/v0" + H(inp["geo_digest"]) + H(inp["names_digest"])
                                 + len(inp["tensor_roots"]).to_bytes(8, "big") + fr).digest()
            rec(C, "weights_root_fold", name, got, r["root"], "device fold of the tensor roots; binding hashed on the host")
        else:
            skip(C, "root", name, "not a weights root")
    for k in ("chunk_leaf", "thread_leaf", "id_leaf"):
        skip(C, k, f"{k}[*]", "leaf rule not implemented by this copy")
except Exception as ex:  # noqa: BLE001
    results["copies"].setdefault("C_native_leafhash", {"checks": [], "not_covered": []})["error"] = repr(ex)[:600]
    bad.append(f"C_native_leafhash error {ex!r}"[:300])

# ----------------------------------------------------------------------------------------------------------------- D: verity_tap.h (H1)
HARNESS = r'''
#include <cuda_runtime.h>
#include <cstdint>
#include <cute/tensor.hpp>
using namespace cute;   // FA2's kernel_traits.h does this at global scope before utils.h, which relies on it
#include "namespace_config.h"
namespace FLASH_NAMESPACE {
struct Verity_tap { void *acc_ptr; long acc_cap_words; float *diag_ptr; int mode; int H, M, N, NB; int tag; int BN, D; };
}
#define VERITY_TAP 4
#define VERITY_SHA_SRC @MASK@
#include "@TAP@"

using namespace FLASH_NAMESPACE;

__global__ void h1_leaf_kernel(const uint32_t *words, int n_words, int slab, int m_block, int n_block, int tidx, int seqlen_q, int seqlen_k,
                               int tag, int nbmax, int ok0, int ok1, uint32_t *acc, int NB, int *derived_ok) {
    Verity_tap vt{};
    vt.acc_ptr = acc; vt.NB = NB; vt.tag = tag;
    Verity_sha_ctx c(vt, 0, 1, slab, m_block, tidx, 4, seqlen_q, seqlen_k, nbmax);
    derived_ok[0] = (c.ok0 ? 1 : 0) | (c.ok1 ? 2 : 0);
    c.ok0 = ok0 != 0; c.ok1 = ok1 != 0;
    c.init();
    c.header(n_block);
    for (int b = 0; b < n_words / 16; ++b) {
        for (int i = 0; i < 16; ++i) c.m[i] = vsha_bswap(words[b * 16 + i]);
        c.compress_m();
    }
    c.finish_store(n_block);
}

extern "C" int h1_leaf(const uint32_t *words_h, int n_words, int slab, int m_block, int n_block, int tidx, int seqlen_q, int seqlen_k, int tag,
                       int nbmax, int ok0, int ok1, uint8_t *leaf_out, int *derived_ok_out) {
    const int NB = n_block + 1;
    const long idx = ((((long)slab * 1 + m_block) * NB + n_block) * 128 + tidx) * 8;
    const long cap = idx + 8;
    uint32_t *dw, *dacc; int *dok;
    cudaMalloc(&dw, sizeof(uint32_t) * (n_words > 0 ? n_words : 1));
    cudaMalloc(&dacc, sizeof(uint32_t) * cap);
    cudaMalloc(&dok, sizeof(int));
    cudaMemset(dacc, 0, sizeof(uint32_t) * cap);
    cudaMemcpy(dw, words_h, sizeof(uint32_t) * n_words, cudaMemcpyHostToDevice);
    h1_leaf_kernel<<<1, 1>>>(dw, n_words, slab, m_block, n_block, tidx, seqlen_q, seqlen_k, tag, nbmax, ok0, ok1, dacc, NB, dok);
    int rc = (int)cudaDeviceSynchronize();
    cudaMemcpy(leaf_out, dacc + idx, 32, cudaMemcpyDeviceToHost);
    cudaMemcpy(derived_ok_out, dok, sizeof(int), cudaMemcpyDeviceToHost);
    cudaFree(dw); cudaFree(dacc); cudaFree(dok);
    return rc;
}
'''
D = "D_fa2_tap_h1"
try:
    tap = os.path.join(ACQ, "fa2_tap_src", "verity_tap.h")
    new_copy(D, tap, "harness kernel: Verity_sha_ctx(init, header, compress_m over the vector words, finish_store) at VERITY_TAP=4")
    trees = sorted(glob.glob("/workspace/cp/fa2/trees/tap8/csrc")) or sorted(glob.glob("/workspace/cp/vllm-flash-attn/csrc"))
    if not trees:
        raise RuntimeError("no flash-attention csrc tree on this pod (pod_fa2_tap.sh not run)")
    csrc = trees[0]
    results["copies"][D]["fa_tree"] = csrc
    from torch.utils.cpp_extension import include_paths
    incs = [os.path.join(csrc, "flash_attn", "src"), os.path.join(csrc, "flash_attn"), os.path.join(csrc, "common"), os.path.join(csrc, "cutlass", "include")] + include_paths()
    libs = {}
    for tv in V["thread_leaf"]:
        mask = tv["fields"]["src_mask"]
        if mask in libs:
            continue
        cu = os.path.join(WORK, f"h1_harness_{mask}.cu")
        open(cu, "w").write(HARNESS.replace("@MASK@", str(mask)).replace("@TAP@", tap))
        so = os.path.join(WORK, f"h1_harness_{mask}.so")
        cmd = [nvcc, "-O3", "-DNDEBUG", "-std=c++17", "--expt-relaxed-constexpr", "--expt-extended-lambda", "--use_fast_math", f"-arch={ARCH}",
               "-Xcompiler", "-fPIC", "-shared", *[f"-I{i}" for i in incs], cu, "-o", so]
        p = subprocess.run(cmd, capture_output=True, text=True)
        open(cu + ".log", "w").write(" ".join(cmd) + "\n" + p.stdout + p.stderr)
        if p.returncode != 0:
            raise RuntimeError(f"nvcc h1 harness (mask {mask}) failed: {p.stderr[-3000:]}")
        lib = ctypes.CDLL(so)
        lib.h1_leaf.restype = ctypes.c_int
        libs[mask] = lib
    for i, tv in enumerate(V["thread_leaf"]):
        f = tv["fields"]
        w = words_le(H(tv["words"]))
        if w.size % 16:
            skip(D, "thread_leaf", f"thread_leaf[{i}]", "the kernel absorbs whole 16-word blocks only")
            continue
        leaf = (ctypes.c_uint8 * 32)()
        dok = (ctypes.c_int * 1)()
        wbuf = (ctypes.c_uint32 * w.size)(*[int(x) for x in w])
        rc = libs[f["src_mask"]].h1_leaf(wbuf, int(w.size), f["slab"], f["m_block"], f["n_block"], f["tidx"], f["seqlen_q"], f["seqlen_k"],
                                         ctypes.c_int(f["launch_tag"] - (1 << 32) if f["launch_tag"] >= (1 << 31) else f["launch_tag"]),
                                         f["n_block_max"], int(f["ok0"]), int(f["ok1"]), leaf, dok)
        want_ok = (1 if f["ok0"] else 0) | (2 if f["ok1"] else 0)
        note = f"rc {rc}; kernel-derived row validity {dok[0]} vs vector {want_ok}" + ("" if dok[0] == want_ok else " (vector sets it; the header encodes whatever the kernel holds)")
        rec(D, "thread_leaf", f"thread_leaf[{i}] src_mask={f['src_mask']} words={w.size}", bytes(leaf), tv["leaf"], note)
    for k in ("chunk_leaf", "pos_leaf", "id_leaf", "tree", "hash", "roots"):
        skip(D, k, f"{k}[*]", "the tap hashes thread leaves only; its tree is built by B / A on the host side of the launch")
except Exception as ex:  # noqa: BLE001
    results["copies"].setdefault(D, {"checks": [], "not_covered": []})["error"] = repr(ex)[:3000]
    bad.append(f"{D} error {ex!r}"[:300])

# ----------------------------------------------------------------------------------------------------------------- summary
summary = {}
for k, c in results["copies"].items():
    ch = c.get("checks", [])
    summary[k] = {"checks": len(ch), "equal": sum(1 for x in ch if x.get("equal")), "not_covered": len(c.get("not_covered", [])),
                  "error": c.get("error")}
results["summary"] = summary
results["mismatches"] = bad
json.dump(results, open(os.path.join(OUT, "cuda_vectors.json"), "w"), indent=1)
for k, s in summary.items():
    print(f"{k}: {s['equal']}/{s['checks']} equal, {s['not_covered']} not covered" + (f", ERROR {s['error'][:200]}" if s["error"] else ""))
print("MISMATCHES:", len(bad))
for b in bad:
    print("  ", b)
print("CUDA-VECTORS-" + ("OK" if not bad else "MISMATCH"))
sys.exit(0 if not bad else 1)
