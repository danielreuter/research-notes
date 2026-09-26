#!/usr/bin/env python3
"""red-team-flock-3: one registered pure-block GEMM cell from its verifier run's own record: TG6 (relation, pin, domain,
statement digest), PB1 (commit and binary named), PB2 (union), PB3 (my CPU replay of every recorded session with a build of the
cell's verifier commit, and proofs from another session / swapped reps rejected), PB4 (require_link, exchange link, one Sigma
per sub-batch), the verifier's staged instance files regenerated from the registered input set, contention and validation.

  gemm_cell_check.py ART [--relation bf16-ampere-total] [--pin HEX] [--points p0-1024,...] [--regen] [--procs 4]

Prints one GEMMCELL json line (ok = every check true). The replay binary is /tmp/rtf3/bin-<commit8>/flock-pure-gpu, built by
/tmp/rtf3/build-pure.sh from a worktree of that commit when missing (the Flock patch files must be the reviewed ones).
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

TREES = Path.home() / ".research/store/trees"
PATCHES = {"flock-link-b684b12.patch": "8a3c2697eaa0", "flock-gpu-link-b684b12.patch": "0880801bbbb5"}


def sh(*a, check=False):
    return subprocess.run(list(a), capture_output=True, text=True, check=check).stdout


def meta_of(art):
    return next(json.loads(l.split(None, 1)[1]) for l in sh("research", "data", "show", art).splitlines() if l.startswith("meta"))


def record_of(run):
    rows = [l.split() for l in sh("research", "data", "select", "--attempt", run, "--kind", "run-record/v1").splitlines() if l.startswith("art:")]
    a = rows[0][0]
    sh("research", "data", "fetch", a)
    return next(TREES.glob(a[4:] + "*"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def binary(commit):
    b = Path(f"/tmp/rtf3/bin-{commit[:8]}/flock-pure-gpu")
    if b.exists():
        return b
    wt = Path(f"/tmp/rtf3-wt-{commit[:8]}")
    if not wt.exists():
        sh("git", "-C", "/workspace", "fetch", "-q", "origin", commit)
        sh("git", "-C", "/workspace", "worktree", "add", "-q", "--detach", str(wt), commit, check=True)
    for f, want in PATCHES.items():
        got = sha(wt / "backends/flock" / f)[:12]
        if got != want:
            sys.exit(f"{commit[:8]}: {f} is {got}, not the reviewed {want}; rebuild the Flock checkout by hand")
    sh("bash", "/tmp/rtf3/build-pure.sh", str(wt), str(b.parent), check=True)
    return b


def digest_of_binding(s):
    m = re.search(r"statement_digest: \[([0-9, ]+)\]", s)
    return bytes(int(x) for x in m.group(1).split(",")).hex() if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("art")
    ap.add_argument("--relation", default="bf16-ampere-total")
    ap.add_argument("--pin", default="fef256dfde97d7998570b385ee22067fa6cbf0d4683fa89cdaa215360ff975d8")
    ap.add_argument("--domain", default="total")
    ap.add_argument("--points", default="")
    ap.add_argument("--regen", action="store_true")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    meta = meta_of(a.art)
    wf, cell = meta["workload_fingerprint"], meta.get("cell") or {}
    be = wf["software"]["backend"]
    c = {}
    c["TG6_relation"] = wf.get("relation") == a.relation == cell.get("relation")
    c["TG6_pin"] = be.get("lowering_sha256") == a.pin
    c["TG6_domain"] = wf.get("domain") == a.domain
    c["PB1_named"] = bool(be.get("commit")) and bool(be.get("binary_sha256"))
    sec = wf.get("security") or {}
    c["PB2_union"] = sec.get("proofs") == wf.get("N_subbatches") and (sec.get("achieved_log2") or 0) <= -128
    c["contended_false"] = (meta.get("contention") or {}).get("contended") is False
    c["validation_passed"] = (meta.get("validation") or {}).get("status") == "passed"
    V = record_of(meta["derived_from"]["verifier_run"])
    net = V / f"out/verifier/net-{a.relation}.txt"
    c["netlist_pinned"] = net.exists() and sha(net) == a.pin
    b = binary(be["commit"])
    points = sorted((V / "out/verifier").glob("p*-*"), key=lambda p: int(p.name[1:].split("-")[0]))
    if a.points:
        points = [p for p in points if p.name in a.points.split(",")]
    ses_n = ses_ok = link_ok = dig_ok = 0
    sigmas, digests, neg = {}, set(), {}
    regen = {}
    for pdir in points:
        for sd in sorted(pdir.glob("sessions-s*")):
            j = sd.name.split("-s")[1]
            inst = pdir / f"instances-s{j}.bin"
            for ses in sorted(sd.glob("l*")):
                if not (ses / "pure.rep0.bin").exists():
                    continue
                r = json.load(open(ses / "session.json"))
                bd = digest_of_binding(r["config"]["tables"][0]["binding"])
                out = sh(str(b), "replay", "--instances", str(inst), "--netlist", str(net), "--pin", a.pin, "--session", str(ses / "session.json"),
                         "--proofs", f"{ses / 'pure.rep0.bin'},{ses / 'pure.rep1.bin'}")
                line = next((l.split("\t", 1)[1] for l in out.splitlines() if l.startswith("REPLAY")), "{}")
                rep = json.loads(line) if line.startswith("{") else {}
                ses_n += 1
                ses_ok += rep.get("accepted") is True and r["verdict"]["accepted"] is True
                link_ok += r["config"].get("require_link") is True and (r.get("link") or {}).get("mode") == "exchange"
                dig_ok += bd is not None and rep.get("statement_digest") == bd
                digests.add(bd)
                sigmas.setdefault(f"{pdir.name}/s{j}", set()).add((r.get("link") or {}).get("sigma"))
                last = (inst, ses, r)
        if a.regen:
            regen[pdir.name] = sorted(sha(f) for f in pdir.glob("instances-s*.bin"))
    # PB3 negatives on the last session: another session's proofs, the reps swapped
    if ses_n >= 2:
        inst, ses, _ = last
        other = next(s for s in sorted(ses.parent.glob("l*")) if s != ses and (s / "pure.rep0.bin").exists())
        for name, p0, p1 in (("proofs_from_other_session", other / "pure.rep0.bin", other / "pure.rep1.bin"),
                             ("reps_swapped", ses / "pure.rep1.bin", ses / "pure.rep0.bin")):
            out = sh(str(b), "replay", "--instances", str(inst), "--netlist", str(net), "--pin", a.pin, "--session", str(ses / "session.json"),
                     "--proofs", f"{p0},{p1}")
            neg[name] = '"accepted":true' not in out
    c["PB3_replay"] = ses_n > 0 and ses_ok == ses_n
    c["PB3_negatives"] = len(neg) == 2 and all(neg.values())
    c["PB4_link"] = link_ok == ses_n
    c["PB4_one_sigma_per_subbatch"] = all(len(s) == 1 for s in sigmas.values())
    c["TG6_statement_digest"] = dig_ok == ses_n
    if a.regen:
        sys.path[:0] = [str(Path(f"/tmp/rtf3-wt-{be['commit'][:8]}") / p) for p in ("backends/flock/python", "packages/verity/src", "backends/numerical/python")]
        from argparse import Namespace
        from verity_flock import bench
        tars = list((V / "inputs").glob("*.tar"))
        sd = Path(f"/tmp/rtf3/set-{a.art[4:12]}")
        if tars and not sd.exists():
            sd.mkdir(parents=True)
            with tarfile.open(tars[0]) as t:
                t.extractall(sd)
        setdir = next((m.parent for m in sd.glob("**/manifest.json")), None)
        per = wf["batching"]["per_proof"]
        leaf = "sha256" if "sha-256" in str(wf.get("scheme")) else "blake3"
        ns = Namespace(relation=wf.get("relation"), procs=a.procs, cache=None, scheme="frame-v3", leaf=leaf,
                       set=str(setdir) if setdir else None, y_model=False, k=wf["K"])
        ok = True
        try:
            for pdir in points:
                total = int(pdir.name.split("-")[1])
                for jj, (lo, hi) in enumerate(bench.subbatches(total, per)):
                    f = Path(f"/tmp/rtf3/regen-{a.art[4:12]}/{pdir.name}/instances-s{jj}.bin")
                    f.parent.mkdir(parents=True, exist_ok=True)
                    bench.write_instances(ns, f, total, lo, hi)
                    ok &= sha(f) == sha(pdir / f"instances-s{jj}.bin")
        except Exception as x:  # noqa: BLE001
            ok = False
            c["instances_regen_error"] = False
            print(f"regen: {type(x).__name__}: {x}", file=sys.stderr)
        c["instances_regenerated_equal"] = ok
    res = {"cell": a.art[:12], "verifier_run": meta["derived_from"]["verifier_run"], "prover_run": meta["derived_from"]["prover_run"],
           "commit": be.get("commit", "")[:8], "binary": be.get("binary_sha256", "")[:8], "relation": wf.get("relation"), "K": wf.get("K"),
           "B": wf.get("B"), "domain": wf.get("domain"), "pin": (be.get("lowering_sha256") or "")[:8], "proofs": sec.get("proofs"),
           "achieved_log2": sec.get("achieved_log2"), "sigma": (wf.get("sigma") or "")[:8], "sessions_replayed": ses_n, "sessions_accepted": ses_ok,
           "negatives": neg, "statement_digests": sorted(d[:8] for d in digests if d), "points": [p.name for p in points],
           "supersedes": meta["derived_from"].get("supersedes"), "checks": c, "ok": all(c.values())}
    print("GEMMCELL\t" + json.dumps(res), flush=True)


if __name__ == "__main__":
    main()
