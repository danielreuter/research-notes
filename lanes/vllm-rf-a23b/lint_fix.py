"""Pod-only: apply the stale-entry deletions / count lowerings a lint run printed, plus the lane's two code-side fixes.

usage: python lint_fix.py TREE LINT_LOG
"""
import json
import re
import sys
from pathlib import Path

TREE = Path(sys.argv[1])
LOG = Path(sys.argv[2])
AL = TREE / "integrations/vllm/tests/lint/allowlists"
MOVED = {("verity_vllm/input_provenance/weights_of_record.py", "cwd", "_default_manifest", "os.getcwd"): "pathlib.Path.cwd"}

head = re.compile(r"^E\s+AssertionError: .*?(\d+) entr\(y/ies\) in allowlists/(\w+)\.json")
act = re.compile(r"^E\s+(?:delete |lower count to (\d+): )(\{.*\})\s*$")
plan: dict[str, list] = {}
expected: dict[str, int] = {}
cur = None
for line in LOG.read_text().splitlines():
    m = head.match(line)
    if m:
        cur = m.group(2)
        expected[cur] = expected.get(cur, 0) + int(m.group(1))
        plan.setdefault(cur, [])
        continue
    m = act.match(line)
    if m and cur:
        d = json.loads(m.group(2))
        plan[cur].append(((d["file"], d["kind"], d["symbol"], d["detail"]), int(m.group(1)) if m.group(1) else 0))
    elif line.startswith("____"):
        cur = None


def is_entry(s: str) -> bool:
    return s.strip().rstrip(",").startswith('{"file"')


for name, acts in sorted(plan.items()):
    assert len(acts) == expected[name], (name, len(acts), expected[name])
    path = AL / f"{name}.json"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    idx = {}
    for i, ln in enumerate(lines):
        if is_entry(ln):
            d = json.loads(ln.strip().rstrip(","))
            idx[(d["file"], d["kind"], d["symbol"], d["detail"])] = i
    drop = set()
    nd = nl = nm = 0
    for key, n in acts:
        i = idx[key]
        indent = lines[i][: len(lines[i]) - len(lines[i].lstrip())]
        d = json.loads(lines[i].strip().rstrip(","))
        if key in MOVED:
            d["detail"] = MOVED[key]
            nm += 1
        elif n == 0:
            drop.add(i)
            nd += 1
            continue
        else:
            if n == 1:
                d.pop("count", None)
            else:
                d["count"] = n
            nl += 1
        lines[i] = indent + json.dumps(d, ensure_ascii=False)
    lines = [ln for i, ln in enumerate(lines) if i not in drop]
    ent = [i for i, ln in enumerate(lines) if is_entry(ln)]
    for j, i in enumerate(ent):
        lines[i] = lines[i].rstrip().rstrip(",") + ("," if j < len(ent) - 1 else "")
    out = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    json.loads(out)
    path.write_text(out, encoding="utf-8")
    print(f"{name}: deleted {nd}, lowered {nl}, moved {nm}, entries now {len(ent)}")


def edit(rel: str, old: str, new: str) -> None:
    p = TREE / rel
    s = p.read_text(encoding="utf-8")
    assert s.count(old) == 1, (rel, old)
    p.write_text(s.replace(old, new), encoding="utf-8")
    print(f"edited {rel}")


edit("integrations/vllm/verity_vllm/tp/worker.py",
     "    import sys as _sys\n\n    from verity_vllm.config import ROOT as root\n",
     "    import sys as _sys\n    from verity_vllm.config import ROOT as root\n")
imports = "integrations/vllm/tests/lint/_imports.py"
edit(imports, '    "verity_vllm.build_paths": "pipeline",                     # -> pipeline/layout.py\n',
     '    "verity_vllm.build_paths": "pipeline",                     # -> pipeline/layout.py\n    "verity_vllm.config": "config",\n')
for mod in ("harness.synthetic", "check.adversarial", "check.fa2_attn_oracle", "commit.fa2_prototype", "commit.stream_merkle",
            "program.frontend.b1_authored", "program.numerics.inductor_models"):
    edit(imports, f'    "verity_vllm.{mod}": "tests",\n', "")
