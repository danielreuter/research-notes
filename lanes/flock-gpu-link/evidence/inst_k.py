"""flock-pure-instances/v1 files at any K (flock-gpu-link test inputs; the cell instances are flock-backend's).

  python3 /tmp/inst_k.py synth fp8-hopper 2048 N out.bin      synthetic E4M3 operands (rng([seed, i]), K words each)
  python3 /tmp/inst_k.py captured bf16-ampere DIR N out.bin   a captured vllm-vu-set/v1 (x.u16, w.u16, y.u16), first N VUs

The accumulators are the model's chain (tc_dot per unit); a captured set's recorded y must equal f32_to_bf16 of the last.
The statement is flock-backend's instances.statement with its K and instance digest set for this set.
"""
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path[:0] = ["/tmp/fb2/backends/flock/python", "/tmp/fb2/packages/verity/src", "/tmp/fb2/backends/numerical/python"]
from verity_flock import instances as I  # noqa: E402
from verity_flock.lowering import PIPES  # noqa: E402


def _chain(args):
    name, x, w = args
    from verity.ml.tc.silicon import tc_dot
    relation, _, _ = I._ligero()
    rel = relation(name)
    k = rel.k
    out = []
    for a, b in zip(x, w):
        al, bl, c, row = a.tolist(), b.tolist(), 0, []
        for s in range(len(al) // k):
            c = tc_dot(rel.model, c, al[k * s:k * s + k], bl[k * s:k * s + k])
            row.append(c)
        out.append(row)
    return out


def chain(name, x, w, procs=32):
    step = max(1, len(x) // (4 * procs))
    jobs = [(name, x[i:i + step], w[i:i + step]) for i in range(0, len(x), step)]
    with ProcessPoolExecutor(procs) as ex:
        return np.asarray([r for part in ex.map(_chain, jobs) for r in part], dtype=np.uint32)


def main():
    mode, name, src, n, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
    from verity.ml.tc.cast import f32_to_bf16_word
    relation, _, _ = I._ligero()
    rel = relation(name)
    pipe = PIPES[name]
    if mode == "synth":
        K = int(src)
        xs, ws = [], []
        for i in range(n):
            rng = np.random.default_rng([rel.instance_seed, i])
            xs.append(I._e4m3_operands(rng, (K,)))
            ws.append(I._e4m3_operands(rng, (K,)))
        x, w = np.asarray(xs, dtype=np.uint8), np.asarray(ws, dtype=np.uint8)
        digest = hashlib.sha256(f"{rel.name} synthetic|seed={rel.instance_seed}|n={n}|K={K}".encode()).hexdigest()
        ref = {"dataset": f"flock-gpu-link-synthetic-{name}-k{K}", "tier": f"k{K}", "range": [0, n], "manifest_sha256": digest,
               "seed": rel.instance_seed}
    else:
        man = json.load(open(f"{src}/manifest.json"))
        K = int(man.get("ports", {}).get("x", {}).get("words", 0) or man["relation"]["statics"]["K"])
        x = np.fromfile(f"{src}/x.u16", dtype="<u2").reshape(-1, K)[:n]
        w = np.fromfile(f"{src}/w.u16", dtype="<u2").reshape(-1, K)[:n]
        y = np.fromfile(f"{src}/y.u16", dtype="<u2")[:n]
        digest = man.get("content_digest") or hashlib.sha256(open(f"{src}/manifest.json", "rb").read()).hexdigest()
        ref = {"dataset": man.get("set", "captured"), "tier": f"captured-k{K}", "range": [0, n], "manifest_sha256": digest}
    accs = chain(name, x, w)
    if mode == "captured":
        bad = sum(int(f32_to_bf16_word(int(a[-1])) != int(v)) for a, v in zip(accs, y))
        assert bad == 0, f"{bad} captured outputs differ from the model chain"
    I.K = K
    I.instances_digest = lambda _name, _n: digest
    st = I.statement(name, x, w, accs, n, 0, "blake3")
    o = np.asarray([f32_to_bf16_word(int(a[-1])) if pipe.epilogue else int(a[-1]) for a in accs], dtype="<u4")
    header = {"format": I.FORMAT, "relation": name, "vus": n, "k": K, "word_bits": pipe.word_bits, "units": accs.shape[1],
              "row_bytes": K * pipe.word_bits // 8, "epilogue": pipe.epilogue, "instances": ref,
              **{k: v for k, v in st.items() if k != "y"}}
    with open(out, "wb") as f:
        f.write(json.dumps(header, sort_keys=True).encode() + b"\n")
        f.write(np.ascontiguousarray(x.astype("<u2" if pipe.word_bits == 16 else "u1")).tobytes())
        f.write(np.ascontiguousarray(w.astype("<u2" if pipe.word_bits == 16 else "u1")).tobytes())
        f.write(np.ascontiguousarray(accs.astype("<u4")).tobytes())
        f.write(o.tobytes())
        f.write(np.asarray(st["y"], dtype="<u4").tobytes())
    print(json.dumps({"relation": name, "K": K, "vus": n, "units": int(accs.shape[1]), "roots": header["roots"]}))


if __name__ == "__main__":
    main()
