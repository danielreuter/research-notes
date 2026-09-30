"""proofs-rows: the (b) stage/prove split's marker and checks, for this directory's 73-sweep-shape.sh.

    stage_mark.py write OUT_K SHAPE   after a stage-only job (STAGE_ONLY=1): the marker $FLOCK_STAGE_CACHE/staged/<ident>.json, naming
                                      the cache entry the job wrote and its files' sha256
    stage_mark.py pre OUT_K SHAPE     before a GPU job (REQUIRE_STAGED=1): exit 3 unless that marker and its cache entry exist
    stage_mark.py post OUT_K SHAPE    after it: exit 3 if the job staged the shape itself (a GPU-side stage), proved from another
                                      entry, or the entry's bytes are no longer the marker's

ident is what class_statement's FLOCK_STAGE_CACHE key reads that 73-sweep-shape.sh sets: the staging code (class_statement's own
_source_digest), the Definitions file (the program and the shape's row units), the shape and the batch settings. The key's other
inputs (seed, partition, max ANDs) are class_statement's defaults, which 70-class-sweep.sh never changes; post catches a miss anyway.
Each op writes OUT_K/stage-check.json (SUMMARY's stage_checks).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

SETTINGS = {"SELECT": "units", "BATCH": "auto", "N": "", "BATCH_ANDS": "", "MAX_STATEMENT_BITS": "", "FLOCK_GEMM_TILE": ""}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while b := f.read(1 << 24):
            h.update(b)
    return h.hexdigest()


def files(d: Path) -> dict[str, str]:
    return {f.name: sha256(f) for f in sorted(d.iterdir()) if f.is_file() and f.name not in ("rec.json", "serve.log")}


def ident(o: Path, shape: str) -> tuple[str, dict]:
    from verity_flock.class_statement import _source_digest
    parts = {"source_digest": _source_digest(), "defs_sha256": sha256(o / "defs.json"), "shape": shape,
             "settings": {k: os.environ.get(k) or v for k, v in SETTINGS.items()}}
    return hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).hexdigest()[:32], parts


def record(o: Path, name: str, shape: str) -> dict | None:
    p = o / "classes" / name
    recs = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()] if p.exists() else []
    return next((r for r in recs if r.get("shape") == shape), None)


def finish(o: Path, check: dict, t0: float) -> int:
    check["check_s"] = round(time.time() - t0, 3)
    (o / "stage-check.json").write_text(json.dumps(check, indent=1))
    print("stage-check", json.dumps(check), flush=True)
    return 0 if check["ok"] else 3


def main() -> int:
    op, o, shape = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    t0, root = time.time(), Path(os.environ["FLOCK_STAGE_CACHE"])
    if op == "write":
        rec = record(o, "staged.jsonl", shape)
        if not rec or "stage" not in rec:
            return finish(o, {"op": op, "ok": False, "why": f"not staged: {(rec or {}).get('broke') or 'no record'}"}, t0)
        fs, csha = files(o / "classes" / shape[:16]), rec["stage"].get("circuit_sha512")
        entry = rec.get("stage_cached")
        if not entry:
            for e in sorted(root.iterdir()):
                r = json.loads((e / "rec.json").read_text()) if len(e.name) == 32 and (e / "rec.json").exists() else {}
                if r.get("shape") == shape and (r.get("stage") or {}).get("circuit_sha512") == csha and files(e) == fs:
                    entry = e.name
                    break
        if not entry:
            return finish(o, {"op": op, "ok": False, "why": f"the stage wrote no entry in {root} holding these bytes"}, t0)
        key, parts = ident(o, shape)
        mark = {"ident": key, **parts, "entry": entry, "files": fs, "circuit_sha512": csha, "stage_s": rec.get("stage_s"),
                "stage_py_maxrss_gb": rec.get("stage_py_maxrss_gb"), "row_units": rec.get("row_units"), "definition": rec.get("definition"),
                "stage_run": os.path.basename(os.environ.get("RESEARCH_RUN_DIR", "")), "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        (root / "staged").mkdir(exist_ok=True)
        tmp = root / "staged" / f".{key}.json.tmp{os.getpid()}"
        tmp.write_text(json.dumps(mark, indent=1))
        os.replace(tmp, root / "staged" / f"{key}.json")
        return finish(o, {"op": op, "ok": True, "ident": key, "entry": entry, "files": fs, "stage_s": rec.get("stage_s")}, t0)
    if op == "pre":
        key, _parts = ident(o, shape)
        m = root / "staged" / f"{key}.json"
        mark = json.loads(m.read_text()) if m.exists() else None
        why = (f"not staged: no marker {m}" if mark is None else
               f"not staged: its cache entry {mark['entry']} is gone" if not (root / mark["entry"] / "rec.json").exists() else None)
        return finish(o, {"op": op, "ok": why is None, "ident": key} | ({"why": why} if why else {"entry": mark["entry"]}), t0)
    if op == "post":
        pre = json.loads((o / "stage-check.json").read_text())
        mark = json.loads((root / "staged" / f"{pre['ident']}.json").read_text())
        rec = record(o, "results.jsonl", shape) or {}
        live, got = rec.get("live") or {}, rec.get("stage_cached")
        fs = files(root / mark["entry"]) if (root / mark["entry"]).is_dir() else {}
        why = ("no result for the shape" if not rec else
               f"staged in the GPU job ({rec.get('stage_s')} s): a GPU-side stage" if not got else
               f"proved from cache entry {got}, not the marker's {mark['entry']}" if got != mark["entry"] else
               "the cache entry's bytes are no longer the marker's" if fs != mark["files"] else
               "the statement's circuit isn't the marker's" if (rec.get("stage") or {}).get("circuit_sha512") != mark["circuit_sha512"] else None)
        return finish(o, {"op": op, "ok": why is None, "ident": pre["ident"], "entry": mark["entry"], "stage_run": mark.get("stage_run"),
                          "stage_cached": got, "stage_s": rec.get("stage_s"), "files_match": fs == mark["files"], "files": fs,
                          "statement_digest": live.get("statement_digest"), "pre_check_s": pre.get("check_s")} | ({"why": why} if why else {}), t0)
    raise SystemExit(f"op {op}?")


if __name__ == "__main__":
    raise SystemExit(main())
