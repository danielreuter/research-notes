"""derive_fp8_chain_sets.py OUT SET_DIR... --tag TAG [--register --set-arts JSON]: the bench spine's FP8 statement over captured operands.

For each captured `ScaledMmFp8BlockCoordinate<K,G>` set (`vllm-vu-set/v1`, the VU exporter's cut of `ScaledMmFp8Block_v1`), write
the `gemm-coordinate/k<K>/sm90-wgmma-e4m3` input set (`input-set/v1`, `templates.gemm_coordinate(K, "sm90.wgmma.m64n8k32.e4m3")`)
over the same captured e4m3 operands x, w.  Its y is the relation's: the FP32 accumulator of K/32 ascending HOPPER_E4M3 wgmma k32
steps from +0 (no scales, no epilogue), evaluated by the subcircuit's IR target (`Subcircuit.evaluate`).  The served kernel applies
the block scales per 128-tile and rounds to bf16 (the captured set's y); this y was never a served word, so the provenance source
is "captured inputs, model y".  `--register` puts each set in the evidence store (`input-set/v1`, preserved, `--ref captured_set`).
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

from verity_numerical.bench import input_sets as IS
from verity_numerical.bench import templates as TM

SEMANTICS = "sm90.wgmma.m64n8k32.e4m3"


def derive(set_dir: Path, out: Path, tag: str) -> tuple[dict, dict] | None:
    man = json.loads((set_dir / "manifest.json").read_text())
    rel = man["relation"]
    if not str(rel.get("subcircuit", "")).startswith("ScaledMmFp8BlockCoordinate<"):
        return None
    n, K = int(man["n"]), int(rel["statics"]["K"])
    x = np.frombuffer((set_dir / man["ports"]["x"]["file"]).read_bytes(), dtype=np.uint8).reshape(n, K)
    w = np.frombuffer((set_dir / man["ports"]["w"]["file"]).read_bytes(), dtype=np.uint8).reshape(n, K)
    idx = json.loads((set_dir / "index.json").read_text())["rows"]
    sub = TM.gemm_coordinate(K, SEMANTICS)
    outs = sub.evaluate({"x": list(x), "w": list(w)})
    keep = [i for i, ok in enumerate(sub.admitted(outs)) if ok]
    rows = [[j, *idx[i][1:8], dict(idx[i][8], captured_set=man["set"], captured_id=idx[i][0])] for j, i in enumerate(keep)]
    mp = man.get("provenance") or {}
    prov = {k: mp.get(k) for k in IS.PROVENANCE_FIELDS}
    prov.update(source="captured inputs, model y",
                recipe={"inputs": f"x, w: the e4m3 operands of captured set {man['set']} (vllm-vu-set/v1, content_digest {man['content_digest']})",
                        "y": f"{sub.id}: {sub.relation['rule']} ({sub.relation['model']}), evaluated by the subcircuit's IR target",
                        "served_y": f"not this y: the served kernel is {rel['subcircuit']} ({rel['rule']})",
                        "dropped": n - len(keep), "deriver": "lanes/vllm-more-exports/evidence/derive_fp8_chain_sets.py"})
    name = f"{sub.set_name}-{tag}"
    s = IS.write(out / "sets", name, sub.relation, {"x": [x[i] for i in keep], "w": [w[i] for i in keep], "y": [outs["y"][i] for i in keep]},
                 rows, prov, schema=IS.SCHEMA)
    return s, man


def register(set_path: Path, captured_art: str | None) -> str:
    meta = IS.InputSet.open(set_path).meta()
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(meta, f, default=str)
    args = ["python3", "-m", "research", "data", "put", "--kind", IS.KIND, "--meta", "@" + f.name, "--preserve", "--tree", str(set_path)]
    if captured_art:
        args += ["--ref", f"captured_set={captured_art}"]
    r = subprocess.run(args, capture_output=True, text=True, env=dict(os.environ, PYTHONPATH="/workspace/tools/research/src"))
    if r.returncode != 0:
        raise SystemExit(f"research data put: rc {r.returncode}\n{r.stderr[-2000:]}")
    return next(x for x in reversed(r.stdout.strip().splitlines()) if x.startswith("art:"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("sets", nargs="+")
    ap.add_argument("--tag", required=True, help="set name suffix naming the capture, e.g. vllm74")
    ap.add_argument("--register", action="store_true")
    ap.add_argument("--set-arts", default="{}", help="JSON {captured set name: art}")
    a = ap.parse_args()
    arts = json.loads(a.set_arts)
    for d in map(Path, a.sets):
        got = derive(d, Path(a.out), a.tag)
        if got is None:
            continue
        s, man = got
        s["verify"] = IS.verify(Path(a.out) / "sets" / s["set"])["ok"]
        if a.register:
            s["art"] = register(Path(a.out) / "sets" / s["set"], arts.get(man["set"]))
        print(json.dumps({k: s.get(k) for k in ("set", "n", "bytes", "content_digest", "verify", "art")}), flush=True)


if __name__ == "__main__":
    main()
