"""Build the flock-verifier vector manifest from the evidence store (flock-verifier lane, phase 1)."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ENV = dict(os.environ, PYTHONPATH="/workspace/tools/research/src", RESEARCH_STORE=os.path.expanduser("~/.research/store"))
CACHE = "/tmp/vec/cache"


def research(*a):
    return subprocess.run([sys.executable, "-m", "research", *a], env=ENV, capture_output=True, text=True, cwd="/workspace").stdout


def listing(art):
    files = {}
    for line in research("data", "fetch", art, "--list").splitlines()[1:]:
        p = line.split()
        if len(p) >= 2 and p[1].isdigit():
            files[p[0]] = int(p[1])
    return files


STATEMENT = {"pure": "flock-pure-block", "irf": "flock-ir-frame", "vllm": "flock-vllm-block", "nl": "flock-netlist"}


def build(cell_row):
    rec = cell_row["verifier_record"]
    files = listing(rec)
    sess = {}
    for p in files:
        m = re.match(r"(.*)/(l\d+-\d+)/([a-z]+)\.rep0\.bin$", p)
        if m:
            sess.setdefault(m.group(1), []).append((m.group(2), m.group(3)))
    # smallest point: the session dir whose point number (p<i>-<N>) is least
    def npt(d):
        m = re.search(r"/p\d+-(\d+)/", d + "/")
        return int(m.group(1)) if m else 0
    d = min(sess, key=lambda k: (npt(k), k))
    chosen = sorted(sess[d])[:2]
    tb = chosen[0][1]
    point = re.search(r"(.*/p\d+-\d+)/", d + "/").group(1) if re.search(r"/p\d+-\d+", d) else os.path.dirname(d)
    sb = re.search(r"sessions-s(\d+)", d)
    inst = [p for p in files if p.startswith(point + "/") and re.search(r"instances-s%s\.bin$" % (sb.group(1) if sb else "0"), p)]
    publics = [p for p in files if re.search(r"(^|/)(net[^/]*\.txt|pub[^/]*\.bin|stage[^/]*/net\.txt|manifest[^/]*\.json|class[^/]*\.json)$", p) and "/l0" not in p]
    sj = f"{d}/{chosen[0][0]}/session.json"
    dst = f"{CACHE}/{rec[4:16]}"
    research("data", "fetch", rec, "--to", dst, "--path", sj)
    try:
        r = json.load(open(f"{dst}/{sj}"))
        hello = json.loads(r["hello"])
        streams = {s["stream"]: len(s["rounds"]) for s in r["streams"]}
        accepted = (r.get("verdict") or {}).get("accepted")
        binding = r["config"]["tables"][0]["binding"]
        dig = bytes(int(x) for x in re.findall(r"\d+", binding.split("[", 1)[1])).hex() if "[" in binding else None
    except Exception as e:
        hello, streams, accepted, dig = {"error": str(e)}, {}, None, None
    return {
        "cell": cell_row["cell"], "statement": STATEMENT.get(tb, tb), "table": tb,
        "verifier_run": cell_row["verifier_run"], "verifier_commit": cell_row.get("verifier_commit"),
        "record": rec, "labels": cell_row.get("labels", {}),
        "sessions_with_proofs": cell_row.get("sessions"),
        "vectors": [{"session": f"{d}/{s}/session.json", "proofs": [f"{d}/{s}/{t}.rep0.bin", f"{d}/{s}/{t}.rep1.bin"], "expect": "accept"} for s, t in chosen],
        "instances": inst[:1], "statement_files": sorted(publics)[:6],
        "hello": hello, "statement_digest": dig, "rounds_per_stream": streams, "recorded_verdict": accepted,
    }


if __name__ == "__main__":
    rows = [json.loads(l) for f in sys.argv[1:] for l in open(f)]
    rows = [r for r in rows if r.get("verifier_record")]
    seen, uniq = set(), []
    for r in rows:
        if r["cell"] not in seen:
            seen.add(r["cell"]); uniq.append(r)
    with ThreadPoolExecutor(8) as ex:
        out = list(ex.map(build, uniq))
    json.dump(out, open("/tmp/vec/manifest-honest.json", "w"), indent=1)
    for o in out:
        h = o["hello"]
        print(o["cell"], o["statement"], h.get("link", {}).get("m"), o["statement_digest"][:12] if o["statement_digest"] else None,
              o["rounds_per_stream"], o["recorded_verdict"], o["instances"], len(o["statement_files"]))
