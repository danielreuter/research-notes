"""program_graphs.py OUT_DIR ROW_KEY PROGRAMS_DIR [--record expected|PATH] [--vus VUS_JSONL] [--run R] [--row N] [--class C]

One served row's program.json (verity_vllm.pipeline.program_graph) from its request Programs (every */instances.json.gz under
PROGRAMS_DIR), with the run's units from its replay strata (the regression record's `replay_partition`, or a run's
`sampled_replay_p0.json`) and the exported VUs of a VU export."""
import argparse
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from site_bundle import REPO, serving  # noqa: E402

from verity_vllm.pipeline.program_graph import program_graph, request_programs_of  # noqa: E402


def request_programs(root: str) -> list[str]:
    """The row's request Programs: every `build_request_LP*` (B > 1; `build_request` is then one of them again, the component of
    record) else `build_request`; on a TP row, rank 0's (the graph of one rank's shard)."""
    allp = sorted(glob.glob(f"{root}/**/instances.json.gz", recursive=True))
    ranks = sorted({p.split("/rank")[1].split("/")[0] for p in allp if "/rank" in p})
    if ranks:
        allp = [p for p in allp if f"/rank{ranks[0]}/" in p]
    lp = [p for p in allp if Path(p).parent.name.startswith("build_request_LP")]
    return lp or [p for p in allp if Path(p).parent.name == "build_request"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("row_key")
    ap.add_argument("programs_dir")
    ap.add_argument("--record", default="expected")
    ap.add_argument("--vus", default=None)
    ap.add_argument("--store", default=None)
    ap.add_argument("--run", default=None)
    ap.add_argument("--row", type=int, default=None)
    ap.add_argument("--klass", default=None)
    ap.add_argument("--programs-art", default=None)
    a = ap.parse_args()
    paths = request_programs(a.programs_dir)
    strata, rec_src, row_no, klass = None, None, a.row, a.klass
    if a.record == "expected":
        f = REPO / "tests/regression/expected" / f"{a.row_key}.json"
        d = json.loads(f.read_text())
        strata = (d.get("replay_partition") or {}).get("strata") or None
        rec_src, row_no, klass = f"tests/regression/expected/{a.row_key}.json", row_no or d.get("row"), klass or d.get("class")
    elif a.record:
        strata = json.loads(Path(a.record).read_text())["sampled_replay"]["strata"]
        rec_src = f"{a.run}: commit/sampled_replay_p0.json"
    row = {"row": row_no, "class": klass, "serving": serving(a.row_key), "run": a.run, "units_from": rec_src,
           "tp_rank": ("rank 0 of the TP row (one rank's shard)" if any("/rank" in p for p in paths) else None),
           "programs_artifact": a.programs_art, "exported_from": a.vus}
    g = program_graph(paths, row=row, strata=strata, vus_jsonl=a.vus, request_programs=request_programs_of(a.store) if a.store else None)
    out = Path(a.out_dir) / f"{a.row_key}.program.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(g, separators=(",", ":"), default=str) + "\n")
    folds = {}
    for m in g["modules"]:
        folds.setdefault(m["subtree_hash"], []).append(m["path"])
    print(json.dumps({"out": str(out), "bytes": out.stat().st_size, "programs": len(g["programs"]), "modules": len(g["modules"]),
                      "groups": len(g["groups"]), "edges": len(g["edges"]), "largest_fold": max((len(v) for v in folds.values()), default=0)}))


if __name__ == "__main__":
    main()
