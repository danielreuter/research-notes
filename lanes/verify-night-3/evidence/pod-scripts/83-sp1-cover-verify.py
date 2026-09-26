"""verify-night-3: non-producer verification of sp1-evaluator's #101 sampled cover (snapshot members), from the store.

Per cover result (paired with its prepare result by bundle_sha256): fetch the prepare run's meta.json and the instance
set, rebuild the cover myself with `benchmarks/ir_call/sp1_cover.py prepare` (same set, range and chunk size), require
my chunk object digests, statement sha256 and public values (and the negatives') to equal the producer's; fetch the
cover run's proofs (sha256 against the run record's manifest) and accept each chunk only when `verify_object` accepts
it under the APPROVED key against MY chunk object; negatives: chunk000's proof against the two changed-output objects
must be refused, and all three negatives from MY bundle must get verdict 00 in the guest executor.

    python 83-sp1-cover-verify.py OUTDIR SNAPSHOT_ART      (cwd = the source tree; lib.sh env; VERITY_SP1_HOST set)
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
sys.path[:0] = [str(SRC / "packages/verity/src"), str(SRC / "backends/sp1/python"), str(SRC / "backends/numerical/python"),
                str(SRC / "integrations/vllm"), str(SRC / "benchmarks/ir_call")]

from verity.proofs.binding import bound_public_values  # noqa: E402
from verity.proofs.typed_obligation import TypedObligationSet, object_digest  # noqa: E402
from verity_sp1.host import APPROVED, Host  # noqa: E402
from verity_sp1.typed import verify_object  # noqa: E402

PY = os.environ.get("PY", sys.executable)
NEGS = ("wrong-first-output-word", "wrong-last-output-word", "tampered-output-leaf")


def R(*args):
    r = subprocess.run([PY, "-m", "research", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"research {' '.join(args)}: rc {r.returncode}: {r.stderr[-400:]}")
    return r.stdout


def show(art):
    return json.loads(R("data", "show", art, "--json"))["manifest"]


def fetch(art, d: Path) -> dict[str, str]:
    listing = json.loads(R("data", "fetch", art, "--list", "--json"))
    files = listing if isinstance(listing, list) else listing.get("files", [])
    R("data", "fetch", art, "--to", str(d))
    return {f["path"]: f.get("sha256") for f in files}


def find(d: Path, rel: str) -> Path:
    p = d / rel
    if p.exists():
        return p
    return next(q for q in d.rglob(Path(rel).name) if str(q).endswith(rel))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_obj(p: Path) -> TypedObligationSet:
    return TypedObligationSet.from_json(json.loads(gzip.decompress(p.read_bytes())))


def one(cover_art: str, cm: dict, prep: dict, out: Path, host: Host) -> dict:
    fp = cm["meta"]["workload_fingerprint"]
    v: dict = {"art": cover_art, "run": cm["meta"].get("run_id"), "subcircuit": fp.get("subcircuit"), "B": fp.get("B"),
               "soundness_log2": (fp.get("security") or {}).get("achieved_log2"), "prepare_art": prep["art"],
               "prepare_run": prep["m"]["meta"].get("run_id"), "checks": {}}
    c = v["checks"]
    tag = cover_art[4:12]
    pd = out / f"prod-prep-{tag}"
    fetch(prep["m"]["refs"]["run_files"], pd)
    pmeta = json.loads(find(pd, "meta.json").read_text())
    inst = pmeta["set"]
    chunk = prep["m"]["meta"]["workload_fingerprint"]["chunk"]
    sd = out / f"set-{inst['art'][4:12]}"
    if not any(sd.rglob("manifest.json")):
        R("data", "fetch", inst["art"], "--to", str(sd))
    sdir = next(p.parent for p in sd.rglob("manifest.json"))
    md = out / f"my-prep-{tag}"
    r = subprocess.run([PY, str(SRC / "benchmarks/ir_call/sp1_cover.py"), "prepare", "--set", str(sdir), "--set-art", inst["art"],
                        "--lo", str(inst["lo"]), "--hi", str(inst["hi"]), "--chunk", str(chunk), "--out", str(md)],
                       capture_output=True, text=True, cwd=SRC)
    (out / f"my-prep-{tag}.log").write_text(r.stdout[-4000:] + r.stderr[-4000:])
    if r.returncode:
        c["prepare_rebuilt"] = {"ok": False, "detail": r.stderr[-300:]}
        return v
    mmeta = json.loads((md / "meta.json").read_text())
    keys = ("object_digest", "statement_sha256", "public_values")
    same_chunks = [all(a[k] == b[k] for k in keys) for a, b in zip(mmeta["chunks"], pmeta["chunks"])]
    same_negs = {n: all(mmeta["negatives"][n][k] == pmeta["negatives"][n][k] for k in keys) for n in pmeta["negatives"]}
    c["prepare_rebuilt"] = {"ok": len(mmeta["chunks"]) == len(pmeta["chunks"]) and all(same_chunks) and all(same_negs.values()),
                            "detail": {"chunks": len(mmeta["chunks"]), "equal": sum(same_chunks), "negatives": same_negs}}
    # my own statements, from my objects: h_O and h_L recomputed here
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress((md / "bundle.tgz").read_bytes()))) as t:
        mine = {m.name: t.extractfile(m).read() for m in t.getmembers() if m.isfile()}
    cd = out / f"cover-{tag}"
    want = fetch(cm["refs"]["run_files"], cd)
    proofs = {}
    for ch in mmeta["chunks"]:
        name = f"chunk{ch['chunk']:03d}"
        rel = f"proofs/{name}-compressed.bin"
        p = find(cd, rel) if rel in want else None
        obj = load_obj(md / "objects" / f"{name}.json.gz")
        own = {"h_O": object_digest(obj) == ch["object_digest"],
               "statement": hashlib.sha256(mine[f"{name}/statement.bin"]).hexdigest() == ch["statement_sha256"],
               "public_values": bound_public_values(obj, statement_format=3).hex() == ch["public_values"]}
        if p is None:
            proofs[name] = {"accepted": False, "why": "no proof in run_files"}
            continue
        a = verify_object(host, obj, p, statement_format=3)
        proofs[name] = {"accepted": a.accepted, "hash_ok": sha(p) == want[rel], "approved_key": a.approved_key, "binding_ok": a.binding.ok,
                        "reasons": a.reasons(), "own_recompute": own}
        if name == "chunk000":
            proofs[name]["negative_objects_accepted"] = {
                n: verify_object(host, load_obj(md / "objects" / f"neg-{n}.json.gz"), p, statement_format=3).accepted for n in NEGS[:2]}
    c["proofs_hash_to_run_record"] = {"ok": bool(proofs) and all(x.get("hash_ok") for x in proofs.values())}
    c["every_chunk_verify_object_accepted"] = {"ok": bool(proofs) and all(x["accepted"] and all(x.get("own_recompute", {}).values())
                                                                          for x in proofs.values()),
                                               "detail": {k: {kk: x.get(kk) for kk in ("accepted", "binding_ok", "approved_key", "reasons")}
                                                          for k, x in proofs.items()}}
    c["negative_objects_refused"] = {"ok": not any((proofs.get("chunk000", {}).get("negative_objects_accepted") or {True: True}).values())}
    ex = {}
    for n in NEGS:
        o = load_obj(md / "objects" / f"neg-{n}.json.gz")
        rep = host.execute(mine[f"neg/{n}/statement.bin"], mine[f"neg/{n}/witness.bin"], typed_object_digest=object_digest(o))
        ex[n] = {"verdict": rep.verdict, "pv_tail": rep.public_values[-1:].hex()}
    c["negatives_rejected_by_guest"] = {"ok": all(not e["verdict"] and e["pv_tail"] == "00" for e in ex.values()), "detail": ex}
    v["proofs"] = len(proofs)
    v["accepted"] = all(x["ok"] for x in c.values())
    for p in cd.rglob("*.bin"):
        p.unlink()
    return v


def main() -> int:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    host = Host(timeout=None)
    ident = host.info()
    print(json.dumps({"host_identity": str(ident), "approved": ident == APPROVED}), flush=True)
    if ident != APPROVED:
        raise SystemExit("the host's guest is not the APPROVED identity")
    snap = show(sys.argv[2])
    covers, preps = {}, {}
    for art in snap["refs"]["members"]:
        m = show(art)
        fp = m["meta"]["workload_fingerprint"]
        (preps if fp.get("workload") == "sp1-ir-call-cover.prepare" else covers)[fp.get("bundle_sha256")] = {"art": art, "m": m}
    print(json.dumps({"covers": len(covers), "prepares": len(preps)}), flush=True)
    res = []
    only = [x for x in os.environ.get("ONLY", "").split(",") if x]
    skip = [x for x in os.environ.get("SKIP", "").split(",") if x]
    for b, cv in sorted(covers.items(), key=lambda kv: kv[1]["art"]):
        if (only and not any(cv["art"].startswith("art:" + x) for x in only)) or any(cv["art"].startswith("art:" + x) for x in skip):
            continue
        try:
            if b not in preps:
                raise RuntimeError(f"no prepare result with bundle_sha256 {b}")
            v = one(cv["art"], cv["m"], preps[b], out, host)
        except Exception as e:  # noqa: BLE001
            v = {"art": cv["art"], "accepted": False, "error": repr(e)[:400]}
        res.append(v)
        (out / f"cover-verdict-{cv['art'][4:12]}.json").write_text(json.dumps(v, indent=1, default=str))
        print(json.dumps({"art": v["art"], "subcircuit": v.get("subcircuit"), "proofs": v.get("proofs"), "accepted": v.get("accepted"),
                          "failed": [k for k, x in v.get("checks", {}).items() if not x["ok"]], "error": v.get("error")}), flush=True)
    (out / "cover-verdicts.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({"covers": len(res), "accepted": sum(bool(v.get("accepted")) for v in res),
                      "proofs": sum(v.get("proofs") or 0 for v in res)}), flush=True)
    return 0 if res and all(v.get("accepted") for v in res) else 1


if __name__ == "__main__":
    sys.exit(main())
