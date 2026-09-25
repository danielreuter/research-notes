"""Every `from verity_vllm.X import name` / `import verity_vllm.X as m; m.name` for changed modules resolves (ast only)."""
import ast, os, re, subprocess, sys

root = sys.argv[1]
pkgroot = {"verity_vllm": root + "/integrations/vllm", "tests": root + "/integrations/vllm", "verity": root + "/packages/verity/src"}
mods = sys.argv[2:]

def mod_path(m):
    base = pkgroot.get(m.split(".")[0])
    if base is None:
        return None
    p = base + "/" + m.replace(".", "/")
    return p + ".py" if os.path.exists(p + ".py") else (p + "/__init__.py" if os.path.exists(p + "/__init__.py") else None)

def top_names(p):
    t = ast.parse(open(p).read())
    out = set()
    for n in t.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
        elif isinstance(n, ast.Assign):
            for tg in n.targets:
                for x in ast.walk(tg):
                    if isinstance(x, ast.Name):
                        out.add(x.id)
        elif isinstance(n, (ast.AnnAssign,)) and isinstance(n.target, ast.Name):
            out.add(n.target.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                out.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, (ast.Try, ast.If)):
            for x in ast.walk(n):
                if isinstance(x, (ast.Import, ast.ImportFrom)):
                    for a in x.names:
                        out.add((a.asname or a.name).split(".")[0])
                elif isinstance(x, ast.Assign):
                    for tg in x.targets:
                        for y in ast.walk(tg):
                            if isinstance(y, ast.Name):
                                out.add(y.id)
                elif isinstance(x, (ast.FunctionDef, ast.ClassDef)):
                    out.add(x.name)
    return out

names = {m: top_names(mod_path(m)) for m in mods}
files = subprocess.run(["git", "-C", root, "ls-files", "*.py"], capture_output=True, text=True).stdout.split()
files += [l[3:] for l in subprocess.run(["git", "-C", root, "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines() if l.startswith("??") and l.endswith(".py")]
bad = 0
for f in sorted(set(files)):
    fp = root + "/" + f
    if not os.path.exists(fp):
        continue
    try:
        t = ast.parse(open(fp).read())
    except SyntaxError:
        continue
    alias = {}
    for n in ast.walk(t):
        if isinstance(n, ast.ImportFrom) and n.module:
            if n.module in names:
                for a in n.names:
                    if a.name != "*" and a.name not in names[n.module] and mod_path(n.module + "." + a.name) is None:
                        print(f"{f}:{n.lineno}: {n.module} has no {a.name}"); bad += 1
            for a in n.names:
                full = n.module + "." + a.name
                if full in names:
                    alias[a.asname or a.name] = full
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name in names and a.asname:
                    alias[a.asname] = a.name
    for n in ast.walk(t):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in alias:
            m = alias[n.value.id]
            if n.attr not in names[m] and not n.attr.startswith("__"):
                print(f"{f}:{n.lineno}: {n.value.id}={m} has no {n.attr}"); bad += 1
print("unresolved", bad)
