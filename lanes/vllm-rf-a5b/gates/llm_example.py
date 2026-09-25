"""verity_vllm.LLM(...).generate(...) against plain vllm.LLM on one GPU, each in its own process.

    python llm_example.py verity OUT      verity_vllm.LLM; writes OUT/verity.json and OUT/engine_record.json
    python llm_example.py vllm-same OUT   vllm.LLM(**engine_record.engine_kwargs) under engine_record.env_flags
    python llm_example.py vllm-plain OUT  vllm.LLM(model=<snapshot>, dtype=bfloat16, enforce_eager=True, seed=0,
                                          max_num_seqs=8, enable_prefix_caching=False), no profile environment
    python llm_example.py compare OUT     token ids of every request and sampling mode, equal or not
"""
import json
import os
import sys

MODEL, REV = "unsloth/Llama-3.2-1B", "9535bd9b1d1dea6acafbdc4813b728796aeb28da"
PROMPTS = ["The capital of France is", "def fibonacci(n):", "Verifiable inference means that", "1, 1, 2, 3, 5, 8,",
           "Once upon a time, in a small village", "The three laws of thermodynamics are"]


def sampling():
    from vllm import SamplingParams
    return {"greedy": SamplingParams(temperature=0.0, max_tokens=48),
            "sampled": SamplingParams(temperature=0.8, top_p=0.95, max_tokens=48, seed=1234)}


def run(generate, out, name):
    res = {}
    for mode, sp in sampling().items():
        outs = generate(PROMPTS, sp)
        res[mode] = [[list(c.token_ids) for c in o.outputs] for o in outs]
        res[mode + "_text"] = [o.outputs[0].text for o in outs]
    json.dump(res, open(os.path.join(out, f"{name}.json"), "w"))
    print(name, json.dumps({k: v for k, v in res.items() if k.endswith("_text")})[:1500])


def main():
    what, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if what == "verity":
        from verity_vllm import LLM
        llm = LLM(MODEL, revision=REV)
        json.dump(llm.engine_record, open(os.path.join(out, "engine_record.json"), "w"), default=str, indent=1)
        run(llm.generate, out, "verity")
        print("records", len(llm.records), "requests", [len(r.requests) for r in llm.records])
    elif what == "vllm-same":
        rec = json.load(open(os.path.join(out, "engine_record.json")))
        os.environ.update({k: str(v) for k, v in rec["env_flags"].items()})
        from vllm import LLM
        print("engine_kwargs", rec["engine_kwargs"], "env_flags", rec["env_flags"])
        run(LLM(**rec["engine_kwargs"]).generate, out, "vllm-same")
    elif what == "vllm-plain":
        rec = json.load(open(os.path.join(out, "engine_record.json")))
        from vllm import LLM
        llm = LLM(model=rec["pin"]["local_path"], dtype="bfloat16", enforce_eager=True, seed=0, max_num_seqs=8,
                  enable_prefix_caching=False)
        run(llm.generate, out, "vllm-plain")
    elif what == "compare":
        v = json.load(open(os.path.join(out, "verity.json")))
        ok = True
        for other in ("vllm-same", "vllm-plain"):
            o = json.load(open(os.path.join(out, f"{other}.json")))
            for mode in ("greedy", "sampled"):
                eq = v[mode] == o[mode]
                ok &= eq or other == "vllm-plain"
                print(f"verity vs {other} {mode}: {'EQUAL' if eq else 'DIFFERENT'} ({len(v[mode])} requests)")
        print("RESULT", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
