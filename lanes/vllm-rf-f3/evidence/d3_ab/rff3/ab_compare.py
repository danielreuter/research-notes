import gzip, json, os, re, sys
ROW = "smollm2-135m__bf16__l40s__tp1__b1__i256__o32__mixed__greedy__bi-eager"
H, B = f"/workspace/cp/sweep-head/{ROW}", f"/workspace/cp/sweep-base/{ROW}"
VOL = re.compile(r"(^|_)(t|ts|time|times|timestamp|date|at|wall|elapsed|duration|dur|seconds|secs|s|ms|us|ns|pid|ppid|rss|peak|mib|mb|gb|bytes_per_s|per_s|gbps|mbps|throughput|started|finished|start|end|stamp|uptime|host|hostname|load|cpu|free)$", re.I)
def norm_str(s):
    s = s.replace("sweep-head", "sweep-X").replace("sweep-base", "sweep-X")
    s = s.replace("/workspace/basetree", "/workspace/T").replace("/workspace/head", "/workspace/T")
    s = re.sub(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z?", "<ts>", s)
    return s
def load(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        txt = f.read()
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return [json.loads(l) for l in txt.splitlines() if l.strip()]
def diff(a, b, path, out):
    if len(out) > 12: return
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if VOL.search(str(k)): continue
            if k not in a or k not in b: out.append(f"{path}/{k}: only in {'head' if k in a else 'base'}"); continue
            diff(a[k], b[k], f"{path}/{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): out.append(f"{path}: len {len(a)} vs {len(b)}"); return
        for i, (x, y) in enumerate(zip(a, b)): diff(x, y, f"{path}[{i}]", out)
    elif isinstance(a, str) and isinstance(b, str):
        if norm_str(a) != norm_str(b): out.append(f"{path}: {a[:90]!r} vs {b[:90]!r}")
    elif isinstance(a, float) and isinstance(b, float):
        if a != b and not VOL.search(path.rsplit("/", 1)[-1]):
            out.append(f"{path}: {a} vs {b}")
    elif a != b:
        out.append(f"{path}: {str(a)[:90]} vs {str(b)[:90]}")
files = []
for root, _, fs in os.walk(H):
    for f in fs:
        if f.endswith((".json", ".json.gz", ".jsonl")):
            files.append(os.path.relpath(os.path.join(root, f), H))
same = []
for rel in sorted(files):
    hb = os.path.join(B, rel)
    if not os.path.exists(hb): print(f"ONLY-HEAD {rel}"); continue
    try:
        a, b = load(os.path.join(H, rel)), load(hb)
    except Exception as e:
        print(f"UNREADABLE {rel}: {e}"); continue
    out = []
    diff(a, b, "", out)
    if out: print(f"DIFF {rel}: " + " | ".join(out[:6]))
    else: same.append(rel)
print(f"SAME ({len(same)}):", " ".join(same))
