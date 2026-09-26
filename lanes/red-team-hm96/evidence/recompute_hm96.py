"""red-team-hm96: independent recomputation of hm96-sha256/v1 vectors.json from PROTOCOL.md text alone, plus math-level negatives.

Imports nothing from verity (hashlib + numpy only); reads vectors.json by path.  Usage:
    python recompute_hm96.py <path to packages/verity/src/verity/commitments/hm96/vectors.json>
Prints one line per check and a JSON summary; exits 1 on any mismatch.
"""
from __future__ import annotations

import hashlib
import json
import os
import struct
import sys

import numpy as np

FAIL: list[str] = []
CHECKS = 0


def check(cond: bool, what: str) -> None:
    global CHECKS
    CHECKS += 1
    if not cond:
        FAIL.append(what)
        print("FAIL", what)


H = lambda b: hashlib.sha256(b).digest()  # noqa: E731
u32be = lambda n: n.to_bytes(4, "big")  # noqa: E731
u64be = lambda n: n.to_bytes(8, "big")  # noqa: E731

# ---- the spec, restated (PROTOCOL.md sections 1-2) --------------------------------------------------------------
KEY_LABEL = b"verity/hm96-sha256/key/v1\0"
SALT_PREFIX = b"verity/hm96-sha256/salt/v1\0".ljust(64, b"\0")
LEAF_TAG = b"verity/hm96-sha256/leaf/v1\0"


def key_from_label(label: bytes) -> bytes:
    raw = bytearray(b"".join(H(label + u32be(i)) for i in range(5)))
    raw[159] &= 0x7F                                   # bit 1279 = bit 7 of byte 159
    return bytes(raw)


def bits(data: bytes) -> np.ndarray:
    """bit t = bit (t mod 8) of byte floor(t/8): numpy 'little' bit order."""
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="little")


def matrix(key: bytes) -> np.ndarray:
    k = bits(key)
    assert len(k) == 1280
    i = np.arange(256)[:, None]
    j = np.arange(1024)[None, :]
    return k[i + j]                                     # M[i][j] = k_{i+j}, 256 x 1024


def mask_np(key: bytes, salt: bytes) -> bytes:
    M = matrix(key).astype(np.int64)
    out = (M @ bits(salt).astype(np.int64)) & 1
    return np.packbits(out.astype(np.uint8), bitorder="little").tobytes()


def mask_loops(key: bytes, salt: bytes) -> bytes:
    """Bit-by-bit, no numpy, a third formulation: (M y)_i = XOR_j k_{i+j} y_j."""
    kb = [(key[t >> 3] >> (t & 7)) & 1 for t in range(1280)]
    yb = [(salt[t >> 3] >> (t & 7)) & 1 for t in range(1024)]
    out = bytearray(32)
    for i in range(256):
        acc = 0
        for j in range(1024):
            acc ^= kb[i + j] & yb[j]
        out[i >> 3] |= acc << (i & 7)
    return bytes(out)


def salt_digest(y: bytes) -> bytes:
    return H(SALT_PREFIX + y)


def leaf_prefix(key: bytes) -> bytes:
    return (LEAF_TAG + H(key)).ljust(64, b"\0")


def tree_leaf(key: bytes, bc: bytes) -> bytes:
    return H(leaf_prefix(key) + bc)


def commit(key: bytes, x: bytes, y: bytes) -> bytes:
    m = mask_np(key, y)
    return bytes(a ^ b for a, b in zip(x, m)) + salt_digest(y)


def tagged_sha256(tag: str, payload: bytes) -> bytes:
    t = tag.encode()
    return H(b"veritor/tagged-sha256/v1\0" + u32be(len(t)) + t + u64be(len(payload)) + payload)


def scheme_digest(key: bytes) -> bytes:
    doc = json.dumps({"name": "hm96-sha256/v1", "salt_bytes": 128, "key_sha256": H(key).hex()}, sort_keys=True, separators=(",", ":"))
    return tagged_sha256("verity/hm96-sha256/scheme/v1", doc.encode())


def pos_leaf_prefix(n: int) -> bytes:
    return b"verity/pos-leaf/v0" + u64be(n)


# vllm-v1 section 3 tree rule, packed form
NODE = u32be(19) + b"verity-vllm/node/v1"
LIFT = u32be(19) + b"verity-vllm/lift/v1"


def node(a: bytes, b: bytes) -> bytes:
    return H(NODE + u64be(32) + a + u64be(32) + b)


def lift(a: bytes) -> bytes:
    return H(LIFT + u64be(32) + a)


def fold(leaves: list[bytes]) -> bytes:
    lv = list(leaves)
    while len(lv) > 1:
        nxt = [node(lv[i], lv[i + 1]) for i in range(0, len(lv) - 1, 2)]
        if len(lv) % 2:
            nxt.append(lift(lv[-1]))
        lv = nxt
    return lv[0]


def fold_path(d: bytes, i: int, path: list) -> bytes:
    for s in path:
        if s is None:
            d = lift(d)
        elif i % 2 == 0:
            d = node(d, s)
        else:
            d = node(s, d)
        i //= 2
    return d


def shape(n: int, i: int) -> list[bool]:
    out, w = [], n
    while w > 1:
        out.append(i != w - 1 or w % 2 == 0)
        w, i = -(-w // 2), i // 2
    return out


def verify_path(root_tree: bytes, n: int, i: int, leaf: bytes, path: list) -> bool:
    sh = shape(n, i)
    if len(path) != len(sh) or any((p is None) == has for p, has in zip(path, sh)):
        return False
    return fold_path(leaf, i, path) == root_tree


def step_root(program: bytes, ctx: bytes, geo: bytes, layout: bytes, n: int, tree_root: bytes) -> bytes:
    return H(b"verity/fa2c/root/v0" + program + ctx + geo + layout + u64be(n) + tree_root)


# ---- a pure-Python SHA-256 (for length extension) ---------------------------------------------------------------
_K = [int(x, 16) for x in (
    "428a2f98 71374491 b5c0fbcf e9b5dba5 3956c25b 59f111f1 923f82a4 ab1c5ed5 d807aa98 12835b01 243185be 550c7dc3 72be5d74 80deb1fe "
    "9bdc06a7 c19bf174 e49b69c1 efbe4786 0fc19dc6 240ca1cc 2de92c6f 4a7484aa 5cb0a9dc 76f988da 983e5152 a831c66d b00327c8 bf597fc7 "
    "c6e00bf3 d5a79147 06ca6351 14292967 27b70a85 2e1b2138 4d2c6dfc 53380d13 650a7354 766a0abb 81c2c92e 92722c85 a2bfe8a1 a81a664b "
    "c24b8b70 c76c51a3 d192e819 d6990624 f40e3585 106aa070 19a4c116 1e376c08 2748774c 34b0bcb5 391c0cb3 4ed8aa4a 5b9cca4f 682e6ff3 "
    "748f82ee 78a5636f 84c87814 8cc70208 90befffa a4506ceb bef9a3f7 c67178f2").split()]
_IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def compress(state: list[int], block: bytes) -> list[int]:
    w = list(struct.unpack(">16I", block))
    for t in range(16, 64):
        s0 = _rotr(w[t - 15], 7) ^ _rotr(w[t - 15], 18) ^ (w[t - 15] >> 3)
        s1 = _rotr(w[t - 2], 17) ^ _rotr(w[t - 2], 19) ^ (w[t - 2] >> 10)
        w.append((w[t - 16] + s0 + w[t - 7] + s1) & 0xFFFFFFFF)
    a, b, c, d, e, f, g, h = state
    for t in range(64):
        S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
        ch = (e & f) ^ (~e & g)
        t1 = (h + S1 + ch + _K[t] + w[t]) & 0xFFFFFFFF
        S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        t2 = (S0 + maj) & 0xFFFFFFFF
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF
    return [(x + y) & 0xFFFFFFFF for x, y in zip(state, [a, b, c, d, e, f, g, h])]


def md_pad(nbytes: int) -> bytes:
    return b"\x80" + b"\0" * ((55 - nbytes) % 64) + u64be(8 * nbytes)


def sha256_py(msg: bytes) -> bytes:
    st, m = list(_IV), msg + md_pad(len(msg))
    for o in range(0, len(m), 64):
        st = compress(st, m[o:o + 64])
    return struct.pack(">8I", *st)


def extend(digest: bytes, orig_len: int, suffix: bytes) -> bytes:
    """SHA-256(m || pad(m) || suffix) from SHA-256(m) and |m| alone: the length-extension forgery."""
    st = list(struct.unpack(">8I", digest))
    total = orig_len + len(md_pad(orig_len)) + len(suffix)
    m = suffix + md_pad(total)
    for o in range(0, len(m), 64):
        st = compress(st, m[o:o + 64])
    return struct.pack(">8I", *st)


def gf2_rank(rows_: list[int]) -> int:
    basis: dict[int, int] = {}
    for v in rows_:
        while v:
            top = v.bit_length() - 1
            if top not in basis:
                basis[top] = v
                break
            v ^= basis[top]
    return len(basis)


def main(path: str) -> int:
    V = json.load(open(path))
    DEFAULT_KEY = key_from_label(KEY_LABEL)
    other = bytes.fromhex(V["other_key"])
    check(V["scheme"] == "hm96-sha256/v1", "scheme name")
    check(V["key_label"] == KEY_LABEL.hex(), "key label")
    check(V["default_key"] == DEFAULT_KEY.hex(), "default key re-derived from label")
    check((other[159] >> 7) == 0 and (DEFAULT_KEY[159] >> 7) == 0 and len(other) == 160, "key bit 1279 zero")
    check(V["salt_prefix"] == SALT_PREFIX.hex(), "salt prefix")
    check(V["leaf_prefix_default_key"] == leaf_prefix(DEFAULT_KEY).hex(), "leaf prefix")
    check(V["scheme_digest_default_key"] == scheme_digest(DEFAULT_KEY).hex(), "scheme digest")
    M = matrix(DEFAULT_KEY)
    weights = [int(r.sum()) for r in M]
    check(V["default_key_row_weights"] == weights, "row weights")
    check(V["default_key_xor_gates"] == sum(weights), "xor gate count = sum of row weights")
    # --- the Hankel structure and rank of the pinned key's M (a fixed key must at least be full rank, else b leaks x mod im(M))
    rows_int = [int.from_bytes(np.packbits(r.astype(np.uint8), bitorder="little").tobytes(), "little") for r in M]
    rank_default = gf2_rank(rows_int)
    Mo = matrix(other)
    rank_other = gf2_rank([int.from_bytes(np.packbits(r.astype(np.uint8), bitorder="little").tobytes(), "little") for r in Mo])
    check(rank_default == 256, f"rank M(DEFAULT_KEY) = {rank_default}")
    check(rank_other == 256, f"rank M(other) = {rank_other}")
    # --- universality: key -> M d is a linear map of rank 256 for nonzero d (rows d<<i), incl. adversarial sparse / top-heavy d
    ds = [1, 1 << 1023, (1 << 1023) | 1, (1 << 1024) - 1, int.from_bytes(os.urandom(128), "little") | 1,
          int.from_bytes(os.urandom(128), "little") & ~((1 << 768) - 1) | (1 << 768)]
    check(all(gf2_rank([d << i for i in range(256)]) == 256 for d in ds), "universal family: rank 256 for adversarial d")
    # --- masks
    for c in V["masks"]:
        key = DEFAULT_KEY if c["key"] == "default" else other
        y = bytes.fromhex(c["salt"])
        m = mask_np(key, y)
        check(m.hex() == c["mask"], f"mask {c['key']}/{c['salt_case']}")
        check(salt_digest(y).hex() == c["salt_digest"], f"salt digest {c['key']}/{c['salt_case']}")
        check(sha256_py(SALT_PREFIX + y).hex() == c["salt_digest"], f"pure-python sha256 {c['salt_case']}")
    for c in V["masks"][:2] + V["masks"][4:5]:
        key = DEFAULT_KEY if c["key"] == "default" else other
        check(mask_loops(key, bytes.fromhex(c["salt"])).hex() == c["mask"], f"mask by loops {c['key']}/{c['salt_case']}")
    # --- leaves
    for c in V["leaves"]:
        v, y = bytes.fromhex(c["value"]), bytes.fromhex(c["salt"])
        pre, suf = bytes.fromhex(c["inner_prefix"]), bytes.fromhex(c["inner_suffix"])
        if c["inner"] == "pos-leaf":
            check(pre == pos_leaf_prefix(len(v)) and suf == b"", f"pos-leaf prefix n={len(v)}")
        else:
            check(pre[:21] == b"verity/sha256-row/v1\0" and pre[22] == 16 and pre[23:27] == u32be(len(v) // 2) and pre[27:] == bytes(37)
                  and len(pre) == 64, f"sha256/row/v1 prefix n={len(v)}")
        x = H(pre + v + suf)
        check(x.hex() == c["inner_digest"], f"inner digest {c['inner']}/{len(v)}")
        bc = commit(DEFAULT_KEY, x, y)
        check(bc[:32].hex() == c["b"] and bc[32:].hex() == c["c"], f"b||c {c['inner']}/{len(v)}")
        check(tree_leaf(DEFAULT_KEY, bc).hex() == c["leaf"], f"leaf {c['inner']}/{len(v)}")
    # --- trees
    for t in V["trees"]:
        d = t["domain"]
        n = d["leaf_count"]
        prog, ctx, geo, lay = (bytes.fromhex(d[k]) for k in ("program", "ctx", "geo", "layout"))
        leaves = []
        for i in range(n):
            v, y = bytes.fromhex(t["values"][i]), bytes.fromhex(t["salts"][i])
            x = H(pos_leaf_prefix(40) + v)
            bc = commit(DEFAULT_KEY, x, y)
            check(bc.hex() == t["proven"][i], f"tree n={n} proven {i}")
            leaves.append(tree_leaf(DEFAULT_KEY, bc))
        check([x.hex() for x in leaves] == t["leaves"], f"tree n={n} leaves")
        tr = fold(leaves)
        check(step_root(prog, ctx, geo, lay, n, tr).hex() == t["root"], f"tree n={n} bound step root")
        for i in range(n):
            p = [None if s is None else bytes.fromhex(s) for s in t["paths"][i]]
            check(verify_path(tr, n, i, leaves[i], p), f"tree n={n} path {i}")
    # ============================== negatives (math level) =========================================================
    rng = np.random.default_rng(96)
    v = rng.bytes(40)
    y = rng.bytes(128)
    x = H(pos_leaf_prefix(40) + v)
    bc = commit(DEFAULT_KEY, x, y)
    leaf = tree_leaf(DEFAULT_KEY, bc)
    # wrong nonce: every single-bit flip of y at a spread of positions, and a fresh salt
    for t in (0, 1, 7, 8, 511, 512, 1022, 1023):
        y2 = bytearray(y)
        y2[t >> 3] ^= 1 << (t & 7)
        check(tree_leaf(DEFAULT_KEY, commit(DEFAULT_KEY, x, bytes(y2))) != leaf, f"neg: salt bit {t} flipped")
    check(tree_leaf(DEFAULT_KEY, commit(DEFAULT_KEY, x, os.urandom(128))) != leaf, "neg: fresh salt")
    # a salt differing only in the kernel of M: same mask, different c -> still rejected by c (binding does not rest on M)
    ker = None
    # find a nonzero vector in ker(M): M is 256x1024, so ker has dim 768; solve via elimination on columns
    Mi = M.astype(np.uint8).copy()
    piv_cols, r = [], 0
    A = Mi.copy()
    for col in range(1024):
        piv = next((k for k in range(r, 256) if A[k, col]), None)
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        for k in range(256):
            if k != r and A[k, col]:
                A[k] ^= A[r]
        piv_cols.append(col)
        r += 1
        if r == 256:
            break
    free = next(c for c in range(1024) if c not in piv_cols)
    z = np.zeros(1024, dtype=np.uint8)
    z[free] = 1
    for k, pc in enumerate(piv_cols):
        z[pc] = A[k, free]
    ker = np.packbits(z, bitorder="little").tobytes()
    check(mask_np(DEFAULT_KEY, ker) == bytes(32) and any(ker), "found nonzero kernel vector of M(DEFAULT_KEY)")
    y_k = bytes(a ^ b for a, b in zip(y, ker))
    check(mask_np(DEFAULT_KEY, y_k) == mask_np(DEFAULT_KEY, y), "kernel shift preserves the mask")
    check(tree_leaf(DEFAULT_KEY, commit(DEFAULT_KEY, x, y_k)) != leaf, "neg: kernel-shifted salt (same b) rejected via c")
    # swapped leaf: value/salt of position j presented at position i (same tree): leaf differs
    v2, y2 = rng.bytes(40), rng.bytes(128)
    leaf2 = tree_leaf(DEFAULT_KEY, commit(DEFAULT_KEY, H(pos_leaf_prefix(40) + v2), y2))
    check(leaf2 != leaf, "neg: swapped leaf differs")
    # the randomness of a different position: value i with salt j
    check(tree_leaf(DEFAULT_KEY, commit(DEFAULT_KEY, x, y2)) != leaf, "neg: salt of another position")
    # truncated opening: salt 127 bytes / value 39 bytes (pos-leaf length prefix changes)
    check(H(pos_leaf_prefix(39) + v[:39]) != x, "neg: truncated value -> different inner digest")
    # length ambiguity: move one byte from the salt to the value (value||salt split shifted) -> pos-leaf length prefix changes
    xv = H(pos_leaf_prefix(41) + v + y[:1])
    check(tree_leaf(DEFAULT_KEY, commit(DEFAULT_KEY, xv, y[1:] + b"\0")) != leaf, "neg: value/salt boundary shifted")
    # length extension on each SHA-256 layer: forge the digest of an extended message; show no valid opening maps to it
    ext = b"\xffextension"
    # (a) inner pos-leaf: x' = SHA256(prefix(40)||v||pad||ext) is computable, but a pos-leaf opening of v' = v||pad||ext hashes
    #     prefix(len v') -- the length field differs, so x' is not the pos-leaf digest of any value (barring a collision)
    msg = pos_leaf_prefix(40) + v
    x_ext = extend(x, len(msg), ext)
    check(x_ext == H(msg + md_pad(len(msg)) + ext), "length extension forgery works on raw SHA-256 (sanity)")
    v_ext = v + md_pad(len(msg)) + ext
    check(H(pos_leaf_prefix(len(v_ext)) + v_ext) != x_ext, "neg: length-extended inner digest is no pos-leaf of the extended value")
    # (b) salt digest: c' = SHA256(SALT_PREFIX||y||pad||ext) -- a salt is exactly 128 bytes, and |y||pad||ext| != 128
    c_ext = extend(salt_digest(y), 64 + 128, ext)
    check(len(y + md_pad(192) + ext) != 128, "neg: length-extended salt is not 128 bytes (refused by length)")
    # (c) leaf: leaf' = SHA256(leaf_prefix||b||c||pad||ext): the commit string is exactly 64 bytes, so no b||c maps to it
    leaf_ext = extend(leaf, 128, ext)
    check(leaf_ext != leaf and len(bc + md_pad(128) + ext) != 64, "neg: length-extended leaf needs a 64+ byte commit string")
    # (d) can an extended leaf preimage be a vllm-v1 node preimage? node starts 00 00 00 13, leaf starts 'verity/h'
    check(leaf_prefix(DEFAULT_KEY)[:8] == b"verity/h" and NODE[:4] == b"\0\0\0\x13" and LIFT[:4] == b"\0\0\0\x13",
          "first bytes separate hm96 leaf from node/lift preimages")
    check(b"verity/pos-leaf/v0"[:8] != leaf_prefix(DEFAULT_KEY)[:8] and SALT_PREFIX[:24] != leaf_prefix(DEFAULT_KEY)[:24],
          "hm96 leaf preimage differs from pos-leaf and salt preimages")
    # cross-key: the same b||c under another key is another leaf; a key is bound through its digest in the prefix
    check(tree_leaf(other, bc) != leaf, "neg: other key")
    # leaf-vs-salt-hash domain: salt preimage is 192 bytes, leaf preimage 128 bytes, prefixes differ at byte 19
    check(len(SALT_PREFIX + y) == 192 and len(leaf_prefix(DEFAULT_KEY) + bc) == 128, "fixed preimage lengths")
    # hiding sanity (not a proof): b over many fresh salts at a fixed x has balanced bits
    B = np.stack([np.frombuffer(commit(DEFAULT_KEY, x, os.urandom(128))[:32], dtype=np.uint8) for _ in range(2000)])
    frac = np.unpackbits(B, axis=1).mean(axis=0)
    check(float(np.abs(frac - 0.5).max()) < 0.06, f"b bits balanced over 2000 salts (max dev {np.abs(frac - 0.5).max():.3f})")
    # equivocation if a circuit took the key as a WITNESS: solve M_{k'} y = b XOR x' for k' (256 equations, 1279 unknowns; the
    # map k' -> M_{k'} y has rows y << i, rank 256), so b||c of (x, y) "opens" to any x' under k'.  The leaf binds SHA-256(key), so
    # this only works where the verifier's leaf key and the circuit's matrix key can differ: the circuit key must be the statement's.
    x_target = H(b"any other value")
    t_int = int.from_bytes(bytes(a ^ b for a, b in zip(bc[:32], x_target)), "little")
    y_int = int.from_bytes(y, "little")
    eqs = [((y_int << i), (t_int >> i) & 1) for i in range(256)]
    piv: dict[int, tuple[int, int]] = {}
    for row, rhs in eqs:
        while row:
            top = row.bit_length() - 1
            if top not in piv:
                piv[top] = (row, rhs)
                break
            prow, prhs = piv[top]
            row, rhs = row ^ prow, rhs ^ prhs
        else:
            check(rhs == 0, "witness-key system consistent")
    k_sol = 0
    for top in sorted(piv):
        row, rhs = piv[top]
        low = row & ~(1 << top)
        if (bin(low & k_sol).count("1") & 1) != rhs:
            k_sol |= 1 << top
    k_forged = k_sol.to_bytes(160, "little")
    check(k_sol < (1 << 1279) and mask_np(k_forged, y) == t_int.to_bytes(32, "little"), "witness key k' solves M_k' y = b ^ x'")
    check(bytes(a ^ b for a, b in zip(x_target, mask_np(k_forged, y))) == bc[:32], "b opens to x' under k' (equivocation if key is a witness)")
    check(tree_leaf(k_forged, bc) != leaf, "the leaf's key digest defeats k' where the verifier recomputes the leaf with k'")
    # scheme digest injectivity versus the vllm-v1 ctx text: does D contain '/step=' (would matter for the ctx-suffix parse)?
    D = scheme_digest(DEFAULT_KEY)
    check(b"/step=" not in D and b"/leaf=" not in D, "scheme digest holds no '/step=' or '/leaf=' text")
    summary = {"checks": CHECKS, "failed": FAIL, "rank_default": rank_default, "rank_other": rank_other,
               "xor_gates_default": sum(weights), "scheme_digest_default": D.hex(), "c_ext": c_ext.hex()[:16]}
    print(json.dumps(summary, indent=1))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
