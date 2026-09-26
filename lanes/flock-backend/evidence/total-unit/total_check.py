import sys, random
sys.path.insert(0, "/tmp/fp"); sys.path.insert(0, "/workspace/backends/flock/python")
from total_proto import build, tc_total
from verity.ml.tc import total, models
from verity.ml.tc.cast import f32_to_bf16_hw_word
pipe = getattr(total, "AMPERE_BF16_M16N8K16", None) or getattr(models, "AMPERE_BF16_M16N8K16")
C = build(tc_total)
rng = random.Random(7)
SPEC16 = [0x7F80, 0xFF80, 0x7FC0, 0x7F81, 0xFFFF, 0x0000, 0x8000, 0x0001, 0x7F7F, 0xFF7F]
SPEC32 = [0x7F800000, 0xFF800000, 0x7FC00000, 0x7F800001, 0, 0x80000000, 0x7F7FFFFF, 0xFF7FFFFF, 1]
def near(e0):
    return (rng.getrandbits(1) << 15) | (min(254, max(0, e0 + rng.randint(-8, 8))) << 7) | rng.getrandbits(7)
def op(p, e0=None):
    if e0 is not None and rng.random() >= p: return near(e0)
    r = rng.random()
    if r < p: return rng.choice(SPEC16)
    return rng.getrandbits(16)
T = 64; bad = 0; n = 0; nonfin = 0
for batch in range(200):
    cases = []
    for t in range(T):
        p = [0.0, 0.02, 0.1, 0.5][t % 4]
        e0 = rng.randint(0, 254) if t % 2 == 0 else None
        x = [op(p, e0) for _ in range(16)]; w = [op(p, e0) for _ in range(16)]
        c = rng.choice(SPEC32) if rng.random() < p else ((rng.getrandbits(1) << 31) | (min(254, max(0, 2*e0 - 127 + rng.randint(-20, 20))) << 23) | rng.getrandbits(23) if e0 is not None else rng.getrandbits(32))
        cases.append((x, w, c))
    iv = {"x": [0]*256, "w": [0]*256, "c": [0]*32}
    for t, (x, w, c) in enumerate(cases):
        for i in range(16):
            for bb in range(16):
                iv["x"][i*16+bb] |= ((x[i] >> bb) & 1) << t
                iv["w"][i*16+bb] |= ((w[i] >> bb) & 1) << t
        for bb in range(32): iv["c"][bb] |= ((c >> bb) & 1) << t
    outs, fail = C.evaluate(iv, T)
    for t, (x, w, c) in enumerate(cases):
        got = sum(((outs["c_out"][bb] >> t) & 1) << bb for bb in range(32))
        y = sum(((outs["y16"][bb] >> t) & 1) << bb for bb in range(16))
        want = total.tc_dot_total(pipe, c, x, w)
        n += 1; nonfin += (want >> 23) & 0xFF == 0xFF
        if got != want or y != f32_to_bf16_hw_word(want): bad += 1
print("cases", n, "non-finite results", nonfin, "mismatches", bad)
