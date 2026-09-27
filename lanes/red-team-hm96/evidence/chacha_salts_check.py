"""red-team-hm96 (PR #83 @ b32e1a7b): M0's salt stream on the CPU.

Cross-checks four ChaCha20 implementations on the stream layout M0 uses (64-bit block counter in words 12-13, 64-bit nonce in words
14-15, 20 rounds): M0's Rust `zk_hooks::chacha20_block` (extracted verbatim, `chacha_rs`), M0's device `chacha20_block` / `hm96_salt`
from `cuda/sha512.cuh` compiled for the host (`chacha_cu`), an RFC 7539 implementation here, and OpenSSL's ChaCha20 through
`cryptography` (16-byte IV = words 12-15).  Then checks the RFC 7539 section 2.3.2 block in full, the salt layout (leaf i = blocks
3i..3i+2), and the (id, block) uniqueness of the session's tree-id schedule on both paths.

    python chacha_salts_check.py <dir with chacha_rs and chacha_cu>
"""
from __future__ import annotations

import json
import os
import struct
import subprocess
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

FAIL: list[str] = []
N = 0


def check(cond: bool, what: str) -> None:
    global N
    N += 1
    if not cond:
        FAIL.append(what)
        print("FAIL", what, flush=True)


M32 = 0xFFFFFFFF


def rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & M32


def block(key: bytes, counter: int, nonce: int) -> bytes:
    """RFC 7539 section 2.3 block function with words 12-13 a 64-bit counter and 14-15 a 64-bit nonce."""
    s = [0x61707865, 0x3320646E, 0x79622D32, 0x6B206574, *struct.unpack("<8I", key),
         counter & M32, counter >> 32, nonce & M32, nonce >> 32]
    x = list(s)

    def qr(a, b, c, d):
        x[a] = (x[a] + x[b]) & M32; x[d] = rotl(x[d] ^ x[a], 16)
        x[c] = (x[c] + x[d]) & M32; x[b] = rotl(x[b] ^ x[c], 12)
        x[a] = (x[a] + x[b]) & M32; x[d] = rotl(x[d] ^ x[a], 8)
        x[c] = (x[c] + x[d]) & M32; x[b] = rotl(x[b] ^ x[c], 7)

    for _ in range(10):
        qr(0, 4, 8, 12); qr(1, 5, 9, 13); qr(2, 6, 10, 14); qr(3, 7, 11, 15)
        qr(0, 5, 10, 15); qr(1, 6, 11, 12); qr(2, 7, 8, 13); qr(3, 4, 9, 14)
    return struct.pack("<16I", *(((a + b) & M32) for a, b in zip(x, s)))


def openssl_block(key: bytes, counter: int, nonce: int) -> bytes:
    iv = counter.to_bytes(8, "little") + nonce.to_bytes(8, "little")
    return Cipher(algorithms.ChaCha20(key, iv), mode=None).encryptor().update(bytes(64))


def run(binary: str, lines: list[str], *mode: str) -> list[str]:
    out = subprocess.run([binary, *mode], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True).stdout.split()
    return out


def main(bindir: str) -> int:
    rs, cu = f"{bindir}/chacha_rs", f"{bindir}/chacha_cu"
    # RFC 7539 section 2.3.2: key 00..1f, nonce 00:00:00:09:00:00:00:4a:00:00:00:00, block count 1 -- in M0's layout the words are
    # counter = 1 | 0x09000000 << 32 (words 12-13), nonce = 0x4a000000 (words 14-15), as zk_hooks' unit test passes them
    k = bytes(range(32))
    c, n = 1 | (0x09000000 << 32), 0x4A000000
    rfc = bytes.fromhex("10f1e7e4d13b5915500fdd1fa32071c4c7d1f4c733c068030422aa9ac3d46c4e"
                        "d2826446079faa0914c2d705d98b02a2b5129cd1de164eb9cbd083e8a2503c4e")
    ietf = Cipher(algorithms.ChaCha20(k, (1).to_bytes(4, "little") + bytes.fromhex("000000090000004a00000000")), mode=None).encryptor().update(bytes(64))
    check(ietf == rfc, "OpenSSL reproduces the RFC 7539 2.3.2 serialized block (IETF layout)")
    check(block(k, c, n) == rfc, "the RFC block function here reproduces 2.3.2 in M0's layout")
    got_rs, got_cu = run(rs, [f"{k.hex()} {c} {n}"])[0], run(cu, [f"{k.hex()} {c} {n}"])[0]
    check(got_rs == rfc.hex(), "M0's Rust chacha20_block: the full 64-byte 2.3.2 block (its unit test checks 16 bytes)")
    check(got_cu == rfc.hex(), "M0's device chacha20_block (host build): the full 2.3.2 block")
    # random and edge inputs: counter carries across the 32-bit word boundary, the top of both 64-bit ranges
    cases = []
    edges = [0, 1, 2, 3, M32 - 1, M32, M32 + 1, 1 << 32, (1 << 63), (1 << 64) - 2, (1 << 64) - 1]
    for cc in edges:
        for nn in (0, 1, M32, 1 << 32, (1 << 64) - 1):
            cases.append((os.urandom(32), cc, nn))
    for _ in range(1500):
        cases.append((os.urandom(32), int.from_bytes(os.urandom(8), "little"), int.from_bytes(os.urandom(8), "little")))
    lines = [f"{kk.hex()} {cc} {nn}" for kk, cc, nn in cases]
    R, C = run(rs, lines), run(cu, lines)
    mism = [i for i, (kk, cc, nn) in enumerate(cases) if not (R[i] == C[i] == block(kk, cc, nn).hex() == openssl_block(kk, cc, nn).hex())]
    check(not mism, f"Rust == device == RFC == OpenSSL on {len(cases)} blocks (edges incl. 2^32 carry, 2^64-1): {len(mism)} mismatches")
    # salt layout: device hm96_salt(key, id, i) == Rust blocks 3i, 3i+1, 3i+2 == RFC here
    sl, exp = [], []
    for _ in range(300):
        kk, nid, i = os.urandom(32), int.from_bytes(os.urandom(2), "little"), int.from_bytes(os.urandom(4), "little")
        sl.append(f"{kk.hex()} 0 {nid} {i}")
        exp.append((kk, nid, i))
    S = run(cu, sl, "salt")
    RB = run(rs, [f"{kk.hex()} {3 * i + j} {nid}" for kk, nid, i in exp for j in range(3)])
    ok = all(S[t] == RB[3 * t] + RB[3 * t + 1] + RB[3 * t + 2] == b"".join(block(kk, 3 * i + j, nid) for j in range(3)).hex()
             for t, (kk, nid, i) in enumerate(exp))
    check(ok and all(len(s) == 384 for s in S), "salt of leaf i under nonce id = blocks 3i..3i+2 (device == Rust == RFC), 192 bytes")
    # the session's id schedule, as the code assigns it (CPU: hm96::begin per rep, level0 = expand(0); GPU: hm96_tree(ctx, 0) = 0,
    # else LeafSalts::next_id; one LeafSalts per session, next starts at 1)
    def schedule(trees_per_rep: list[int]) -> dict[tuple[int, int], str]:
        nxt, owner = 1, {}
        for rep in range(2):
            for k, leaves in enumerate(trees_per_rep):
                if k == 0:
                    nid, content = 0, "level0"            # the same tree in both reps (R1 binds one root)
                else:
                    nid, content = nxt, f"rep{rep}/tree{k}"
                    nxt += 1
                for i in range(leaves):
                    for j in range(3):
                        key = (nid, 3 * i + j)
                        if owner.setdefault(key, content) != content:
                            owner["COLLISION"] = f"{key} {owner[key]} vs {content}"
        return owner
    small = schedule([64, 32, 16, 8, 4, 2])
    check("COLLISION" not in small, "id schedule: no (id, block) used by two different trees, both reps (6 trees per rep)")
    ids = sorted({k[0] for k in small if isinstance(k, tuple)})
    check(ids == list(range(0, 1 + 2 * 5)), f"id schedule: ids {ids[0]}..{ids[-1]}, level 0 alone at id 0")
    # sizes: 670 MB of salts per proof at m = 33 (M0) = 3.49e6 leaves in all trees; even 2^40 leaves in one tree need 3 * 2^40 blocks
    n_total = 670_000_000 // 192
    check(3 * n_total < (1 << 32) and 3 * (1 << 40) < (1 << 64), f"no counter wrap: {3 * n_total} blocks per proof << 2^64 per nonce")
    print(json.dumps({"checks": N, "failed": FAIL, "blocks_compared": len(cases), "salts_compared": len(exp)}))
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
