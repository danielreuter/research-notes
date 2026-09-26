"""red-team-flock-3: write attention-head input sets (the captured set's relation and schema) and stage the verifier's frame files.

  mkset.py captured PARENT_SET T N OUT            the first N captured heads of key count T, as a set of their own
  mkset.py adversarial T N SEED CATEGORY OUT      gen_attn instances (outputs: the IR's)
  mkset.py stage SET_DIR N OUT                     verity_flock.ir_frame.stage of the first N instances (the verifier's staging)
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from verity_numerical.bench import input_sets as IS  # noqa: E402

D = 64
REL = {"definition": "Attention_v3", "dot": "AmpereBF16TcDot16_v1", "inv": "Fa2InvSum_v1",
       "rule": "one query at position T-1 over keys 0..T-1 of its KV head, ceil(T/BN) key blocks last -> first (the Definition's head)",
       "statics": {"BN": 128, "D": 64}, "subcircuit": "AttentionHead<T,64>"}


def write(flat, out, T, name, prov):
    n = len(flat)
    q = [r[:D].astype(np.uint16) for r in flat]
    k = [r[D:D + T * D].astype(np.uint16) for r in flat]
    v = [r[D + T * D:].astype(np.uint16) for r in flat]
    import attn_e2e as E
    o = [x.astype(np.uint16) for x in E.ir_outputs(T, flat)]
    rows = [[i, i, "r0", 0, "red-team-flock-3", T - 1, "synthetic", "synthetic", {"head": 0, "kv_head": 0, "T": T, "NH": 1, "KVH": 1}]
            for i in range(n)]
    return IS.write(out, name, REL, {"q": q, "k": k, "v": v, "out": o}, rows, prov, schema="vllm-vu-set/v1")


def main():
    m = sys.argv[1]
    if m == "captured":
        s = IS.InputSet.open(sys.argv[2]); T, N, out = int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
        ks = s.port("k")
        ids = [i for i in range(s.n) if len(ks[i]) == T * D][:N]
        q, v = s.port("q"), s.port("v")
        flat = np.stack([np.concatenate([q[i], ks[i], v[i]]).astype(np.uint64) for i in ids])
        print(json.dumps(write(flat, out, T, "attention-head-fa2-d64-bn128", {"source": "captured", "subset_of": s.content_digest, "ids": ids})))
    elif m == "adversarial":
        import gen_attn as G
        T, N, seed, cat, out = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
        flat = G.instances(T, N, seed, cat)
        print(json.dumps(write(flat, out, T, "attention-head-fa2-d64-bn128", {"source": "synthetic", "recipe": f"red-team-flock-3 gen_attn {cat} seed {seed}"})))
    elif m == "stage":
        from verity_flock import ir_frame
        from verity_flock.templates import attention_head as AH
        s = IS.InputSet.open(sys.argv[2]); N, out = int(sys.argv[3]), sys.argv[4]
        low = AH.lowering_for_set(s)
        p = ir_frame.stage(low, s, 0, N, out)
        Path(out, "pin").write_text(hashlib.sha256(low.text.encode()).hexdigest())
        print("STAGED", p, hashlib.sha256(low.text.encode()).hexdigest())


if __name__ == "__main__":
    main()
