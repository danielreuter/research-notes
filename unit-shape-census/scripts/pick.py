import glob, json, pickle, sys, __main__
sys.path[:0] = ["/workspace/packages/verity/src", "/workspace/backends/numerical/python", "/workspace/backends/flock/python", "/workspace/integrations/vllm"]
from verity_flock import unit_shapes as US
__main__.UnitShape = US.UnitShape
rows = {p.split("/")[-1][:-4]: pickle.loads(open(p, "rb").read()) for p in sorted(glob.glob("/tmp/census/out/*.pkl"))}
out = {}
for S in [(16, 21, 9), (16, 22, 9), (17, 22, 10), (18, 23, 11)]:
    Sv = tuple(1 << x for x in S)
    out[",".join(map(str, S))] = {k: US.assess(cl, Sv, {}) for k, cl in rows.items()}
    print(S, flush=True)
json.dump(out, open("/tmp/census/out/analysis-pick.json", "w"), default=float)
