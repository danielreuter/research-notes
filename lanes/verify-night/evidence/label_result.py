"""verify-night: register a verification-verdict/v1 (payload: the evidence files) for one bench-result verified outside reverify.py
and label it verified=accepted --by verify-night --ref <verdict>.

    python3 label_result.py ART --verifier TEXT --detail TEXT --seconds S EVIDENCE_FILE...

Refuses when the result's producer is verify-night or a lane verify-night succeeded (none: verify-night took over no lane)."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

R = str(Path.home() / ".research" / "bin" / "research")
STORE = Path.home() / ".research" / "store"


def run(*a):
    r = subprocess.run([R, *a], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{' '.join(a[:3])}: rc {r.returncode}: {r.stderr[-800:]}")
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("art")
    ap.add_argument("--verifier", required=True)
    ap.add_argument("--detail", required=True)
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("evidence", nargs="+")
    a = ap.parse_args()
    show = json.loads(run("data", "show", a.art, "--json"))
    man = show.get("manifest", show)
    lanes = {str(v) for v in json.dumps(man).split('"') if v in ("verify-night",)}
    if lanes:
        raise SystemExit(f"{a.art}: manifest names verify-night; refusing")
    payload = {"result": a.art, "detail": a.detail, "evidence": {Path(p).name: Path(p).read_text() for p in a.evidence}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=1)
        pf = f.name
    meta = {"result": "PASS", "verifier": a.verifier, "detail": a.detail, "subject_kind": man.get("kind", "bench-result/v1"),
            "lane": "verify-night"}
    vid = run("data", "put", "--kind", "verification-verdict/v1", "--meta", json.dumps(meta), "--ref", f"result={a.art}",
              "--file", pf, "--preserve").splitlines()[-1].split()[0]
    for key, val in (("verified", "accepted"), ("verifier", a.verifier), ("verifier_seconds", f"{a.seconds:g}"), ("note", a.detail)):
        run("data", "label", a.art, key, val, "--by", "verify-night", "--ref", vid)
    print(f"{a.art}: verified=accepted by verify-night, verdict {vid}")


if __name__ == "__main__":
    main()
