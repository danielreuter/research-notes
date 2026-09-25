"""Move lint allowlist entries with their files after one rewrite.py group.

usage: python allow.py REPO GROUP
Reads /tmp/a4-map-GROUP.json.  File keys and dotted/path details are remapped; P9 layer details (short names) are
remapped; P9 package- and module-cycles are recomputed from the import graph; P11 module-name and P12 root-list
details are recomputed from the moved sources.  Prints what it cannot place.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import graph as G  # noqa: E402

DOTTED = re.compile(r"(?<![\w.])((?:integrations\.vllm\.)?verity_vllm(?:\.\w+)+)")
PATH = re.compile(r"(?<![\w.])(verity_vllm/[\w./*\-]*)")
BAD_TOKEN = re.compile(r"^(v[0-9]+[a-z]?|fast|poc|m[0-9]+|b[0-9]+|tp[0-9]+|g[1-8])$")
CODE_ROOT = re.compile(r"^(?:\.\./)*(verity_vllm|verity|research|integrations/vllm|packages/verity|tools/research)(?:/|$)")
LAYERS = ("tests", "pipeline", "check|properties", "acquire", "observe|commit", "engine", "query|correspondence",
          "program", "collectives", "config", "core")
RANK = {n: len(LAYERS) - i for i, n in enumerate(LAYERS)}


class Maps:
    def __init__(self, d):
        self.modmap, self.pathmap = d["modmap"], d["pathmap"]

    def mod(self, name):
        parts = name.split(".")
        for i in range(len(parts), 0, -1):
            k = ".".join(parts[:i])
            if k in self.modmap:
                return ".".join([self.modmap[k], *parts[i:]])
        return name

    def path(self, p):
        tail = ""
        while p and p[-1] == ".":
            tail, p = "." + tail, p[:-1]
        best = None
        for k in self.pathmap:
            if (p == k or p.startswith(k + "/")) and (best is None or len(k) > len(best)):
                best = k
        return p + tail if best is None else self.pathmap[best] + p[len(best):] + tail

    def text(self, s):
        s = DOTTED.sub(lambda m: self.mod(m.group(1)), s)
        return PATH.sub(lambda m: self.path(m.group(1)), s)

    def short(self, s):
        full = s if s == "verity_vllm" else "verity_vllm." + s
        n = self.mod(full)
        return n if n == "verity_vllm" else n.removeprefix("verity_vllm.")


def name_tokens(name):
    out = []
    for part in re.split(r"[_\-.]+", name):
        out += re.findall(r"[A-Z]+[0-9]*(?![a-z])|[A-Z]?[a-z]+[0-9]*|[0-9]+", part) if not part.islower() else [part]
    return [t.lower() for t in out if t]


def bad_name(name):
    if name.startswith("__") and name.endswith("__"):
        return False
    return any(BAD_TOKEN.match(t) and (t[0] != "g" or re.search(r"(?<![A-Za-z0-9])G[1-8]|_g[1-8]\b|^g[1-8]\b", name))
               for t in name_tokens(name))


def walk(node, symbol="<module>"):
    out = []

    def visit(n, sym):
        for c in ast.iter_child_nodes(n):
            out.append((c, sym))
            visit(c, (c.name if sym == "<module>" else f"{sym}.{c.name}")
                  if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else sym)
    visit(node, symbol)
    return out


def root_lists(src):
    tree = ast.parse(src)
    out = []
    for node, symbol in walk(tree):
        if isinstance(node, (ast.Tuple, ast.List, ast.Set)) and len(node.elts) >= 2 \
                and all(isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts):
            roots = [e.value for e in node.elts if CODE_ROOT.match(e.value)]
            if roots:
                out.append((symbol, ", ".join(roots)[:120]))
    return out


def interim(repo):
    tree = ast.parse((repo / "integrations/vllm/tests/lint/_imports.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("INTERIM_LAYER", "LAYER"):
            return ast.literal_eval(node.value)


def layer_of(m, table):
    parts = m.split(".")
    for i in range(len(parts), 0, -1):
        hit = table.get(".".join(parts[:i]))
        if hit:
            return hit
    raise KeyError(m)


def short(m):
    return m if m == "verity_vllm" else m.removeprefix("verity_vllm.")


def main():
    repo = Path(sys.argv[1]).resolve()
    group = sys.argv[2]
    maps = Maps(json.load(open(f"/tmp/a4-map-{group}.json")))
    integ = repo / "integrations/vllm"
    adir = integ / "tests/lint/allowlists"
    pkg = integ / "verity_vllm"
    known, es = G.edges(pkg)
    rel_of = {m: str(p.relative_to(integ)) for m, p in known.items()}
    for f in sorted(adir.glob("*.json")):
        data = json.loads(f.read_text())
        before = len(data["entries"])
        new_entries = []
        for e in data["entries"]:
            e = dict(e)
            if e["file"].startswith("verity_vllm/"):
                e["file"] = maps.path(e["file"])
                if not e["file"].startswith("verity_vllm/"):
                    print(f"  {f.name}: drop {e['kind']} {e['detail']!r} ({e['file']} left the library)")
                    continue
            if f.name == "p09_layering.json" and e["kind"] == "layer":
                a, b = e["detail"].split(" -> ")
                e["detail"] = f"{maps.short(a)} -> {maps.short(b)}"
            elif f.name == "p09_layering.json" and e["kind"] in ("package-cycle", "module-cycle"):
                continue
            elif f.name == "p11_names.json" and e["kind"] == "module-name":
                stem = e["file"].rsplit("/", 1)[-1].removesuffix(".py")
                if not bad_name(stem):
                    print(f"  {f.name}: drop module-name {e['detail']} (now {stem})")
                    continue
                e["detail"] = stem
            elif f.name == "p12_shared_keys.json" and e["kind"] == "root-list":
                pass
            else:
                e["detail"] = maps.text(e["detail"])
            new_entries.append(e)
        if f.name == "p12_shared_keys.json":
            # recompute root-list details from the (rewritten) sources, per file, in source order
            byfile = {}
            for e in new_entries:
                if e["kind"] == "root-list":
                    byfile.setdefault(e["file"], []).append(e)
            for fn, es_ in byfile.items():
                got = root_lists((integ / fn).read_text())
                for e in es_:
                    cands = [d for s, d in got if s == e["symbol"]]
                    if e["detail"] in cands:
                        continue
                    guess = maps.text(e["detail"])
                    match = [d for d in cands if d == guess or d.startswith(guess[:60])]
                    if len(match) == 1:
                        e["detail"] = match[0]
                    else:
                        print(f"  p12: cannot place {fn} {e['symbol']} {e['detail']!r}; candidates {cands}")
        if f.name == "p09_layering.json":
            # layer entries: check against the graph and the (rewritten) layer map
            table = interim(repo)
            want = {}
            for a, b, fl, ln in es:
                if RANK[layer_of(a, table)] < RANK[layer_of(b, table)] and (a, b) not in want:
                    want[(a, b)] = (rel_of[a], f"{short(a)} -> {short(b)}")
            have = {(e["file"], e["detail"]) for e in new_entries if e["kind"] == "layer"}
            wantset = set(want.values())
            for x in sorted(wantset - have):
                print("  p09 layer MISSING", x)
            for x in sorted(have - wantset):
                print("  p09 layer STALE", x)
            adj = {}
            for a, b, *_ in es:
                adj.setdefault(a, set()).add(b)
            for c in G.package_cycles(es):
                new_entries.append({"file": "verity_vllm", "kind": "package-cycle", "symbol": "<package>", "detail": c})
            for comp in G.sccs(set(known), adj):
                new_entries.append({"file": "verity_vllm", "kind": "module-cycle", "symbol": "<package>",
                                    "detail": " <-> ".join(short(m) for m in comp)})
        keys = {}
        for e in new_entries:
            k = (e["file"], e["kind"], e["symbol"], e["detail"])
            if k in keys:
                keys[k]["count"] = keys[k].get("count", 1) + e.get("count", 1)
                print(f"  {f.name}: merged duplicate {k}")
            else:
                keys[k] = e
        kf = lambda e: (e["file"], e["kind"], e["symbol"], e["detail"])  # noqa: E731
        was_sorted = [kf(e) for e in data["entries"]] == sorted(kf(e) for e in data["entries"])
        new_entries = sorted(keys.values(), key=kf) if was_sorted else list(keys.values())
        if new_entries != data["entries"]:
            data["entries"] = new_entries
            body = ",\n".join("    " + json.dumps(e, ensure_ascii=False) for e in new_entries)
            head = {k: v for k, v in data.items() if k != "entries"}
            text = "{\n" + "".join(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},\n" for k, v in head.items()) \
                + '  "entries": [\n' + body + "\n  ]\n}\n"
            f.write_text(text)
            print(f"{f.name}: {before} -> {len(new_entries)} entries")


if __name__ == "__main__":
    main()
