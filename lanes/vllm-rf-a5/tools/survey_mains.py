"""Survey argparse/__main__ modules: size of main, add_argument count, callers. No verity_vllm import."""
import ast, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(sys.argv[1])  # integrations/vllm
REPO = ROOT.parents[1]
al = json.load(open(ROOT / "tests/lint/allowlists/p06_one_cli.json"))["entries"]
files = sorted({e["file"] for e in al if e["kind"] in ("argparse", "main-block")})


def rg(pat, *paths):
    r = subprocess.run(["rg", "-l", "--no-messages", pat, *paths], capture_output=True, text=True, cwd=REPO)
    return [l for l in r.stdout.splitlines() if l]


rows = []
for f in files:
    p = ROOT / f
    src = p.read_text()
    tree = ast.parse(src)
    mod = f[:-3].replace("/", ".")
    n_add = src.count("add_argument(")
    main_len = 0
    mains = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and ("argparse" in ast.unparse(node)[:4000] and "ArgumentParser" in ast.unparse(node)):
            mains.append((node.name, node.end_lineno - node.lineno + 1))
    short = mod.rsplit(".", 1)[-1]
    callers_m = rg(re.escape(mod) + r"\b", "integrations", "tools", "packages")
    callers_m = [c for c in callers_m if c != "integrations/vllm/" + f]
    rows.append(dict(file=f, lines=len(src.splitlines()), n_add=n_add, mains=mains, callers=callers_m))

for r in rows:
    print(f"{r['file']}  L={r['lines']} add={r['n_add']} mains={r['mains']}")
    for c in r["callers"]:
        print("     <-", c)
print("total add_argument", sum(r["n_add"] for r in rows))
