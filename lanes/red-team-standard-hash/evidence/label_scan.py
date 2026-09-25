"""List verified=accepted bench results with a blake3 / sha256 leaf and whether red-team-standard-hash labelled them.

Usage (laptop, after `set -a; . ~/.config/verity/r2.env; set +a`):
    research data refresh; research data select --kind bench-result/v1 --label verified=accepted --json > /tmp/rtsh-acc.json
    python3 label_scan.py /tmp/rtsh-acc.json
"""
import json
import subprocess
import sys

rows = json.load(open(sys.argv[1]))
for r in rows:
    m = r["manifest"].get("meta", {})
    wf = m.get("workload_fingerprint") or {}
    leaf = wf.get("leaf") if isinstance(wf.get("leaf"), dict) else {}
    if leaf.get("scheme") not in ("blake3", "sha256"):
        continue
    out = subprocess.run(["research", "data", "labels", r["id"], "--remote"], capture_output=True, text=True).stdout
    mine = "proof_class=" in out and "by red-team-standard-hash" in out
    ver = [ln.split("verifier=", 1)[1][:90] for ln in out.splitlines() if "verifier=" in ln]
    print(r["id"][:12], leaf["scheme"], "LABELLED" if mine else "open", "|", (m.get("label") or "")[:70], "|", ver[-1] if ver else "")
