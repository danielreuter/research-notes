"""Syntax + P10 size check for changed files (ast only; imports nothing from the repo)."""
import ast
import json
import subprocess
import sys

root = sys.argv[1]
pkg = root + "/integrations/vllm"
out = subprocess.run(["git", "-C", root, "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()
import os
files = [l[3:] for l in out if l[3:].endswith(".py") and os.path.exists(root + "/" + l[3:])]
caps = {(e["file"], e["kind"], e["symbol"]): e["count"] for e in json.load(open(pkg + "/tests/lint/allowlists/p10_size.json"))["entries"]}
bad = 0
for f in files:
    src = open(root + "/" + f).read()
    try:
        tree = ast.parse(src, f)
    except SyntaxError as e:
        print("SYNTAX", f, e)
        bad += 1
        continue
    if not f.startswith("integrations/vllm/verity_vllm/"):
        continue
    rel = f[len("integrations/vllm/"):]
    n = len(src.splitlines())
    key = (rel, "module", "<module>")
    if n > 800 or key in caps:
        print(f"{rel}: {n} lines (cap {caps.get(key)})")
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            span = node.end_lineno - node.lineno + 1
            if span > 150:
                print(f"  fn {node.name}: {span}")
print("files", len(files), "syntax errors", bad)
