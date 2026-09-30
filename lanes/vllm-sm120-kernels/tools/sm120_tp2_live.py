"""Live two-rank collectives on sm_120 (lane vllm-sm120-kernels; two-GPU pod, torch venv, cwd integrations/vllm).

A tiny TP2 vLLM engine built as a TP2 config run builds it (the engine profile's env pins, `disable_custom_all_reduce=True`;
NCCL_P2P_DISABLE=1 from the caller), then in every worker vLLM's own `tensor_model_parallel_all_reduce` / `_all_gather(dim=-1)` on
seeded bf16 words (both ranks draw the same [2, N] words and contribute row `rank`).  Every rank's received words are checked against
`AllReduce2_v1{N}` / `AllGather2_v1{N}` (`registry.collectives_difftest.spec`), and the engine's greedy tokens are recorded.

    python sm120_tp2_live.py OUT_DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

SHAPES = (2048, 576, 4096, 1536, 64)
KINDS = ("random", "zeros", "max", "subnormal", "alternating")
CASES = [(n, k) for n in SHAPES for k in KINDS]


def _w_collectives(worker) -> dict:
    import torch
    from vllm.distributed import (get_tensor_model_parallel_rank, tensor_model_parallel_all_gather,
                                  tensor_model_parallel_all_reduce)

    from verity_vllm.properties.admission import words_for

    r = get_tensor_model_parallel_rank()
    got = []
    for i, (n, kind) in enumerate(CASES):
        w = words_for(kind, [2, n], "bfloat16", np.random.default_rng(1000 + i))
        t = torch.from_numpy(w[r].view(np.int16).copy()).view(torch.bfloat16).cuda()
        ar = tensor_model_parallel_all_reduce(t.clone())
        ag = tensor_model_parallel_all_gather(t.clone(), dim=-1)
        torch.cuda.synchronize()
        got.append({"ar": ar.cpu().view(torch.int16).numpy().view(np.uint16).tolist(),
                    "ag": ag.cpu().view(torch.int16).numpy().view(np.uint16).tolist()})
    return {"rank": r, "got": got, "device": torch.cuda.get_device_name(), "nccl": ".".join(map(str, torch.cuda.nccl.version()))}


def main() -> int:
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    from verity_vllm.engine import engine_profile as prof
    env_flags = prof.apply_env()
    from vllm import LLM, SamplingParams

    from tests.properties.vocab_range_exactness_gpu import PROMPTS, make_tiny
    from verity_vllm.program.registry import collectives_difftest as CD
    from verity_vllm.properties.admission import evaluate_spec, words_for

    tok = prof.checkpoint_for("B0", "manifests/checkpoints.json")["local_path"]
    d = str(out / "tiny-llama")
    make_tiny(tok, d, 20260930)
    llm = LLM(model=d, tokenizer=d, dtype="bfloat16", seed=0, max_model_len=512, gpu_memory_utilization=0.5, tensor_parallel_size=2,
              enforce_eager=True, disable_custom_all_reduce=True, enable_prefix_caching=False, max_num_seqs=4)
    tokens = [list(o.outputs[0].token_ids) for o in llm.generate(list(PROMPTS), SamplingParams(temperature=0.0, max_tokens=8, ignore_eos=True),
                                                                 use_tqdm=False)]
    ranks = sorted(llm.collective_rpc(_w_collectives), key=lambda x: x["rank"])
    rep = {"env_flags": env_flags, "ranks": [{k: v for k, v in x.items() if k != "got"} for x in ranks], "tokens": tokens, "cases": []}
    ok = len(ranks) == 2
    for i, (n, kind) in enumerate(CASES):
        w = words_for(kind, [2, n], "bfloat16", np.random.default_rng(1000 + i))
        row = {"N": n, "kind": kind}
        for op, key in (("all_reduce", "ar"), ("all_gather", "ag")):
            want = [int(v) for v in evaluate_spec(CD.spec({"op": op, "N": n}), [w[0], w[1]])]
            diffs = [sum(a != b for a, b in zip(x["got"][i][key], want)) + abs(len(x["got"][i][key]) - len(want)) for x in ranks]
            row[op] = {"words": len(want), "diff_rank0": diffs[0], "diff_rank1": diffs[1]}
            ok &= diffs == [0, 0]
        rep["cases"].append(row)
    rep["ok"] = bool(ok)
    (out / "tp2_live.json").write_text(json.dumps(rep, indent=1))
    print("TP2-LIVE", "OK" if ok else "FAIL", json.dumps({"cases": len(CASES), "ranks": rep["ranks"], "tokens0": tokens[0]}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
