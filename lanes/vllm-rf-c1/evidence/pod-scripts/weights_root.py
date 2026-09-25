"""Weights root of a live vLLM model: the production committer against core's vllm-v1 reference over the same bytes.

Run from the shipped tree root (`research run --cwd source`) with /workspace/venv312/bin/python after pod_bootstrap.sh.

  1. Build the engine the way a Commit does (`vllm_adapter.build_engine`, the row's case and execution).
  2. Production: `NativeHostCommitter(engine, gpu_tree=True).register_weights()` (chunk 256, the native_collect committers' setting) under
     VERITY_WEIGHTS_HASH = host, device (native_leafhash.cu) and device-checked.
  3. Core: `verity.commitments.vllm_v1` over the same tensors' bytes: pos_leaf per 256-byte piece, fold per tensor, weights_root over
     the committer's geo digest and the names digest (both integration-owned, opaque to the scheme).
  4. With --records DIR (a regression row's records tree): the recorded Commit weights root (commit/runs.jsonl), and the weights of
     record (`build_request/weights_of_record.json`) checked field by field against the live parameters (`weights_of_record.check`).

usage: weights_root.py --case LLAMA32_1B --execution bi-eager [--records DIR]
Writes $RESEARCH_RUN_DIR/weights_root.json; exit 1 when any two roots differ.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

TREE = os.getcwd()
INT = os.path.join(TREE, "integrations", "vllm")
sys.path.insert(0, INT)
sys.path.insert(0, os.path.join(TREE, "packages", "verity", "src"))
os.chdir(INT)

ap = argparse.ArgumentParser()
ap.add_argument("--case", default="LLAMA32_1B")
ap.add_argument("--execution", default="bi-eager")
ap.add_argument("--records", default=None)
ap.add_argument("--chunk", type=int, default=256)
args = ap.parse_args()
OUT = os.environ.get("RESEARCH_RUN_DIR") or "/tmp/c1-weights"
os.makedirs(OUT, exist_ok=True)

import torch  # noqa: E402

from verity.commitments import vllm_v1 as V  # noqa: E402
from verity_vllm.acquire.native_host import NativeHostCommitter, _dtype_name  # noqa: E402
from verity_vllm.observe import vllm_adapter as va  # noqa: E402

res: dict = {"case": args.case, "execution": args.execution, "chunk": args.chunk}
t0 = time.time()
eng = va.build_engine("manifests/checkpoints.json", max_num_seqs=1, case=args.case, execution=args.execution)
res["engine"] = {"build_s": round(eng.build_s, 1), "checkpoint": {k: eng.cp.get(k) for k in ("repo", "revision")}, "kwargs": eng.kwargs,
                 "effective": eng.effective}
try:
    import vllm
    res["env"] = {"torch": torch.__version__, "cuda": torch.version.cuda, "vllm": vllm.__version__, "device": torch.cuda.get_device_name(0)}
except Exception as e:  # noqa: BLE001
    res["env"] = {"error": repr(e)}

com = NativeHostCommitter(eng, run_id="c1-weights-root", gpu_tree=True, staging="direct", arena_bytes=None)
assert com.chunk == args.chunk, (com.chunk, args.chunk)
res["geo_digest"] = com._geo_digest.hex()
hf = eng.llm.llm_engine.vllm_config.model_config.hf_config
geo_doc = {k: getattr(hf, k, None) for k in ("hidden_size", "num_hidden_layers", "num_attention_heads", "num_key_value_heads", "head_dim",
                                             "intermediate_size", "vocab_size", "model_type")}
geo_doc.update(repo=eng.cp.get("repo"), revision=eng.cp.get("revision"), chunk=com.chunk)
res["geo_doc"] = geo_doc
res["geo_digest_recomputed"] = hashlib.sha256(json.dumps(geo_doc, sort_keys=True, default=str).encode()).hexdigest()

prod: dict = {}
for mode in ("host", "device", "device-checked"):
    os.environ["VERITY_WEIGHTS_HASH"] = mode
    w = com.register_weights()
    prod[mode] = {k: w.get(k) for k in ("root", "tensors", "bytes", "wall_s", "hash", "chunk", "device_checked_tensors")}
    print(f"[weights] production {mode}: root {w['root']} tensors {w['tensors']} bytes {w['bytes']} {w['wall_s']:.1f}s", flush=True)
res["production"] = prod

t1 = time.perf_counter()
seen: set[int] = set()
names, troots, nbytes = [], [], 0
per_tensor = []
for name, p in list(com.model.named_parameters()) + list(com.model.named_buffers()):
    if not isinstance(p, torch.Tensor) or id(p) in seen or p.numel() == 0:
        continue
    seen.add(id(p))
    src = p.detach().contiguous().reshape(-1)
    flat = src.view(torch.uint8) if src.dtype != torch.uint8 else src
    b = flat.cpu().numpy().tobytes()
    tr = V.fold([V.pos_leaf(b[o:o + args.chunk]) for o in range(0, len(b), args.chunk)])
    troots.append(tr)
    names.append([name, _dtype_name(p), list(p.shape), len(b)])
    per_tensor.append({"name": name, "nbytes": len(b), "tensor_root": tr.hex(), "sha256": hashlib.sha256(b).hexdigest()})
    nbytes += len(b)
names_digest = hashlib.sha256(json.dumps(names, separators=(",", ":")).encode()).digest()
core_root = V.weights_root(com._geo_digest, names_digest, troots)
res["core"] = {"root": core_root.hex(), "tensors": len(troots), "bytes": nbytes, "wall_s": round(time.perf_counter() - t1, 1),
               "names_digest": names_digest.hex(), "reference": "verity.commitments.vllm_v1 (pos_leaf, fold, weights_root)"}
print(f"[weights] core vllm-v1: root {core_root.hex()} tensors {len(troots)} bytes {nbytes} {res['core']['wall_s']}s", flush=True)
json.dump(per_tensor, open(os.path.join(OUT, "weights_tensors.json"), "w"), indent=0)

roots = {f"production.{m}": prod[m]["root"] for m in prod} | {"core": core_root.hex()}

if args.records:
    rd = args.records
    found = []

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, dict) and "weight" in k.lower() and isinstance(v.get("root"), str):
                    found.append({"path": path + "/" + k, "root": v["root"], **{x: v.get(x) for x in ("tensors", "bytes", "hash", "chunk")}})
                walk(v, path + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")

    for rel in ("commit/runs.jsonl", "commit/summary.json", "commit_summary.json"):
        fp = os.path.join(rd, rel)
        if not os.path.exists(fp):
            continue
        txt = open(fp).read()
        docs = [json.loads(ln) for ln in txt.splitlines() if ln.strip()] if rel.endswith(".jsonl") else [json.loads(txt)]
        for j, d in enumerate(docs):
            n0 = len(found)
            walk(d, f"{rel}#{j}")
            for f in found[n0:]:
                f["file"] = rel
    res["recorded"] = found
    for i, f in enumerate(found):
        roots[f"recorded[{i}] {f['path']}"] = f["root"]
    wor = os.path.join(rd, "build_request", "weights_of_record.json")
    if os.path.exists(wor):
        from verity_vllm.input_provenance import weights_of_record as WR
        record = json.load(open(wor))
        live = WR.live_param_digests(com.model)
        chk = WR.check(record, live)
        res["weights_of_record"] = {"file": "build_request/weights_of_record.json", "root_of_record": record.get("root_of_record"),
                                    "n_fields": record.get("n_fields"), "n_pinned": record.get("n_pinned"),
                                    "check": {k: v for k, v in chk.items() if k in ("result", "compared", "mismatched", "missing", "unpinned",
                                                                                     "shards_ok", "all_shards_pinned", "why")}}
        print(f"[weights] weights of record: root {record.get('root_of_record')} check {res['weights_of_record']['check']}", flush=True)

res["roots"] = roots
res["all_equal"] = len(set(roots.values())) == 1
res["wall_s"] = round(time.time() - t0, 1)
json.dump(res, open(os.path.join(OUT, "weights_root.json"), "w"), indent=1, default=str)
for k, v in roots.items():
    print(f"  {v}  {k}")
print("WEIGHTS-ROOT-" + ("EQUAL" if res["all_equal"] else "DIFFER"))
sys.exit(0 if res["all_equal"] else 1)
