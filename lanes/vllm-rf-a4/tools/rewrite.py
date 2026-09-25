"""Apply one group of the move map to the worktree: git mv, then rewrite every reference (line counts preserved).

usage: python rewrite.py REPO GROUP [--dry]

Never imports verity_vllm.  Import statements are rewritten from the AST (relative imports of moved files or to moved
modules become absolute); everything else gets a longest-prefix rewrite of dotted module names
(``[integrations.vllm.]verity_vllm.a.b``) and of paths (``verity_vllm/a/b.py``).
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import movemap as M  # noqa: E402

TEXT_SUFFIXES = {".py", ".sh", ".json", ".txt", ".toml", ".cfg", ".ini", ".yaml", ".yml", ".diff", ".cpp", ".cu", ".h"}
SCOPES = ("integrations/vllm/", "tools/research/", "packages/verity/src/", "backends/sp1/common/src/")
DOTTED = re.compile(r"(?<![\w.])((?:integrations\.vllm\.)?verity_vllm(?:\.\w+)+)")
PATH = re.compile(r"(?<![\w.])(verity_vllm/[\w./*\-]*)")
FROM_HEAD = re.compile(r"from\s+([.\w]+)\s+import\b")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def mod_of(rel: str) -> str:
    """verity_vllm-relative .py path -> module name."""
    parts = ["verity_vllm", *Path(rel).with_suffix("").parts]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


class Plan:
    def __init__(self, repo: Path, group: str):
        self.repo = repo
        self.pkg = repo / "integrations/vllm/verity_vllm"
        moves = dict(M.GROUPS)[group]
        tracked = git(repo, "ls-files", "integrations/vllm/verity_vllm").splitlines()
        rels = [t.removeprefix("integrations/vllm/verity_vllm/") for t in tracked]
        self.known = {mod_of(r) for r in rels if r.endswith(".py")}
        self.dir_moves: list[tuple[str, str]] = []     # (old dir, new dir), rel to verity_vllm
        final: dict[str, str] = {}                     # original file -> current destination, applied in order
        for old, new in moves:
            if (self.pkg / old).is_dir():
                self.dir_moves.append((old, new))
                for k, v in list(final.items()):
                    if v.startswith(old + "/"):
                        final[k] = new + v[len(old):]
                for r in rels:
                    if r.startswith(old + "/") and r not in final:
                        final[r] = new + r[len(old):]
            else:
                assert (self.pkg / old).exists(), old
                final[old] = new
        self.to_tests = {}
        if group == "collectives":
            for o, n in M.TO_TESTS:
                self.to_tests[o] = n
        self.final = final
        self.modmap = {mod_of(o): mod_of(n) for o, n in final.items() if o.endswith(".py")}
        self.pathmap = {f"verity_vllm/{o}": f"verity_vllm/{n}" for o, n in final.items()}
        for o, n in final.items():
            if o.endswith(".py") and not o.endswith("__init__.py"):
                self.pathmap[f"verity_vllm/{o[:-3]}"] = f"verity_vllm/{n[:-3]}"
        for d_old, d_new in self.dir_moves:
            self.pathmap[f"verity_vllm/{d_old}"] = f"verity_vllm/{d_new}"
        self.new_of_old_file = {f"integrations/vllm/verity_vllm/{o}": f"integrations/vllm/verity_vllm/{n}" for o, n in final.items()}
        for o, n in self.to_tests.items():
            self.modmap[mod_of(o.removeprefix("verity_vllm/"))] = n.removesuffix(".py").replace("/", ".")
            self.pathmap[o] = n
            self.pathmap[o[:-3]] = n[:-3]
            self.new_of_old_file[f"integrations/vllm/{o}"] = f"integrations/vllm/{n}"
        self.old_of_new_file = {v: k for k, v in self.new_of_old_file.items()}
        self.flags: list[str] = []

    # --- name maps ------------------------------------------------------------------------------------------------------
    def ren_mod(self, name: str) -> str:
        pre = ""
        if name.startswith("integrations.vllm."):
            pre, name = "integrations.vllm.", name[len("integrations.vllm."):]
        parts = name.split(".")
        for i in range(len(parts), 0, -1):
            k = ".".join(parts[:i])
            if k in self.modmap:
                return pre + ".".join([self.modmap[k], *parts[i:]])
        return pre + name

    def ren_path(self, p: str) -> str:
        tail = ""
        while p and p[-1] in ".":
            tail, p = p[-1] + tail, p[:-1]
        best = None
        for k in self.pathmap:
            if (p == k or p.startswith(k + "/")) and (best is None or len(k) > len(best)):
                best = k
        if best is None:
            return p + tail
        return self.pathmap[best] + p[len(best):] + tail

    # --- text rewriting -------------------------------------------------------------------------------------------------
    def sub_text(self, s: str) -> str:
        s = DOTTED.sub(lambda m: self.ren_mod(m.group(1)), s)
        return PATH.sub(lambda m: self.ren_path(m.group(1)), s)

    def rewrite_imports(self, text: str, old_file: str | None, cur_file: str) -> tuple[str, list[tuple[int, int]]]:
        """Rewrite ImportFrom statements; returns (text, list of (start, end) offsets of every verity ImportFrom)."""
        try:
            tree = ast.parse(text)
        except SyntaxError as e:
            self.flags.append(f"SYNTAX {cur_file}: {e}")
            return text, []
        lines = text.splitlines(keepends=True)
        starts = [0]
        for ln in lines:
            starts.append(starts[-1] + len(ln))

        def off(lineno: int, col: int) -> int:
            # ast col offsets are utf-8 byte offsets
            line = lines[lineno - 1]
            return starts[lineno - 1] + len(line.encode("utf-8")[:col].decode("utf-8", errors="ignore"))

        in_pkg = old_file is not None and old_file.startswith("integrations/vllm/verity_vllm/")
        old_mod = mod_of(old_file.removeprefix("integrations/vllm/verity_vllm/")) if in_pkg else None
        is_pkg = in_pkg and old_file.endswith("__init__.py")
        file_moved = in_pkg and old_file != cur_file
        edits: list[tuple[int, int, str]] = []
        spans: list[tuple[int, int]] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            prefix = ""
            if node.level:
                if not in_pkg:
                    continue
                pk = old_mod if is_pkg else old_mod.rpartition(".")[0]
                anchor = pk.split(".")[: len(pk.split(".")) - node.level + 1]
                base = ".".join([*anchor, *([node.module] if node.module else [])])
            else:
                base = node.module or ""
                if base.startswith("integrations.vllm."):
                    prefix, base = "integrations.vllm.", base[len("integrations.vllm."):]
            if not (base == "verity_vllm" or base.startswith("verity_vllm.")):
                continue
            s, e = off(node.lineno, node.col_offset), off(node.end_lineno, node.end_col_offset)
            spans.append((s, e))
            parts = []  # (new_from, new_name, asname, alias node, changed_name)
            changed = bool(node.level) and (file_moved or False)
            for a in node.names:
                full = f"{base}.{a.name}"
                if a.name != "*" and full in self.known:
                    new = self.ren_mod(full)
                    nf, _, nn = new.rpartition(".")
                    parts.append((nf, nn, a.asname, a))
                    if new != full:
                        changed = True
                else:
                    nf = self.ren_mod(base)
                    parts.append((nf, a.name, a.asname, a))
                    if nf != base:
                        changed = True
            if not changed:
                continue
            froms = []
            for p in parts:
                if not froms or froms[-1] != p[0]:
                    froms.append(p[0])
            stmt = text[s:e]
            if len(set(froms)) == 1:
                # in place: module text, then renamed alias names
                m = FROM_HEAD.match(stmt)
                assert m, stmt
                local: list[tuple[int, int, str]] = [(s + m.start(1), s + m.end(1), prefix + froms[0])]
                for nf, nn, asn, a in parts:
                    if nn != a.name:
                        a_s = off(a.lineno, a.col_offset)
                        a_e = a_s + len(a.name)
                        assert text[a_s:a_e] == a.name, (cur_file, text[a_s:a_e], a.name)
                        local.append((a_s, a_e, nn if asn else f"{nn} as {a.name}"))
                edits += local
            else:
                groups: list[tuple[str, list[str]]] = []
                for nf, nn, asn, a in parts:
                    item = nn + (f" as {asn}" if asn else (f" as {a.name}" if nn != a.name else ""))
                    if groups and groups[-1][0] == nf:
                        groups[-1][1].append(item)
                    else:
                        groups.append((nf, [item]))
                new_stmt = "; ".join(f"from {prefix}{g} import {', '.join(items)}" for g, items in groups)
                pad = "\n" * (node.end_lineno - node.lineno)
                edits.append((s, e, new_stmt + pad))
                self.flags.append(f"SPLIT {cur_file}:{node.lineno}: {new_stmt}")
        for s, e, r in sorted(edits, reverse=True):
            text = text[:s] + r + text[e:]
        # recompute spans on the edited text: every verity ImportFrom, so the generic pass skips them
        try:
            tree2 = ast.parse(text)
        except SyntaxError as ex:
            self.flags.append(f"SYNTAX-AFTER {cur_file}: {ex}")
            return text, []
        lines = text.splitlines(keepends=True)
        starts = [0]
        for ln in lines:
            starts.append(starts[-1] + len(ln))
        spans = []
        for node in ast.walk(tree2):
            if isinstance(node, ast.ImportFrom) and (node.level and in_pkg or (node.module or "").split(".")[0] in ("verity_vllm", "integrations")):
                spans.append((off(node.lineno, node.col_offset), off(node.end_lineno, node.end_col_offset)))
        return text, sorted(spans)

    def rewrite_file(self, cur_file: str) -> bool:
        p = self.repo / cur_file
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            return False
        orig = text
        spans: list[tuple[int, int]] = []
        if cur_file.endswith(".py"):
            text, spans = self.rewrite_imports(text, self.old_of_new_file.get(cur_file, cur_file), cur_file)
        out, pos = [], 0
        for s, e in spans:
            out.append(self.sub_text(text[pos:s]))
            out.append(PATH.sub(lambda m: self.ren_path(m.group(1)), text[s:e]))
            pos = e
        out.append(self.sub_text(text[pos:]))
        text = "".join(out)
        if text != orig:
            assert text.count("\n") == orig.count("\n"), f"line count changed: {cur_file}"
            p.write_text(text, encoding="utf-8")
            return True
        return False


def main():
    repo = Path(sys.argv[1]).resolve()
    group = sys.argv[2]
    dry = "--dry" in sys.argv
    plan = Plan(repo, group)
    print(f"{group}: {len(plan.final)} files, {len(plan.modmap)} modules")
    for k, v in sorted(plan.modmap.items()):
        print(f"  {k} -> {v}")
    if dry:
        return
    pkg = plan.pkg
    for old, new in [(o, n) for o, n in dict(M.GROUPS)[group]]:
        src, dst = pkg / old, pkg / new
        if not src.exists():
            continue   # already carried by an earlier entry
        dst.parent.mkdir(parents=True, exist_ok=True)
        git(repo, "mv", str(src), str(dst))
    for init, doc in M.NEW_INITS.items():
        d = pkg / init
        if d.parent.is_dir() and not d.exists():
            d.write_text(f'"""{doc}"""\n', encoding="utf-8")
            git(repo, "add", str(d))
    for rel in M.DELETED_INITS:
        d = pkg / rel
        if d.exists() and not [x for x in d.parent.iterdir() if x.name not in ("__init__.py", "__pycache__")]:
            git(repo, "rm", "-q", str(d))
    for src_rel, dst_rel in M.TO_TESTS:
        src = repo / "integrations/vllm" / src_rel
        if group == "collectives" and src.exists():
            dst = repo / "integrations/vllm" / dst_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            git(repo, "mv", str(src), str(dst))
    files = [f for f in git(repo, "ls-files").splitlines()
             if f.startswith(SCOPES) and (Path(f).suffix in TEXT_SUFFIXES or Path(f).name in (".gitignore", "README.md"))]
    files += [f for f in git(repo, "ls-files", "--others", "--exclude-standard").splitlines() if f.endswith(".py") and f.startswith(SCOPES)]
    n = 0
    for f in sorted(set(files)):
        if f.startswith("integrations/vllm/tests/lint/allowlists/"):
            continue
        if plan.rewrite_file(f):
            n += 1
    print(f"rewrote {n} files")
    json.dump({"modmap": plan.modmap, "pathmap": plan.pathmap}, open(f"/tmp/a4-map-{group}.json", "w"), indent=1)
    for fl in plan.flags:
        print("FLAG", fl)


if __name__ == "__main__":
    main()
