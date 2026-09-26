"""verify-bligero-real-k: non-producer check of one B-interactive cell on a CPU pod, from the shipped source (main).

  python cell_check.py CELL_ART --out DIR --work DIR --verifier BIN [--jobs N]

1. re-stage the cell's input set from the store myself (`research data fetch`), check every file against its manifest and the
   content digest the cell names, re-evaluate every instance with the IR evaluator (`input_sets.verify`), and compare each file's
   sha256 with the copy the prover staged (its run record's `set/` entries);
2. main's reverify on the cell (dry run: labels are written from the VM with --ref this run): custody, system PINNED, hash
   commitments recomputed from MY staged set (--instances-root), coverage, `ligero-verify batch --target-bits 128` on every rep;
3. sha256 of every dumped .proof / .stmt / .coins, for the comparison with the live verifier's session records (done on the VM).
"""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path


def sh(*a, **kw):
    return subprocess.run(list(a), capture_output=True, text=True, **kw)


def show(ref):
    r = sh("research", "data", "show", ref, "--json")
    if r.returncode:
        raise SystemExit(f"research data show {ref}: {r.stderr[-400:]}")
    return json.loads(r.stdout)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


ap = argparse.ArgumentParser()
ap.add_argument("cell"); ap.add_argument("--out", type=Path, required=True); ap.add_argument("--work", type=Path, required=True)
ap.add_argument("--verifier", required=True); ap.add_argument("--jobs", type=int, default=os.cpu_count())
ns = ap.parse_args()
ns.out.mkdir(parents=True, exist_ok=True); ns.work.mkdir(parents=True, exist_ok=True)
summary = {"cell": ns.cell, "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

cell = show(ns.cell)
man, meta = cell["manifest"], cell["manifest"]["meta"]
cid = cell["id"]
summary |= {"cell": cid, "run": meta["run_id"], "relation": meta["cell"]["relation"], "input_set": man["refs"]["input_set"],
            "run_files": man["refs"]["run_files"]}

# 1. the input set, re-staged by me
from verity_numerical.bench import input_sets as IS
set_art = man["refs"]["input_set"]
want_cd = meta["cell"]["input_set"]["content_digest"]
sdir_root = ns.work / "sets" / set_art[4:16]
r = sh("research", "data", "fetch", set_art, "--to", str(sdir_root))
if r.returncode:
    raise SystemExit(f"fetch {set_art}: {r.stderr[-400:]}")
fetched = Path(r.stdout.strip().splitlines()[-1])
cands = [fetched] + [p.parent for p in fetched.rglob("manifest.json")]
sdir = next(c for c in cands if (c / "manifest.json").is_file() and "ports" in json.loads((c / "manifest.json").read_text()))
s = IS.InputSet.open(sdir)
bad_files = s.check_files()
t = time.time()
ver = IS.verify(sdir)
mine = {f: sha(sdir / f) for f in s.manifest["files"]} | {"manifest.json": s.manifest_sha256()}
att = show(meta["run_id"])
rec = show(att["outputs"]["run_record"]) if "outputs" in att else None
if rec is None:
    rec_files = {}
else:
    rec_files = {f["path"].split("/", 2)[2]: f["sha256"] for f in rec["manifest"]["payload"]["files"] if f["path"].startswith("set/")}
summary["input_set_check"] = {
    "dir": str(sdir), "set": s.name, "schema": s.manifest["schema"], "n": s.n, "source": s.source,
    "content_digest": s.content_digest, "content_digest_eq_cell": s.content_digest == want_cd, "files_vs_manifest": bad_files or "all match",
    "ir_verify": {k: ver[k] for k in ("ok", "checked", "bad_n", "bad", "subcircuit") if k in ver}, "ir_verify_seconds": round(time.time() - t, 1),
    "manifest_sha256": s.manifest_sha256(),
    "prover_staged_copy": {"record": (rec or {}).get("id"), "files_compared": sorted(set(mine) & set(rec_files)),
                           "equal": bool(rec_files) and all(mine[f] == rec_files[f] for f in set(mine) & set(rec_files)),
                           "only_mine": sorted(set(mine) - set(rec_files)), "only_prover": sorted(set(rec_files) - set(mine))},
}

# 2. main's reverify checks (backends.direct.ligero.reverify.verify_tree, unchanged) on the cell's proof dir with my staged set.
#    reverify's own entry point looks for proofs/ or dumps/ at the tree root only; a bench.cell tree nests it under the result's
#    meta.artifacts[0] (sweep/<point>/proofs), so the dir is located here and handed to verify_tree as reverify would.
from backends.direct.ligero import reverify as RV
tree = ns.work / "rv" / cid[4:20]
t = time.time()
r = sh("research", "data", "fetch", man["refs"]["run_files"], "--to", str(tree))
if r.returncode:
    raise SystemExit(f"fetch run_files: {r.stderr[-400:]}")
arts = meta.get("artifacts") or []
pdir = tree / arts[0] if arts and (tree / arts[0] / "manifest.json").is_file() else None
v = RV.load_verifier(Path(ns.verifier))
rep = RV.Report(cid)
rep.run_files, rep.run = man["refs"]["run_files"], meta["run_id"]
if pdir is None:
    rep.status, rep.why = "ERROR", [f"no proof dir at meta.artifacts {arts} in {rep.run_files}"]
else:
    pman = json.loads((pdir / "manifest.json").read_text())
    params = att.get("params") or {}
    rep.mode = pman.get("mode") or params.get("mode")
    RV.verify_tree(pdir, pman, v, rep, jobs=ns.jobs, params=params, asserted=meta["cell"]["relation"].split("+")[0],
                   out_dir=ns.out / "reps", instances_root=str(sdir), fingerprint=meta.get("workload_fingerprint"))
det = RV.detail(rep, v) if rep.status == "PASS" else None
summary["reverify"] = {"entry": "reverify.verify_tree (main)", "seconds": round(time.time() - t, 1), "proof_dir": str(pdir),
                       "verifier": {"path": str(v.path), "sha256": v.sha256, "tag": v.tag}, "detail": det,
                       **{k: getattr(rep, k) for k in ("status", "why", "relation", "mode", "hashed", "custody", "run", "run_files", "tile")},
                       "reps": {k: {q: x.get(q) for q in ("n", "accepted", "rejected", "batch_accepted", "batch_bits", "system_pinned",
                                                          "python_disagree", "verify_seconds_sum", "wall_seconds", "batch_reason")}
                                for k, x in rep.reps.items()}}

# 3. the dumped files' digests
pdirs = [pdir] if pdir is not None else []
files = {}
for pdir in pdirs:
    files["system.bin"] = sha(pdir / "system.bin")
    for rep in sorted(q for q in pdir.iterdir() if q.is_dir() and q.name.startswith("rep")):
        for f in sorted(rep.iterdir()):
            if f.suffix in (".proof", ".stmt", ".coins", ".hproof"):
                files[f"{rep.name}/{f.name}"] = sha(f)
(ns.out / "files.json").write_text(json.dumps(files, indent=0))
summary["files_hashed"] = len(files)
summary["t1"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
(ns.out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
print(json.dumps({k: summary[k] for k in ("cell", "relation", "files_hashed")} | {"set_ok": summary["input_set_check"]["ir_verify"].get("ok"),
      "set_cd": summary["input_set_check"]["content_digest_eq_cell"], "staged_eq": summary["input_set_check"]["prover_staged_copy"]["equal"],
      "reverify": summary["reverify"]["status"], "why": summary["reverify"]["why"]}), flush=True)
