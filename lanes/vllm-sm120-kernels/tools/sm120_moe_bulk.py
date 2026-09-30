"""sm_120 fused-MoE step discrimination at volume (lane vllm-sm120-kernels; pod, torch venv).

The admission difftest's shapes are sized for the plain evaluator; at bf16 outputs the Ampere (8+8, w25, -132) and the Hopper-shaped
(16, w26, -133) k16 steps disagree on only ~1 in 4k words at K <= 512.  This runs `moe_difftest.production` (vLLM's fused_experts,
both fused_moe_kernel launches recorded) at OLMoE-like width, H = 2048, I = 1024, E = 8, TOPK = 2, M = 16, on CASES cases (half with
per-element exponents spread over 2^-8..2^8), and recomputes both GEMM stages on the captured operands under each step model with
core's vectorized kernel.

    python sm120_moe_bulk.py OUT.json [CASES]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sm120_b_diag import MODELS, chain, f32  # noqa: E402

from verity.ml.kernels import f2fp_bf16_batch  # noqa: E402
from verity_vllm.program.registry import moe_difftest as MD  # noqa: E402


def words(t: torch.Tensor) -> np.ndarray:
    return t.detach().contiguous().cpu().view(torch.int16).numpy().view(np.uint16)


def main() -> int:
    out, n = Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else 16
    E, TOPK, H, I, M = 8, 2, 2048, 1024, 16
    gen = torch.Generator(device="cuda").manual_seed(20260930)
    tot = {m: {"up_words": 0, "up_diff": 0, "down_words": 0, "down_diff": 0} for m in MODELS}
    cases = []
    for c in range(n):
        wide = c % 2 == 1

        def draw(*shape):
            v = torch.randn(*shape, generator=gen, device="cuda")
            if wide:
                v = v * torch.exp2(torch.randint(-8, 9, shape, generator=gen, device="cuda").float())
            return v.to(torch.bfloat16)

        x, w13, w2 = draw(M * H), draw(E * 2 * I * H) * 0.05, draw(E * H * I) * 0.05
        ids = torch.stack([torch.randperm(E, generator=gen, device="cuda")[:TOPK] for _ in range(M)]).to(torch.int32).reshape(-1)
        g = torch.softmax(torch.randn(M, TOPK, generator=gen, device="cuda"), -1).reshape(-1).float()
        st = {"E": E, "TOPK": TOPK, "H": H, "I": I, "M": M}
        up_t, act_t, down_t, _ = MD.production(st, [x, w13, w2, ids, g])
        X, W13, W2 = words(x).reshape(M, H), words(w13).reshape(E, 2 * I, H), words(w2).reshape(E, H, I)
        idn, gn = ids.cpu().numpy().astype(np.int64), g.cpu().numpy().astype(np.float32)
        up, act, down = words(up_t).reshape(M * TOPK, 2 * I), words(act_t).reshape(M * TOPK, I), words(down_t).reshape(M * TOPK, H)
        tok = np.repeat(np.arange(M), TOPK)
        row = {"case": c, "wide": wide, "launches": st.get("launches")}
        for name, model in MODELS.items():
            u = f2fp_bf16_batch(chain(model, X[tok], W13[idn]).reshape(-1))[0].astype(np.uint16).reshape(up.shape)
            acc = chain(model, act, W2[idn]).view(np.float32) * gn[:, None]
            dn = f2fp_bf16_batch(acc.astype(np.float32).view(np.uint32).reshape(-1))[0].astype(np.uint16).reshape(down.shape)
            fin = np.isfinite(f32(down))
            ud, dd = int((u != up).sum()), int(((dn != down) & fin).sum())
            tot[name]["up_words"] += up.size; tot[name]["up_diff"] += ud
            tot[name]["down_words"] += int(fin.sum()); tot[name]["down_diff"] += dd
            row[name] = {"up_diff": ud, "down_diff": dd}
        cases.append(row)
        print(json.dumps(row), flush=True)
    rep = {"shape": {"E": E, "TOPK": TOPK, "H": H, "I": I, "M": M, "cases": n}, "device": torch.cuda.get_device_name(0),
           "cc": list(torch.cuda.get_device_capability(0)), "models": tot, "cases": cases}
    out.write_text(json.dumps(rep, indent=1))
    print("MOE-BULK", json.dumps(tot))
    return 0


if __name__ == "__main__":
    sys.exit(main())
