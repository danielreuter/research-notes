"""register_export.py RUN_ID EPOCH BRANCH: fetch a vux_row.sh run's vu-export/ from its run record and register every set
(`vllm-vu-set/v1`) and the export summary (`vllm-vu-export/v1`) in the evidence store, preserved on the remote.

The set trees are registered byte-for-byte as the pod wrote them; the source tree (the attempt's recorded source commit,
dirty flag), the branch and the epoch go in each artifact's meta.  Prints one JSON line per artifact."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RESEARCH = ["python3", "-m", "research"]
ENV = dict(os.environ, PYTHONPATH="/workspace/tools/research/src")


def research(*args: str) -> str:
    r = subprocess.run([*RESEARCH, *args], capture_output=True, text=True, env=ENV)
    if r.returncode != 0:
        raise SystemExit(f"research {' '.join(args[:3])}: rc {r.returncode}\n{r.stderr[-2000:]}")
    return r.stdout


def put(kind: str, meta: dict, refs: dict[str, str], *, tree: Path | None = None, file: Path | None = None) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(meta, f)
    args = ["data", "put", "--kind", kind, "--meta", "@" + f.name, "--preserve"]
    for k, v in refs.items():
        args += ["--ref", f"{k}={v}"]
    args += ["--tree", str(tree)] if tree else ["--file", str(file)]
    out = research(*args).strip().splitlines()
    return next(x for x in reversed(out) if x.startswith("art:"))


def main(run: str, epoch: str, branch: str, sub: str = "") -> None:
    att = json.loads(research("data", "show", run, "--json"))
    rr = att["outputs"]["run_record"]
    src = att.get("source") or {}
    pre = f"vu-export/{sub}" if sub else "vu-export"
    root = Path(research("data", "fetch", rr, "--path", f"{pre}/*").strip().splitlines()[-1])
    exp = root / pre
    summary = json.loads((exp / "export.json").read_text())
    prov = summary["provenance"]
    base = {"row": prov.get("row"), "row_key": prov.get("row_key"), "model": prov.get("model"), "revision": prov.get("revision"),
            "run": run, "run_root": prov["run_root"], "program_digests": prov.get("program_digests"),
            "manifest_digest": prov.get("manifest_digest"),
            "source": {"commit": src.get("commit"), "dirty": src.get("dirty"), "tree": src.get("tree"), "branch": branch},
            "epoch": epoch, "table2": "not admitted (captured realistic-distribution sets await Daniel's decision)"}
    sets = {}
    for s in summary["sets"]:
        d = exp / "sets" / s["set"]
        man = json.loads((d / "manifest.json").read_text())
        meta = dict(base, set=s["set"], relation=man["relation"], n=man["n"], bytes=s["bytes"], content_digest=man["content_digest"],
                    ports={k: {kk: vv for kk, vv in p.items() if kk in ("dtype", "words")} for k, p in man["ports"].items()})
        art = put("vllm-vu-set/v1", meta, {"run_record": rr}, tree=d)
        sets[s["set"]] = art
        print(json.dumps({"set": s["set"], "n": man["n"], "bytes": s["bytes"], "art": art}), flush=True)
    meta = dict(base, sets={k: v for k, v in sets.items()}, by_family=summary["by_family"], population=summary["population"],
                limits=summary["limits"], wall_s=summary["wall_s"])
    refs = {"run_record": rr, "sets": ",".join(sets.values())}
    if (exp / "store").is_dir():
        store = put("vllm-vu-store/v1", dict(base, store=summary.get("store")), {"run_record": rr}, tree=exp / "store")
        refs["store"] = store
        print(json.dumps({"store": store}), flush=True)
    art = put("vllm-vu-export/v1", meta, refs, file=exp / "export.json")
    print(json.dumps({"export": art, "run": run, "sets": len(sets)}), flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])
