"""Enumerate replayable Flock verifier sessions for a list of cell artifacts (flock-verifier lane, phase 1)."""
import json, os, subprocess, sys, re
from concurrent.futures import ThreadPoolExecutor

ENV = dict(os.environ, PYTHONPATH="/workspace/tools/research/src", RESEARCH_STORE=os.path.expanduser("~/.research/store"))


def research(*a):
    p = subprocess.run([sys.executable, "-m", "research", *a], env=ENV, capture_output=True, text=True, cwd="/workspace")
    return p.stdout


def show(x):
    out = research("data", "show", x, "--json")
    try:
        return json.loads(out)
    except Exception:
        return None


def attempt_record(run):
    out = research("data", "show", run)
    m = re.search(r'"run_record": "(art:[0-9a-f]+)"', out)
    src = re.search(r'"commit": "([0-9a-f]+)"', out)
    return (m.group(1) if m else None), (src.group(1) if src else None)


def listing(art):
    out = research("data", "fetch", art, "--list")
    files = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1].isdigit():
            files.append((parts[0], int(parts[1])))
    return files


def labels(art):
    out = research("data", "labels", art, "--remote", "--json")
    try:
        d = json.loads(out)
    except Exception:
        return {}
    res = {}
    for l in d if isinstance(d, list) else d.get("labels", []):
        l = l.get("label", l)
        k, v, by = l.get("key"), l.get("value"), l.get("by")
        if k in ("verified", "proof_class", "independently_verified", "superseded_by", "finding"):
            res.setdefault(k, []).append(f"{v} ({by})" if k != "finding" else f"{str(v)[:60]} ({by})")
    return res


def one(cell):
    s = show(cell)
    if not s:
        return {"cell": cell, "error": "not found"}
    meta = s["manifest"].get("meta", {})
    df = meta.get("derived_from", {})
    vr = df.get("verifier_run")
    fp = meta.get("fingerprint", {}) or {}
    row = {"cell": s["id"][:12], "kind": s["manifest"]["kind"], "lane": meta.get("lane"), "verifier_run": vr,
           "prover_run": df.get("prover_run"), "profile": fp.get("profile") or meta.get("profile"),
           "labels": labels(cell)}
    if vr:
        rec, commit = attempt_record(vr)
        row["verifier_record"], row["verifier_commit"] = rec, commit
        if rec:
            files = listing(rec)
            sess = {}
            for path, size in files:
                m = re.match(r"(.*/(l\d+-\d+))/([^/]+)$", path)
                if m:
                    d = sess.setdefault(m.group(1), {})
                    d[m.group(3)] = size
            with_proofs = {k: v for k, v in sess.items() if any(n.endswith(".rep0.bin") for n in v)}
            row["sessions"] = len(with_proofs)
            if with_proofs:
                k0 = sorted(with_proofs)[0]
                row["example_session"] = k0
                row["example_files"] = with_proofs[k0]
            row["other_inputs"] = sorted({p for p, _ in files if re.search(r"(net|instances|netlist|manifest|inst)[^/]*\.(txt|bin|json)$", p) and "/l0" not in p})[:12]
    return row


if __name__ == "__main__":
    cells = sys.argv[1:]
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(one, cells):
            print(json.dumps(r), flush=True)
