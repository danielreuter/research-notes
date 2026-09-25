"""verify-night-2: the byte-identity claim across a producer's runs (hash-commit 0612Z: every run's commit evidence and rep-1
statements are the same bytes, whatever the committer).  For each run-files tree: sha256 of commit-evidence.json, the
evidence's own `sha256` field, `cat proofs/rep1/*.stmt | sha256sum` (sorted names), the tree roots, the system.bin sha256,
and, for trees that carry .proof files, whether every dumped file's sha256 equals the tree's proofs.sha256 line.

    python 07-byte-identity.py LIST     (LIST: lines with tree=art:... result=art:... as lanes/hash-commit/evidence/registered-4090.txt)
"""
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

from research.store.local import LocalStore


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(listfile):
    st = LocalStore()
    rows = []
    for line in Path(listfile).read_text().splitlines():
        mt, mr = re.search(r"tree=(art:\w+)", line), re.search(r"result=(art:\w+)", line)
        if not mt:
            continue
        tag = line.split()[1] if len(line.split()) > 1 else ""
        with tempfile.TemporaryDirectory(dir="/workspace/verify-night-2") as td:
            d = Path(st.fetch(mt.group(1), Path(td) / "t"))
            ce = sorted(d.rglob("commit-evidence.json"))
            ev = json.loads(ce[0].read_text()) if ce else {}
            rep1 = sorted(p for p in d.rglob("*.stmt") if p.parent.name == "rep1")
            stmt_sha = hashlib.sha256(b"".join(p.read_bytes() for p in rep1)).hexdigest()
            sysb = sorted(d.rglob("system.bin"))
            proofs = sorted(d.rglob("*.proof"))
            shaf = sorted(d.rglob("proofs.sha256"))
            listed = {}
            if shaf:
                for ln in shaf[0].read_text().splitlines():
                    if ln.strip():
                        h, name = ln.split(None, 1)
                        listed[name.strip().lstrip("*").lstrip("./")] = h
            pdir = shaf[0].parent if shaf else (proofs[0].parent.parent if proofs else d)
            present = [p for p in pdir.rglob("*") if p.is_file() and p.name not in ("proofs.sha256",)]
            mism = []
            for p in present:
                rel = str(p.relative_to(pdir))
                if rel in listed and sha(p) != listed[rel]:
                    mism.append(rel)
            # the statements listed in proofs.sha256 must be the ones present
            stmt_listed = sorted(k for k in listed if k.endswith(".stmt") and k.startswith("rep1/"))
            rows.append({"tag": tag, "tree": mt.group(1), "result": mr.group(1) if mr else None,
                         "commit_evidence_file_sha256": sha(ce[0]) if ce else None, "evidence_sha256": ev.get("sha256"),
                         "roots": {n: t.get("root") for n, t in (ev.get("trees") or {}).items()},
                         "rep1_stmts": len(rep1), "rep1_stmt_cat_sha256": stmt_sha,
                         "system_sha256": sha(sysb[0]) if sysb else None, "proof_files": len(proofs),
                         "proofs_sha256_lines": len(listed), "present_checked": sum(1 for p in present if str(p.relative_to(pdir)) in listed),
                         "sha_mismatches": mism, "rep1_stmts_listed": len(stmt_listed)})
            r = rows[-1]
            print(f"{tag:28s} ce={str(r['commit_evidence_file_sha256'])[:12]} ev={str(r['evidence_sha256'])[:12]} "
                  f"stmt={stmt_sha[:12]} ({len(rep1)}) sys={str(r['system_sha256'])[:12]} proofs={len(proofs)} "
                  f"listed={len(listed)} checked={r['present_checked']} mism={len(mism)}", file=sys.stderr, flush=True)
    keys = ("commit_evidence_file_sha256", "evidence_sha256", "rep1_stmt_cat_sha256", "system_sha256")
    summary = {k: sorted({r[k] for r in rows}, key=str) for k in keys}
    summary["roots"] = sorted({json.dumps(r["roots"], sort_keys=True) for r in rows})
    summary["runs"] = len(rows)
    summary["any_sha_mismatch"] = any(r["sha_mismatches"] for r in rows)
    print(json.dumps({"summary": summary, "rows": rows}, indent=1))
    ok = all(len(v) == 1 for k, v in summary.items() if k in keys or k == "roots") and not summary["any_sha_mismatch"]
    print("IDENTICAL" if ok else "DIFFER", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
