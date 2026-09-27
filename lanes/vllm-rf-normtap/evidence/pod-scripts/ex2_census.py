"""ex2_census.py FIX OUT DUMP...: the MufuEx2Ftz inputs of #101's committed layer-0 FA2 streams (dump_step{s}_pair0_fa2.m1_L0_g{HB}x{M}x{NB}.bin,
the MS build of #102's evidence run r20260927-013003-0f64: step 0 = the causal prefill, step 1 = a swapped-GQA decode step), from every
visited (slab, row, block)'s ROW word 0 (the running max after the block) and MS word (the IR's max_scaled):

* the rescale input F32MulFtz(F32SubFtz(m_prev, GuardNegInfZero(m)), scale_log2) of every block after a row's first, exactly;
* a bound for every P input F32FmaSubFtz(s, scale_log2, max_scaled): with |max_scaled| >= 2^-15, s * scale_log2 - max_scaled is 0 or a
  nonzero multiple of 2^-63 or more (the exact product's grain is 2^(E_s + E_l - 46) and |s * scale_log2| > 2^-15 - 2^-63 gives
  E_s + E_l >= -17; max_scaled's grain is 2^-38 or more), so it never lies in 0 < |x| < 2^-63, the only inputs the shift clamp changes
  (with max_scaled = 0 the input is s * scale_log2 itself, so a zero row max is counted).
Writes OUT/census.json."""
import json
import re
import sys

import numpy as np

FIX, OUT, *DUMPS = sys.argv[1:]
sys.path[:0] = [f"{FIX}/integrations/vllm", f"{FIX}/packages/verity/src"]
from verity_vllm.commit.hidden_stream import StreamLayout  # noqa: E402
from verity_vllm.program.kernels.derived_rows import guard_neg_inf_zero, mul_ftz, sub_ftz  # noqa: E402
from verity_vllm.properties import fa_tap_exactness as X  # noqa: E402


def f32(w):
    return np.asarray(w, dtype=np.uint32).view(np.float32).astype(np.float64)


res = {}
for path in DUMPS:
    g = re.search(r"dump_step(\d+)_.*_g(\d+)x(\d+)x(\d+)(?:x(\d+)x(\d+))?\.bin$", path)
    step, HB, M, NB, BN, Dh = int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5] or 128), int(g[6] or 64)
    L = StreamLayout(HB, M, NB, BN, Dh, ms=True)
    w = np.fromfile(path, dtype=np.uint32)
    R, o = X._row_plane(w, L), L.offsets
    MS = w[o["MS"]:o["total"]].reshape(HB, M, NB)
    sl2 = np.uint32(X.scale_log2_bits({"softcap": 0.0}, Dh))
    # visited blocks nbm-1 .. 0 (ms_row101.sh): prefill rows by kBlockM 64 against BN; the decode rows visit all NB blocks
    rows = [(h, r, min(NB, -(-((r // 64 + 1) * 64) // BN)) if step == 0 else NB) for h in range(HB) for r in range(M)]
    at = np.array([(h, r, b) for h, r, nbm in rows for b in range(nbm)])
    later = np.array([(h, r, b) for h, r, nbm in rows for b in range(nbm - 1)])
    m, ms = R[at[:, 0], at[:, 1], at[:, 2], 0], MS[at[:, 0], at[:, 1], at[:, 2]]
    rec = {"geometry": [HB, M, NB, BN, Dh], "visited_blocks": int(len(at)), "scale_log2": float(f32(sl2)),
           "ms_is_the_irs_max_scaled": int(np.count_nonzero(ms != mul_ftz(guard_neg_inf_zero(m), sl2))) == 0,
           "row_max_nonfinite": int(np.count_nonzero((m & 0x7F800000) == 0x7F800000)),
           "row_max_zero": int(np.count_nonzero((m & 0x7FFFFFFF) == 0)),
           "min_abs_row_max": float(np.abs(f32(m)).min()), "min_abs_max_scaled": float(np.abs(f32(ms)).min()),
           "max_scaled_below_2^-15": int(np.count_nonzero(np.abs(f32(ms)) < 2.0 ** -15))}
    if len(later):
        mp, mn = R[later[:, 0], later[:, 1], later[:, 2] + 1, 0], R[later[:, 0], later[:, 1], later[:, 2], 0]
        x = mul_ftz(sub_ftz(mp, guard_neg_inf_zero(mn)), sl2)
        e = (x >> 23) & 0xFF
        rec.update(rescale_inputs=int(x.size), rescale_zero=int(np.count_nonzero((x & 0x7FFFFFFF) == 0)),
                   rescale_biased_exponent_1_to_63=int(np.count_nonzero((e >= 1) & (e <= 63))),
                   rescale_min_abs_nonzero=float(np.abs(f32(x[(x & 0x7FFFFFFF) != 0])).min()) if np.any(x & 0x7FFFFFFF) else None)
    rec["p_inputs_in_(0,2^-63)_possible"] = rec["row_max_zero"] > 0 or rec["max_scaled_below_2^-15"] > 0
    res[f"step{step}"] = rec
json.dump(res, open(f"{OUT}/census.json", "w"), indent=1)
print(json.dumps(res, indent=1))
