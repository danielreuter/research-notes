"""red-team-hm96 (PR #93): independent recomputation of the three SHA-512 vector files from the spec text alone, plus math-level
negatives.  hashlib + numpy only; imports nothing from verity.  Usage:
    python recompute_sha512.py <packages/verity/src/verity/commitments>
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import sys

import numpy as np

FAIL: list[str] = []
N = 0


def check(cond: bool, what: str) -> None:
    global N
    N += 1
    if not cond:
        FAIL.append(what)
        print("FAIL", what, flush=True)


S2 = lambda b: hashlib.sha256(b).digest()  # noqa: E731
S5 = lambda b: hashlib.sha512(b).digest()  # noqa: E731
u32be = lambda n: n.to_bytes(4, "big")  # noqa: E731
u64be = lambda n: n.to_bytes(8, "big")  # noqa: E731
hx = bytes.fromhex


def tagged_sha256(tag: str, payload: bytes) -> bytes:
    t = tag.encode()
    return S2(b"veritor/tagged-sha256/v1\0" + u32be(len(t)) + t + u64be(len(payload)) + payload)


def cjson(doc) -> bytes:
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def expand(label: str, n: int) -> bytes:
    out, c = bytearray(), 0
    while len(out) < n:
        out += S2(label.encode() + u32be(c))
        c += 1
    return bytes(out[:n])


# ============================== hm96-sha512/v1 (hm96/PROTOCOL.md sections 1-3, SHA-512 column) ============================
NB, LB = 512, 1536                       # n, l bits
KEYBITS = NB + LB - 1                    # 2047
KEYBYTES = 256
SALT_PREFIX = b"verity/hm96-sha512/salt/v1\0".ljust(128, b"\0")
LEAF_TAG = b"verity/hm96-sha512/leaf/v1\0"
KEY_LABEL = b"verity/hm96-sha512/key/v1\0"


def key_from_label(label: bytes) -> bytes:
    raw = bytearray(b"".join(S5(label + u32be(i)) for i in range(4)))
    raw[255] &= 0x7F
    return bytes(raw)


def bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="little")


def matrix(key: bytes) -> np.ndarray:
    k = bits(key)
    return k[np.arange(NB)[:, None] + np.arange(LB)[None, :]]


def mask(key: bytes, y: bytes) -> bytes:
    out = (matrix(key).astype(np.int64) @ bits(y).astype(np.int64)) & 1
    return np.packbits(out.astype(np.uint8), bitorder="little").tobytes()


def mask_loops(key: bytes, y: bytes) -> bytes:
    kb = [(key[t >> 3] >> (t & 7)) & 1 for t in range(8 * KEYBYTES)]
    yb = [(y[t >> 3] >> (t & 7)) & 1 for t in range(LB)]
    out = bytearray(64)
    for i in range(NB):
        acc = 0
        for j in range(LB):
            acc ^= kb[i + j] & yb[j]
        out[i >> 3] |= acc << (i & 7)
    return bytes(out)


def leaf_prefix(key: bytes) -> bytes:
    return (LEAF_TAG + S5(key)).ljust(128, b"\0")


def commit(key: bytes, x: bytes, y: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(x, mask(key, y))) + S5(SALT_PREFIX + y)


def tree_leaf(key: bytes, bc: bytes) -> bytes:
    return S5(leaf_prefix(key) + bc)


def scheme_digest(key: bytes) -> bytes:
    tag = b"verity/hm96-sha512/scheme/v1"
    doc = cjson({"name": "hm96-sha512/v1", "salt_bytes": 192, "key_sha512": S5(key).hex()})
    return S5(u32be(len(tag)) + tag + u64be(len(doc)) + doc)


def pos_prefix(n: int) -> bytes:
    return b"verity/pos-leaf/v0" + u64be(n)


def sha512_row_prefix(role: int, word_bits: int, n_words: int) -> bytes:
    return (b"verity/sha512-row/v1\0" + bytes([role, word_bits]) + u32be(n_words)).ljust(128, b"\0")


# vllm-v1 section 1 base hash H(tag, parts) through SHA-512; node / lift / empty
def Hv(tag: str, *parts: bytes) -> bytes:
    t = tag.encode()
    return S5(u32be(len(t)) + t + b"".join(u64be(len(p)) + p for p in parts))


node = lambda a, b: Hv("verity-vllm/node/v1", a, b)  # noqa: E731
lift = lambda a: Hv("verity-vllm/lift/v1", a)  # noqa: E731


def fold(leaves: list[bytes]) -> bytes:
    if not leaves:
        return Hv("verity-vllm/empty/v1")
    lv = list(leaves)
    while len(lv) > 1:
        nxt = [node(lv[i], lv[i + 1]) for i in range(0, len(lv) - 1, 2)]
        if len(lv) % 2:
            nxt.append(lift(lv[-1]))
        lv = nxt
    return lv[0]


def shape(n: int, i: int) -> list[bool]:
    out, w = [], n
    while w > 1:
        out.append(i != w - 1 or w % 2 == 0)
        w, i = -(-w // 2), i // 2
    return out


def fold_path(d: bytes, i: int, path: list) -> bytes:
    for s in path:
        d = lift(d) if s is None else (node(d, s) if i % 2 == 0 else node(s, d))
        i //= 2
    return d


def verify_path(root: bytes, n: int, i: int, leaf: bytes, path: list, bind=lambda r: r) -> bool:
    sh = shape(n, i)
    if len(path) != len(sh) or any((p is None) == has for p, has in zip(path, sh)):
        return False
    if len(leaf) != 64 or any(p is not None and len(p) != 64 for p in path):
        return False
    return bind(fold_path(leaf, i, path)) == root


def step_root(program, ctx, geo, layout, n, tree_root) -> bytes:
    return S5(b"verity/fa2c/root/v0" + program + ctx + geo + layout + u64be(n) + tree_root)


def gf2_rank(vs: list[int]) -> int:
    basis: dict[int, int] = {}
    for v in vs:
        while v:
            t = v.bit_length() - 1
            if t not in basis:
                basis[t] = v
                break
            v ^= basis[t]
    return len(basis)


# ---- pure-Python SHA-512 (length extension) ----------------------------------------------------------------------------
_K5 = [int(x, 16) for x in """
428a2f98d728ae22 7137449123ef65cd b5c0fbcfec4d3b2f e9b5dba58189dbbc 3956c25bf348b538 59f111f1b605d019 923f82a4af194f9b ab1c5ed5da6d8118
d807aa98a3030242 12835b0145706fbe 243185be4ee4b28c 550c7dc3d5ffb4e2 72be5d74f27b896f 80deb1fe3b1696b1 9bdc06a725c71235 c19bf174cf692694
e49b69c19ef14ad2 efbe4786384f25e3 0fc19dc68b8cd5b5 240ca1cc77ac9c65 2de92c6f592b0275 4a7484aa6ea6e483 5cb0a9dcbd41fbd4 76f988da831153b5
983e5152ee66dfab a831c66d2db43210 b00327c898fb213f bf597fc7beef0ee4 c6e00bf33da88fc2 d5a79147930aa725 06ca6351e003826f 142929670a0e6e70
27b70a8546d22ffc 2e1b21385c26c926 4d2c6dfc5ac42aed 53380d139d95b3df 650a73548baf63de 766a0abb3c77b2a8 81c2c92e47edaee6 92722c851482353b
a2bfe8a14cf10364 a81a664bbc423001 c24b8b70d0f89791 c76c51a30654be30 d192e819d6ef5218 d69906245565a910 f40e35855771202a 106aa07032bbd1b8
19a4c116b8d2d0c8 1e376c085141ab53 2748774cdf8eeb99 34b0bcb5e19b48a8 391c0cb3c5c95a63 4ed8aa4ae3418acb 5b9cca4f7763e373 682e6ff3d6b2b8a3
748f82ee5defb2fc 78a5636f43172f60 84c87814a1f0ab72 8cc702081a6439ec 90befffa23631e28 a4506cebde82bde9 bef9a3f7b2c67915 c67178f2e372532b
ca273eceea26619c d186b8c721c0c207 eada7dd6cde0eb1e f57d4f7fee6ed178 06f067aa72176fba 0a637dc5a2c898a6 113f9804bef90dae 1b710b35131c471b
28db77f523047d84 32caab7b40c72493 3c9ebe0a15c9bebc 431d67c49c100d4c 4cc5d4becb3e42b6 597f299cfc657e2a 5fcb6fab3ad6faec 6c44198c4a475817
""".split()]
_M64 = (1 << 64) - 1


def _r(x: int, n: int) -> int:
    return ((x >> n) | (x << (64 - n))) & _M64


def compress512(st: list[int], block: bytes) -> list[int]:
    w = list(struct.unpack(">16Q", block))
    for t in range(16, 80):
        s0 = _r(w[t - 15], 1) ^ _r(w[t - 15], 8) ^ (w[t - 15] >> 7)
        s1 = _r(w[t - 2], 19) ^ _r(w[t - 2], 61) ^ (w[t - 2] >> 6)
        w.append((w[t - 16] + s0 + w[t - 7] + s1) & _M64)
    a, b, c, d, e, f, g, h = st
    for t in range(80):
        t1 = (h + (_r(e, 14) ^ _r(e, 18) ^ _r(e, 41)) + ((e & f) ^ (~e & g)) + _K5[t] + w[t]) & _M64
        t2 = ((_r(a, 28) ^ _r(a, 34) ^ _r(a, 39)) + ((a & b) ^ (a & c) ^ (b & c))) & _M64
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & _M64, c, b, a, (t1 + t2) & _M64
    return [(x + y) & _M64 for x, y in zip(st, [a, b, c, d, e, f, g, h])]


def pad512(nbytes: int) -> bytes:
    return b"\x80" + b"\0" * ((111 - nbytes) % 128) + (8 * nbytes).to_bytes(16, "big")


_IV5 = [0x6A09E667F3BCC908, 0xBB67AE8584CAA73B, 0x3C6EF372FE94F82B, 0xA54FF53A5F1D36F1,
        0x510E527FADE682D1, 0x9B05688C2B3E6C1F, 0x1F83D9ABFB41BD6B, 0x5BE0CD19137E2179]


def sha512_py(m: bytes) -> bytes:
    st, mm = list(_IV5), m + pad512(len(m))
    for o in range(0, len(mm), 128):
        st = compress512(st, mm[o:o + 128])
    return struct.pack(">8Q", *st)


def extend512(digest: bytes, orig_len: int, suffix: bytes) -> bytes:
    st = list(struct.unpack(">8Q", digest))
    total = orig_len + len(pad512(orig_len)) + len(suffix)
    m = suffix + pad512(total)
    for o in range(0, len(m), 128):
        st = compress512(st, m[o:o + 128])
    return struct.pack(">8Q", *st)


def hm96(V: dict) -> None:
    K = key_from_label(KEY_LABEL)
    other = hx(V["other_key"])
    check(V["scheme"] == "hm96-sha512/v1" and V["key_label"] == KEY_LABEL.hex(), "hm96: scheme name and key label")
    check(V["default_key"] == K.hex(), "hm96: pinned key = SHA-512(label || u32be i), i < 4, bit 2047 cleared")
    check(len(K) == 256 and K[255] >> 7 == 0 and len(other) == 256 and other[255] >> 7 == 0, "hm96: 256-byte keys, bit 2047 zero")
    check(V["salt_prefix"] == SALT_PREFIX.hex() and V["leaf_prefix_default_key"] == leaf_prefix(K).hex(), "hm96: prefixes")
    check(V["scheme_digest_default_key"] == scheme_digest(K).hex(), "hm96: scheme digest (SHA-512 frame over canonical JSON)")
    M = matrix(K)
    w = [int(r.sum()) for r in M]
    check(V["default_key_row_weights"] == w and V["default_key_xor_gates"] == sum(w), f"hm96: row weights, xor gates {sum(w)}")
    ri = [int.from_bytes(np.packbits(r.astype(np.uint8), bitorder="little").tobytes(), "little") for r in M]
    rk = gf2_rank(ri)
    ro = gf2_rank([int.from_bytes(np.packbits(r.astype(np.uint8), bitorder="little").tobytes(), "little") for r in matrix(other)])
    check(rk == 512 and ro == 512, f"hm96: rank M(pinned) {rk}, M(other) {ro}")
    ds = [1, 1 << (LB - 1), (1 << LB) - 1, int.from_bytes(os.urandom(192), "little") | 1, (1 << (LB - 1)) | (1 << 1024)]
    check(all(gf2_rank([d << i for i in range(NB)]) == 512 for d in ds), "hm96: universal family, rank 512 for adversarial d")
    for c in V["masks"]:
        key = K if c["key"] == "default" else other
        y = hx(c["salt"])
        check(len(y) == 192 and mask(key, y).hex() == c["mask"], f"hm96: mask {c['key']}/{c['salt_case']}")
        check(S5(SALT_PREFIX + y).hex() == c["salt_digest"] == sha512_py(SALT_PREFIX + y).hex(), f"hm96: salt digest {c['salt_case']}")
    for c in V["masks"][:2] + V["masks"][4:5]:
        key = K if c["key"] == "default" else other
        check(mask_loops(key, hx(c["salt"])).hex() == c["mask"], f"hm96: mask by bit loops {c['key']}/{c['salt_case']}")
    for c in V["leaves"]:
        v, y, pre, suf = hx(c["value"]), hx(c["salt"]), hx(c["inner_prefix"]), hx(c["inner_suffix"])
        if c["inner"] == "pos-leaf":
            check(pre == pos_prefix(len(v)) and suf == b"", f"hm96: pos-leaf prefix n={len(v)}")
        else:
            check(len(pre) == 128 and pre[:21] == b"verity/sha512-row/v1\0" and pre[22] in (8, 16) and pre[23:27] == u32be(8 * len(v) // pre[22])
                  and pre[27:] == bytes(101), f"hm96: sha512/row/v1 prefix n={len(v)}")
        x = S5(pre + v + suf)
        check(x.hex() == c["inner_digest"], f"hm96: inner digest {c['inner']}/{len(v)}")
        bc = commit(K, x, y)
        check(bc[:64].hex() == c["b"] and bc[64:].hex() == c["c"] and tree_leaf(K, bc).hex() == c["leaf"], f"hm96: b, c, leaf {c['inner']}/{len(v)}")
    for t in V["trees"]:
        d = t["domain"]
        n = d["leaf_count"]
        check(d["hash"] == "sha512" and d["kind"] == "step", "hm96 tree: a vllm-v1-sha512 step domain")
        prog, ctx, geo, lay = (hx(d[k]) for k in ("program", "ctx", "geo", "layout"))
        check(all(len(z) == 32 for z in (prog, ctx, geo, lay)), "hm96 tree: identity inputs are 32 bytes")
        leaves = []
        for i in range(n):
            v, y = hx(t["values"][i]), hx(t["salts"][i])
            bc = commit(K, S5(pos_prefix(len(v)) + v), y)
            check(bc.hex() == t["proven"][i], f"hm96 tree n={n}: proven {i}")
            leaves.append(tree_leaf(K, bc))
        check([z.hex() for z in leaves] == t["leaves"], f"hm96 tree n={n}: leaves")
        tr = fold(leaves)
        check(step_root(prog, ctx, geo, lay, n, tr).hex() == t["root"], f"hm96 tree n={n}: bound step root (SHA-512)")
        for i in range(n):
            p = [None if s is None else hx(s) for s in t["paths"][i]]
            check(verify_path(tr, n, i, leaves[i], p), f"hm96 tree n={n}: path {i}")
    # ---- negatives
    rng = np.random.default_rng(512)
    v, y = rng.bytes(40), rng.bytes(192)
    x = S5(pos_prefix(40) + v)
    bc = commit(K, x, y)
    leaf = tree_leaf(K, bc)
    for t in (0, 7, 8, 767, 768, 1535):
        y2 = bytearray(y)
        y2[t >> 3] ^= 1 << (t & 7)
        check(tree_leaf(K, commit(K, x, bytes(y2))) != leaf, f"hm96 neg: salt bit {t}")
    # kernel shift: same b, rejected via c
    A = M.astype(np.uint8).copy()
    piv, r = [], 0
    for col in range(LB):
        p = next((k for k in range(r, NB) if A[k, col]), None)
        if p is None:
            continue
        A[[r, p]] = A[[p, r]]
        rows_ = np.nonzero(A[:, col])[0]
        for k in rows_:
            if k != r:
                A[k] ^= A[r]
        piv.append(col)
        r += 1
        if r == NB:
            break
    free = next(c for c in range(LB) if c not in set(piv))
    z = np.zeros(LB, dtype=np.uint8)
    z[free] = 1
    for k, pc in enumerate(piv):
        z[pc] = A[k, free]
    ker = np.packbits(z, bitorder="little").tobytes()
    yk = bytes(a ^ b for a, b in zip(y, ker))
    check(mask(K, ker) == bytes(64) and mask(K, yk) == mask(K, y), "hm96 neg: a kernel vector of M(pinned) keeps the mask")
    check(tree_leaf(K, commit(K, x, yk)) != leaf, "hm96 neg: kernel-shifted salt (same b) rejected via c")
    v2, y2 = rng.bytes(40), rng.bytes(192)
    check(tree_leaf(K, commit(K, S5(pos_prefix(40) + v2), y2)) != leaf, "hm96 neg: swapped leaf")
    check(tree_leaf(K, commit(K, x, y2)) != leaf, "hm96 neg: salt of another position")
    check(S5(pos_prefix(39) + v[:39]) != x, "hm96 neg: truncated value")
    ext = b"\xffext"
    msg = pos_prefix(40) + v
    xe = extend512(x, len(msg), ext)
    check(xe == S5(msg + pad512(len(msg)) + ext), "SHA-512 length extension works on raw SHA-512 (sanity)")
    ve = v + pad512(len(msg)) + ext
    check(S5(pos_prefix(len(ve)) + ve) != xe, "hm96 neg: length-extended inner digest is no pos-leaf of the extended value")
    check(len(y + pad512(128 + 192) + ext) != 192, "hm96 neg: length-extended salt is not 192 bytes")
    check(extend512(leaf, 256, ext) != leaf and len(bc + pad512(256) + ext) != 128, "hm96 neg: length-extended leaf needs a longer commit string")
    check(tree_leaf(other, bc) != leaf, "hm96 neg: other key")
    # witness-key equivocation (PROTOCOL section 5 now states the rule): n = 512 equations in 2047 unknowns
    xt = S5(b"another value")
    ti = int.from_bytes(bytes(a ^ b for a, b in zip(bc[:64], xt)), "little")
    yi = int.from_bytes(y, "little")
    pv: dict[int, tuple[int, int]] = {}
    for i in range(NB):
        row, rhs = yi << i, (ti >> i) & 1
        while row:
            top = row.bit_length() - 1
            if top not in pv:
                pv[top] = (row, rhs)
                break
            row, rhs = row ^ pv[top][0], rhs ^ pv[top][1]
    ks = 0
    for top in sorted(pv):
        row, rhs = pv[top]
        if (bin((row & ~(1 << top)) & ks).count("1") & 1) != rhs:
            ks |= 1 << top
    kf = ks.to_bytes(256, "little")
    check(ks < (1 << KEYBITS) and bytes(a ^ b for a, b in zip(xt, mask(kf, y))) == bc[:64], "hm96 neg: a witness key k' opens b to x' (why §5 forbids it)")
    check(tree_leaf(kf, bc) != leaf, "hm96 neg: the leaf's key digest defeats k' where the verifier recomputes the leaf")
    # cross-instance separation: SHA-256 instance strings and sizes
    check(LEAF_TAG[:19] == b"verity/hm96-sha512/" and b"verity/hm96-sha256/leaf/v1\0"[:19] != LEAF_TAG[:19], "hm96: leaf tags differ at byte 15")
    check(leaf_prefix(K)[:8] == b"verity/h" and len(leaf_prefix(K) + bc) == 256, "hm96: leaf preimage 256 bytes, starts 'verity/h'")
    D = scheme_digest(K)
    check(len(D) == 64 and b"/step=" not in D and b"/leaf=" not in D, "hm96: 64-byte scheme digest holds no '/step=' or '/leaf='")
    B = np.stack([np.frombuffer(commit(K, x, os.urandom(192))[:64], dtype=np.uint8) for _ in range(1500)])
    dev = float(np.abs(np.unpackbits(B, axis=1).mean(axis=0) - 0.5).max())
    check(dev < 0.07, f"hm96: b bits balanced over 1500 salts (max dev {dev:.3f})")
    # the bound, as instantiated: log2 SD = log2 N + (2n - l)/2 (+ t)
    check((2 * NB - LB) / 2 == -256 and 0.5 * 2 ** ((NB - (LB - NB)) / 2) == 2.0 ** -257, "hm96: per-leaf 2^-257, pair 2^-256")


# ============================== vllm-v1-sha512 (vllm_v1/PROTOCOL.md sections 1-4 and 10) ================================
def fa2h_chunk_header(f: dict) -> bytes:
    w = [0x68326166, 7 << 16 | 1 << 8 | f["src_mask"], f["launch_tag"], f["chunk_index"], f["chunk_words"], f["HB"], f["M"], f["NB"],
         f["BN"], f["D"], 0, 0, 0, 0, 0, 0]
    return struct.pack("<16I", *w)


def fa2h_thread_header(f: dict) -> bytes:
    w = [0x68326166, 7 << 16 | f["src_mask"], 0, f["slab"], f["m_block"], f["n_block"], f["tidx"], f["seqlen_q"], f["seqlen_k"],
         f["launch_tag"], f["n_block_max"], int(f["ok0"]) | int(f["ok1"]) << 1, 0, 0, 0, 0]
    return struct.pack("<16I", *w)


def stream_ctx(launch_tag, src_mask, chunk_words, leaf_count) -> bytes:
    return S5(('{"chunk_words": %d, "launch_tag": %d, "leaf_count": %d, "src_mask": %d}' % (chunk_words, launch_tag, leaf_count, src_mask)).encode())


def thread_ctx(launch_tag, src_mask) -> bytes:
    return S5(('{"launch_tag": %d, "src_mask": %d}' % (launch_tag, src_mask)).encode())


def domain_digest(kind: str, fields: dict) -> bytes:
    doc = {"kind": kind, **{k: (v.hex() if isinstance(v, bytes) else v) for k, v in fields.items()}}
    return tagged_sha256("verity/vllm-v1/domain/v1", cjson(doc))


def vllm(V: dict) -> None:
    check(V["scheme"] == "vllm-v1-sha512", "vllm: scheme name")
    for h in V["hash"]:
        check(Hv(h["tag"], *(hx(p) for p in h["parts"])).hex() == h["digest"], f"vllm: H({h['tag']})")
    for p in V["pos_leaves"]:
        v = hx(p["value"])
        check(S5(pos_prefix(len(v)) + v).hex() == p["leaf"], f"vllm: pos leaf n={len(v)}")
    for c in V["chunk_leaves"]:
        hd = fa2h_chunk_header(c["fields"])
        check(hd.hex() == c["header"] and S5(hd + hx(c["chunk"])).hex() == c["leaf"], f"vllm: chunk leaf {c['fields']['chunk_index']}")
    for c in V["thread_leaves"]:
        hd = fa2h_thread_header(c["fields"])
        check(hd.hex() == c["header"] and S5(hd + hx(c["words"])).hex() == c["leaf"], "vllm: thread leaf")
    for t in V["trees"]:
        leaves = [hx(z) for z in t["leaves"]]
        check(fold(leaves).hex() == t["root"], f"vllm: tree n={t['leaf_count']} root")
        for i in range(len(leaves)):
            p = [None if s is None else hx(s) for s in t["paths"][i]]
            check(verify_path(hx(t["root"]), len(leaves), i, leaves[i], p), f"vllm: tree n={len(leaves)} path {i}")
    for r in V["roots"]:
        i, k = r["inputs"], r["kind"]
        if k == "semantic":
            got = S5(b"verity/semantic-root/v0" + hx(i["program_digest"]) + hx(i["query_id"]) + hx(i["template_digest"]) + hx(i["ctx_digest"])
                     + u64be(i["epoch"]) + u64be(i["n"]) + hx(i["tree_root"]))
        elif k == "step":
            got = step_root(hx(i["program_digest"]), hx(i["ctx_digest"]), hx(i["geo_digest"]), hx(i["layout_digest"]), i["n"], hx(i["tree_root"]))
        elif k == "run":
            sr = [hx(s) for s in i["step_roots"]]
            got = S5(b"verity/cmt-integ/run-root/v0" + hx(i["program_digest"]) + hx(i["geo_digest"]) + u64be(len(sr)) + fold(sr))
        elif k == "weights":
            tr = [hx(s) for s in i["tensor_roots"]]
            got = S5(b"verity/cmt-integ/weights-root/v0" + hx(i["geo_digest"]) + hx(i["names_digest"]) + u64be(len(tr)) + fold(tr))
        elif k == "stream":
            sc = stream_ctx(i["launch_tag"], i["src_mask"], i["chunk_words"], i["leaf_count"])
            check(sc.hex() == i["ctx_digest"], "vllm: stream ctx (SHA-512 of the text)")
            got = S5(b"verity/fa2-hidden/root/v7" + hx(i["layout_digest"]) + sc + hx(i["tree_root"]))
        else:
            tc = thread_ctx(i["launch_tag"], i["src_mask"])
            check(tc.hex() == i["ctx_digest"], "vllm: thread ctx (SHA-512 of the text)")
            got = S5(b"verity/fa2-hidden/thread-root/v7" + hx(i["geo_digest"]) + tc + hx(i["tree_root"]))
        check(got.hex() == r["root"], f"vllm: {k} root")
        check(len(hx(i["tree_root"] if "tree_root" in i else r["root"])) == 64, f"vllm: {k} tree root is 64 bytes")
    prog, tmpl, ctx, geo, lay = (expand(x, 32) for x in ("program", "template", "ctx", "geo", "layout"))
    doms = {
        "semantic": ({"program_digest": prog, "query_id": b"q-7", "template_digest": tmpl, "ctx_digest": ctx, "epoch": 2, "leaf_count": 5,
                      "hash": "sha512"}, lambda i, v: S5(pos_prefix(len(v)) + v),
                     lambda tr: S5(b"verity/semantic-root/v0" + prog + b"q-7" + tmpl + ctx + u64be(2) + u64be(5) + tr), 5),
        "step": ({"program_digest": prog, "ctx_digest": ctx, "geo_digest": geo, "layout_digest": lay, "leaf_count": 6, "chunk": None,
                  "hash": "sha512"}, lambda i, v: S5(pos_prefix(len(v)) + v), lambda tr: step_root(prog, ctx, geo, lay, 6, tr), 6),
        "stream": ({"layout_digest": lay, "launch_tag": 7, "src_mask": 63, "chunk_words": 16, "leaf_count": 5, "HB": 2, "M": 8, "NB": 1,
                    "BN": 0, "D": 0, "hash": "sha512"},
                   lambda i, v: S5(fa2h_chunk_header({"launch_tag": 7, "chunk_index": i, "chunk_words": 16, "src_mask": 63, "HB": 2, "M": 8,
                                                      "NB": 1, "BN": 0, "D": 0}) + v),
                   lambda tr: S5(b"verity/fa2-hidden/root/v7" + lay + stream_ctx(7, 63, 16, 5) + tr), 5),
    }
    for o in V["openings"]:
        fields, leaf_of, bind, n = doms[o["kind"]]
        check(domain_digest(o["kind"], fields).hex() == o["domain_digest"], f"vllm: {o['kind']} domain digest (includes hash=sha512)")
        f256 = {k: v for k, v in fields.items() if k != "hash"}
        check(domain_digest(o["kind"], f256).hex() != o["domain_digest"], f"vllm: {o['kind']} domain digest differs from the SHA-256 domain's")
        p = [None if s is None else hx(s) for s in o["path"]]
        ok = verify_path(hx(o["root"]), n, o["index"], leaf_of(o["index"], hx(o["value"])), p, bind)
        check(ok == o["accept"], f"vllm: {o['kind']} opening accept={o['accept']}")


# ============================== frame-v3-sha512 (frame_v3/PROTOCOL.md section 6, merkle frame) ============================
FRAME = b"veritor/protocol/merkle/frame/v3\0"


def fh(tag: bytes, *parts: bytes) -> bytes:
    return S5(FRAME + u32be(len(tag)) + tag + b"".join(u64be(len(p)) + p for p in parts))


def uint(v: int) -> bytes:
    return v.to_bytes(max(1, (v.bit_length() + 7) // 8), "big")


def range_identity(start: int, stop: int) -> bytes:
    return tagged_sha256("veritor/indexed-domain/range/v1", cjson({"start": start, "step": 1, "stop": stop}))


def domain_id(binding: bytes, owner: int, start: int, stop: int) -> bytes:
    return fh(b"domain", binding, uint(owner + 2), range_identity(start, stop), uint(stop - start))


def frame(V: dict) -> None:
    check(V["scheme"] == "frame-v3-sha512", "frame: scheme name")
    for r in V["row_leaves"]:
        pre = sha512_row_prefix(r["role"], r["word_bits"], r["n_words"])
        check(pre.hex() == r["prefix"], f"frame: sha512/row/v1 prefix {r['role']}/{r['word_bits']}/{r['n_words']}")
        check(len(hx(r["row_bytes"])) == r["n_words"] * r["word_bits"] // 8 and S5(pre + hx(r["row_bytes"])).hex() == r["digest"],
              f"frame: row digest {r['role']}/{r['word_bits']}/{r['n_words']}")
    e = V["empty_root"]
    d = e["domain"]
    did = domain_id(hx(d["binding"]), d["owner"], *d["range"])
    check(did.hex() == d["domain_id"] and fh(b"empty", did).hex() == e["root"], "frame: empty domain id and root")
    for wl in V["word_leaves"]:
        d = wl["domain"]
        did = domain_id(hx(d["binding"]), d["owner"], *d["range"])
        check(did.hex() == d["domain_id"], "frame: word-leaf domain id")
        rank = wl["position"] - d["range"][0]
        pre = FRAME + u32be(4) + b"leaf" + u64be(64) + did + u64be(len(uint(rank))) + uint(rank) + u64be(len(uint(wl["position"]))) + \
            uint(wl["position"]) + u64be(len(wl["schema"])) + wl["schema"].encode() + u64be(len(hx(wl["value"])))
        check(pre.hex() == wl["prefix"] and S5(pre + hx(wl["value"])).hex() == wl["leaf"], f"frame: word leaf at {wl['position']}")
    for t in V["row_trees"]:
        d = t["domain"]
        n = d["range"][1] - d["range"][0]
        did = domain_id(hx(d["binding"]), d["owner"], *d["range"])
        check(did.hex() == d["domain_id"], f"frame tree n={n}: domain id")
        dg = [S5(sha512_row_prefix(t["role"], t["word_bits"], t["n_words"]) + hx(row)) for row in t["rows"]]
        check([z.hex() for z in dg] == t["digests"], f"frame tree n={n}: row digests")
        leaves = [fh(b"leaf", did, uint(r), uint(r), b"sha512/row/v1", dg[r]) for r in range(n)]
        check([z.hex() for z in leaves] == t["leaves"], f"frame tree n={n}: row leaves")
        width = 1 << max(0, (n - 1).bit_length())
        pads = [fh(b"pad", did, uint(r)) for r in range(n, width)]
        check([z.hex() for z in pads] == t["pads"], f"frame tree n={n}: pads")
        lv, levels, depth = leaves + pads, [], 0
        levels.append(lv)
        while len(lv) > 1:
            lv = [fh(b"node", did, uint(depth), uint(i // 2), lv[i], lv[i + 1]) for i in range(0, len(lv), 2)]
            levels.append(lv)
            depth += 1
        check(lv[0].hex() == t["root"], f"frame tree n={n}: root")
        for r in range(n):
            idx, want = r, []
            for level in levels[:-1]:
                want.append(level[idx ^ 1].hex())
                idx >>= 1
            check(want == t["paths"][r], f"frame tree n={n}: path {r}")


def main(root: str) -> int:
    hm96(json.load(open(f"{root}/hm96/vectors_sha512.json")))
    vllm(json.load(open(f"{root}/vllm_v1/vectors_sha512.json")))
    frame(json.load(open(f"{root}/frame_v3/vectors_sha512.json")))
    print(json.dumps({"checks": N, "failed": FAIL, "scheme_digest_sha512": scheme_digest(key_from_label(KEY_LABEL)).hex()}, indent=1))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
