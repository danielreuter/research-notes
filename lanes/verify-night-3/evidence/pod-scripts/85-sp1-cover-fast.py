"""verify-night-3: the cover verification's check step for covers whose rebuild 83-sp1-cover-verify.py already made on
this pod (MY prepare output in PREP_DIR, the producer's prepare run_files in PROD_DIR). Same acceptance as
verify_object, without re-lowering each object twice more: my prepare lowered MY objects once, so each chunk's
statement and bound public values h_O || h_L || 01 are mine.

Per chunk: my statement / h_O / public values equal the producer's meta (the rebuild check); the cover run's proof
hashes to the run record; `veritor-zk-host verify --proof P --statement MY_statement` (Host.verify) says the proof
verifies, the vk is APPROVED, the guest is sound, statement_match is true, and the public values are exactly my
h_O || h_L || 01. Negatives: chunk000's proof against the two changed-output negatives' statements is refused, and all
three negatives from my bundle get verdict 00 in the executor.

    python 85-sp1-cover-fast.py OUTDIR COVER_ART PREP_DIR PROD_DIR
"""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

SRC = Path.cwd()
sys.path[:0] = [str(SRC / "packages/verity/src"), str(SRC / "backends/sp1/python")]
from verity.proofs.typed_obligation import TypedObligationSet, object_digest  # noqa: E402
from verity_sp1.host import APPROVED, Host  # noqa: E402

PY = os.environ.get("PY", sys.executable)
NEGS = ("wrong-first-output-word", "wrong-last-output-word", "tampered-output-leaf")


def R(*args):
    r = subprocess.run([PY, "-m", "research", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"research {' '.join(args)}: rc {r.returncode}: {r.stderr[-400:]}")
    return r.stdout


def main() -> int:
    out, art, md, pd = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
    out.mkdir(parents=True, exist_ok=True)
    host = Host(timeout=None)
    ident = host.info()
    if ident != APPROVED:
        raise SystemExit("the host's guest is not the APPROVED identity")
    cm = json.loads(R("data", "show", art, "--json"))["manifest"]
    fp = cm["meta"]["workload_fingerprint"]
    mmeta = json.loads((md / "meta.json").read_text())
    pmeta = json.loads(next(pd.rglob("meta.json")).read_text())
    keys = ("object_digest", "statement_sha256", "public_values")
    c: dict = {}
    same = [all(a[k] == b[k] for k in keys) for a, b in zip(mmeta["chunks"], pmeta["chunks"])]
    same_negs = {n: all(mmeta["negatives"][n][k] == pmeta["negatives"][n][k] for k in keys) for n in pmeta["negatives"]}
    c["prepare_rebuilt"] = {"ok": len(mmeta["chunks"]) == len(pmeta["chunks"]) and all(same) and all(same_negs.values()),
                            "detail": {"chunks": len(mmeta["chunks"]), "equal": sum(same), "negatives": same_negs}}
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress((md / "bundle.tgz").read_bytes()))) as t:
        mine = {m.name: t.extractfile(m).read() for m in t.getmembers() if m.isfile()}
    cd = out / f"cover-{art[4:12]}"
    listing = json.loads(R("data", "fetch", cm["refs"]["run_files"], "--list", "--json"))
    files = listing if isinstance(listing, list) else listing.get("files", [])
    want = {f["path"]: f.get("sha256") for f in files}
    R("data", "fetch", cm["refs"]["run_files"], "--to", str(cd))
    proofs = {}
    for ch in mmeta["chunks"]:
        name = f"chunk{ch['chunk']:03d}"
        rel = f"proofs/{name}-compressed.bin"
        p = next((q for q in cd.rglob(f"{name}-compressed.bin")), None)
        st = mine[f"{name}/statement.bin"]
        obj = TypedObligationSet.from_json(json.loads(gzip.decompress((md / "objects" / f"{name}.json.gz").read_bytes())))
        own = object_digest(obj) == ch["object_digest"] and hashlib.sha256(st).hexdigest() == ch["statement_sha256"]
        if p is None:
            proofs[name] = {"accepted": False, "why": "no proof"}
            continue
        rep = host.verify(p, st)
        acc = (rep.ok and rep.vk_hash == APPROVED.vk_hash and not rep.unsound and rep.statement_match is True
               and rep.public_values.hex() == ch["public_values"] and own)
        proofs[name] = {"accepted": acc, "hash_ok": hashlib.sha256(p.read_bytes()).hexdigest() == want.get(rel), "ok": rep.ok,
                        "vk": rep.vk_hash, "unsound": rep.unsound, "statement_match": rep.statement_match,
                        "public_values_are_mine": rep.public_values.hex() == ch["public_values"], "own_object": own}
        if name == "chunk000":
            neg = {}
            for n in NEGS[:2]:
                r2 = host.verify(p, mine[f"neg/{n}/statement.bin"])
                neg[n] = bool(r2.ok and r2.statement_match and r2.public_values.hex() == mmeta["negatives"][n]["public_values"])
            proofs[name]["negative_statements_accepted"] = neg
    c["proofs_hash_to_run_record"] = {"ok": bool(proofs) and all(x.get("hash_ok") for x in proofs.values())}
    c["every_chunk_accepted"] = {"ok": bool(proofs) and all(x["accepted"] for x in proofs.values()), "detail": proofs}
    c["negative_statements_refused"] = {"ok": not any(proofs.get("chunk000", {}).get("negative_statements_accepted", {True: True}).values())}
    ex = {}
    for n in NEGS:
        o = TypedObligationSet.from_json(json.loads(gzip.decompress((md / "objects" / f"neg-{n}.json.gz").read_bytes())))
        rep = host.execute(mine[f"neg/{n}/statement.bin"], mine[f"neg/{n}/witness.bin"], typed_object_digest=object_digest(o))
        ex[n] = {"verdict": rep.verdict, "pv_tail": rep.public_values[-1:].hex()}
    c["negatives_rejected_by_guest"] = {"ok": all(not e["verdict"] and e["pv_tail"] == "00" for e in ex.values()), "detail": ex}
    v = {"art": art, "run": cm["meta"].get("run_id"), "subcircuit": fp.get("subcircuit"), "B": fp.get("B"),
         "soundness_log2": (fp.get("security") or {}).get("achieved_log2"), "proofs": len(proofs), "checks": c,
         "accepted": all(x["ok"] for x in c.values()), "method": "85-sp1-cover-fast (Host.verify on my statement, my public values)"}
    (out / f"cover-verdict-{art[4:12]}.json").write_text(json.dumps(v, indent=1, default=str))
    print(json.dumps({"art": art, "subcircuit": v["subcircuit"], "proofs": v["proofs"], "accepted": v["accepted"],
                      "failed": [k for k, x in c.items() if not x["ok"]]}), flush=True)
    for p in cd.rglob("*.bin"):
        p.unlink()
    return 0 if v["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
