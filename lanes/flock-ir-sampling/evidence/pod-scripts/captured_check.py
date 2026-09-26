"""flock-ir-sampling: the captured #101 sampling set (art:ea781b02, 32 rows, V = 128256) through the lane units and against the IR
evaluator. Stages the verifier's own file, then (1) every lane of every row through the laid-out lane netlist: outputs equal the
staged unit words, every row satisfied; (2) check_native; (3) the token of every row equals the set's recorded output and the
IR evaluator's full GumbelTopPTokenSelect_v1{128256} on ROWS rows (the interpreter, ~1 min a row), with the tempered and masked
rows and the noise compared word for word."""
import json, sys, time
import numpy as np
from verity.evaluation import evaluate
from verity.ir.defs import bind
from verity_numerical.bench.input_sets import InputSet
from verity_vllm.program.registry import sampling as SM
from verity_flock import ir_sampling as S

SET, OUT, ROWS = sys.argv[1], sys.argv[2], int(sys.argv[3])
s = InputSet.open(SET)
V = 128256
low = S.lane(V)
t = time.time()
path = S.stage(low, s, 0, s.n, OUT)
res = {"set": s.name, "content_digest": s.content_digest, "n": s.n, "stage_s": round(time.time() - t, 1), "lane_sha256": low.sha256,
       "pin": S.pin_digest(low)}
head, logits, _d, pub, cuts = S.read(path)
res["public_sha256"] = S.public_sha256(path)
bad_units, unsat = 0, 0
for lo in range(0, s.n, 4):
    hi = min(s.n, lo + 4)
    outs, ok = low.evaluate(S.unit_ports(cuts[lo:hi], logits[lo:hi]))
    want = S.unit_outputs(cuts[lo:hi], V)
    bad_units += sum(int((o != w).sum()) for o, w in zip(outs, want))
    unsat += (hi - lo) * V - bin(ok).count("1")
res.update({"lanes": s.n * V, "unit_word_mismatches": bad_units, "unsatisfied_lanes": unsat, "native": S.check_native(path)})
_, _, outs_set = S.instances(s, 0, s.n)
tok_file = cuts[:, S.lane_word(V - 1, "best_i")]
res["token_mismatches_vs_set"] = int((tok_file.astype(np.uint64) != outs_set).sum())
ir = []
for i in range(min(ROWS, s.n)):
    t = time.time()
    args = [int(pub[p][i]) for p in S.PUBLIC_PORTS]
    row = [int(x) for x in logits[i]]
    tok = evaluate(bind(SM.GumbelTopPTokenSelect, V=V), row, *args)[0]
    scaled = evaluate(bind(SM.TemperatureScale, V=V), row, args[3])
    lane = cuts[i, 7:].reshape(V, 6).astype(np.int64)
    masked = evaluate(bind(SM.TopPMask, V=V), list(scaled), args[0], args[4])
    key = SM.GumbelStreamKey.evaluate(args[1], args[2])
    gmis = sum(SM.GumbelNoiseLane.evaluate(key, v) != lane[v, 1] for v in range(0, V, 97))
    ir.append({"row": i, "token_ir": tok, "token_file": int(tok_file[i]), "token_set": int(outs_set[i]),
               "scaled_mismatches": int(sum(a != b for a, b in zip(lane[:, 2], scaled))),
               "masked_mismatches": int(sum(a != b for a, b in zip(np.where(lane[:, 0] == 1, lane[:, 2], S.NEG_INF), masked))),
               "noise_mismatches_every_97th": int(gmis), "kept": int(lane[:, 0].sum()), "s": round(time.time() - t, 1)})
    print(json.dumps(ir[-1]), flush=True)
res["ir_rows"] = ir
print("CAPTURED\t" + json.dumps(res), flush=True)
