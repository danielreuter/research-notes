"""vo_fp8_values.py OUT_DIR PROGRAM_DIR WORKLOAD CHECKPOINT_DIR [--steps S] [--coords C] [--all-coords-layers L,L] [--jobs J]
[--tokens TOKENS_JSON]

#74's SHARED_SCALE on the values of the recorded Build.  The recorded request Program (PROGRAM_DIR/instances.json.gz) is evaluated Call by
Call in Program order with the replay's row kernels (`verity_vllm.check.replay.evaluate.evaluate`, `kernels/rows.py`), from the
Program's own inputs only: the request's prompt ids (WORKLOAD) and the weights composed from the checkpoint of record
(`check.weights_of_record.compose`: q|k|v and gate|up stacked as the served model fuses them).  No committed value is read: every
activation, `x_s` included, is the Program's.  The first S engine steps are evaluated (default: all).

At every `ScaledMmFp8Block_v1` Call:
  products    the host-computed products `P = fp8.scale_products(x_s, w_s)` (the committer's words, through the IR's F32Mul_v1) against
              the old construction's `F32Mul_v1(sx[kb], sw[n // G][kb])` at EVERY output coordinate n and kb: the plain-integer reference
              (`F32Mul_v1.evaluate`) on each coordinate's operand pair; a bare numpy float32 multiply is counted beside it for information
  coordinates C sampled output coordinates per Call (every coordinate on the Calls of the layers in --all-coords-layers, first
              step): the old coordinate `ScaledMmFp8BlockCoordinate_v1{K,G}` evaluated gate by gate (`evaluate_call` with its
              transcript), whose own F32Mul gate values must equal P[n // G], whose output must equal the row kernel's; and the new
              `ScaledMmFp8BlockCoordinateGivenScale_v1{K,G}` fed P[n // G], whose output must equal both
Each step's TokenSelect output is compared with the recorded generation (TOKENS_JSON, `match/control/tokens.json`) when given.
Writes OUT_DIR/calls.jsonl (one line per FP8 Call) and OUT_DIR/summary.json."""
import gzip
import json
import os
import re
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from verity.evaluation.reference import standalone_call
from verity.ir.defs import bind
from verity.ir.evaluate import evaluate_call
from verity_vllm.check import weights_of_record as WR
from verity_vllm.check.replay.evaluate import evaluate as row_eval
from verity_vllm.check.replay.index import ProgramIndex
from verity_vllm.program import model as analytic
from verity_vllm.program.kernels.rows import ROWS
from verity_vllm.program.registry import fp8 as F8
from verity_vllm.program.registry import prims as P


def opt(name, default, cast=str):
    if name in sys.argv:
        k = sys.argv.index(name)
        v = sys.argv[k + 1]
        del sys.argv[k:k + 2]
        return cast(v)
    return default


STEPS = opt("--steps", None, int)
MAX_ROWS = opt("--max-rows", None, int)
COORDS = opt("--coords", 64, int)
COORD_EVERY = opt("--coord-every", 1, int)
ALL_LAYERS = {int(x) for x in opt("--all-coords-layers", "", str).split(",") if x}
JOBS = opt("--jobs", 8, int)
TOKENS = opt("--tokens", None)
out_dir, prog_dir, workload, ck_dir = sys.argv[1:5]
os.makedirs(out_dir, exist_ok=True)
LAYER = re.compile(r"\.layers\.(\d+)\.")
F32MUL = P.F32Mul


def f32mul_ref(a: int, b: int) -> int:
    return int(F32MUL.evaluate(int(a), int(b)))


def coord_check(args):
    """Old and new coordinate Definitions on one output coordinate, gate by gate: (n, old products, old out, new out)."""
    K, G, n, xq, sx, wrow, sw, p = args
    old_fn, new_fn = bind(F8.ScaledMmFp8BlockCoordinate, K=K, G=G), bind(F8.ScaledMmFp8BlockCoordinateGivenScale, K=K, G=G)
    prog, call = standalone_call(old_fn)
    t: dict = {}
    (old_out,) = evaluate_call(prog.circuit, call, [*map(int, xq), *map(int, sx), *map(int, wrow), *map(int, sw)], t)
    pos = {g: j for j, g in enumerate(call.args)}
    prods = {}
    for gv in call:
        if getattr(gv.prim, "id", "") == F32MUL.id:
            a, b = (pos.get(o) for o in gv.operands)
            kb = a - K                                  # sx[kb] sits after the K xq words
            assert b == 2 * K + K // G + kb, (a, b)     # and sw[kb] after xq, sx, wrow: the product of THIS coordinate's scale row
            prods[kb] = t[gv.index]
    prog2, call2 = standalone_call(new_fn)
    (new_out,) = evaluate_call(prog2.circuit, call2, [*map(int, xq), *map(int, p), *map(int, wrow)])
    return n, [prods[kb] for kb in range(K // G)], int(old_out), int(new_out)


EDGE_WORDS = [0x00000000, 0x80000000, 0x00000001, 0x80000001, 0x007FFFFF, 0x807FFFFF, 0x00800000, 0x80800000, 0x3F800000, 0xBF800000,
              0x7F7FFFFF, 0xFF7FFFFF, 0x7F800000, 0xFF800000, 0x7FC00000, 0xFFC00000, 0x7FC00001, 0x7FFFFFFF, 0xFFFFFFFF, 0x7F800001,
              0x7FA00000, 0x2C700000, 0x1F800000, 0x0C800000, 0x5F800000, 0x3A83126F, 0x33D6BF95, 0x3F7FFFFF]


def edge_pairs() -> dict:
    """numpy float32 multiply of arrays (the host path) against the IR's F32Mul_v1 on every ordered pair of edge words: signed zeros,
    subnormals, the smallest normal, +-1, +-max, +-inf, quiet / signalling NaNs with payloads, products that underflow to subnormal or
    zero and that overflow."""
    a = np.repeat(np.asarray(EDGE_WORDS, dtype=np.uint32), len(EDGE_WORDS))
    b = np.tile(np.asarray(EDGE_WORDS, dtype=np.uint32), len(EDGE_WORDS))
    with np.errstate(all="ignore"):
        host = (a.view(np.float32) * b.view(np.float32)).view(np.uint32)
        swapped = (b.view(np.float32) * a.view(np.float32)).view(np.uint32)
    ref = np.asarray([f32mul_ref(x, y) for x, y in zip(a, b)], dtype=np.uint32)
    diff = np.flatnonzero(host != ref)
    both_nan = [int(i) for i in diff if (host[i] & 0x7FFFFFFF) > 0x7F800000 and (ref[i] & 0x7FFFFFFF) > 0x7F800000]
    a_nan, b_nan = (a & 0x7FFFFFFF) > 0x7F800000, (b & 0x7FFFFFFF) > 0x7F800000
    return {"pairs": int(a.size), "mismatches": int(diff.size), "nan_payload_only": len(both_nan),
            "mismatch_pairs_have_two_nan_operands": bool(np.all(a_nan[diff] & b_nan[diff])),
            "swapped_order_array_mismatches": int((swapped != ref).sum()),
            "examples": [{"a": hex(int(a[i])), "b": hex(int(b[i])), "host": hex(int(host[i])), "ir": hex(int(ref[i]))} for i in diff[:6]]}


def main():
    t0 = time.time()
    edges = edge_pairs()
    print(f"[fp8-values] edge pairs numpy vs F32Mul_v1: {json.dumps(edges)[:600]}", flush=True)
    inst = json.load(gzip.open(f"{prog_dir}/instances.json.gz"))
    pi = ProgramIndex(inst)
    pnames = [n for n, _t in inst["params"]]
    wl = json.load(open(workload))
    LP = int(re.search(r"LP(\d+)_T(\d+)", os.path.basename(prog_dir.rstrip("/"))).group(1))
    req = next(r for r in wl["requests"] if int(r["prompt_len"]) == LP)
    prompt = np.asarray(req["prompt_token_ids"], dtype=np.uint32)
    fields = {n: (shape, bits) for n, shape, bits in WR.program_weight_fields(inst)}
    ck = WR.CheckpointIndex(ck_dir, verify_shards=False)
    cands = sorted({f.split(".")[0] + "." for f in fields if "." in f} | {""})
    prefix = max(cands, key=lambda p: (sum(1 for f in fields if ck.has(WR.strip_prefix(f, p))), -len(p)))
    cache: dict = {}

    def field(name):
        a = cache.get(name)
        if a is None:
            shape, bits = fields[name]
            if WR.ENGINE_ROTARY_RE.search(name):
                # no checkpoint tensor: the analytic table (the served words are CUDA libm's, within gate I9's bound of this one)
                a = cache.get("cos_sin")
                if a is None:
                    C, _prov = analytic.config_of(ck.config)
                    a = cache["cos_sin"] = np.ascontiguousarray(analytic.cos_sin_table(C)).reshape(-1).astype(np.uint16)
                    assert a.size == int(np.prod(shape)), (name, shape, a.size)
                cache[name] = a
                return a
            raw, _note = WR.compose(WR.strip_prefix(name, prefix), shape, bits, ck)
            a = cache[name] = np.ascontiguousarray(raw).reshape(-1).view({8: np.uint8, 16: np.uint16, 32: np.uint32}[bits])
        return a

    def weights(fname, lo, hi):
        return field(fname)[lo:hi]

    outs: dict[int, list[np.ndarray]] = {}
    steps_of = Counter()
    tokens_rec = None
    if TOKENS:
        tokens_rec = next((q.get("generated_token_ids") for q in json.load(open(TOKENS))["requests"] if int(q["prompt_len"]) == LP), None)
    sel, calls_out, tot = [], open(f"{out_dir}/calls.jsonl", "w"), Counter()
    pool = ProcessPoolExecutor(max_workers=JOBS)
    rng = np.random.default_rng(LP)
    first_step_layers_done: set = set()
    for r in inst["rows"]:
        i = r["i"]
        step = pi.step_of(i)
        if (STEPS is not None and step >= STEPS) or (MAX_ROWS is not None and i >= MAX_ROWS):
            break
        d = pi.describe(r)
        fam, st = d["family"], d["statics"]
        inputs, wsl = [], []
        for group in r["args"]:
            words, w = [], None
            for kind, a, lo, hi in group:
                if kind == "p" and pnames[a] == "prompt":
                    words.append(prompt[lo:hi])
                elif kind == "p" and pnames[a] == "weights":
                    fname, flo, fhi, _shape = pi.weight_slice(lo, hi)
                    w = weights(fname, flo, fhi)
                elif kind == "n":
                    src = outs[a]
                    flat = src[0] if len(src) == 1 else None
                    if flat is None:                                 # a multi-port node: the run lies in one port
                        base = 0
                        for port in src:
                            if lo >= base and hi <= base + port.size:
                                flat, lo, hi = port, lo - base, hi - base
                                base = -1
                                break
                            base += port.size
                        assert base == -1, (i, a, lo, hi)
                        words.append(flat[lo:hi])
                    else:
                        words.append(flat[lo:hi])
                else:
                    raise ValueError(f"row {i}: run {kind, a} not resolvable")
            inputs.append(words)
            wsl.append(w)
        res = row_eval(fam, st, inputs, wsl)
        outs[i] = [np.asarray(res[m]).reshape(-1) for m in ROWS[fam].returns]
        steps_of[step] += 1
        if fam == "TokenSelect_v1":
            tok = int(outs[i][0][0])
            sel.append({"step": step, "token": tok})
            tot["token_selects"] += 1
        if fam != "ScaledMmFp8Block_v1":
            continue
        K, N, G = int(st["K"]), int(st["N"]), int(st["G"])
        xq, sx = (np.concatenate(inputs[0]), np.concatenate(inputs[1]))
        w, ws = wsl[2].reshape(N, K), wsl[3].reshape(N // G, K // G)
        y = outs[i][0]
        host = F8.scale_products(sx, ws)                                                        # [N/G, K/G]: the committer's words
        pairs = {(int(a), int(b)) for a, b in zip(np.broadcast_to(sx[None, :], ws.shape).reshape(-1), ws.reshape(-1))}
        ref = {ab: f32mul_ref(*ab) for ab in pairs}
        ref_blk = np.vectorize(lambda a, b: ref[(int(a), int(b))], otypes=[np.uint32])(np.broadcast_to(sx[None, :], ws.shape), ws)
        blk_mismatch = int((ref_blk != host).sum())
        coords_eq = int((ref_blk == host).sum()) * G                                            # every coordinate n of block nb reads row nb
        with np.errstate(all="ignore"):
            npmul = (sx.view(np.float32)[None, :] * ws.view(np.float32)).view(np.uint32)
        tot["numpy_array_multiply_differs"] += int((npmul != host).sum())                       # informational: the bare numpy path
        layer = int(LAYER.search(r["name"]).group(1)) if LAYER.search(r["name"]) else -1
        lin = r["name"].rsplit("/", 1)[0].rsplit(".", 1)[-1]
        full = layer in ALL_LAYERS and step == 0 and (layer, lin) not in first_step_layers_done
        if full:
            first_step_layers_done.add((layer, lin))
        if full:
            ns = np.arange(N)
        elif tot["fp8_calls"] % COORD_EVERY == 0:
            ns = np.unique(np.concatenate([[0, N - 1, G - 1, G], rng.integers(0, N, COORDS)]))[:COORDS + 4]
        else:
            ns = np.arange(0)
        xs_f, ws_f = sx.view(np.float32), ws.view(np.float32)
        for nm, arr in (("xs", sx), ("ws", ws), ("prod", host)):
            e, m = arr & 0x7F800000, arr & 0x007FFFFF
            tot[f"{nm}_words"] += int(arr.size)
            tot[f"{nm}_zero"] += int(((e == 0) & (m == 0)).sum())
            tot[f"{nm}_subnormal"] += int(((e == 0) & (m != 0)).sum())
            tot[f"{nm}_inf"] += int(((e == 0x7F800000) & (m == 0)).sum())
            tot[f"{nm}_nan"] += int(((e == 0x7F800000) & (m != 0)).sum())
        fin = np.isfinite(xs_f).all() and np.isfinite(ws_f).all()
        if fin:
            lo_, hi_ = float(np.abs(host.view(np.float32)).min()), float(np.abs(host.view(np.float32)).max())
            tot["prod_min_abs"] = lo_ if "prod_min_abs" not in tot else min(tot["prod_min_abs"], lo_)
            tot["prod_max_abs"] = max(tot.get("prod_max_abs", 0.0), hi_)
        jobs = [(K, G, int(n), xq, sx, w[n], ws[n // G], host[n // G]) for n in ns]
        c_old_prod = c_old_out = c_new_out = 0
        for n, prods, old_out, new_out in pool.map(coord_check, jobs, chunksize=max(1, len(jobs) // (JOBS * 4))):
            c_old_prod += int(np.any(np.asarray(prods, dtype=np.uint32) != host[n // G]))
            c_old_out += int(old_out != int(y[n]))
            c_new_out += int(new_out != int(y[n]))
        rec = {"row": i, "step": step, "layer": layer, "linear": lin, "K": K, "N": N, "G": G, "coordinates": N * (K // G),
               "host_vs_reference_product_mismatches": blk_mismatch * G, "host_equals_reference_at": coords_eq,
               "nan_products": int(np.isnan(host.view(np.float32)).sum()),
               "subnormal_products": int((((host & 0x7F800000) == 0) & ((host & 0x007FFFFF) != 0)).sum()),
               "sampled_coordinates": int(len(ns)), "all_coordinates": bool(full),
               "old_coordinate_products_differ": c_old_prod, "old_coordinate_out_vs_row_kernel": c_old_out, "new_coordinate_out_vs_row_kernel": c_new_out}
        calls_out.write(json.dumps(rec) + "\n")
        tot["fp8_calls"] += 1
        tot["coordinates"] += rec["coordinates"]
        tot["host_equals_reference_at"] += coords_eq
        tot["host_vs_reference_product_mismatches"] += rec["host_vs_reference_product_mismatches"]
        tot["sampled_coordinates"] += rec["sampled_coordinates"]
        tot["all_coordinate_calls"] += int(full)
        tot["coordinate_checked_calls"] += int(len(ns) > 0)
        for k in ("old_coordinate_products_differ", "old_coordinate_out_vs_row_kernel", "new_coordinate_out_vs_row_kernel"):
            tot[k] += rec[k]
        if tot["fp8_calls"] % 200 == 0:
            print(f"[fp8-values] {tot['fp8_calls']} FP8 Calls, step {step} layer {layer}; {round(time.time() - t0)} s; {dict(tot)}", flush=True)
    pool.shutdown()
    calls_out.close()
    ok = tot["fp8_calls"] > 0 and all(tot[k] == 0 for k in ("host_vs_reference_product_mismatches", "old_coordinate_products_differ",
                                                             "old_coordinate_out_vs_row_kernel", "new_coordinate_out_vs_row_kernel"))
    got = [s["token"] for s in sel]
    tokens_equal = None if tokens_rec is None else got == list(tokens_rec[:len(got)])
    summary = {"program": prog_dir, "request": {"index": req.get("index"), "prompt_len": LP, "request_id": req.get("request_id")},
               "steps_evaluated": len(steps_of), "calls_evaluated": sum(steps_of.values()), "token_selects": sel,
               "tokens_record": None if tokens_rec is None else list(tokens_rec[:len(got)]), "tokens_equal_record": tokens_equal,
               "totals": dict(tot), "edge_pairs": edges, "ok": ok, "seconds": round(time.time() - t0)}
    json.dump(summary, open(f"{out_dir}/summary.json", "w"), indent=1)
    print(f"FP8-VALUES {os.path.basename(prog_dir)}: ok={ok} {json.dumps(dict(tot))} tokens={got[:6]} = record {tokens_equal} "
          f"({summary['seconds']} s)", flush=True)


if __name__ == "__main__":
    main()
