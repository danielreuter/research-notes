import json, subprocess, sys, re
ARTS = sys.argv[1:]
rows = []
for a in ARTS:
    t = subprocess.run(["uv", "run", "--frozen", "research", "data", "show", a], capture_output=True, text=True, cwd="/workspace").stdout
    d = json.loads(t[t.find("{"):])
    c = d["cell"]; s = d["cell_sweep"]; p = s["points"][s["plateau_point"]]
    probs = (d.get("validation") or {}).get("cell_problems") or []
    m = [re.search(r"is (-?\+?\d+)% from", x) for x in probs if "interaction" in x]
    inter = "pass" if not probs else ("; ".join(f"{x.group(1)}%" for x in m if x) or "; ".join(probs))
    rows.append((c["relation"], c["prover_pod"].split("-")[-1] if "h100" not in c["prover_pod"] else "h100", a[:12], c["input_set"]["source"], c["input_set"]["n"], int(p[0]), round(p[1]), inter, d["run_id"]))
for r in sorted(rows):
    print(" | ".join(map(str, r)))
