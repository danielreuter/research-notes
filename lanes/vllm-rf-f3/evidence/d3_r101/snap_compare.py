import hashlib, json, os, sys
import numpy as np
ROW = sys.argv[1] if len(sys.argv) > 1 else "smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager"
H, B = f"/workspace/cp/sweep-head/{ROW}/match/capture", f"/workspace/cp/sweep-base/{ROW}/match/capture"
h, b = json.load(open(f"{H}/snapshots.json")), json.load(open(f"{B}/snapshots.json"))
eh, eb = h["entries"], b["entries"]
print("entries", len(eh), len(eb), "top keys", sorted(h.keys()))
diffs = [i for i, (x, y) in enumerate(zip(eh, eb)) if x.get("sha256") != y.get("sha256")]
print("differing entries", len(diffs), diffs[:20])
print("differing names", sorted({str(eh[i].get("name") or eh[i].get("identity") or eh[i].get("key")) for i in diffs}))
for i in diffs[:4]:
    x, y = eh[i], eb[i]
    meta = {k: v for k, v in x.items() if k not in ("file", "sha256")}
    same_meta = meta == {k: v for k, v in y.items() if k not in ("file", "sha256")}
    print(i, "meta", json.dumps(meta)[:400], "same_meta", same_meta)
    fa, fb = os.path.join(H, x["file"]), os.path.join(B, y["file"])
    if os.path.exists(fa) and os.path.exists(fb):
        ra, rb = open(fa, "rb").read(), open(fb, "rb").read()
        print("   bytes", len(ra), len(rb))
        if len(ra) == len(rb):
            a, c = np.frombuffer(ra, np.uint8), np.frombuffer(rb, np.uint8)
            nd = np.nonzero(a != c)[0]
            print("   differing bytes", nd.size, "first/last", (int(nd[0]), int(nd[-1])) if nd.size else None)
    else:
        print("   files present", os.path.exists(fa), os.path.exists(fb))
for p in ("/workspace/head/integrations/vllm/out/gen/r9/cmt-hidden/src/hidden_gpu.py",
          "/workspace/head/integrations/vllm/verity_vllm/acquire/hidden_gpu_src/hidden_gpu.py",
          "/workspace/basetree/integrations/vllm/verity_vllm/acquire/hidden_gpu_src/hidden_gpu.py"):
    print(hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] if os.path.exists(p) else "absent", p)
