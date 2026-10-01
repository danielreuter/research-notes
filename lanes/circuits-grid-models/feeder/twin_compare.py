"""On vy-nebius-1 (stdin of ssh python3 -): each packed golden twin cov-gmNNN-pk against cov-gmNNN: run root (verdict.json
run_roots), binding map digest (commit/binding_map_p0.json), commit_pass, the config line, and whether its Commit packed."""
import json
from pathlib import Path

COV = Path("/workspace/jobs/cov")
BASES = ["cov-gm002", "cov-gm003", "cov-gm004", "cov-gm005", "cov-gm006", "cov-gm007", "cov-gm008", "cov-gm009", "cov-gm001"]
log = Path("/workspace/jobs/dispatch/log.jsonl").read_text().splitlines()


def facts(item):
    rows = [p for p in (COV / item).glob("*__tp*") if p.is_dir()]
    if len(rows) != 1:
        return None
    d = rows[0]
    out = {"row": d.name}
    try:
        v = json.loads((d / "commit/verdict.json").read_text())
        out.update(run_roots=v.get("run_roots"), commit_pass=v.get("commit_pass"))
    except (OSError, ValueError):
        out.update(run_roots=None, commit_pass=None)
    try:
        out["map"] = json.loads((d / "commit/binding_map_p0.json").read_text()).get("digest")
    except (OSError, ValueError):
        out["map"] = None
    st = (d / "stages.txt").read_text().splitlines() if (d / "stages.txt").exists() else []
    out["config"] = next((s for s in reversed(st) if s.startswith("config ")), None)
    return out


for base in BASES:
    twin = f"{base}-pk"
    evs = [json.loads(ln) for ln in log if f'"vllm-epoch-run/{twin}"' in ln]
    packed = next((e["packed"] for e in evs if e.get("packed")), None)
    spooled = any(e.get("ev") == "spool" and int(e.get("task", 0) or 0) == 1 for e in evs)
    last = evs[-1] if evs else {}
    a, b = facts(base), facts(twin)
    if not b or not b.get("run_roots"):
        print(f"{twin}: not committed yet (last {last.get('ev')} task {last.get('task')} {last.get('state', '')}; spooled {spooled})")
        continue
    same = {k: a.get(k) == b.get(k) for k in ("run_roots", "map", "commit_pass")}
    word = {k: "same" if s else "pending-replay" if k == "commit_pass" and b.get(k) is None else "DIFFERENT" for k, s in same.items()}
    print(f"{twin} {b['row'].split('__')[0]}: packed={packed or 'no'} spooled={spooled} "
          + " ".join(f"{k}={w}" for k, w in word.items())
          + f" | base root {str((a.get('run_roots') or ['-'])[0])[:16]} map {str(a.get('map'))[:16]}"
          + f" | twin root {str((b.get('run_roots') or ['-'])[0])[:16]} map {str(b.get('map'))[:16]}"
          + f" | base {str(a.get('config'))[:60]} | twin {str(b.get('config'))[:60]}")
