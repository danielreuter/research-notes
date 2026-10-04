"""Host half of `scalar_model_sm120.cu`: samples for the device, and the comparison with the pinned Python models.
  mkcast OUT / mkfadd OUT          write a sample of FP32 inputs (u32 LE) or input pairs
  cmpcast IN DEV / cmpfadd IN DEV  compare the device's outputs with `pearl_kw.f32_to_fp8` / `verity.ml.tc.fp32.add`
Run from a source tree with PYTHONPATH=packages/verity/src:protocols/pouw.
"""
import json
import random
import struct
import sys

from verity.ml.tc import fp32
from verity_pouw.schemes import pearl_kw as P


def f32(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def e4m3_vals():
    return [P.fp8_to_f32(c) for c in range(256) if c & 0x7F != 0x7F]


def cast_sample(rng):
    out = set()
    vals = sorted(set(e4m3_vals()))
    for v in vals:
        u = f32(v)
        out.update({u, (u + 1) & 0xFFFFFFFF, (u - 1) & 0xFFFFFFFF})
    for a, b in zip(vals, vals[1:]):
        mid = f32((a + b) / 2)                           # exact in FP32: E4M3 neighbours differ by one quantum
        out.update({mid, mid + 1, mid - 1})
    for v in (448.0, 464.0, 480.0, 496.0, 512.0, 1e30, 2.0 ** -10, 2.0 ** -9, 1.5 * 2.0 ** -10, 2.0 ** -11, 2.0 ** -7):
        for s in (1.0, -1.0):
            u = f32(s * v)
            out.update({u, u + 1, u - 1})
    for e in range(90, 150):                             # dense around E4M3's range: every exponent, random mantissas
        for _ in range(20000):
            out.add((rng.getrandbits(1) << 31) | (e << 23) | rng.getrandbits(23))
    for e in range(1, 90):                               # far below: all round to +-0
        for _ in range(500):
            out.add((rng.getrandbits(1) << 31) | (e << 23) | rng.getrandbits(23))
    for _ in range(300000):
        u = rng.getrandbits(32)
        if (u >> 23) & 0xFF != 0xFF:
            out.add(u)
    out.update({0, 0x80000000, 1, 0x80000001, 0x7F7FFFFF, 0xFF7FFFFF})
    return sorted(u for u in out if (u >> 23) & 0xFF != 0xFF)


def fadd_sample(rng, n=1_000_000):
    def pick():
        cls = rng.randrange(4)
        e = 0 if cls == 0 else rng.randrange(1, 5) if cls == 1 else rng.randrange(120, 136) if cls == 2 else rng.randrange(1, 255)
        m = rng.getrandbits(23)
        if rng.randrange(8) == 0:
            m &= 0x7FFF00
        return (rng.getrandbits(1) << 31) | (e << 23) | m
    pairs = []
    for i in range(n):
        a = pick()
        b = ((a ^ 0x80000000) + rng.randrange(-3, 4)) & 0xFFFFFFFF if i % 4 == 0 else pick()
        if (b >> 23) & 0xFF == 0xFF:
            b = pick()
        pairs.append((a, b))
    return pairs


def main():
    mode = sys.argv[1]
    rng = random.Random(f"scalar-model-sm120/{mode}")
    if mode == "mkcast":
        s = cast_sample(rng)
        open(sys.argv[2], "wb").write(struct.pack(f"<{len(s)}I", *s))
    elif mode == "mkfadd":
        p = fadd_sample(rng)
        open(sys.argv[2], "wb").write(struct.pack(f"<{2 * len(p)}I", *[w for ab in p for w in ab]))
    elif mode == "cmpcast":
        raw = open(sys.argv[2], "rb").read()
        ins = struct.unpack(f"<{len(raw) // 4}I", raw)
        dev = open(sys.argv[3], "rb").read()
        bad, first, sub = 0, [], 0
        for u, d in zip(ins, dev):
            want = P.f32_to_fp8(P.f32_of_bits(u))
            sub += want & 0x78 == 0 and want & 7 != 0
            if d != want:
                bad += 1
                if len(first) < 5:
                    first.append([u, d, want])
        print(json.dumps(dict(check="cast-vs-pearl_kw.f32_to_fp8", n=len(ins), subnormal_codes=sub, bad=bad, first=first)))
    elif mode == "cmpfadd":
        raw = open(sys.argv[2], "rb").read()
        w = struct.unpack(f"<{len(raw) // 4}I", raw)
        dev = open(sys.argv[3], "rb").read()
        d = struct.unpack(f"<{len(dev) // 4}I", dev)
        bad, first, sub = 0, [], 0
        for i, got in enumerate(d):
            a, b = w[2 * i], w[2 * i + 1]
            want = fp32.add(a, b)
            sub += any((x >> 23) & 0xFF == 0 and x & 0x7FFFFF for x in (a, b, want))
            if got != want:
                bad += 1
                if len(first) < 5:
                    first.append([a, b, got, want])
        print(json.dumps(dict(check="fadd-vs-verity.ml.tc.fp32.add", n=len(d), subnormal_cases=sub, bad=bad, first=first)))


if __name__ == "__main__":
    main()
