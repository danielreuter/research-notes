"""verify-night-3: non-producer verification of sp1-evaluator's SP1 proofs, from the store alone.

Per result artifact: fetch its run_files (the proofs, their sha256 checked against the run record's manifest), fetch the
instance set it names, rebuild the statement with `benchmarks/ir_call/sp1_ir_call.py prepare` from this tree (object
digest and statement sha256 must equal the recorded ones), verify every proof with `verify_object` under the APPROVED
key against MY object (public values h_O || h_L || 01 recomputed from my statement), and run the three negatives:
the two object-changing ones against the same proof (must be refused) and all three in the guest executor (verdict 00).

    python 81-sp1-verify.py OUTDIR ART...      (cwd = the source tree; lib.sh's store env; VERITY_SP1_HOST set)
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SRC = Path.cwd()
sys.path[:0] = [str(SRC / "packages/verity/src"), str(SRC / "backends/sp1/python"), str(SRC / "backends/numerical/python"),
                str(SRC / "integrations/vllm"), str(SRC / "benchmarks/ir_call")]

from verity.proofs.binding import bound_public_values  # noqa: E402
from verity.proofs.typed_obligation import object_digest  # noqa: E402
from verity_sp1.host import APPROVED, Host  # noqa: E402
from verity_sp1.typed import verify_object  # noqa: E402

import sp1_ir_call as S  # noqa: E402

PY = os.environ.get("PY", sys.executable)


def R(*args, out=True):
    r = subprocess.run([PY, "-m", "research", *args], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"research {' '.join(args)}: rc {r.returncode}: {r.stderr[-400:]}")
    return r.stdout


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def one(art: str, out: Path, host: Host) -> dict:
    v: dict = {"art": art, "checks": {}}
    c = v["checks"]
    m = json.loads(R("data", "show", art, "--json"))["manifest"]
    meta, fp = m["meta"], m["meta"]["workload_fingerprint"]
    v["run"], inst = meta.get("run_id"), fp["instances"]
    rf = m["refs"]["run_files"]
    d = out / f"rf-{art[4:12]}"
    listing = json.loads(R("data", "fetch", rf, "--list", "--json"))
    R("data", "fetch", rf, "--to", str(d))
    files = listing if isinstance(listing, list) else listing.get("files", [])
    want = {f["path"]: f.get("sha256") for f in files}
    proofs = sorted(p for p in want if Path(p).name.startswith("proof-") and p.endswith(".bin"))
    got = {}
    for p in proofs:
        f = next((q for q in d.rglob(Path(p).name)), None)
        got[p] = f is not None and sha(f) == want[p]
    c["proofs_hash_to_run_record"] = {"ok": bool(proofs) and all(got.values()), "detail": got}
    sd = out / f"set-{inst['set_art'][4:12]}"
    if not (sd / "manifest.json").exists():
        R("data", "fetch", inst["set_art"], "--to", str(sd))
    sdir = next(p.parent for p in sd.rglob("manifest.json"))
    pd = out / f"prep-{art[4:12]}"
    r = subprocess.run([PY, str(SRC / "benchmarks/ir_call/sp1_ir_call.py"), "prepare", "--set", str(sdir), "--set-art", inst["set_art"],
                        "--lo", str(inst["lo"]), "--hi", str(inst["hi"]), "--out", str(pd)], capture_output=True, text=True, cwd=SRC)
    (out / f"prep-{art[4:12]}.log").write_text(r.stdout + r.stderr)
    if r.returncode:
        c["statement_rebuilt"] = {"ok": False, "detail": r.stderr[-300:]}
        return v
    pm, bundles = S._read_bundle(pd / "bundle.tar")
    honest = bundles["honest"]
    mine = {"object_digest": object_digest(honest["obj"]), "statement_sha256": hashlib.sha256(honest["statement"]).hexdigest()}
    c["statement_rebuilt"] = {"ok": mine["object_digest"] == fp["object_digest"] and mine["statement_sha256"] == fp["statement_sha256"],
                              "detail": {"mine": mine, "recorded": {k: fp[k] for k in mine}}}
    pv = bound_public_values(honest["obj"], statement_format=3).hex()
    acc = {}
    for p in proofs:
        f = next(q for q in d.rglob(Path(p).name))
        a = verify_object(host, honest["obj"], f, statement_format=3)
        negs = {name: verify_object(host, bundles[name]["obj"], f, statement_format=3).accepted
                for name in ("wrong-first-output-word", "wrong-last-output-word")}
        acc[Path(p).name] = {"accepted": a.accepted, "reasons": a.reasons(), "approved_key": a.approved_key, "binding_ok": a.binding.ok,
                             "negative_objects_accepted": negs}
    c["proofs_verify_approved_key_bound_to_my_statement"] = {
        "ok": bool(acc) and all(x["accepted"] and x["approved_key"] and x["binding_ok"] for x in acc.values()),
        "detail": acc, "public_values_mine": pv}
    c["negative_objects_refused"] = {"ok": bool(acc) and not any(any(x["negative_objects_accepted"].values()) for x in acc.values())}
    ex = {}
    for name in S.NEGATIVES:
        b = bundles[name]
        rep = host.execute(b["statement"], b["witness"], typed_object_digest=object_digest(b["obj"]))
        ex[name] = {"verdict": rep.verdict, "pv_tail": rep.public_values[-1:].hex()}
    c["negatives_rejected_by_guest"] = {"ok": all(not e["verdict"] and e["pv_tail"] == "00" for e in ex.values()), "detail": ex}
    v["soundness_log2"] = (fp.get("security") or {}).get("achieved_log2")
    v["subcircuit"], v["B"] = fp.get("subcircuit"), fp.get("B")
    v["accepted"] = all(x["ok"] for x in c.values())
    for p in d.rglob("proof-*.bin"):
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
    res = []
    for art in sys.argv[2:]:
        try:
            v = one(art, out, host)
        except Exception as e:  # noqa: BLE001
            v = {"art": art, "accepted": False, "error": repr(e)[:400]}
        res.append(v)
        (out / f"verdict-{art[4:12]}.json").write_text(json.dumps(v, indent=1, default=str))
        print(json.dumps({"art": art, "accepted": v.get("accepted"), "failed": [k for k, x in v.get("checks", {}).items() if not x["ok"]],
                          "error": v.get("error")}), flush=True)
    (out / "verdicts.json").write_text(json.dumps(res, indent=1, default=str))
    return 0 if all(v.get("accepted") for v in res) else 1


if __name__ == "__main__":
    sys.exit(main())
