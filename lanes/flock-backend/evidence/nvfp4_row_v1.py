"""Proposed frame-v3 NVFP4 row leaves (flock-backend, 2026-09-26): reference and conformance vectors.

A K-code NVFP4 row (x row or W column, K = 1536, 24 units of 64 codes) is K E2M1 codes and K/16 UE4M3 scale bytes.
row_bytes_nvfp4 = the codes packed two per byte (code 2i in the low nibble, 2i+1 in the high nibble, in row order: unit u's
codes are bytes [32u, 32u + 32)), then the scale bytes in row order (unit u's 4 scales are bytes [K/2 + 4u, K/2 + 4u + 4)).
K = 1536 -> 768 + 96 = 864 bytes.

sha256/row-nvfp4/v1:       prefix = ("verity/sha256-row-nvfp4/v1\\0" || u8 role || u8 4 || u32be K || u32be K/16) zero-padded to
                           64 bytes;  digest = SHA-256(prefix || row_bytes_nvfp4)
blake3-keyed/row-nvfp4/v1: digest = BLAKE3(row_bytes_nvfp4, key = rowleaf.blake3_row_key(role))   (the frame-v3 keys; the
                           schema string, which the tree leaf binds, separates it from blake3-keyed/row/v2)
Tree leaves as for every frame-v3 row leaf: leaf(domain, rank, position, schema, digest).

    python3 nvfp4_row_v1.py > nvfp4_row_v1_vectors.json
"""
import hashlib
import json
import random

K, SCALES = 1536, 1536 // 16
TAG = b"verity/sha256-row-nvfp4/v1\0"
KEY_PREFIX = b"verity/blake3-leaf/v1/"


def row_bytes(codes, scales):
    assert len(codes) == K and len(scales) == SCALES
    assert all(0 <= c < 16 for c in codes) and all(0 <= s < 256 for s in scales)
    return bytes(codes[2 * i] | (codes[2 * i + 1] << 4) for i in range(K // 2)) + bytes(scales)


def prefix(role):
    return (TAG + bytes([role, 4]) + K.to_bytes(4, "big") + SCALES.to_bytes(4, "big")).ljust(64, b"\0")


def key(role):
    return (KEY_PREFIX + (b"x" if role == 1 else b"w")).ljust(32, b"\0")


def vectors():
    import blake3
    rng = random.Random(20260926)
    cases = {"zeros": ([0] * K, [0] * SCALES),
             "ramp": ([i % 16 for i in range(K)], [0x38] * SCALES),
             "random": ([rng.randrange(16) for _ in range(K)], [rng.randrange(128) for _ in range(SCALES)])}
    out = []
    for name, (c, s) in cases.items():
        rb = row_bytes(c, s)
        for role in (1, 2):
            out.append({"case": name, "role": role, "row_bytes_len": len(rb), "row_bytes_sha256": hashlib.sha256(rb).hexdigest(),
                        "row_bytes_head_hex": rb[:40].hex(), "scale_bytes_hex": rb[K // 2:K // 2 + 8].hex(),
                        "sha256/row-nvfp4/v1": hashlib.sha256(prefix(role) + rb).hexdigest(),
                        "blake3-keyed/row-nvfp4/v1": blake3.blake3(rb, key=key(role)).hexdigest()})
    return out


if __name__ == "__main__":
    print(json.dumps({"K": K, "scales": SCALES, "row_bytes": K // 2 + SCALES, "vectors": vectors()}, indent=1))
