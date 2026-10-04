"""Host half of `divsqrt_ftz_sm120.cu`: a sample of (a, b) pairs, and the device's div and sqrt against the pinned models.
  mk OUT        write 1,000,000 pairs (u32 LE), weighted to subnormals, ties and the overflow edge; no NaN or Inf inputs
  cmp IN DEV    compare the device's (a / b, sqrt(a)) with `verity.ml.tc.fp32.div` and `fp32.sqrt` bit for bit
"""
import json
import random
import struct
import sys

from verity.ml.tc import fp32


def pick(rng):
    cls = rng.randrange(5)
    e = (0 if cls == 0 else rng.randrange(1, 9) if cls == 1 else rng.randrange(247, 255) if cls == 2
         else rng.randrange(120, 136) if cls == 3 else rng.randrange(1, 255))
    m = rng.getrandbits(23)
    if rng.randrange(8) == 0:
        m &= 0x7F0000
    return (rng.getrandbits(1) << 31) | (e << 23) | m


def main():
    if sys.argv[1] == "mk":
        rng = random.Random("divsqrt-ftz-sm120")
        w = []
        for _ in range(1_000_000):
            a, b = pick(rng), pick(rng)
            if b & 0x7FFFFFFF == 0:
                b = 0x3F800000
            w += [a, b]
        open(sys.argv[2], "wb").write(struct.pack(f"<{len(w)}I", *w))
        return
    raw = open(sys.argv[2], "rb").read()
    w = struct.unpack(f"<{len(raw) // 4}I", raw)
    d = struct.unpack(f"<{len(raw) // 4}I", open(sys.argv[3], "rb").read())
    bad_div = bad_sqrt = sub = n_sqrt = 0
    first = []
    for i in range(len(w) // 2):
        a, b = w[2 * i], w[2 * i + 1]
        q = fp32.div(a, b)
        sub += any((x >> 23) & 0xFF == 0 and x & 0x7FFFFF for x in (a, b, q))
        if d[2 * i] != q:
            bad_div += 1
            if len(first) < 5:
                first.append(["div", a, b, d[2 * i], q])
        if not a >> 31:                                  # sqrt of non-negative inputs (negative gives NaN either way)
            n_sqrt += 1
            s = fp32.sqrt(a)
            if d[2 * i + 1] != s:
                bad_sqrt += 1
                if len(first) < 5:
                    first.append(["sqrt", a, d[2 * i + 1], s])
    print(json.dumps(dict(check="vs-verity.ml.tc.fp32", pairs=len(w) // 2, subnormal_cases=sub, div_bad=bad_div,
                          sqrt_inputs=n_sqrt, sqrt_bad=bad_sqrt, first=first)))


if __name__ == "__main__":
    main()
