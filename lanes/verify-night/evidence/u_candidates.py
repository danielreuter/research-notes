"""verify-night: rejected results whose only reasons are U (not independently verified) and/or an unlabelled instance-equiv,
with t.total vs the current Table 2 cell of their row/column.

    python3 u_candidates.py RENDER.json [--all]
"""
import json
import sys
from pathlib import Path

STORE = Path.home() / ".research" / "store"
U = "not independently verified"
E = "(instance-equiv:"


def meta(art):
    return json.loads((STORE / "manifests" / f"{art.removeprefix('art:')}.json").read_text())["meta"]


def main():
    d = json.load(open(sys.argv[1]))
    show_all = "--all" in sys.argv
    cur = {}
    for row in d["table2"]["rows"]:
        for slot, auth in (("cells", "excluded"), ("committed", "included-hash")):
            for cand, c in row[slot].items():
                cur[(row["target"], cand, auth)] = (c["t_total"], c["artifact"]) if c else (None, None)
    out = []
    for r in d["rejected"]:
        rs = r["reasons"]
        kinds = {"U" if x.startswith(U) else "E" if (E in x and "has no verified=accepted" in x) else "other" for x in rs}
        if "other" in kinds:
            continue
        m = meta(r["artifact"])
        fp = m.get("workload_fingerprint") or {}
        auth = fp.get("authentication") if fp.get("authentication") in ("excluded", "included-hash") else "excluded"
        tt = next((x["value"] for x in m.get("measurements", []) if x["name"] == "t.total"), None)
        ct, ca = cur.get((r["target"], r["candidate"], auth), (None, None))
        beats = tt is not None and (ct is None or tt < ct)
        eq = [x for x in rs if E in x]
        out.append((r["target"], r["candidate"], auth, tt, beats, "+".join(sorted(kinds)), r["artifact"], ct, ca,
                    (eq[0].split("(instance-equiv: ")[1].split(" ")[0] if eq else "")))
    out.sort(key=lambda x: (x[0], x[1], x[2], x[3] if x[3] is not None else 9e9))
    for t, c, a, tt, b, k, art, ct, ca, eq in out:
        if b or show_all:
            print(f"{'BEATS' if b else '     '} {t.split('/')[0]:24s} {c:8s} {a:13s} t={tt:.4g} cur={ct if ct is None else round(ct, 4)} "
                  f"{k:3s} {art[:12]} {('equiv ' + eq[:12]) if eq else ''}")


if __name__ == "__main__":
    main()
