"""`memory-tiers/sm120` as scoped: are the weights, which are costly to regenerate, incompressible?

Reads real safetensors shards (no safetensors package: the 8-byte header length, the JSON header, raw little-endian data)
and, for a sample of 2-D BF16 matrices, reports:
- `bf16`: the order-0 entropy of the 16-bit codes (bits per weight, a bound any per-symbol coder reaches) and an actual
  lossless ratio (LZMA preset 6 on the raw bytes, after splitting the high and low bytes into two planes);
- `e4m3`: the same for E4M3 codes with a per-row scale (448 / row max, nearest-even, saturating), 8-bit codes;
- `e4m3-rot`: E4M3 codes after the approved-weights transform's shape (random signs, a normalized Walsh–Hadamard along k,
  random signs), which makes rows Gaussian-like.
Usage: python3 weight_compressibility.py SHARD [SHARD ...] [--max-tensors N] [--max-elems M]
"""
import argparse
import json
import lzma
import struct

import numpy as np


def tensors(path):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(n))
        base = 8 + n
    mm = np.memmap(path, dtype=np.uint8, mode="r")
    for name, meta in header.items():
        if name == "__metadata__" or meta["dtype"] != "BF16" or len(meta["shape"]) != 2:
            continue
        a, b = meta["data_offsets"]
        yield name, meta["shape"], mm[base + a: base + b].view(np.uint16).reshape(meta["shape"])


def entropy_bits(codes):
    _, counts = np.unique(codes, return_counts=True)
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def lzma_ratio(planes):
    raw = sum(len(p) for p in planes)
    return sum(len(lzma.compress(p, preset=6)) for p in planes) / raw


def bf16_to_f32(u16):
    return (u16.astype(np.uint32) << 16).view(np.float32)


E4M3_VALUES = np.array(sorted({(1 + m / 8) * 2.0 ** (e - 7) for e in range(1, 16) for m in range(8) if not (e == 15 and m == 7)}
                              | {m * 2.0 ** -9 for m in range(8)}))


def to_e4m3(x):
    s = np.abs(x).max(axis=1, keepdims=True)
    y = np.clip(np.abs(x) * (448.0 / np.where(s > 0, s, 1)), 0, 448)
    idx = np.clip(np.searchsorted(E4M3_VALUES, y), 1, len(E4M3_VALUES) - 1)
    lo, hi = E4M3_VALUES[idx - 1], E4M3_VALUES[idx]
    pick = np.where((y - lo) < (hi - y), idx - 1, np.where((y - lo) > (hi - y), idx, np.where((idx - 1) % 2 == 0, idx - 1, idx)))
    return (pick.astype(np.uint8) | (np.signbit(x).astype(np.uint8) << 7))


def hadamard_rows(x, rng):
    k = x.shape[1]
    n = 1 << (k.bit_length() - 1)
    y = x[:, :n] * rng.choice((-1.0, 1.0), n)
    h = 1
    while h < n:
        y = y.reshape(y.shape[0], -1, 2, h)
        y = np.concatenate((y[:, :, 0] + y[:, :, 1], y[:, :, 0] - y[:, :, 1]), axis=2).reshape(y.shape[0], n)
        h *= 2
    return y / np.sqrt(n) * rng.choice((-1.0, 1.0), n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shards", nargs="+")
    ap.add_argument("--max-tensors", type=int, default=12)
    ap.add_argument("--max-elems", type=int, default=1 << 23)
    args = ap.parse_args()
    rng = np.random.default_rng(20260930)
    done = 0
    for path in args.shards:
        for name, shape, w in tensors(path):
            if done >= args.max_tensors:
                return
            rows = max(1, min(shape[0], args.max_elems // shape[1]))
            w = np.ascontiguousarray(w[:rows])
            hi, lo = (w >> 8).astype(np.uint8), (w & 0xFF).astype(np.uint8)
            x = bf16_to_f32(w).astype(np.float64)
            q = to_e4m3(x)
            qr = to_e4m3(hadamard_rows(x, rng))
            out = dict(tensor=name, shape=shape, sampled_rows=rows,
                       bf16_entropy_bits=entropy_bits(w), bf16_lzma_ratio=lzma_ratio([hi.tobytes(), lo.tobytes()]),
                       e4m3_entropy_bits=entropy_bits(q), e4m3_lzma_ratio=lzma_ratio([q.tobytes()]),
                       e4m3_rot_entropy_bits=entropy_bits(qr), e4m3_rot_lzma_ratio=lzma_ratio([qr.tobytes()]))
            print(json.dumps(out), flush=True)
            done += 1


if __name__ == "__main__":
    main()
