"""rl_cmp.py BASE_LOGDIR MOVED_LOGDIR MOVE_MAP -- the relayout's before/after comparison, with every base name carried through the map.

imports:    every base module's import result against its successor's (ok -> fail is a regression; messages compared after mapping)
collection: base `collect_all` node ids (file path mapped) against the moved tree's; default-testpath counts side by side
junit:      (when both dirs hold *.xml) per-test outcome over the union of the suites, base ids mapped; lists any test whose outcome
            differs, tests only one side ran, and per-side F / E / pass / skip totals."""
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

bdir, mdir, mpath = sys.argv[1:4]
files, prefixes = {}, []
for line in open(mpath):
    line = line.split("#", 1)[0].strip() if not line.startswith("REWRITE") else ""
    if " -> " not in line:
        continue
    old, rest = line.split(" -> ", 1)
    new = rest.split()[0]
    (prefixes.append((old, new)) if old.endswith("/") else files.setdefault(old, new))
prefixes.sort(key=lambda p: -len(p[0]))


def map_path(p):
    if p in files:
        return files[p]
    for o, n in prefixes:
        if p.startswith(o):
            return n + p[len(o):]
    return p


def mod_file(m):
    return m.replace(".", "/") + ".py"


def map_mod(m):
    for cand in (mod_file(m), m.replace(".", "/") + "/__init__.py"):
        n = map_path(cand)
        if n != cand or cand in files:
            if n == "DROP":
                return None
            n = n[:-3].replace("/", ".")
            return n[: -len(".__init__")] if n.endswith(".__init__") else n
    return m


NAME_RE = re.compile(r"\b(?:verity_capture|verity_vllm_adapter|verity_vllm_numerics|verity_vllm|tests)(?:\.\w+)+")


def norm_msg(msg):
    return NAME_RE.sub(lambda mo: map_mod(mo.group(0)) or mo.group(0), msg)


# ---- imports
bi, mi = json.load(open(f"{bdir}/imports.json")), json.load(open(f"{mdir}/imports.json"))
print(f"imports base: {sum(v == 'ok' for v in bi.values())}/{len(bi)} ok   moved: {sum(v == 'ok' for v in mi.values())}/{len(mi)} ok")
seen, regress, changed, missing = set(), [], [], []
for m, r in sorted(bi.items()):
    n = map_mod(m)
    if n is None:
        continue
    seen.add(n)
    if n not in mi:
        missing.append(f"{m} -> {n}")
    elif r == "ok" and mi[n] != "ok":
        regress.append(f"{m} -> {n}: {mi[n]}")
    elif r != "ok" and mi[n] != "ok" and norm_msg(r) != mi[n]:
        changed.append(f"{n}: base '{norm_msg(r)[:140]}' moved '{mi[n][:140]}'")
    elif r != "ok" and mi[n] == "ok":
        changed.append(f"{n}: base failed ({r[:100]}), moved ok")
extra = sorted(n for n in mi if n not in seen)
print(f"  ok->fail: {len(regress)}", *regress[:30], sep="\n    ")
print(f"  base module has no successor in the moved tree: {len(missing)}", *missing[:30], sep="\n    ")
print(f"  failure message changed / fixed: {len(changed)}", *changed[:30], sep="\n    ")
print(f"  moved-only modules (new __init__ etc.): {len(extra)}; failing: " + ", ".join(f"{n} ({mi[n][:80]})" for n in extra if mi[n] != "ok"))


# ---- collection
def ids(path):
    out = []
    for l in open(path):
        l = l.rstrip("\n")
        if "::" in l and not l.startswith((" ", "=", "_")):
            out.append(l)
    return out


def tail(path):
    lines = [l.strip() for l in open(path) if l.strip()]
    return lines[-1] if lines else "?"


def map_id(i):
    f, _, rest = i.partition("::")
    return map_path(f) + "::" + rest


for kind in ("default", "all"):
    print(f"collect {kind}: base '{tail(f'{bdir}/collect_{kind}.txt')}'   moved '{tail(f'{mdir}/collect_{kind}.txt')}'")
bset, mset = {map_id(i) for i in ids(f"{bdir}/collect_all.txt")}, set(ids(f"{mdir}/collect_all.txt"))
print(f"  collect all: base {len(bset)} ids (mapped), moved {len(mset)}; base-only {len(bset - mset)}, moved-only {len(mset - bset)}")
for tag, s in (("base-only", sorted(bset - mset)), ("moved-only", sorted(mset - bset))):
    for i in s[:25]:
        print(f"    {tag} {i}")


# ---- junit
def junit(d, mapped):
    res = {}
    for x in sorted(glob.glob(f"{d}/*.xml")):
        for tc in ET.parse(x).getroot().iter("testcase"):
            cls, name = tc.get("classname") or "", tc.get("name")
            if mapped:
                parts = cls.split(".") if cls else name.split(".")
                for k in range(len(parts), 0, -1):
                    f = "/".join(parts[:k]) + ".py"
                    if f in files or map_path(f) != f:
                        n = map_path(f)[:-3].replace("/", ".")
                        rest = ".".join(parts[k:])
                        if cls:
                            cls = n + ("." + rest if rest else "")
                        else:
                            name = n + ("." + rest if rest else "")
                        break
            kinds = {c.tag for c in tc}
            o = "F" if "failure" in kinds else "E" if "error" in kinds else "s" if "skipped" in kinds else "."
            key = f"{cls}::{name}"
            prev = res.get(key)
            res[key] = o if prev is None or prev == o else (o if o in "FE" else prev)
    return res


bj, mj = junit(bdir, True), junit(mdir, False)
if bj and mj:
    for tag, r in (("base", bj), ("moved", mj)):
        c = {k: sum(v == k for v in r.values()) for k in "FE.s"}
        print(f"junit {tag}: {c['F']} F / {c['E']} E / {c['.']} pass / {c['s']} skip over {len(r)} tests")
    diff = sorted(k for k in set(bj) & set(mj) if bj[k] != mj[k])
    print(f"  outcome differs: {len(diff)}", *[f"{k}: {bj[k]} -> {mj[k]}" for k in diff[:40]], sep="\n    ")
    bo, mo = sorted(set(bj) - set(mj)), sorted(set(mj) - set(bj))
    print(f"  base-only tests: {len(bo)} (bad: {sum(bj[k] in 'FE' for k in bo)})", *[f"{k}: {bj[k]}" for k in bo if bj[k] in "FE"][:20], sep="\n    ")
    print(f"  moved-only tests: {len(mo)} (bad: {sum(mj[k] in 'FE' for k in mo)})", *[f"{k}: {mj[k]}" for k in mo if mj[k] in "FE"][:20], sep="\n    ")
