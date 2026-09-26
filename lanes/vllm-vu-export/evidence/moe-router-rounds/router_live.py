"""router_live.py N OUT: vLLM's `_moe_C.topk_softmax` on an L40S against MoeRouterTopKRounds[Norm]_v1 and the kernel-order MoeRouterTopK[Norm]_v1,
bit for bit (weights as f32 words, ids), on router_eq.py's edge rows plus N random rows per (E, TOPK, VPT) in {(64, 8, 8), (128, 8, 8)}."""
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from router_eq import cases  # noqa: E402

N, OUT = int(sys.argv[1]), sys.argv[2]
_DEFS = None


def _defs(E, TOPK, VPT, renorm):
    from verity.ir.defs import bind
    from verity_vllm.program.registry import moe
    old, new = (moe.MoeRouterTopKNorm, moe.MoeRouterTopKRoundsNorm) if renorm else (moe.MoeRouterTopK, moe.MoeRouterTopKRounds)
    return bind(old, E=E, TOPK=TOPK, VPT=VPT), bind(new, E=E, TOPK=TOPK, VPT=VPT)


def _eval(job):
    E, TOPK, VPT, renorm, row = job
    from verity.evaluation import evaluate
    old, new = _defs(E, TOPK, VPT, renorm)
    return [int(x) & 0xFFFFFFFF for x in evaluate(new, row)], [int(x) & 0xFFFFFFFF for x in evaluate(old, row)]


def kernel(rows, TOPK, renorm):
    import vllm  # noqa: F401  (registers torch.ops._moe_C)
    x = torch.from_numpy(np.array(rows, dtype=np.uint16).view(np.int16)).view(torch.bfloat16).cuda()
    M = x.shape[0]
    w = torch.empty(M, TOPK, dtype=torch.float32, device="cuda")
    ids = torch.empty(M, TOPK, dtype=torch.int32, device="cuda")
    tei = torch.empty(M, TOPK, dtype=torch.int32, device="cuda")
    op = torch.ops._moe_C.topk_softmax
    for args in ((w, ids, tei, x, renorm, None, None), (w, ids, tei, x, renorm, None), (w, ids, tei, x, renorm)):
        try:
            op(*args)
            break
        except (RuntimeError, TypeError) as e:
            err = e
    else:
        raise err
    torch.cuda.synchronize()
    wb = w.cpu().view(torch.int32).numpy().astype(np.int64) & 0xFFFFFFFF
    return [list(map(int, wb[i])) + list(map(int, ids.cpu().numpy()[i].astype(np.int64) & 0xFFFFFFFF)) for i in range(M)]


def main():
    rng = np.random.default_rng(20260926 + 1)
    report = {"torch": torch.__version__, "device": torch.cuda.get_device_name(0), "cases": {}}
    import vllm
    report["vllm"] = getattr(vllm, "__version__", None)
    with Pool(max(1, (os.cpu_count() or 4) - 2)) as pool:
        for E, TOPK, VPT in ((64, 8, 8), (128, 8, 8)):
            named = cases(E, rng, N)
            names, rows = list(named), list(named.values())
            for renorm in (False, True):
                t = time.time()
                k = kernel(rows, TOPK, renorm)
                ev = pool.map(_eval, [(E, TOPK, VPT, renorm, r) for r in rows], chunksize=4)
                bad_new = [names[i] for i in range(len(rows)) if ev[i][0] != k[i]]
                bad_old = [names[i] for i in range(len(rows)) if ev[i][1] != k[i]]
                first = next((i for i in range(len(rows)) if ev[i][0] != k[i]), None)
                key = f"E={E},TOPK={TOPK},VPT={VPT},renormalize={renorm}"
                report["cases"][key] = {"rows": len(rows), "rounds_unequal_to_kernel": len(bad_new), "kernel_order_unequal_to_kernel": len(bad_old),
                                        "rounds_unequal_names": bad_new[:20], "kernel_order_unequal_names": bad_old[:20],
                                        "first": None if first is None else {"case": names[first], "row": rows[first], "kernel": k[first],
                                                                             "rounds": ev[first][0], "kernel_order": ev[first][1]},
                                        "seconds": round(time.time() - t, 1)}
                print(key, len(rows), "rows; rounds != kernel:", len(bad_new), "; kernel-order != kernel:", len(bad_old), bad_new[:6], flush=True)
    json.dump(report, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
