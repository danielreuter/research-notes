"""Order gm-feed's unsubmitted items by gm_feed.est_min, quickest deployment first (circuits 1158Z: the quickest Builds first after
the 5:55 AM PDT cutover). Items already submitted or attempted keep their place ahead. Backs items.json up first.

With --pack (circuits 1555Z, from 9:30 AM PDT), classes come before est_min: first the cheapest row of each model with no deployment
yet (the 30-model floor), then the rows dispatch's own packable() would spool (the pack pods stay full), then rows with real GPU
work (B8 or 1024-token), then the rest.

    reorder.py [--pack] [--write]      (on vy-nebius-1, in /workspace/jobs/gm-feed)"""
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

HERE = Path("/workspace/jobs/gm-feed")
sys.path.insert(0, str(HERE))
import gm_feed as F  # noqa: E402

PACK = "--pack" in sys.argv
items = json.loads((HERE / "items.json").read_text())
att = set((HERE / "attempted.txt").read_text().split())
st = F.stages()
obs = F.walls()
done = [i for i in items if f"{F.WS}/{i['key']}" in st or i["key"] in att]
todo = [i for i in items if not (f"{F.WS}/{i['key']}" in st or i["key"] in att)]
est = [F.est_min(i["item"]["env"]["ROW"], obs) for i in todo]
NAMES = ["new model", "packable", "B8/1k", "rest"]
if PACK:
    spec = importlib.util.spec_from_file_location("dispatch", F.DISPATCH_PY)
    D = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(D)
    tasks, _ = D.load_template("config-run")
    GPU = next(n for n, t in enumerate(tasks) if t.get("name") == "gpu")
    started = {i["role"] for i in done}
    firsts = {}
    for n in sorted(range(len(todo)), key=lambda n: (est[n], n)):
        if todo[n]["role"] not in started:
            firsts.setdefault(todo[n]["role"], n)
    firsts = set(firsts.values())


def cls(n: int) -> int:
    if not PACK:
        return 0
    it = todo[n]["item"]
    parts = it["env"]["ROW"].split("__")
    if n in firsts:
        return 0
    if D.packable(it, f"{F.WS}/{todo[n]['key']}", GPU) is None:
        return 1
    return 2 if ("b8" in parts or "i1024" in parts) else 3


classes = [cls(n) for n in range(len(todo))]
order = sorted(range(len(todo)), key=lambda n: (classes[n], est[n], n))
new = done + [todo[n] for n in order]
assert sorted(i["key"] for i in new) == sorted(i["key"] for i in items) and len(new) == len(items)
for n in order[:16]:
    i = todo[n]
    print(f"{i['key']} {NAMES[classes[n]] if PACK else '':9s} {est[n]:5.0f} min  {i['item']['env']['ROW'][:80]}")
if PACK:
    print("classes:", ", ".join(f"{NAMES[c]} {classes.count(c)}" for c in range(4)))
print(f"... {len(todo)} unsubmitted, {len(done)} submitted or attempted")
if "--write" in sys.argv:
    stamp = time.strftime("%H%MZ", time.gmtime())
    (HERE / f"items.bak-{stamp}.json").write_text((HERE / "items.json").read_text())
    (HERE / "items.json.tmp").write_text(json.dumps(new, indent=1))
    os.replace(HERE / "items.json.tmp", HERE / "items.json")
    print(f"wrote items.json (backup items.bak-{stamp}.json)")
