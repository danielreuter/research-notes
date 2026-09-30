"""Candidate f32 sequences for sm_120's `_C.silu_and_mul` and `_C.rotary_embedding`, scored over EVERY captured word (lane
vllm-sm120-kernels).  silu: the registered stand-in (RN32 of the exact g / (1 + e^-g)) vs `g / (1 + NvExpf(-g))` with IEEE division;
rotary: fma(x, c, -RN(y s)) (RopeOut_v1) vs fma(-y, s, RN(x c)) vs RN(RN(x c) - RN(y s)); each with the NaN word 0x7FC0 or 0x7FFF.

    python sm120_edge_probe.py MOE_DIR ROPE_DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from verity.evaluation import evaluate
from verity.ir.defs import bind
from verity_vllm.program.registry import moe as M
from verity_vllm.program.registry import prims as P

f32 = np.float32
np.seterr(all="ignore")


def bf(w):
    return (np.asarray(w, np.uint32) << 16).view(np.float32)


def to_bf16(x, nan):
    x = np.asarray(x, np.float32)
    u = x.view(np.uint32).astype(np.uint64)
    r = ((u + 0x7FFF + ((u >> 16) & 1)) >> 16).astype(np.uint16)
    return np.where(np.isnan(x), np.uint16(nan), r)


_EXP: dict[int, int] = {}


def nv_expf(x: np.ndarray) -> np.ndarray:
    bits = np.asarray(x, np.float32).view(np.uint32)
    out = np.empty_like(bits)
    for i, b in enumerate(bits.tolist()):
        if b not in _EXP:
            _EXP[b] = evaluate(bind(M.NvExpf), [b])[0]
        out[i] = _EXP[b]
    return out.view(np.float32)


def silu(moe: Path) -> dict:
    man = json.loads((moe / "manifest.json").read_text())
    score: dict[str, int] = {}
    words = 0
    for rec in man["cases"]:
        st = rec["statics"]; I, TOPK, Mt = int(st["I"]), int(st["TOPK"]), int(st["M"])
        c = moe / f"case_{rec['i']}"
        up = np.load(c / "out_0.npy").reshape(-1, 2 * I)
        act = np.load(c / "out_1.npy").reshape(-1, I)
        g, u = bf(up[:, :I]).reshape(-1), bf(up[:, I:]).reshape(-1)
        want = act.reshape(-1)
        words += want.size
        reg = np.array([P._silu_f32_bits(int(b)) for b in g.view(np.uint32).tolist()], np.uint32).view(np.float32)
        gpu = (g / (f32(1) + nv_expf(-g)).astype(f32)).astype(f32)
        for name, s in (("registered_exact", reg), ("div_nvexpf", gpu)):
            for nan in (0x7FC0, 0x7FFF):
                out = to_bf16(bf(to_bf16(s, nan)) * u, nan)
                k = f"{name}/nan{nan:#06x}"
                score[k] = score.get(k, 0) + int((out != want).sum())
    return {"words": words, "mismatches": score}


def rope(d: Path) -> dict:
    man = json.loads((d / "manifest.json").read_text())
    score: dict[str, int] = {}
    words = 0
    for rec in man["cases"]:
        st = rec["statics"]; D = int(st["D"]); R = D // 2
        c = d / f"case_{rec['i']}"
        cs = bf(np.load(c / "in_2.npy")); cos, sin = cs[:R], cs[R:]
        for xin, o in (("in_0.npy", "out_0.npy"), ("in_1.npy", "out_1.npy")):
            h = bf(np.load(c / xin)).reshape(-1, D); want = np.load(c / o).reshape(-1, D)
            x, y = h[:, :R], h[:, R:]
            words += want.size
            x64, y64, c64, s64 = (a.astype(np.float64) for a in (x, y, cos, sin))
            cands = {
                "fma_x_c_minus_RNys": ((x64 * c64 - (y * sin).astype(f32).astype(np.float64)).astype(f32),
                                       (y64 * c64 + (x * sin).astype(f32).astype(np.float64)).astype(f32)),
                "fma_y_s_plus_RNxc": (((x * cos).astype(f32).astype(np.float64) - y64 * s64).astype(f32),
                                      ((y * cos).astype(f32).astype(np.float64) + x64 * s64).astype(f32)),
                "no_fma": (((x * cos).astype(f32) - (y * sin).astype(f32)).astype(f32), ((y * cos).astype(f32) + (x * sin).astype(f32)).astype(f32)),
            }
            for name, (lo, hi) in cands.items():
                for nan in (0x7FC0, 0x7FFF):
                    out = np.concatenate([to_bf16(lo, nan), to_bf16(hi, nan)], axis=1)
                    k = f"{name}/nan{nan:#06x}"
                    score[k] = score.get(k, 0) + int((out != want).sum())
    return {"words": words, "mismatches": score,
            "note": "float64 products of two f32 values are exact only below 2^-1022 underflow and when no f32 product overflows; "
                    "a fused a*b+c is emulated as RN32(exact a*b + c) through float64 (exact for bf16 x bf16 products)"}


def main() -> int:
    rep = {"silu": silu(Path(sys.argv[1])), "rope": rope(Path(sys.argv[2]))}
    print(json.dumps(rep, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
