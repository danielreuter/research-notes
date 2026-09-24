"""rl_imports.py ROOT OUT.json -- import every non-test module of an integration tree, each in its own subprocess (a module may have
import-time side effects); write {dotted module: "ok" | "<last stderr line>"}.  PYTHONPATH comes from the caller's environment."""
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys

root, out = sys.argv[1], sys.argv[2]
TEST = re.compile(r"(^|/)(tests?/|test_[^/]+\.py$|conftest\.py$)")
mods = []
for pkg in ("verity_vllm", "verity_capture", "verity_vllm_numerics", "verity_vllm_adapter"):
    for d, dirs, files in os.walk(os.path.join(root, pkg)):
        dirs[:] = sorted(x for x in dirs if x != "__pycache__" and not x.startswith("."))
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(d, f), root)
            if not f.endswith(".py") or TEST.search(rel):
                continue
            m = rel[:-3].replace(os.sep, ".")
            mods.append(m[: -len(".__init__")] if m.endswith(".__init__") else m)


def probe(m):
    try:
        r = subprocess.run([sys.executable, "-c", f"import importlib; importlib.import_module({m!r})"], cwd=root,
                           capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return m, "TIMEOUT"
    if r.returncode == 0:
        return m, "ok"
    lines = [l for l in r.stderr.strip().splitlines() if l.strip()]
    return m, (lines[-1] if lines else f"rc {r.returncode}")[:300]


with cf.ThreadPoolExecutor(int(os.environ.get("RL_JOBS", "16"))) as ex:
    res = dict(ex.map(probe, mods))
json.dump(res, open(out, "w"), indent=0, sort_keys=True)
print(f"{len(res)} modules: {sum(v == 'ok' for v in res.values())} ok, {sum(v != 'ok' for v in res.values())} fail")
