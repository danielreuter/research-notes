"""verify-night-2: register a verification-verdict/v1 (payload: the evidence files) for one result verified outside reverify.py,
label it verified=accepted (or rejected) --by verify-night-2 --ref <verdict>, and push the labels. Runs ON THE POD (store = the
runner's $RESEARCH_STORE, remote = the minted credential in the environment), as verify-night's label_result.py did on the laptop.

    python 11-label.py ART --tree ART --verifier TEXT --detail TEXT --seconds S [--verdict accepted|rejected] EVIDENCE_FILE...

    --hold       register (and preserve) the verdict only; no labels (coordinator hold, 20260925T0050Z)
    --vid ART    label from an already-registered verdict ART (the release of a hold); no new verdict

Refuses when the result's manifest names verify-night-2 (this lane never labels its own result)."""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BY = "verify-night-2"


def run(*a):
    r = subprocess.run([sys.executable, "-m", "research", *a], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"{' '.join(a[:3])}: rc {r.returncode}: {r.stderr[-800:]}")
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("art")
    ap.add_argument("--tree", required=True)
    ap.add_argument("--verifier", required=True)
    ap.add_argument("--detail", required=True)
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--verdict", default="accepted", choices=("accepted", "rejected"))
    ap.add_argument("--hold", action="store_true")
    ap.add_argument("--vid")
    ap.add_argument("evidence", nargs="*")
    a = ap.parse_args()
    man = json.loads(run("data", "show", a.art, "--json"))["manifest"]
    if BY in json.dumps(man):
        raise SystemExit(f"{a.art}: manifest names {BY}; refusing")
    if a.vid:
        label(a, a.vid)
        return
    payload = {"result": a.art, "detail": a.detail, "evidence": {Path(p).name: Path(p).read_text(errors="replace") for p in a.evidence}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=1)
        pf = f.name
    meta = {"result": "PASS" if a.verdict == "accepted" else "FAIL", "verifier": a.verifier, "detail": a.detail,
            "subject_kind": man.get("kind", "bench-result/v1"), "lane": BY}
    out = run("data", "put", "--kind", "verification-verdict/v1", "--meta", json.dumps(meta), "--ref", f"result={a.art}",
              "--ref", f"proof={a.tree}", "--file", pf, "--preserve")
    vid = out.splitlines()[-1].split()[0]
    print("put output:", out)
    if a.hold:
        print(f"{a.art}: verdict {vid} registered, labels HELD")
        return
    label(a, vid)


def label(a, vid):
    for key, val, extra in (("verified", a.verdict, []), ("verifier", a.verifier, []), ("verifier_seconds", f"{a.seconds:g}", ["--value-json"]),
                            ("note", a.detail, []), ("same_device", "false", ["--value-json"])):
        run("data", "label", a.art, key, val, "--by", BY, "--ref", vid, *extra)
    print(run("data", "labels-sync", "--push-only", "--jobs", "16").splitlines()[-1])
    print(f"{a.art}: verified={a.verdict} by {BY}, verdict {vid}")


if __name__ == "__main__":
    main()
