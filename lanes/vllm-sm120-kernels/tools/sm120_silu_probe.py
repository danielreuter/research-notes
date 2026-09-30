"""Which `silu` does sm_120's `_C.silu_and_mul` compute?  On job B's fused-MoE capture (the w13 output = the silu_and_mul input, the w2
input = its output), the words where `SiluMul_v1` differs, against candidate f32 silu sequences (lane vllm-sm120-kernels).

    python sm120_silu_probe.py MOE_DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from verity.evaluation import evaluate
from verity.ir.defs import bind
from verity_vllm.program.kernels.kernel_registry import instance
from verity_vllm.program.kernels import twins  # noqa: F401
from verity_vllm.program.registry import b1, moe as M

f32 = np.float32


def bf(w):
    return (np.asarray(w, np.uint32) << 16).view(np.float32)


def to_bf16(x):
    u = np.asarray(x, np.float32).view(np.uint32).astype(np.uint64)
    r = ((u + 0x7FFF + ((u >> 16) & 1)) >> 16).astype(np.uint16)
    return np.where(np.isnan(np.asarray(x, np.float32)), np.uint16(0x7FC0), r)


def nv_expf(x: np.ndarray) -> np.ndarray:
    return np.array([evaluate(bind(M.NvExpf), [int(b)])[0] for b in np.asarray(x, np.float32).view(np.uint32)], np.uint32).view(np.float32)


def main() -> int:
    d = Path(sys.argv[1])
    man = json.loads((d / "manifest.json").read_text())
    tw = instance(b1.SiluMul, "twin")
    rows = []
    stats = {"diff": 0, "cand_ieee_div_nvexpf": 0, "cand_mul_rcp_nvexpf": 0}
    for rec in man["cases"]:
        st = rec["statics"]; I, TOPK, M_ = int(st["I"]), int(st["TOPK"]), int(st["M"])
        c = d / f"case_{rec['i']}"
        up = np.load(c / "out_0.npy").reshape(M_ * TOPK, 2 * I)
        act = np.load(c / "out_1.npy").reshape(M_ * TOPK, I)
        for p in range(M_ * TOPK):
            t = np.asarray(tw(up[p].astype(np.uint64), I=I)).astype(np.uint16)
            bad = np.nonzero(t != act[p])[0]
            if not bad.size:
                continue
            g, u = bf(up[p, :I][bad]), bf(up[p, I:][bad])
            fin = np.isfinite(g) & np.isfinite(u)
            e = nv_expf(-g)
            den = (f32(1) + e).astype(f32)
            s_div = (g / den).astype(f32)
            s_rcp = (g * (f32(1) / den).astype(f32)).astype(f32)
            o_div = to_bf16(bf(to_bf16(s_div)) * u)
            o_rcp = to_bf16(bf(to_bf16(s_rcp)) * u)
            stats["diff"] += int(bad.size)
            stats["cand_ieee_div_nvexpf"] += int((o_div == act[p][bad]).sum())
            stats["cand_mul_rcp_nvexpf"] += int((o_rcp == act[p][bad]).sum())
            for j in range(min(3, bad.size)):
                rows.append({"case": rec["i"], "kinds": [s.get("kind") for s in rec["inputs"]][:1], "g": f"{int(up[p, bad[j]]):#06x}",
                             "u": f"{int(up[p, I + bad[j]]):#06x}", "gpu": f"{int(act[p, bad[j]]):#06x}", "twin": f"{int(t[bad[j]]):#06x}",
                             "div_nvexpf": f"{int(o_div[j]):#06x}", "rcp_nvexpf": f"{int(o_rcp[j]):#06x}", "finite": bool(fin[j])})
    print(json.dumps(stats))
    for r in rows[:40]:
        print(json.dumps(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
