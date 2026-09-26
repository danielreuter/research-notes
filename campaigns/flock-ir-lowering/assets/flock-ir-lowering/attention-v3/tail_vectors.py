import json, random, sys
from verity_vllm.program.registry import prims as P
from verity.ml import prims as M
rng = random.Random(2026)
sp = [0, 0x80000000, 0x7F800000, 0xFF800000, 0x7FC00000, 0x7FA00001, 0xFFC00003, 1, 0x80000001, 0x7FFFFF, 0x807FFFFF, 0x800000,
      0x7F7FFFFF, 0xFF7FFFFF, 0x3F800000, 0xBF800000, 0x3E38AA3B, 0x42FE0000, 0xC2FE0000, 0x43000000, 0xC3000000]
def w():
    r = rng.random()
    if r < 0.2: return rng.choice(sp)
    if r < 0.5: return (rng.getrandbits(1) << 31) | (rng.randint(100, 150) << 23) | rng.getrandbits(23)
    if r < 0.6: return (rng.getrandbits(1) << 31) | rng.getrandbits(23)
    return rng.getrandbits(32)
prims = {"F32AddFtz_v1": (P.F32AddFtz, 2), "F32SubFtz_v1": (P.F32SubFtz, 2), "F32MulFtz_v1": (P.F32MulFtz, 2), "F32FmaFtz_v1": (P.F32FmaFtz, 3),
         "F32FmaSubFtz_v1": (P.F32FmaSubFtz, 3), "F32Max_v1": (P.F32Max, 2), "GuardNegInfZero_v1": (P.GuardNegInfZero, 1),
         "MufuEx2Ftz_v1": (P.MufuEx2Ftz, 1), "Fa2InvSum_v1": (P.Fa2InvSum, 1), "F2fpBf16_v1": (M.F2fpBf16, 1)}
n = int(sys.argv[2])
out = {}
for pid, (p, k) in prims.items():
    cases = []
    for _ in range(n):
        a = [w() for _ in range(k)]
        if pid == "MufuEx2Ftz_v1" and rng.random() < 0.7:
            a = [(rng.getrandbits(1) << 31) | (rng.randint(90, 135) << 23) | rng.getrandbits(23)]
        cases.append(a + [p.evaluate(*a) & 0xFFFFFFFF])
    out[pid] = cases
json.dump(out, open(sys.argv[1], "w"))
print({k: len(v) for k, v in out.items()})
