"""sm_120 job B diagnostics (lane vllm-sm120-kernels), on the difftest captures of `rope_difftest` and `moe_difftest`:

  * the fused-MoE GEMM stages recomputed on the CAPTURED operands under each k16 step model (Ampere 8+8/w25/-132, the Hopper-shaped
    16/w26/-133 that core measured on the RTX 5090's mma.sync): the w13 output (x_t, W13[e]) and the w2 output (the captured SiLU
    output, W2[e], the routed weight) -- which pipeline does sm_120's fused_moe_kernel run;
  * the twins on the new target: rope.neox.bf16.v1 on every rotary case (query and key), silu_mul.bf16.table.v1 on every MoE pair
    (captured w13 output -> captured w2 input), and the moe_sum reduction (captured w2 output -> block output).

    python sm120_b_diag.py ROPE_DIR MOE_DIR OUT.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from verity.ml.kernels import f2fp_bf16_batch, group_sum_total_batch
from verity.ml.tc.models import AMPERE_BF16_M16N8K16, HOPPER_BF16_M16N8K16
from verity_vllm.program.kernels import twins  # noqa: F401  (registers the twins)
from verity_vllm.program.kernels.kernel_registry import instance
from verity_vllm.program.registry import b1

MODELS = {"ampere_8+8_w25_-132": AMPERE_BF16_M16N8K16, "hopper_16_w26_-133": HOPPER_BF16_M16N8K16}


def chain(model, X: np.ndarray, W: np.ndarray) -> np.ndarray:
    """(P, K) x (P, N, K) bf16 words -> (P, N) f32 words: one ascending k16 chain per coordinate from a zero accumulator."""
    P, N, K = W.shape
    Xb = np.ascontiguousarray(np.broadcast_to(X[:, None, :], (P, N, K))).reshape(P * N, K)
    Wb = W.reshape(P * N, K)
    acc = np.zeros(P * N, np.uint32)
    for s in range(K // 16):
        acc, _ = group_sum_total_batch(model, acc, Xb[:, 16 * s:16 * s + 16], Wb[:, 16 * s:16 * s + 16])
    return acc.astype(np.uint32).reshape(P, N)


def f32(w16):
    return (np.asarray(w16, np.uint32) << 16).view(np.float32)


def moe(d: Path) -> dict:
    man = json.loads((d / "manifest.json").read_text())
    tot = {m: {"up_words": 0, "up_diff": 0, "down_words": 0, "down_diff": 0} for m in MODELS}
    silu = {"words": 0, "diff": 0}
    msum = {"words": 0, "diff": 0}
    per_case = []
    for rec in man["cases"]:
        st = rec["statics"]
        E, TOPK, H, I, M = (int(st[k]) for k in ("E", "TOPK", "H", "I", "M"))
        c = d / f"case_{rec['i']}"
        x = np.load(c / "in_0.npy").reshape(M, H)
        w13 = np.load(c / "in_1.npy").reshape(E, 2 * I, H)
        w2 = np.load(c / "in_2.npy").reshape(E, H, I)
        ids = np.load(c / "in_3.npy").reshape(-1).astype(np.int64)
        g = np.load(c / "in_4.npy").reshape(-1).astype(np.uint32)
        up = np.load(c / "out_0.npy").reshape(M * TOPK, 2 * I)
        act = np.load(c / "out_1.npy").reshape(M * TOPK, I)
        down = np.load(c / "out_2.npy").reshape(M * TOPK, H)
        out = np.load(c / "out_3.npy").reshape(M, H)
        tok = np.repeat(np.arange(M), TOPK)
        row = {"i": rec["i"], "statics": {k: st[k] for k in ("E", "TOPK", "H", "I", "M")}, "kinds": [s.get("kind") for s in rec["inputs"]],
               "launches": st.get("launches")}
        for name, model in MODELS.items():
            u = f2fp_bf16_batch(chain(model, x[tok], w13[ids]).reshape(-1))[0].astype(np.uint16).reshape(up.shape)
            acc = chain(model, act, w2[ids]).view(np.float32) * g.view(np.float32)[:, None]
            dn = f2fp_bf16_batch(acc.astype(np.float32).view(np.uint32).reshape(-1))[0].astype(np.uint16).reshape(down.shape)
            fin_u = np.isfinite(f32(up)); fin_d = np.isfinite(f32(down))
            ud, dd = int((u != up).sum()), int(((dn != down) & fin_d).sum())
            tot[name]["up_words"] += up.size; tot[name]["up_diff"] += ud
            tot[name]["down_words"] += int(fin_d.sum()); tot[name]["down_diff"] += dd
            row[name] = {"up_diff": ud, "up_diff_finite": int(((u != up) & fin_u).sum()), "down_diff_finite": dd}
        s_tw = instance(b1.SiluMul, "twin")
        sd = sum(int((np.asarray(s_tw(up[p].astype(np.uint64), I=I)).astype(np.uint16) != act[p]).sum()) for p in range(M * TOPK))
        silu["words"] += act.size; silu["diff"] += sd
        ms = np.zeros((M, H), np.float32)
        for k in range(TOPK):
            ms = (ms + f32(down.reshape(M, TOPK, H)[:, k, :])).astype(np.float32)
        msd = int((f2fp_bf16_batch(ms.view(np.uint32).reshape(-1))[0].astype(np.uint16).reshape(M, H) != out).sum())
        msum["words"] += out.size; msum["diff"] += msd
        row.update(silu_twin_diff=sd, moe_sum_diff=msd)
        per_case.append(row)
    return {"models": tot, "silu_twin": silu, "moe_sum": msum, "cases": per_case}


def rope(d: Path) -> dict:
    man = json.loads((d / "manifest.json").read_text())
    tw = instance(b1.RoPE, "twin")
    words = diff = 0
    for rec in man["cases"]:
        st = rec["statics"]
        c = d / f"case_{rec['i']}"
        q, k, cs = (np.load(c / f"in_{j}.npy").astype(np.uint64) for j in range(3))
        for x, nh, o in ((q, st["NH"], "out_0.npy"), (k, st["KVH"], "out_1.npy")):
            want = np.load(c / o).reshape(-1)
            got = np.asarray(tw(x, cs, NHEADS=int(nh), D=int(st["D"]))).astype(np.uint16)
            words += want.size; diff += int((got != want).sum())
    return {"twin": "rope.neox.bf16.v1", "words": words, "diff": diff}


def main() -> int:
    rep = {"rope": rope(Path(sys.argv[1])), "moe": moe(Path(sys.argv[2]))}
    Path(sys.argv[3]).write_text(json.dumps(rep, indent=1))
    print(json.dumps({"rope": rep["rope"], "moe_models": rep["moe"]["models"], "silu_twin": rep["moe"]["silu_twin"], "moe_sum": rep["moe"]["moe_sum"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
