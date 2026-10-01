"""Order gm-feed's unsubmitted items by gm_feed.est_min, quickest deployment first (circuits 1158Z: the quickest Builds first after
the 5:55 AM PDT cutover). Items already submitted or attempted keep their place ahead. Backs items.json up first.

    reorder.py [--write]      (on vy-nebius-1, in /workspace/jobs/gm-feed)"""
import json
import os
import sys
import time
from pathlib import Path

HERE = Path("/workspace/jobs/gm-feed")
sys.path.insert(0, str(HERE))
import gm_feed as F  # noqa: E402

items = json.loads((HERE / "items.json").read_text())
att = set((HERE / "attempted.txt").read_text().split())
st = F.stages()
obs = F.walls()
done = [i for i in items if f"{F.WS}/{i['key']}" in st or i["key"] in att]
todo = [i for i in items if not (f"{F.WS}/{i['key']}" in st or i["key"] in att)]
order = sorted(range(len(todo)), key=lambda n: (F.est_min(todo[n]["item"]["env"]["ROW"], obs), n))
new = done + [todo[n] for n in order]
assert sorted(i["key"] for i in new) == sorted(i["key"] for i in items) and len(new) == len(items)
for n in order[:12]:
    i = todo[n]
    print(f"{i['key']} {F.est_min(i['item']['env']['ROW'], obs):5.0f} min  {i['item']['env']['ROW'][:70]}")
print(f"... {len(todo)} unsubmitted, {len(done)} submitted or attempted")
if "--write" in sys.argv:
    stamp = time.strftime("%H%MZ", time.gmtime())
    (HERE / f"items.bak-{stamp}.json").write_text((HERE / "items.json").read_text())
    (HERE / "items.json.tmp").write_text(json.dumps(new, indent=1))
    os.replace(HERE / "items.json.tmp", HERE / "items.json")
    print(f"wrote items.json (backup items.bak-{stamp}.json)")
