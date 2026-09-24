import json, sys
runs = dict(a.split("=") for a in sys.argv[1:])
rows = {}
for name, r in runs.items():
    d = json.load(open(f"/workspace/research/runs/{r}/result.json"))
    rows[name] = {m["name"]: m["value"] for m in d["measurements"]}
first = next(iter(rows.values()))
keys = [k for k in first if isinstance(first[k], (int, float)) and not isinstance(first[k], bool)]
print(f"{'metric':40s}" + "".join(f"{n:>15s}" for n in runs))
for k in keys:
    print(f"{k:40s}" + "".join(f"{rows[n].get(k, float('nan')):15.5g}" for n in runs))
