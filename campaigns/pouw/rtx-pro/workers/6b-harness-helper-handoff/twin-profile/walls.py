import json
import sys

b = json.load(open(sys.argv[1]))
row = b["shapes"][0]
print("shape", row["label"], "wall_s", {k: round(v, 2) for k, v in row["wall_s"].items()})
arm_names = {a for a in (b.get("arms") or {})} if isinstance(b.get("arms"), dict) else set()
tot = {"arm": 0.0, "chain-arm": 0.0, "chain-other": 0.0, "baseline": 0.0}
for g in b["gates"]:
    k = g["key"]
    w = g.get("wall_s") or 0.0
    if k[0] == "arm":
        tot["arm"] += w
        print(f"  {'/'.join(k[1:]):60s} {w:7.2f} s  ok={g['ok']}")
    elif k[0] == "chain" and "pearl" in k[2]:
        tot["chain-arm"] += w
        print(f"  {'/'.join(k[1:]):60s} {w:7.2f} s  ok={g['ok']}")
    elif k[0] == "chain":
        tot["chain-other"] += w
    else:
        tot["baseline"] += w
neg = [(n["key"], n.get("wall_s"), n.get("rejected")) for n in b.get("negative_controls", []) if "pearl" in "/".join(map(str, n["key"]))]
for k, w, r in neg:
    print(f"  negative {'/'.join(map(str, k[1:])):51s} {w or 0:7.2f} s  rejected={r}")
print("totals", {k: round(v, 2) for k, v in tot.items()}, "pearl negatives", round(sum(w or 0 for _, w, _ in neg), 2))
tiles = 0
for g in b["gates"]:
    def walk(x):
        global tiles
        if isinstance(x, dict):
            if "twin_tiles" in x:
                tiles += len(x["twin_tiles"])
                assert not any(t["failed"] for t in x["twin_tiles"]) or not g["ok"]
            for y in x.values():
                walk(y)
        elif isinstance(x, list):
            for y in x:
                walk(y)
    walk(g)
print("tile comparisons", tiles, "gates ok", all(g["ok"] for g in b["gates"]), "exit", b.get("exit"))
