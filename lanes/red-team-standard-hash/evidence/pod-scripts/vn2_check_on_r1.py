"""red-team-standard-hash: run verify-night-2's 06-core-roots.py `check` VERBATIM on my R1 fixture (forgery + control).

The fixture's manifests predate the store layout, so a fake store serves each fixture dir as `<tree>/proofs/`, with the
manifest's relation set to the statement's full name and each file given the (vus, rep) a producer manifest carries.
Expected: forgery -> MISMATCH naming the leaf indices and the y tree; a/b trees (binding, owner, count, root) equal core.
(The control shares the forgery's committed y tree, so it is MISMATCH on y only.)

    VN2_N=2 python vn2_check_on_r1.py FIXTURE_DIR PATH_TO_06
"""
import importlib.util
import json
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

fix, p06 = Path(sys.argv[1]), sys.argv[2]
os.makedirs("/workspace/verify-night-2", exist_ok=True)
spec = importlib.util.spec_from_file_location("core_roots", p06)
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)
n = cr.N


class FakeStore:
    def get_manifest(self, art):
        return SimpleNamespace(refs={"run_files": art}, meta={})

    def fetch(self, tree, dest, paths=None):
        dest = Path(dest)
        shutil.copytree(fix / tree, dest / "proofs", ignore=shutil.ignore_patterns("system.bin", "*.proof", "reverify"))
        m = json.loads((dest / "proofs" / "manifest.json").read_text())
        m["relation"] = "fp8-ada+blake3"
        for f in m["files"]:
            f.setdefault("vus", [0, n])
            f.setdefault("rep", 0)
        (dest / "proofs" / "manifest.json").write_text(json.dumps(m))
        return dest


out = {}
for tag in ("forgery", "control"):
    r = cr.check(FakeStore(), tag)
    r.pop("info", None)
    out[tag] = r
    print(f"{tag}: {r['status']} problems={r.get('problems')}", flush=True)
print(json.dumps(out, indent=1))
fp = " | ".join(out["forgery"]["problems"])
ok = (out["forgery"]["status"] == "MISMATCH" and "leaf indices" in fp and "tree y" in fp
      and "tree a" not in fp and "tree b" not in fp)
print("EXPECTED" if ok else "UNEXPECTED")
sys.exit(0 if ok else 1)
