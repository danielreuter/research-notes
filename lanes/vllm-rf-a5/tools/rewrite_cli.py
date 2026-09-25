"""Rewrite a library module's argparse main into an options dataclass + run(options).  No verity_vllm import.

usage: rewrite_cli.py ROOT FILE [FILE ...]      (ROOT = integrations/vllm; FILE relative to ROOT)
Prints one report line per file; files it cannot convert safely are left untouched and reported as SKIP.
"""
from __future__ import annotations

import ast
import keyword
import re
import sys
from pathlib import Path

WIDTH = 128
KNOWN_KW = {"default", "help", "type", "action", "required", "choices", "nargs", "metavar", "dest"}


def seg(src: str, node: ast.AST) -> str:
    return ast.get_source_segment(src, node)


def is_parser_call(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and (ast.unparse(node.func).endswith("ArgumentParser"))


def camel(name: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in re.split(r"[-_]", name) if p)


class Skip(Exception):
    pass


def env_default(v: ast.AST):
    """os.environ.get("X", d) / int(os.environ.get("X", "8")) / os.environ.get("X") or None -> (X, default source)."""
    def get_call(n):
        if isinstance(n, ast.Call) and ast.unparse(n.func) in ("os.environ.get", "os.getenv"):
            name = n.args[0].value
            d = seg_src(n.args[1]) if len(n.args) > 1 else "None"
            return name, d
        return None
    if isinstance(v, ast.BoolOp) and isinstance(v.op, ast.Or) and len(v.values) == 2 and ast.unparse(v.values[1]) == "None":
        g = get_call(v.values[0])
        if g:
            return g[0], "None"
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in ("int", "float") and len(v.args) == 1:
        g = get_call(v.args[0])
        if g:
            d = ast.literal_eval(g[1])
            return g[0], repr(type(0 if v.func.id == "int" else 0.0)(d)) if d is not None else "None"
    return get_call(v)


SRC = ""


def seg_src(n):
    return seg(SRC, n)


class Arg:
    def __init__(self, call: ast.Call, src: str):
        self.call = call
        self.flags = [a for a in call.args]
        if not self.flags or not all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in self.flags):
            raise Skip(f"add_argument with non-literal flags at line {call.lineno}")
        self.kw = {k.arg: k.value for k in call.keywords}
        if None in self.kw or set(self.kw) - KNOWN_KW:
            raise Skip(f"add_argument kwargs {sorted(k for k in self.kw if k)} at line {call.lineno}")
        flags = [a.value for a in self.flags]
        self.positional = not flags[0].startswith("-")
        if "dest" in self.kw:
            self.name = self.kw["dest"].value
        elif self.positional:
            self.name = flags[0]
        else:
            longs = [f for f in flags if f.startswith("--")]
            self.name = (longs[0] if longs else flags[0]).lstrip("-").replace("-", "_")
        if keyword.iskeyword(self.name) or not self.name.isidentifier():
            raise Skip(f"dest {self.name!r} is not an identifier")

    def annotation(self) -> str:
        kw = self.kw
        action = kw["action"].value if "action" in kw else None
        base = {"int": "int", "float": "float", "Path": "Path"}.get(ast.unparse(kw["type"]) if "type" in kw else "", "str")
        if "type" in kw and ast.unparse(kw["type"]) not in ("int", "float", "Path"):
            raise Skip(f"type={ast.unparse(kw['type'])}")
        if action in ("store_true", "store_false"):
            return "bool"
        nargs = kw["nargs"].value if "nargs" in kw else None
        listy = action == "append" or nargs in ("+", "*") or isinstance(nargs, int)
        t = f"list[{base}]" if listy else base
        d = self.default_src()
        if d == "None" or (d is None and False):
            t += " | None"
        return t

    def default_src(self) -> str | None:
        """Source of the field default; None = required."""
        kw = self.kw
        if "default" in kw:
            e = env_default(kw["default"])
            if e:
                return e[1]
            return seg_src(kw["default"])
        action = kw["action"].value if "action" in kw else None
        if action == "store_true":
            return "False"
        if action == "store_false":
            return "True"
        if "required" in kw and ast.unparse(kw["required"]) == "True":
            return None
        nargs = kw["nargs"].value if "nargs" in kw else None
        if self.positional:
            if nargs == "?":
                return "None"
            if nargs == "*":
                return "[]"
            return None
        return "None"

    def render(self, indent: str) -> str:
        parts: list[str] = [seg_src(f) for f in self.flags]
        d = self.default_src()
        inserted = False
        env = env_default(self.kw["default"]) if "default" in self.kw else None
        for k in self.call.keywords:
            if k.arg == "dest":
                continue
            if k.arg == "default":
                if env:
                    parts.append(f'env="{env[0]}"')
                    parts.append(f"default={env[1]}")
                else:
                    parts.append(f"default={seg_src(k.value)}")
                continue
            if k.arg == "required" and d is None:
                continue
            parts.append(f"{k.arg}={seg_src(k.value)}")
        if "default" not in self.kw and d is not None:
            parts.insert(len(self.flags), f"default={d}")
            inserted = True
        head = f"{indent}{self.name}: {self.annotation()} = option("
        return wrap(head, parts, self.call)


def wrap(head: str, parts: list[str], call: ast.Call) -> str:
    cont = " " * len(head)
    lines = [head]
    for i, p in enumerate(parts):
        piece = p + (", " if i < len(parts) - 1 else ")")
        if "\n" in p:
            # a multi-line segment: own continuation line, inner lines shifted to keep their relative alignment
            node_col = None
            first, *rest = p.split("\n")
            rest_lines = []
            base = min((len(r) - len(r.lstrip()) for r in rest if r.strip()), default=0)
            m = re.match(r"\w+=", first)
            pad = " " * (len(m.group(0)) if m else 0)
            for r in rest:
                rest_lines.append(cont + pad + r[base:] if r.strip() else r)
            block = first + "\n" + "\n".join(rest_lines)
            block += (", " if i < len(parts) - 1 else ")")
            if lines[-1].strip() and lines[-1] != head:
                lines.append(cont)
            if lines[-1] == head:
                lines[-1] += block
            else:
                lines[-1] = cont + block
            lines.append(cont)
            continue
        if len(lines[-1]) + len(piece.rstrip()) > WIDTH and lines[-1].strip() and lines[-1] not in (head, cont):
            lines[-1] = lines[-1].rstrip()
            lines.append(cont)
        lines[-1] += piece
    out = [ln.rstrip() for ln in lines if ln.strip()]
    return "\n".join(out)


def convert(root: Path, rel: str) -> str:
    global SRC
    path = root / rel
    src = path.read_text()
    SRC = src
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)

    mains = [n for n in tree.body if isinstance(n, ast.If) and "__main__" in ast.unparse(n.test) and "__name__" in ast.unparse(n.test)]
    fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and any(is_parser_call(c) for c in ast.walk(n))]
    if len(fns) != 1:
        raise Skip(f"{len(fns)} functions build a parser")
    fn = fns[0]
    if fn not in tree.body:
        raise Skip("parser function is not top-level")
    body = fn.body
    doc_i = 1 if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str) else 0

    parser = None
    parser_kw: dict[str, ast.AST] = {}
    subs_var = None
    sub_dest = None
    subparsers: dict[str, tuple[str, ast.Call]] = {}   # var -> (name, call)
    order: list[str] = []
    args_by: dict[str | None, list[Arg]] = {None: []}
    remove: list[ast.stmt] = []
    args_var = None
    parse_stmt = None
    for st in body:
        if isinstance(st, ast.Import) and [a.name for a in st.names] == ["argparse"]:
            remove.append(st)
            continue
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) and is_parser_call(st.value):
            parser = st.targets[0].id
            parser_kw = {k.arg: k.value for k in st.value.keywords}
            if st.value.args:
                raise Skip("ArgumentParser positional args")
            remove.append(st)
            continue
        if parser is None:
            continue
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name) and isinstance(st.value, ast.Call) \
                and isinstance(st.value.func, ast.Attribute):
            owner = ast.unparse(st.value.func.value)
            m = st.value.func.attr
            if owner == parser and m == "add_subparsers":
                subs_var = st.targets[0].id
                kw = {k.arg: k.value for k in st.value.keywords}
                if "dest" not in kw:
                    raise Skip("add_subparsers without dest")
                sub_dest = kw["dest"].value
                remove.append(st)
                continue
            if owner == subs_var and m == "add_parser":
                name = st.value.args[0].value
                subparsers[st.targets[0].id] = (name, st.value)
                order.append(st.targets[0].id)
                args_by[st.targets[0].id] = []
                remove.append(st)
                continue
            if m == "parse_args" and owner == parser:
                args_var = st.targets[0].id
                parse_stmt = st
                remove.append(st)
                break
            if m == "parse_known_args":
                raise Skip("parse_known_args")
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Attribute) \
                and st.value.func.attr == "add_argument":
            owner = ast.unparse(st.value.func.value)
            if owner == parser:
                args_by[None].append(Arg(st.value, src))
            elif owner in subparsers:
                args_by[owner].append(Arg(st.value, src))
            else:
                raise Skip(f"add_argument on {owner}")
            remove.append(st)
            continue
        if isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Attribute) \
                and st.value.func.attr == "add_parser" and ast.unparse(st.value.func.value) == subs_var:
            raise Skip("add_parser without a variable")
        if isinstance(st, (ast.Expr, ast.Assign)) and ("add_argument" in ast.unparse(st) or "add_parser" in ast.unparse(st)):
            raise Skip(f"unhandled parser statement at line {st.lineno}: {ast.unparse(st)[:80]}")
        # a non-parser statement between the parser and parse_args
        raise Skip(f"statement between parser and parse_args at line {st.lineno}: {ast.unparse(st)[:80]}")
    if parse_stmt is None:
        raise Skip("no parse_args assignment")
    call = parse_stmt.value
    if call.args and not (isinstance(call.args[0], ast.Name) and call.args[0].id == "argv"):
        raise Skip(f"parse_args({ast.unparse(call.args[0])})")

    # remaining uses of the parser / subparser vars
    uses_error = False
    edits: list[tuple[int, int, int, int, str]] = []    # (l0, c0, l1, c1, text) 1-based lines
    err_names = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) \
                and n.value.func.attr == "error" and ast.unparse(n.value.func.value) == parser:
            err_names.add(id(n.value.func.value))
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and n.id in ({parser} | set(subparsers) | ({subs_var} if subs_var else set())):
            if any(n in list(ast.walk(r)) for r in remove) or id(n) in err_names:
                continue
            raise Skip(f"parser variable {n.id} used at line {n.lineno}")
    # ap.error(...) statements -> raise UsageError(...)
    for n in ast.walk(fn):
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Attribute) \
                and n.value.func.attr == "error" and ast.unparse(n.value.func.value) == parser:
            pass
    # recheck: parser uses remaining = error calls; handled textually below
    # description
    desc = parser_kw.get("description")
    desc_doc = None
    if desc is not None:
        u = ast.unparse(desc)
        if "__doc__" not in u:
            desc_doc = seg(src, desc)

    fn_names = {fn.name}
    other_calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in fn_names
                   and not any(n in list(ast.walk(m)) for m in mains)]
    if other_calls:
        raise Skip(f"{fn.name}() called inside the module at line {other_calls[0].lineno}")
    for m in mains:
        inner = [s for s in m.body]
        txt = ast.unparse(m)
        if len(inner) != 1 or fn.name not in txt:
            raise Skip(f"main block does more than call {fn.name}: {txt[:120]!r}")

    ind = "    "
    classes: list[str] = []

    def cls_text(name: str, doc: str | None, argl: list[Arg], fixed: tuple[str, str] | None) -> str:
        out = ["@dataclass(frozen=True, kw_only=True)", f"class {name}:"]
        if doc:
            try:
                val = ast.literal_eval("(" + doc + ")")
            except (ValueError, SyntaxError):
                raise Skip(f"non-literal description for {name}")
            val = " ".join(val.split()) if "\n" not in val.strip() else val.strip()
            if "\n" in val:
                out.append(f'{ind}"""' + val.replace("\n", "\n" + ind) + '"""')
            else:
                import textwrap
                w = textwrap.wrap(val, WIDTH - len(ind) - 6)
                if len(w) == 1:
                    out.append(f'{ind}"""{w[0]}"""')
                else:
                    out.append(f'{ind}"""{w[0]}')
                    out += [f"{ind}{x}" for x in w[1:-1]]
                    out.append(f'{ind}{w[-1]}"""')
            if argl or fixed:
                out.append("")
        for a in argl:
            out.append(a.render(ind))
        if fixed:
            out.append(f'{ind}{fixed[0]}: str = field(default="{fixed[1]}", init=False)')
        if not argl and not fixed and not doc:
            out.append(f"{ind}pass")
        return "\n".join(out)

    if subparsers:
        names = []
        seen = set()
        for var in order:
            sname, scall = subparsers[var]
            skw = {k.arg: k.value for k in scall.keywords}
            sdoc = None
            for k in ("description", "help"):
                if k in skw and "__doc__" not in ast.unparse(skw[k]):
                    sdoc = seg(src, skw[k])
                    break
            cname = camel(sname) + "Options"
            if cname in seen:
                raise Skip("duplicate subcommand class")
            seen.add(cname)
            names.append((sname, cname))
            dupe = {a.name for a in args_by[None]} & {a.name for a in args_by[var]}
            if dupe:
                raise Skip(f"parent and subparser share {dupe}")
            classes.append(cls_text(cname, sdoc, args_by[None] + args_by[var], (sub_dest, sname)))
        classes.append("COMMANDS = {" + ", ".join(f'"{s}": {c}' for s, c in names) + "}")
        ann = " | ".join(c for _, c in names)
        if len(ann) > 60:
            ann = "Any"
    else:
        classes.append(cls_text("Options", desc_doc, args_by[None], None))
        ann = "Options"

    # --- text edits
    # 1. function header -> run(args_var: ann) -> <returns>
    ret = f" -> {seg(src, fn.returns)}" if fn.returns is not None else ""
    header_l0 = fn.lineno
    body_first = body[doc_i] if doc_i < len(body) else body[0]
    # the def line(s) end at the line before the first body statement (or docstring)
    first_stmt = body[0]
    header_l1 = first_stmt.lineno - 1
    hdr_lines = lines[header_l0 - 1:header_l1]
    hdr = "".join(hdr_lines)
    if not hdr.rstrip().endswith(":"):
        raise Skip("cannot find the def header end")
    new_hdr = f"def run({args_var}: {ann}){ret}:\n"
    # decorators? none expected
    if fn.decorator_list:
        raise Skip("decorated main")
    rm_lines: set[int] = set()
    for st in remove:
        for ln in range(st.lineno, st.end_lineno + 1):
            rm_lines.add(ln)
    # comment lines inside the removed parser block are dropped with it (a comment between two add_argument lines)
    if remove:
        lo = min(st.lineno for st in remove if st is not None)
        hi = parse_stmt.end_lineno
        for ln in range(lo, hi + 1):
            if lines[ln - 1].strip().startswith("#") or not lines[ln - 1].strip():
                rm_lines.add(ln)
    for m in mains:
        for ln in range(m.lineno, m.end_lineno + 1):
            rm_lines.add(ln)
    # module-level import argparse
    for n in tree.body:
        if isinstance(n, ast.Import) and [a.name for a in n.names] == ["argparse"]:
            rm_lines.add(n.lineno)
        elif isinstance(n, ast.Import) and "argparse" in [a.name for a in n.names]:
            raise Skip("import argparse, ...")
    out: list[str] = []
    i = 1
    n_lines = len(lines)
    body_text: list[str] = []
    while i <= n_lines:
        if i == header_l0:
            out.append("\n".join(classes) + "\n\n\n")
            out.append(new_hdr)
            i = header_l1 + 1
            continue
        if i in rm_lines:
            i += 1
            continue
        out.append(lines[i - 1])
        i += 1
    text = "".join(out)
    # ap.error( -> raise UsageError(
    n_err = len(re.findall(rf"(?m)^(\s*){re.escape(parser)}\.error\(", text))
    text = re.sub(rf"(?m)^(\s*){re.escape(parser)}\.error\(", r"\1raise UsageError(", text)
    if re.search(rf"\b{re.escape(parser)}\.", text[text.index(new_hdr):]):
        raise Skip(f"parser {parser} still used after the rewrite (non-statement error call?)")
    # imports
    need = ["option"] + (["UsageError"] if n_err else [])
    dc = "from dataclasses import dataclass, field" if subparsers else "from dataclasses import dataclass"
    text = add_imports(text, dc, f"from verity_vllm.config import {', '.join(sorted(need, key=str.lower))}", uses_any=(ann == "Any"))
    text = re.sub(r"\n{4,}", "\n\n\n", text).rstrip("\n") + "\n"
    ast.parse(text)
    path.write_text(text)
    nargs = sum(len(v) for v in args_by.values())
    return f"OK   {rel}: {fn.name} -> run({args_var}: {ann}); {nargs} options; {len(subparsers)} subcommands; {n_err} error->UsageError"


def add_imports(text: str, dc_line: str, cfg_line: str, uses_any: bool) -> str:
    tree = ast.parse(text)
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    lines = text.splitlines(keepends=True)
    # merge into an existing `from dataclasses import ...`
    have_dc = [n for n in top if isinstance(n, ast.ImportFrom) and n.module == "dataclasses"]
    want = {"dataclass"} | ({"field"} if "field" in dc_line else set())
    if have_dc:
        n = have_dc[0]
        names = {a.name for a in n.names} | want
        lines[n.lineno - 1] = "from dataclasses import " + ", ".join(sorted(names)) + "\n"
        for ln in range(n.lineno + 1, n.end_lineno + 1):
            lines[ln - 1] = ""
        dc_line = None
    if uses_any:
        have_t = [n for n in top if isinstance(n, ast.ImportFrom) and n.module == "typing"]
        if have_t and "Any" not in {a.name for a in have_t[0].names}:
            n = have_t[0]
            names = {a.name for a in n.names} | {"Any"}
            lines[n.lineno - 1] = "from typing import " + ", ".join(sorted(names)) + "\n"
            for ln in range(n.lineno + 1, n.end_lineno + 1):
                lines[ln - 1] = ""
        elif not have_t:
            dc_line = (dc_line + "\nfrom typing import Any") if dc_line else "from typing import Any"
    std = [n for n in top if not (isinstance(n, ast.ImportFrom) and (n.module or "").startswith("verity"))
           and not (isinstance(n, ast.ImportFrom) and n.module == "__future__")]
    first_party = [n for n in top if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("verity_vllm")]
    ins: dict[int, list[str]] = {}
    if dc_line:
        anchor = max((n.end_lineno for n in std), default=None)
        if anchor is None:
            fut = [n for n in top if isinstance(n, ast.ImportFrom) and n.module == "__future__"]
            anchor = fut[-1].end_lineno if fut else (tree.body[0].end_lineno if isinstance(tree.body[0], ast.Expr) else 0)
        ins.setdefault(anchor, []).append(dc_line + "\n")
    if first_party:
        # alphabetical position among the first-party block, else after it
        pos = first_party[-1].end_lineno
        for n in first_party:
            if (n.module or "") > "verity_vllm.config":
                pos = n.lineno - 1
                break
        ins.setdefault(pos, []).append(cfg_line + "\n")
    else:
        anchor = max((n.end_lineno for n in top), default=0)
        if dc_line and anchor in ins:
            ins[anchor].append("\n" + cfg_line + "\n")
        else:
            ins.setdefault(anchor, []).append(("\n" if top else "") + cfg_line + "\n")
    out = []
    if 0 in ins:
        out.extend(ins[0])
    for i, ln in enumerate(lines, 1):
        out.append(ln)
        if i in ins and i != 0:
            out.extend(ins[i])
    return "".join(out)


def main() -> None:
    root = Path(sys.argv[1])
    for rel in sys.argv[2:]:
        try:
            print(convert(root, rel))
        except Skip as e:
            print(f"SKIP {rel}: {e}")


if __name__ == "__main__":
    main()
